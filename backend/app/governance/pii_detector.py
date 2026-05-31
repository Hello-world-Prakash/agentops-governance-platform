import re
from typing import Any


SSN_PATTERN = re.compile(r"\b(\d{3})-(\d{2})-(\d{4})\b")
PHONE_PATTERN = re.compile(r"\b(\d{3})-(\d{3})-(\d{4})\b")
EMAIL_PATTERN = re.compile(r"\b([A-Za-z0-9._%+-])([A-Za-z0-9._%+-]*)(@([A-Za-z0-9.-]+\.[A-Za-z]{2,}))\b")
POLICY_PATTERN = re.compile(r"\b(POL-)([A-Za-z0-9]+)\b", re.IGNORECASE)
CREDIT_CARD_PATTERN = re.compile(r"\b\d{16}\b")


def mask_pii_in_text(value: str) -> str:
    masked = SSN_PATTERN.sub(r"***-**-\3", value)
    masked = PHONE_PATTERN.sub(r"***-***-\3", masked)
    masked = EMAIL_PATTERN.sub(lambda match: f"{match.group(1)}***{match.group(3)}", masked)
    masked = POLICY_PATTERN.sub(lambda match: f"{match.group(1)}{'*' * len(match.group(2))}", masked)
    masked = CREDIT_CARD_PATTERN.sub("****-****-****-****", masked)
    return masked


def mask_pii(value: Any) -> Any:
    if isinstance(value, str):
        return mask_pii_in_text(value)
    if isinstance(value, list):
        return [mask_pii(item) for item in value]
    if isinstance(value, dict):
        return {key: mask_pii(item) for key, item in value.items()}
    return value

