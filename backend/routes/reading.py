from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from backend.database.connection import get_db
from backend.database.models import Book, ChapterSummary as ChapterDB, ReadingSchedule, NotificationLog
from backend.models.schemas import (
    DailyReadingResponse, ReadingSchedule as ScheduleSchema,
)
from backend.services.ai_summarizer import summarizer
from backend.services.notification_service import (
    email_notifier, telegram_notifier, whatsapp_notifier,
)

router = APIRouter(prefix="/api/reading", tags=["Reading"])


@router.get("/daily", response_model=Optional[DailyReadingResponse])
async def get_daily_reading(
    user_id: int = Query(1),
    db: Session = Depends(get_db),
):
    today = date.today().isoformat()
    schedules = db.query(ReadingSchedule).filter(
        ReadingSchedule.user_id == user_id,
        ReadingSchedule.is_active == True,
    ).all()

    for schedule in schedules:
        book = db.query(Book).filter(Book.id == schedule.book_id).first()
        if not book or not book.is_active:
            continue

        next_chapter = schedule.current_chapter + 1
        if next_chapter > (book.total_chapters or 999):
            continue

        chapter = db.query(ChapterDB).filter(
            ChapterDB.book_id == book.id,
            ChapterDB.chapter_number == next_chapter,
        ).first()

        if not chapter:
            result = summarizer.generate_summary(
                book_title=book.title,
                chapter_number=next_chapter,
                book_author=book.author,
            )
            chapter = ChapterDB(
                book_id=book.id,
                chapter_number=next_chapter,
                summary=result.get("summary", ""),
                key_points=result.get("key_points", []),
                reading_time_minutes=result.get("reading_time_minutes", 5),
                scheduled_date=today,
            )
            db.add(chapter)
            db.commit()
            db.refresh(chapter)

        progress = (next_chapter / (book.total_chapters or 1)) * 100 if book.total_chapters else 0

        return DailyReadingResponse(
            book_title=book.title,
            book_author=book.author,
            chapter_number=next_chapter,
            chapter_title=chapter.chapter_title,
            summary=chapter.summary,
            key_points=chapter.key_points or [],
            reading_time_minutes=chapter.reading_time_minutes or 5,
            date=today,
            progress=round(progress, 1),
        )

    return None


@router.post("/schedule", response_model=ScheduleSchema)
async def create_schedule(
    payload: dict,
    db: Session = Depends(get_db),
):
    book_id = payload.get("book_id")
    user_id = payload.get("user_id", 1)
    start_date = payload.get("start_date")
    chapters_per_day = payload.get("chapters_per_day", 1)
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")

    existing = db.query(ReadingSchedule).filter(
        ReadingSchedule.book_id == book_id,
        ReadingSchedule.user_id == user_id,
        ReadingSchedule.is_active == True,
    ).first()
    if existing:
        raise HTTPException(400, "Book already scheduled for this user")

    if not start_date:
        start_date = date.today().isoformat()

    schedule = ReadingSchedule(
        book_id=book_id,
        user_id=user_id,
        start_date=start_date,
        chapters_per_day=chapters_per_day,
        current_chapter=0,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


@router.get("/schedules", response_model=List[ScheduleSchema])
async def list_schedules(user_id: int = Query(1), db: Session = Depends(get_db)):
    return db.query(ReadingSchedule).filter(
        ReadingSchedule.user_id == user_id
    ).all()


@router.post("/advance/{schedule_id}")
async def advance_chapter(schedule_id: int, db: Session = Depends(get_db)):
    schedule = db.query(ReadingSchedule).filter(ReadingSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(404, "Schedule not found")

    book = db.query(Book).filter(Book.id == schedule.book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")

    schedule.current_chapter += schedule.chapters_per_day
    book.current_chapter = schedule.current_chapter

    if book.total_chapters and schedule.current_chapter >= book.total_chapters:
        schedule.is_active = False

    db.commit()
    return {"message": f"Advanced to chapter {schedule.current_chapter}"}


@router.post("/send-notification")
async def send_todays_reading(
    user_id: int = Query(1),
    db: Session = Depends(get_db),
):
    from backend.database.models import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    daily = await get_daily_reading(user_id=user_id, db=db)
    if not daily:
        raise HTTPException(404, "No reading available for today")

    results = []

    if user.email_notifications and user.email:
        ok = email_notifier.send_daily_reading(
            to_email=user.email,
            book_title=daily.book_title,
            chapter_num=daily.chapter_number,
            chapter_title=daily.chapter_title,
            summary=daily.summary,
            key_points=daily.key_points,
        )
        results.append({"channel": "email", "status": "sent" if ok else "failed"})

    if user.telegram_notifications and user.telegram_chat_id:
        ok = telegram_notifier.send_daily_reading(
            chat_id=user.telegram_chat_id,
            book_title=daily.book_title,
            chapter_num=daily.chapter_number,
            chapter_title=daily.chapter_title,
            summary=daily.summary,
            key_points=daily.key_points,
        )
        results.append({"channel": "telegram", "status": "sent" if ok else "failed"})

    if user.whatsapp_notifications and user.whatsapp_number:
        ok = whatsapp_notifier.send_daily_reading(
            to_number=user.whatsapp_number,
            book_title=daily.book_title,
            chapter_num=daily.chapter_number,
            chapter_title=daily.chapter_title,
            summary=daily.summary,
            key_points=daily.key_points,
        )
        results.append({"channel": "whatsapp", "status": "sent" if ok else "failed"})

    return {"results": results}
