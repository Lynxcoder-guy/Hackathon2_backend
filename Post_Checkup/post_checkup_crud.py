from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session

from Auth_funcs.crud_auth import Base


class post_checkup_advices(Base):
    __tablename__ = "doctor_advice_notes"
    id = Column(Integer, primary_key=True)
    userToken = Column(String(225), nullable=True, unique=True)
    simplifiedAdvice = Column(String(1000), nullable=True)
    originalAdvice = Column(String(1000), nullable=True)
    last_checkup_date = Column(DateTime, nullable=True)

class actionable_plan_lists(Base):
    __tablename__ = "user_actionable_plan"
    id = Column(Integer, primary_key=True)
    userToken = Column(String(225), nullable=False)
    actionableTitle = Column(String(225), nullable=False)
    actionableDesc = Column(String(225), nullable=False)

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


def save_actionable_plan(
    db: Session,
    user_token: str,
    tasks: list[dict],
) -> None:
    db.query(actionable_plan_lists).filter_by(userToken=user_token).delete()

    for task in tasks:
        db.add(
            actionable_plan_lists(
                userToken=user_token,
                actionableTitle=task["title"],
                actionableDesc=task["description"],
            )
        )
    db.commit()

from sqlalchemy.orm import Session

def save_simple_advices(
    db: Session,
    user_token: str,
    simple_advice: str,
):
    record = (
        db.query(post_checkup_advices)
        .filter(post_checkup_advices.userToken == user_token)  # Changed from user_token
        .first()
    )

    if record:
        record.simpleAdvice = simple_advice  # Check your model if this is simpleAdvice or simplified_advice
    else:
        record = post_checkup_advices(
            userToken=user_token,
            simplifiedAdvice=simple_advice,
        )
        db.add(record)

    db.commit()
    db.refresh(record)
    print(record)
    return record


def save_individual_AP(
    user_token: str,
    tasks: list[dict[str, str]],
    db: Session,
) -> bool:
    for task in tasks:
        db.add(
            actionable_plan_lists(
                userToken=user_token,
                actionableTitle=task["title"],
                actionableDesc=task["description"],
            )
        )
    db.commit()
    return True

def get_actionable_plan(db: Session, user_token: str):
    plans = (
        db.query(actionable_plan_lists)
        .filter_by(userToken=user_token)
        .all()
    )
    return [
        {
            "actionableTitle": plan.actionableTitle,
            "actionableDesc": plan.actionableDesc,
        }
        for plan in plans
    ]
        
def get_doctor_advice(db: Session, user_token: str):
    loc = db.query(post_checkup_advices).filter_by(userToken=user_token).first()
    if loc is None:
        return {"advice": False}
    return {"advice": loc.originalAdvice}

    
