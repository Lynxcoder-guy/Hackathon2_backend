from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import Session

from Auth_funcs.crud_auth import Base

class user_weekly_logs(Base):
    __tablename__ = "user_weekly_logs"

    healthLogs = Column(String(1000), nullable=False, unique=False)
    createdWhen = Column(DateTime, nullable=False, unique=False)
    userToken = Column(String(255), nullable=False, unique=False)
    __mapper_args__ = {
        "primary_key": [healthLogs, createdWhen, userToken],
    }


def setHealthLogs(
    db: Session,
    healthLogs: str,
    createdWhen: datetime,
    userToken: str,
):
    new_log = user_weekly_logs(
        healthLogs=healthLogs,
        createdWhen=createdWhen,
        userToken=userToken
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return "Health log added successfully."

