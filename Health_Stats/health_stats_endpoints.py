from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from Auth_funcs.database import get_db
from Health_Stats.health_stats_crud import (
    add_health_stats,
    check_user_token,
    get_health_stats,
)

router = APIRouter()


class PostHealthStats(BaseModel):
    body_weight: float | None = None
    height: float | None = None
    waist_circumference: float | None = None
    lila: float | None = None
    head_circumference: float | None = None
    systolic_bp: int | None = None
    diastolic_bp: int | None = None
    blood_sugar: int | None = None
    uric_acid: float | None = None
    cholesterol: int | None = None


@router.post("/get-health-stats")
def get_user_health_stats(
    user_token: str = Header(..., convert_underscores=False),
    session: Session = Depends(get_db),
):
    return get_health_stats(db=session, user_token=user_token)


@router.post("/post-health-stats", status_code=status.HTTP_201_CREATED)
def post_user_health_stats(
    stats: PostHealthStats,
    user_token: str = Header(..., convert_underscores=False),
    session: Session = Depends(get_db),
):
    if not user_token.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="user_token header is required.",
        )

    if not check_user_token(db=session, user_token=user_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user token.",
        )

    measurements = {
        "bodyWeight": stats.body_weight,
        "height": stats.height,
        "waistCircumference": stats.waist_circumference,
        "lila": stats.lila,
        "headCircumference": stats.head_circumference,
        "systolicBp": stats.systolic_bp,
        "diastolicBp": stats.diastolic_bp,
        "bloodSugar": stats.blood_sugar,
        "uricAcid": stats.uric_acid,
        "cholesterol": stats.cholesterol,
    }
    recorded_at = datetime.now(timezone.utc).replace(tzinfo=None)

    record = add_health_stats(
        db=session,
        userToken=user_token,
        recorded_at=recorded_at,
        body_weight=stats.body_weight,
        height=stats.height,
        waist_circumference=stats.waist_circumference,
        lila=stats.lila,
        head_circumference=stats.head_circumference,
        systolic_bp=stats.systolic_bp,
        diastolic_bp=stats.diastolic_bp,
        blood_sugar=stats.blood_sugar,
        uric_acid=stats.uric_acid,
        cholesterol=stats.cholesterol,
    )

    return {
        "message": "Health stats saved successfully.",
        "healthStats": {
            "id": record.id,
            "userToken": record.userToken,
            "recordedAt": record.recorded_at.isoformat(),
            **measurements,
        },
    }