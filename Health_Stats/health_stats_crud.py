from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import Session

from Auth_funcs.crud_auth import (
    Base,
    users_auths,
)

class HealthCheckRecord(Base):
    __tablename__ = "health_check_records"

    id = Column(Integer, primary_key=True)
    userToken = Column(String(225), nullable=False)
    recorded_at = Column(DateTime, nullable=False)
    
    # Antropometri
    body_weight = Column(Float) # kg
    height = Column(Float) # cm
    waist_circumference = Column(Float, nullable=True) # cm (Dewasa)
    lila = Column(Float, nullable=True) # cm (Ibu hamil / Remaja putri)
    head_circumference = Column(Float, nullable=True) # cm (Balita)
    
    # Vital & Cek Darah Sederhana (Posbindu)
    systolic_bp = Column(Integer, nullable=True) # mmHg
    diastolic_bp = Column(Integer, nullable=True) # mmHg
    blood_sugar = Column(Integer, nullable=True) # mg/dL
    uric_acid = Column(Float, nullable=True) # mg/dL
    cholesterol = Column(Integer, nullable=True) # mg/dL


def add_health_stats(
    db: Session,
    userToken: str,
    recorded_at: datetime,
    body_weight: Optional[float] = None,
    height: Optional[float] = None,
    waist_circumference: Optional[float] = None,
    lila: Optional[float] = None,
    head_circumference: Optional[float] = None,
    systolic_bp: Optional[int] = None,
    diastolic_bp: Optional[int] = None,
    blood_sugar: Optional[int] = None,
    uric_acid: Optional[float] = None,
    cholesterol: Optional[int] = None,
) -> HealthCheckRecord:
    if not userToken.strip():
        raise ValueError("userToken is required")

    health_stats = HealthCheckRecord(
        userToken=userToken,
        recorded_at=recorded_at, 
        body_weight=body_weight,
        height=height,
        waist_circumference=waist_circumference,
        lila=lila,
        head_circumference=head_circumference,
        systolic_bp=systolic_bp,
        diastolic_bp=diastolic_bp,
        blood_sugar=blood_sugar,
        uric_acid=uric_acid,
        cholesterol=cholesterol,
    )
    db.add(health_stats)
    db.commit()
    db.refresh(health_stats)
    return health_stats

def check_user_token(db: Session, user_token: str) -> bool:
    if not user_token:
        return False

    return db.query(users_auths).filter_by(userToken=user_token).first() is not None


def get_health_stats(db: Session, user_token: str):
    if not check_user_token(db, user_token):
        return []

    records = (
        db.query(HealthCheckRecord)
        .filter_by(userToken=user_token)
        .order_by(HealthCheckRecord.recorded_at.desc())
        .all()
    )

    if not records:
        return []

    return [
        {
            "id": record.id,
            "userToken": record.userToken,
            "recordedAt": record.recorded_at.isoformat() if record.recorded_at else None,
            "bodyWeight": record.body_weight,
            "height": record.height,
            "waistCircumference": record.waist_circumference,
            "lila": record.lila,
            "headCircumference": record.head_circumference,
            "systolicBp": record.systolic_bp,
            "diastolicBp": record.diastolic_bp,
            "bloodSugar": record.blood_sugar,
            "uricAcid": record.uric_acid,
            "cholesterol": record.cholesterol,
        }
        for record in records
    ]
