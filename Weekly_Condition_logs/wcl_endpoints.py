from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from Auth_funcs.database import get_db
from Weekly_Condition_logs.wcl_crud import setHealthLogs

router = APIRouter()


class HealthLogData(BaseModel):
    healthLogs: str
    createdWhen: datetime
    userToken: str


@router.post("/submit-health-log", status_code=status.HTTP_201_CREATED)
def submit_health_log(log_data: HealthLogData, session: Session = Depends(get_db)):
    created_when = log_data.createdWhen
    if created_when.tzinfo is not None:
        created_when = created_when.astimezone(timezone.utc).replace(tzinfo=None)

    action = setHealthLogs(
        db=session,
        healthLogs=log_data.healthLogs,
        createdWhen=created_when,
        userToken=log_data.userToken
    )
    if action == True:
        return True
    else:
        return False
