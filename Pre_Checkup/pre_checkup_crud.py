from sqlalchemy.orm import Session

from Auth_funcs.crud_auth import users_auths
from Weekly_Condition_logs.wcl_crud import user_weekly_logs


def get_health_logs(db: Session, userToken: str):
    logs = (
        db.query(user_weekly_logs.healthLogs, user_weekly_logs.createdWhen)
        .filter(user_weekly_logs.userToken == userToken)
        .order_by(user_weekly_logs.createdWhen.asc())
        .all()
    )
    return [
        {"healthLogs": row.healthLogs, "createdWhen": row.createdWhen}
        for row in logs
    ]


def get_user_name(db: Session, userToken: str):
    user = (
        db.query(users_auths)
        .filter(users_auths.userToken == userToken)
        .first()
    )
    return user.userName if user else None
