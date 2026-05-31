from app.llm.local_llm import call_ollama
from app.schemas.claim_schema import PolicyEvidence


def retrieve_policy_evidence(claim_type: str, incident_type: str) -> PolicyEvidence:
    if claim_type.lower() == "auto":
        clauses = [
            "AUTO-COLLISION-01 covers sudden and accidental collision damage subject to deductible.",
            "AUTO-DOCS-02 requires repair estimate and police report when applicable.",
        ]
        exclusions = ["Intentional damage", "Unlicensed driver", "Commercial use without endorsement"]
        deductible = 500.0
        coverage_limit = 10000.0
    else:
        clauses = [f"GENERAL-{claim_type.upper()}-01 provides coverage when documents support the loss."]
        exclusions = ["Intentional loss", "Pre-existing damage"]
        deductible = 750.0
        coverage_limit = 8000.0

    summary = call_ollama(
        prompt="Summarize these policy clauses without changing their meaning:\n" + "\n".join(clauses),
        system="You summarize policy clauses only. Do not make governance or claim decisions.",
    )
    if summary:
        clauses = [summary, *clauses]

    return PolicyEvidence(
        relevant_policy_clauses=clauses,
        exclusions=exclusions,
        deductible=deductible,
        coverage_limit=coverage_limit,
        confidence_score=0.88 if "unknown" not in incident_type else 0.7,
    )

