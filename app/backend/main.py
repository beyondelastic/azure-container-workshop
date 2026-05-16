"""Patient Triage Assistant — FastAPI backend.

Accepts patient symptoms, calls a model deployed in Microsoft Foundry
to classify urgency, and returns structured triage results.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

import requests
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

app = FastAPI(title="Patient Triage API", version="1.0.0")
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# State store — uses Dapr when available, falls back to in-memory
# ---------------------------------------------------------------------------
DAPR_PORT = os.environ.get("DAPR_HTTP_PORT")
DAPR_STATE_URL = f"http://localhost:{DAPR_PORT}/v1.0/state/statestore" if DAPR_PORT else None
PATIENT_INDEX_KEY = "patient-index"

# In-memory fallback (used when Dapr is not available, e.g. AKS lessons)
_patients_memory: dict[str, dict] = {}


def _dapr_available() -> bool:
    return DAPR_STATE_URL is not None


def save_patient(record: dict) -> None:
    """Persist a patient record."""
    if _dapr_available():
        # Save the patient record and update the index
        index = _get_patient_index()
        index.append(record["id"])
        requests.post(DAPR_STATE_URL, json=[
            {"key": record["id"], "value": record},
            {"key": PATIENT_INDEX_KEY, "value": index},
        ], timeout=5)
    else:
        _patients_memory[record["id"]] = record


def get_all_patients() -> list[dict]:
    """Retrieve all patient records."""
    if _dapr_available():
        index = _get_patient_index()
        patients = []
        for patient_id in index:
            resp = requests.get(f"{DAPR_STATE_URL}/{patient_id}", timeout=5)
            if resp.status_code == 200 and resp.text:
                patients.append(resp.json())
        return patients
    else:
        return list(_patients_memory.values())


def clear_all_patients() -> None:
    """Delete all patient records."""
    if _dapr_available():
        index = _get_patient_index()
        for patient_id in index:
            requests.delete(f"{DAPR_STATE_URL}/{patient_id}", timeout=5)
        requests.delete(f"{DAPR_STATE_URL}/{PATIENT_INDEX_KEY}", timeout=5)
    else:
        _patients_memory.clear()


def _get_patient_index() -> list[str]:
    """Get the list of patient IDs from the state store."""
    resp = requests.get(f"{DAPR_STATE_URL}/{PATIENT_INDEX_KEY}", timeout=5)
    if resp.status_code == 200 and resp.text:
        return resp.json()
    return []

# ---------------------------------------------------------------------------
# Microsoft Foundry client
# ---------------------------------------------------------------------------
_openai_client: Optional[OpenAI] = None


def get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        project_client = AIProjectClient(
            endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
            credential=DefaultAzureCredential(),
        )
        _openai_client = project_client.get_openai_client()
    return _openai_client


SYSTEM_PROMPT = """You are a clinical triage assistant. Given a patient's name,
age, and reported symptoms, classify the urgency level as one of:
- Critical  (life-threatening, immediate attention)
- High      (serious, needs attention within 1 hour)
- Medium    (moderate, needs attention within 4 hours)
- Low       (minor, can wait)

Respond with ONLY a JSON object (no markdown, no extra text):
{
  "urgency": "<Critical|High|Medium|Low>",
  "reasoning": "<one-sentence clinical reasoning>"
}"""


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class TriageRequest(BaseModel):
    name: str
    age: int
    symptoms: str


class TriageResult(BaseModel):
    id: str
    name: str
    age: int
    symptoms: str
    urgency: str
    reasoning: str
    timestamp: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return {"status": "healthy"}


@app.post("/api/triage", response_model=TriageResult)
def triage_patient(req: TriageRequest):
    oai = get_openai_client()
    deployment = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4.1-mini")

    try:
        response = oai.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Patient: {req.name}, Age: {req.age}\n"
                        f"Symptoms: {req.symptoms}"
                    ),
                },
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Model call failed: {exc}")

    try:
        result = json.loads(response.choices[0].message.content)
    except (json.JSONDecodeError, IndexError) as exc:
        raise HTTPException(status_code=502, detail=f"Bad model response: {exc}")

    record = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "age": req.age,
        "symptoms": req.symptoms,
        "urgency": result.get("urgency", "Medium"),
        "reasoning": result.get("reasoning", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    save_patient(record)
    return record


@app.get("/api/patients", response_model=list[TriageResult])
def list_patients():
    return sorted(get_all_patients(), key=lambda p: p["timestamp"], reverse=True)


@app.delete("/api/patients")
def clear_patients():
    clear_all_patients()
    return {"status": "cleared"}
