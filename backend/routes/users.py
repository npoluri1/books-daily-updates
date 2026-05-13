from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from backend.database.connection import get_db
from backend.database.models import User
from backend.models.schemas import UserSettings

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("/")
async def create_user(
    email: str,
    name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return {"id": existing.id, "message": "User already exists"}

    user = User(email=email, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "name": user.name}


@router.get("/{user_id}", response_model=UserSettings)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return UserSettings(
        email=user.email,
        notification_time=user.notification_time or "08:30",
        timezone=user.timezone or "Asia/Kolkata",
        email_notifications=user.email_notifications,
        telegram_notifications=user.telegram_notifications,
        telegram_chat_id=user.telegram_chat_id,
        whatsapp_notifications=user.whatsapp_notifications,
        whatsapp_number=user.whatsapp_number,
    )


@router.put("/{user_id}", response_model=UserSettings)
async def update_user_settings(user_id: int, settings: UserSettings, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    user.email = settings.email
    user.notification_time = settings.notification_time
    user.timezone = settings.timezone
    user.email_notifications = settings.email_notifications
    user.telegram_notifications = settings.telegram_notifications
    user.telegram_chat_id = settings.telegram_chat_id
    user.whatsapp_notifications = settings.whatsapp_notifications
    user.whatsapp_number = settings.whatsapp_number

    db.commit()
    return settings
