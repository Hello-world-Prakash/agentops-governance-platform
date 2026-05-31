from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_approval_decision_requires_comment():
    review_response = client.post(
        "/claims/review",
        json={
            "customer_id": "CUST-APPROVAL-1",
            "claim_text": "Customer reports auto accident. Police report is available. Repair estimate is available.",
            "claim_type": "auto",
            "claim_amount": 9000,
        },
    )
    assert review_response.status_code == 200
    approval_id = review_response.json()["approval_id"]
    assert approval_id is not None

    missing_comment_response = client.post(
        f"/approvals/{approval_id}/approve",
        json={"reviewer_name": "Risk Reviewer", "decision_comment": ""},
    )
    assert missing_comment_response.status_code == 422


def test_approval_history_records_reviewer_comment_and_timestamp():
    review_response = client.post(
        "/claims/review",
        json={
            "customer_id": "CUST-APPROVAL-2",
            "claim_text": "Customer reports auto accident. Police report is available. Repair estimate is available.",
            "claim_type": "auto",
            "claim_amount": 9000,
        },
    )
    assert review_response.status_code == 200
    approval_id = review_response.json()["approval_id"]
    assert approval_id is not None

    decision_response = client.post(
        f"/approvals/{approval_id}/approve",
        json={"reviewer_name": "Risk Reviewer", "decision_comment": "Evidence is complete and risk is low."},
    )
    assert decision_response.status_code == 200
    decision = decision_response.json()
    assert decision["status"] == "approved"
    assert decision["reviewer_name"] == "Risk Reviewer"
    assert decision["decision_comment"] == "Evidence is complete and risk is low."
    assert decision["decided_at"] is not None

    history_response = client.get("/approvals?status=approved")
    assert history_response.status_code == 200
    assert any(row["id"] == approval_id for row in history_response.json())

