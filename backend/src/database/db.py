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

def get_user_answer_stats(db: Session, user_id: str):
    """Returns total_attempts, total_correct, total_incorrect, current_streak, best_streak, accuracy_pct."""
    answers = (
        db.query(models.UserAnswer)
        .filter(models.UserAnswer.user_id == user_id)
        .order_by(models.UserAnswer.answered_at.asc())
        .all()
    )
    total = len(answers)
    correct = sum(1 for a in answers if a.is_correct == 1)
    incorrect = total - correct

    # Best streak: max consecutive correct in chronological order
    best_streak = 0
    current_run = 0
    for a in answers:
        if a.is_correct == 1:
            current_run += 1
            best_streak = max(best_streak, current_run)
        else:
            current_run = 0

    # Current streak: consecutive correct from the most recent answers (newest first)
    current_streak = 0
    for a in reversed(answers):
        if a.is_correct == 1:
            current_streak += 1
        else:
            break

    accuracy_pct = round(100 * correct / total, 1) if total else 0.0

    return {
        "total_attempts": total,
        "total_correct": correct,
        "total_incorrect": incorrect,
        "current_streak": current_streak,
        "best_streak": best_streak,
        "accuracy_pct": accuracy_pct,
    }

