from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import RedTeamScenario
from app.evaluation.evaluation_runner import run_red_team_suite, seed_evaluation_data, serialize_red_team_scenario

router = APIRouter(prefix="/red-team", tags=["red-team"])


class RedTeamRunRequest(BaseModel):
    scenario_id: Optional[int] = None


@router.get("/scenarios")
def list_scenarios(db: Session = Depends(get_db)):
    seed_evaluation_data(db)
    scenarios = db.query(RedTeamScenario).order_by(RedTeamScenario.id).all()
    return [serialize_red_team_scenario(scenario) for scenario in scenarios]


@router.post("/run")
def run_red_team(request: RedTeamRunRequest | None = None, db: Session = Depends(get_db)):
    return run_red_team_suite(db, scenario_id=request.scenario_id if request else None)
