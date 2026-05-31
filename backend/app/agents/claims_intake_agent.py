import re
import uuid
from typing import Dict, List

from app.llm.local_llm import call_ollama
from app.schemas.claim_schema import ClaimIntakeOutput


def _detect_incident_type(claim_text: str, claim_type: str) -> str:
    text = claim_text.lower()
    if "accident" in text or "bumper" in text or claim_type == "auto":
        return "auto_accident"
    if "water" in text:
        return "water_damage"
    if "fire" in text:
        return "fire_damage"
    return f"{claim_type}_incident"


def _missing_documents(claim_text: str) -> List[str]:
    text = claim_text.lower()
    missing = []
    if "police report" not in text:
        missing.append("police_report")
    if "repair estimate" not in text:
        missing.append("repair_estimate")
    return missing


def extract_claim_facts(claim_text: str, claim_amount: float, claim_type: str, customer_id: str) -> ClaimIntakeOutput:
    incident_type = _detect_incident_type(claim_text, claim_type)
    missing = _missing_documents(claim_text)
    llm_summary = call_ollama(
        prompt=f"Summarize these insurance claim facts in one sentence without making decisions:\n{claim_text}",
        system="You extract and summarize claim facts only. Do not approve or deny claims.",
    )

    extracted_facts: Dict[str, object] = {
        "summary": llm_summary or claim_text[:240],
        "mentions_police_report": "police report" in claim_text.lower(),
        "mentions_repair_estimate": "repair estimate" in claim_text.lower(),
        "detected_amounts": re.findall(r"\$?\d+(?:,\d{3})*(?:\.\d+)?", claim_text),
        "llm_used": bool(llm_summary),
    }
    confidence_score = 0.86 if not missing else 0.72

    return ClaimIntakeOutput(
        claim_id=f"CLM-{uuid.uuid4().hex[:10].upper()}",
        customer_id=customer_id,
        incident_type=incident_type,
        claim_amount=claim_amount,
        extracted_facts=extracted_facts,
        missing_documents=missing,
        confidence_score=confidence_score,
    )

