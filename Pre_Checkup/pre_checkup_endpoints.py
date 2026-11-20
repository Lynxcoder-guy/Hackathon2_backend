from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json

from Auth_funcs.database import get_db
from Pre_Checkup.pre_checkup_crud import get_health_logs, get_user_name
from Pre_Checkup.gobbie.gobbie_ai.precheckup_ai import PreCheckupAI

router = APIRouter()


class PreCheckupData(BaseModel):
    userToken: str


@router.post("/pre-checkup", status_code=status.HTTP_201_CREATED)
def pre_checkup(
    pre_checkup_data: PreCheckupData,
    session: Session = Depends(get_db),
):
    logs = get_health_logs(
        db=session,
        userToken=pre_checkup_data.userToken
    )
    if not logs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No health logs found for this user.",
        )

    name = get_user_name(
        db=session,
        userToken=pre_checkup_data.userToken
    )
    str_logs = json.dumps(logs, separators=(",", ":"), default=str)
    patient_data = {
        "patient_id": "anonymous",
        "logs": json.loads(str_logs),
    }
    logs_summary = PreCheckupAI().generate_summary(patient_data)
    logs_summary["generated_at"] = datetime.now(timezone.utc).isoformat()
    return {
        "message": "creating summary successful",
        "name": name,
        "LogsSummary": logs_summary,
    }