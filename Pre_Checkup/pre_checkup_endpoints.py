import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from Auth_funcs.database import get_db
from Pre_Checkup.pre_checkup_crud import (
    get_health_logs,
    get_user_group,
    get_user_name,
    validate_checkup,
)
from Pre_Checkup.gobbie.gobbie_ai.precheckup_ai import PreCheckupAI

router = APIRouter()
logger = logging.getLogger(__name__)


class PreCheckupData(BaseModel):
    userToken: str

class UserKeyValidate(BaseModel):
    userName: str
    userGroup: str
    userPassword: str


@router.post("/pre-checkup/summary", status_code=status.HTTP_201_CREATED)
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
    try:
        logs_summary = PreCheckupAI().generate_summary(patient_data)
        if (
            not isinstance(logs_summary, dict)
            or not isinstance(logs_summary.get("summary"), dict)
        ):
            raise ValueError("Gobbie AI returned no usable summary.")
    except Exception:
        logger.exception("Gobbie AI failed; returning the user's health logs.")
        return {
            "message": "Maaf, fitur AI tidak tersedia saat ini. Berikut daftar log kesehatan Anda.",
            "Name": name,
            "Summary": logs,
            "aiAvailable": False,
        }

    logs_summary["generated_at"] = datetime.now(timezone.utc).isoformat()
    return {
        "message": "creating summary successful",
        "Name": name,
        "Summary": logs_summary,
        "aiAvailable": True,
    }

@router.get("/join-checkup/{userToken}")
def join_checkup(
    userToken: str,
    session: Session = Depends(get_db),
):
    userName = get_user_name(db=session, userToken=userToken)
    userGroup = get_user_group(db=session, user_token=userToken)
    return {"user_name" : userName, "user_group": userGroup}

@router.post("/join-checkup/validate-key")
def validate_key(user_key: UserKeyValidate, session: Session = Depends(get_db),):
    result = validate_checkup(
        db=session,
        user_name=user_key.userName,
        user_group=user_key.userGroup,
        user_password=user_key.userPassword,
    )
    return result