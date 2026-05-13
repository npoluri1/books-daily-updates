from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, time


class BookBase(BaseModel):
    title: str
    author: Optional[str] = None
    isbn: Optional[str] = None
    total_chapters: int = 0
    source_file: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookResponse(BookBase):
    id: int
    current_chapter: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChapterSummary(BaseModel):
    id: int
    book_id: int
    chapter_number: int
    chapter_title: Optional[str] = None
    summary: str
    key_points: List[str] = []
    reading_time_minutes: int = 5
    created_at: datetime
    scheduled_date: Optional[str] = None

    class Config:
        from_attributes = True


class ChapterSummaryCreate(BaseModel):
    chapter_number: int
    chapter_title: Optional[str] = None
    summary: str
    key_points: List[str] = []


class BookWithChapters(BookResponse):
    chapters: List[ChapterSummary] = []


class BookUploadResponse(BaseModel):
    message: str
    books_found: int
    books_added: int
    books: List[str]


class GenerateSummaryRequest(BaseModel):
    book_id: int
    chapter_number: int
    chapter_title: Optional[str] = None
    book_context: Optional[str] = None


class NotificationSettings(BaseModel):
    email_enabled: bool = True
    email_address: Optional[str] = None
    telegram_enabled: bool = False
    telegram_chat_id: Optional[str] = None
    whatsapp_enabled: bool = False
    whatsapp_number: Optional[str] = None
    notification_time: str = "08:30"
    timezone: str = "Asia/Kolkata"


class ReadingSchedule(BaseModel):
    id: int
    book_id: int
    user_id: int
    start_date: str
    chapters_per_day: int = 1
    is_active: bool = True
    current_chapter: int = 0

    class Config:
        from_attributes = True


class UserSettings(BaseModel):
    email: str
    notification_time: str = "08:30"
    timezone: str = "Asia/Kolkata"
    email_notifications: bool = True
    telegram_notifications: bool = False
    telegram_chat_id: Optional[str] = None
    whatsapp_notifications: bool = False
    whatsapp_number: Optional[str] = None


class DailyReadingResponse(BaseModel):
    book_title: str
    book_author: Optional[str]
    chapter_number: int
    chapter_title: Optional[str]
    summary: str
    key_points: List[str]
    reading_time_minutes: int
    date: str
    progress: float


class SearchRequest(BaseModel):
    query: str
    regex: bool = False
    page: int = 1
    page_size: int = 20


class SearchResult(BaseModel):
    books: List[BookResponse]
    total: int
    page: int
    page_size: int
