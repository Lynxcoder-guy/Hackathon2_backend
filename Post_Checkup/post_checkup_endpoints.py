from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from Auth_funcs.database import get_db
from Post_Checkup.post_checkup_crud import save_post_checkup_advices

router = APIRouter()


class PostCheckupAdviceData(BaseModel):
    userToken: str
    simplifiedAdvice: str
    originalAdvice: str


@router.post("/post-checkup", status_code=status.HTTP_201_CREATED)
def post_checkup(
    advice_data: PostCheckupAdviceData,
    session: Session = Depends(get_db),
):
    save_post_checkup_advices(
        db=session,
        user_token=advice_data.userToken,
        simplified_advice=advice_data.simplifiedAdvice,
        original_advice=advice_data.originalAdvice,
    )
    return {"message": "Post-checkup advice saved successfully."}
