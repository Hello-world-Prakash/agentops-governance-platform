from fastapi.testclient import TestClient

from app.governance.pii_detector import mask_pii_in_text
from app.main import app


client = TestClient(app)


def test_pii_detector_masks_sensitive_values():
    text = "SSN 123-45-6789 phone 203-718-8960 email test@gmail.com policy POL-123456"
    masked = mask_pii_in_text(text)
    assert "***-**-6789" in masked
    assert "***-***-8960" in masked
    assert "t***@gmail.com" in masked
    assert "POL-******" in masked


def test_audit_log_masks_pii_before_storage():
    response = client.post(
        "/claims/review",
        json={
            "customer_id": "CUST-PII",
            "claim_text": "Customer email test@gmail.com phone 203-718-8960 SSN 123-45-6789 policy POL-123456. Repair estimate and police report are available.",
            "claim_type": "auto",
            "claim_amount": 3000,
        },
    )
    assert response.status_code == 200
    trace_id = response.json()["trace_id"]

    audit_response = client.get(f"/audit-logs/{trace_id}")
    assert audit_response.status_code == 200
    stored_text = audit_response.json()["user_request"]["claim_text"]
    assert "123-45-6789" not in stored_text
    assert "203-718-8960" not in stored_text
    assert "test@gmail.com" not in stored_text
    assert "POL-123456" not in stored_text
    assert "***-**-6789" in stored_text
    assert "***-***-8960" in stored_text
    assert "t***@gmail.com" in stored_text
    assert "POL-******" in stored_text

