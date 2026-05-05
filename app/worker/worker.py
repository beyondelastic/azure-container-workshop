"""Batch triage worker — processes queued patient records.

Used in Container Apps Jobs lesson (09) to demonstrate scheduled
and manual-trigger jobs.
"""

import json
import os
import sys
from datetime import datetime, timezone

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

SYSTEM_PROMPT = """You are a clinical triage assistant performing batch review.
Given a list of patient records with symptoms, produce a JSON array of objects:
[{"patient": "<name>", "urgency": "<Critical|High|Medium|Low>", "summary": "<one line>"}]
Respond with ONLY the JSON array."""

SAMPLE_PATIENTS = [
    {"name": "Maria Garcia", "age": 67, "symptoms": "chest tightness, shortness of breath, dizziness"},
    {"name": "James Wilson", "age": 34, "symptoms": "mild headache, runny nose, sneezing for 2 days"},
    {"name": "Aiko Tanaka", "age": 52, "symptoms": "severe abdominal pain, nausea, fever 39.2°C"},
    {"name": "Liam O'Brien", "age": 8, "symptoms": "scraped knee, minor bleeding, no swelling"},
    {"name": "Fatima Al-Rashid", "age": 45, "symptoms": "persistent cough for 3 weeks, night sweats, weight loss"},
]


def run_batch():
    project_client = AIProjectClient(
        endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    client = project_client.inference.get_chat_completions_client()
    deployment = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4.1-mini")

    patient_text = "\n".join(
        f"- {p['name']} (age {p['age']}): {p['symptoms']}" for p in SAMPLE_PATIENTS
    )

    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting batch triage for {len(SAMPLE_PATIENTS)} patients...")

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": patient_text},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    # The model may wrap the array in an object; handle both cases
    parsed = json.loads(content)
    if isinstance(parsed, dict):
        # Find the first list value
        for v in parsed.values():
            if isinstance(v, list):
                parsed = v
                break

    print("\n=== Batch Triage Report ===\n")
    for item in parsed:
        print(f"  [{item.get('urgency', '?'):>8}]  {item.get('patient', '?')} — {item.get('summary', '')}")

    print(f"\n[{datetime.now(timezone.utc).isoformat()}] Batch triage complete. Processed {len(parsed)} records.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run_batch())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
