from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import EvaluationResult, EvaluationRun, EvaluationTestCase
from app.evaluation.evaluation_runner import run_evaluation_suite, seed_evaluation_data, serialize_run_detail, serialize_test_case
from app.evaluation.metrics import calculate_evaluation_metrics

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.get("/test-cases")
def list_test_cases(db: Session = Depends(get_db)):
    seed_evaluation_data(db)
    test_cases = db.query(EvaluationTestCase).order_by(EvaluationTestCase.id).all()
    return [serialize_test_case(test_case) for test_case in test_cases]


@router.post("/run")
def run_evaluations(db: Session = Depends(get_db)):
    return run_evaluation_suite(db)


@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    runs = db.query(EvaluationRun).order_by(EvaluationRun.started_at.desc()).all()
    return [
        {
            "id": run.id,
            "run_type": run.run_type,
            "status": run.status,
            "started_at": run.started_at.isoformat(),
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            "total_tests": run.total_tests,
            "passed_tests": run.passed_tests,
            "failed_tests": run.failed_tests,
            "critical_failure_count": run.critical_failure_count,
        }
        for run in runs
    ]


@router.get("/runs/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(EvaluationRun).filter(EvaluationRun.id == run_id).first()
    if run is None:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    results = db.query(EvaluationResult).filter(EvaluationResult.run_id == run_id).order_by(EvaluationResult.created_at.desc()).all()
    return serialize_run_detail(run, results)


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    return calculate_evaluation_metrics(db)
