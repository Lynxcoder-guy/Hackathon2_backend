"""fastAPI endpoint for the post-checkup AI.
to enable it, add to main.py:
    from Hackathon2_backend.router import router as post_checkup_router
    app.include_router(post_checkup_router)"""


from fastapi import APIRouter, HTTPException, status


from Hackathon2_backend.sample_data import SAMPLE_NOTES
from Hackathon2_backend.ringkasan import PostCheckUpAI

router = APIRouter(prefix="/post-checkup", tags=["Post Checkup"])

@router.get('/{visit_id}/summary')
def get_summary(visit_id: str):
    """Returns a patient-friendly summary and action plan with basic patient details."""
    note = SAMPLE_NOTES(visit_id)
    if note is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No doctor note found for this visit.")
    try:
        ai = PostCheckUpAI(note)
    except RuntimeError as error:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(error))
    return ai.build_report().to_dict()