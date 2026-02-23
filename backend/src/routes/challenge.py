from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..ai_generator import generate_challenge_with_ai
from ..database.db import (
    create_challenge,
    create_challenge_quota,
    get_challenge_quota,
    reset_quota_if_needed,
    get_user_challenges,
    save_user_answer,
)
from ..utils import authenticate_and_get_user_details
from ..database.models import get_db
from ..database import models
import json
from datetime import datetime
from typing import cast

router = APIRouter()

class ChallengeRequest(BaseModel):
    difficulty: str

    class Config:
        json_schema_extra = {"example": {"difficulty": "easy"}}

@router.post("/generate-challenge")
async def generate_challenge(request: ChallengeRequest, request_obj: Request, db: Session = Depends(get_db)):
    try:
        user_details = authenticate_and_get_user_details(request_obj)
        user_id = user_details.get("user_id")
        if not user_id or not isinstance(user_id, str):
            raise HTTPException(status_code=401, detail="Invalid token")

        quota = get_challenge_quota(db, user_id)
        if not quota:
            quota = create_challenge_quota(db, user_id)

        quota = reset_quota_if_needed(db, quota)

        if cast(int, quota.quota_remaining) <= 0:
            raise HTTPException(status_code=429, detail="Quota exhausted")
        
        challenge_data = generate_challenge_with_ai(request.difficulty)

        new_challenge = create_challenge(
            db=db,
            difficulty=request.difficulty,
            created_by=user_id,
            title=challenge_data["title"],
            options=json.dumps(challenge_data["options"]),
            correct_answer_id=challenge_data["correct_answer_id"],
            explanation=challenge_data["explanation"]
        )

        setattr(quota, "quota_remaining", cast(int, quota.quota_remaining) - 1)
        # Start 24h reset window on first challenge of period
        if getattr(quota, "last_reset_date", None) is None:
            setattr(quota, "last_reset_date", datetime.now())
        db.commit()

        return {
            "id": new_challenge.id,
            "difficulty": request.difficulty,
            "title": new_challenge.title,
            "options": json.loads(cast(str, new_challenge.options)),
            "correct_answer_id": new_challenge.correct_answer_id,
            "explanation": new_challenge.explanation,
            "timestamp": new_challenge.date_created.isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/my-history")
async def my_history(request: Request, db:Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)
    user_id = user_details.get("user_id")
    if not user_id or not isinstance(user_id, str):
        raise HTTPException(status_code=401, detail="Invalid token")

    challenges = get_user_challenges(db, user_id)
    # Serialize Challenge models to dictionaries
    challenges_list = []
    for challenge in challenges:
        challenges_list.append({
            "id": challenge.id,
            "difficulty": cast(str, challenge.difficulty),
            "title": cast(str, challenge.title),
            "options": json.loads(cast(str, challenge.options)),
            "correct_answer_id": cast(int, challenge.correct_answer_id),
            "explanation": cast(str, challenge.explanation),
            "timestamp": (challenge.date_created.isoformat() if getattr(challenge, "date_created", None) is not None else None)
        })
    return {"challenges": challenges_list}


@router.post("/submit-answer")
async def submit_answer(request: Request, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)
    user_id = user_details.get("user_id")
    if not user_id or not isinstance(user_id, str):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    body = await request.json()
    challenge_id = body.get("challenge_id")
    selected_answer_id = body.get("selected_answer_id")
    
    if challenge_id is None or selected_answer_id is None:
        raise HTTPException(status_code=400, detail="Missing challenge_id or selected_answer_id")
    
    # Get the challenge to check if answer is correct
    challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    is_correct = cast(int, challenge.correct_answer_id) == selected_answer_id
    
    # Save the answer
    save_user_answer(db, user_id, challenge_id, selected_answer_id, is_correct)
    
    return {"is_correct": is_correct}

def _serialize_quota(quota):
    """Return a JSON-serializable quota dict."""
    remaining = cast(int, quota.quota_remaining)
    last_reset = getattr(quota, "last_reset_date", None)
    return {
        "quota_remaining": remaining,
        "last_reset_date": last_reset.isoformat() if last_reset else None
    }

@router.get("/quota")
async def get_quota(request: Request, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)
    user_id = user_details.get("user_id")
    if not user_id or not isinstance(user_id, str):
        raise HTTPException(status_code=401, detail="Invalid token")

    quota = get_challenge_quota(db, user_id)
    if not quota:
        # New user: create quota with 50 so they see it as soon as they log in
        quota = create_challenge_quota(db, user_id)
    else:
        quota = reset_quota_if_needed(db, quota)
    return _serialize_quota(quota)
