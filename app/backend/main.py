"""Patient Triage Assistant — FastAPI backend.

Accepts patient symptoms, calls a model deployed in Microsoft Foundry
to classify urgency, and returns structured triage results.
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

app = FastAPI(title="Patient Triage API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory store (replaced by Redis/Dapr state store in later lessons)
# ---------------------------------------------------------------------------
patients: dict[str, dict] = {}

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

    import json

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
    patients[record["id"]] = record
    return record


@app.get("/api/patients", response_model=list[TriageResult])
def list_patients():
    return sorted(patients.values(), key=lambda p: p["timestamp"], reverse=True)


@app.delete("/api/patients")
def clear_patients():
    patients.clear()
    return {"status": "cleared"}
