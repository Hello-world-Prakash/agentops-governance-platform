from typing import Dict, List


UNSAFE_PHRASES = [
    "ignore previous instructions",
    "bypass approval",
    "delete audit logs",
    "approve without review",
    "deny without review",
    "send customer ssn",
    "override policy",
    "disable governance",
    "skip human approval",
]


def detect_prompt_injection(text: str) -> Dict[str, object]:
    lowered = text.lower()
    matches = [phrase for phrase in UNSAFE_PHRASES if phrase in lowered]
    return {"detected": bool(matches), "matches": matches}

