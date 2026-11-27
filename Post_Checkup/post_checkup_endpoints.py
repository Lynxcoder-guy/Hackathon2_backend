from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from Auth_funcs.database import get_db
from Post_Checkup.post_checkup_crud import save_post_checkup_advices
from Post_Checkup.post_checkup_crud import (
    save_actionable_plan as persist_actionable_plan,
)
from Post_Checkup.post_checkup_crud import get_actionable_plan
from Post_Checkup_AI import DoctorNote, PostCheckUpAI
from Post_Checkup.post_checkup_crud import save_individual_AP
from Post_Checkup.post_checkup_crud import get_doctor_advice
from Post_Checkup.post_checkup_crud import save_simple_advices


router = APIRouter()


class PostCheckupAdviceData(BaseModel):
    userToken: str
    originalAdvice: str

class ManualActionableTask(BaseModel):
    title: str = Field(min_length=1, max_length=225)
    description: str = Field(min_length=1, max_length=225)

class IndividualActionablePlan(BaseModel):
    userToken: str
    actionablePlan: list[ManualActionableTask] = Field(default_factory=list)

class UserToken(BaseModel):
    userToken: str

@router.post("/post-checkup", status_code=status.HTTP_201_CREATED)
def post_checkup(
    advice_data: PostCheckupAdviceData,
    session: Session = Depends(get_db),
):
    note = DoctorNote(
        visit_id=advice_data.userToken,
        advice=advice_data.originalAdvice,
    )

    report = PostCheckUpAI(note).build_report()
    simplified_advice = report.ringkasan_simpel
    actionable_plan = report.plan

    save_post_checkup_advices(
        db=session,
        user_token=advice_data.userToken,
        simplified_advice=simplified_advice,
        original_advice=advice_data.originalAdvice,
    )
    persist_actionable_plan(
        db=session,
        user_token=advice_data.userToken,
        tasks=[task.to_dict() for task in actionable_plan],
    )
    save_simple_advices(session, advice_data.userToken, simplified_advice)
    return {
        "message": "Post-checkup advice saved successfully.",
        "simpleAdvice": simplified_advice,
        "actionablePlan": [task.to_dict() for task in actionable_plan],
        "aiGenerated": report.ai_generated,
    }

@router.post("/save-actionable-plan", response_model=bool)
def save_actionable_plan(
    user_data: IndividualActionablePlan,
    session: Session = Depends(get_db),
):
    return save_individual_AP(
        user_data.userToken,
        [task.model_dump() for task in user_data.actionablePlan],
        session,
    )

@router.post("/get-advice")
def get_advice(user_token: UserToken, session: Session = Depends(get_db)):
    advice = get_doctor_advice(db=session, user_token=user_token.userToken)
    return advice


@router.post("/actionable-plan")
def actionable_plan(
    user_data: UserToken,
    session: Session = Depends(get_db),
):
    get_data = get_actionable_plan(
        db=session,
        user_token=user_data.userToken,
    )
    return {"actionablePlan": get_data}