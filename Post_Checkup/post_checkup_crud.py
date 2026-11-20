from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session

from Auth_funcs.crud_auth import Base


class post_checkup_advices(Base):
    __tablename__ = "doctor_advice_notes"

    id = Column(Integer, primary_key=True)
    userToken = Column(String(225), nullable=False, unique=True)
    simplifiedAdvice = Column(String(1000), nullable=False)
    originalAdvice = Column(String(1000), nullable=False)
    last_checkup_date = Column(DateTime, nullable=False)


def save_post_checkup_advices(
    db: Session,
    user_token: str,
    simplified_advice: str,
    original_advice: str,
) -> str:
    advice_result = (
        db.query(post_checkup_advices)
        .filter_by(userToken=user_token)
        .first()
    )
    if advice_result is None:
        advice_result = post_checkup_advices(userToken=user_token)
        db.add(advice_result)

    advice_result.simplifiedAdvice = simplified_advice
    advice_result.originalAdvice = original_advice
    advice_result.last_checkup_date = datetime.now()

    db.commit()
    return True
