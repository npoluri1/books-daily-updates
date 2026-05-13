from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    author = Column(String(300), nullable=True)
    isbn = Column(String(50), nullable=True)
    total_chapters = Column(Integer, default=0)
    current_chapter = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    source_file = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc))

    chapters = relationship("ChapterSummary", back_populates="book", cascade="all, delete-orphan")
    schedules = relationship("ReadingSchedule", back_populates="book", cascade="all, delete-orphan")


class ChapterSummary(Base):
    __tablename__ = "chapter_summaries"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    chapter_title = Column(String(500), nullable=True)
    summary = Column(Text, nullable=False)
    key_points = Column(JSON, default=list)
    reading_time_minutes = Column(Integer, default=5)
    scheduled_date = Column(String(20), nullable=True)
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    book = relationship("Book", back_populates="chapters")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(200), nullable=True)
    notification_time = Column(String(10), default="08:30")
    timezone = Column(String(50), default="Asia/Kolkata")
    email_notifications = Column(Boolean, default=True)
    telegram_notifications = Column(Boolean, default=False)
    telegram_chat_id = Column(String(100), nullable=True)
    whatsapp_notifications = Column(Boolean, default=False)
    whatsapp_number = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    schedules = relationship("ReadingSchedule", back_populates="user", cascade="all, delete-orphan")


class ReadingSchedule(Base):
    __tablename__ = "reading_schedules"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(String(20), nullable=False)
    chapters_per_day = Column(Integer, default=1)
    current_chapter = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    book = relationship("Book", back_populates="schedules")
    user = relationship("User", back_populates="schedules")


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=True)
    chapter_id = Column(Integer, ForeignKey("chapter_summaries.id"), nullable=True)
    channel = Column(String(50), nullable=False)
    status = Column(String(50), default="sent")
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
