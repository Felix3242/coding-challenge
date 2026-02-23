from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import cast
from . import models

def get_challenge_quota(db: Session, user_id: str):
    return (db.query(models.ChallengeQuota)
            .filter(models.ChallengeQuota.user_id == user_id)
            .first())

def create_challenge_quota(db: Session, user_id: str):
    db_quota = models.ChallengeQuota(user_id = user_id)
    db.add(db_quota)
    db.commit()
    db.refresh(db_quota)
    return db_quota

def reset_quota_if_needed(db: Session, quota: models.ChallengeQuota):
    """Reset to 50 if 24h has passed since last_reset_date (start of current period)."""
    now = datetime.now()
    last_reset = getattr(quota, "last_reset_date", None)
    if last_reset is None:
        return quota
    if now - cast(datetime, last_reset) > timedelta(hours=24):
        setattr(quota, "quota_remaining", 50)
        setattr(quota, "last_reset_date", now)
        db.commit()
        db.refresh(quota)
    return quota

def create_challenge(
    db: Session,
    difficulty: str,
    created_by: str,
    title: str,
    options: str,
    correct_answer_id: int,
    explanation: str):
    db_challenge = models.Challenge(
        difficulty = difficulty,
        created_by = created_by,
        title = title,
        options = options,
        correct_answer_id = correct_answer_id,
        explanation = explanation
    )
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

def get_user_challenges(db: Session, user_id: str):
    return db.query(models.Challenge).filter(models.Challenge.created_by == user_id).all()

def save_user_answer(db: Session, user_id: str, challenge_id: int, selected_answer_id: int, is_correct: bool):
    db_answer = models.UserAnswer(
        user_id=user_id,
        challenge_id=challenge_id,
        selected_answer_id=selected_answer_id,
        is_correct=1 if is_correct else 0
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer

