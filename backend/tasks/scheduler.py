import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def start_scheduler():
    if scheduler.running:
        return

    try:
        from backend.config import settings
        notify_time = settings.notification_time
    except Exception:
        notify_time = "08:30"

    hour, minute = notify_time.split(":")
    trigger = CronTrigger(hour=int(hour), minute=int(minute), timezone="Asia/Kolkata")

    scheduler.add_job(
        send_daily_notifications,
        trigger=trigger,
        id="daily_reading_notification",
        name="Daily Reading Notification",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with notification time: %s", notify_time)


def send_daily_notifications():
    try:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            loop.create_task(_send_notifications())
        else:
            asyncio.run(_send_notifications())
    except Exception as e:
        logger.error("Failed to send daily notifications: %s", e)


async def _send_notifications():
    from backend.database.connection import SessionLocal
    from backend.database.models import User, ReadingSchedule, Book, ChapterSummary as ChapterDB
    from backend.services.ai_summarizer import summarizer
    from backend.services.notification_service import (
        email_notifier, telegram_notifier, whatsapp_notifier,
    )
    from datetime import date

    db = SessionLocal()
    try:
        today = date.today().isoformat()
        users = db.query(User).filter(User.is_active == True).all()

        for user in users:
            schedules = db.query(ReadingSchedule).filter(
                ReadingSchedule.user_id == user.id,
                ReadingSchedule.is_active == True,
            ).all()

            for schedule in schedules:
                book = db.query(Book).filter(Book.id == schedule.book_id).first()
                if not book or not book.is_active:
                    continue

                next_chapter = schedule.current_chapter + 1
                if next_chapter > (book.total_chapters or 999):
                    schedule.is_active = False
                    db.commit()
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

                schedule.current_chapter = next_chapter
                book.current_chapter = next_chapter

                key_points = chapter.key_points or []

                if user.email_notifications and user.email:
                    email_notifier.send_daily_reading(
                        to_email=user.email,
                        book_title=book.title,
                        chapter_num=next_chapter,
                        chapter_title=chapter.chapter_title,
                        summary=chapter.summary,
                        key_points=key_points,
                    )

                if user.telegram_notifications and user.telegram_chat_id:
                    telegram_notifier.send_daily_reading(
                        chat_id=user.telegram_chat_id,
                        book_title=book.title,
                        chapter_num=next_chapter,
                        chapter_title=chapter.chapter_title,
                        summary=chapter.summary,
                        key_points=key_points,
                    )

                if user.whatsapp_notifications and user.whatsapp_number:
                    whatsapp_notifier.send_daily_reading(
                        to_number=user.whatsapp_number,
                        book_title=book.title,
                        chapter_num=next_chapter,
                        chapter_title=chapter.chapter_title,
                        summary=chapter.summary,
                        key_points=key_points,
                    )

                if book.total_chapters and next_chapter >= book.total_chapters:
                    schedule.is_active = False

                db.commit()

    except Exception as e:
        logger.error("Notification task error: %s", e)
    finally:
        db.close()
