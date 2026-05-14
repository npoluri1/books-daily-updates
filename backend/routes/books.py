from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import tempfile
import re
import shutil
from pathlib import Path

from backend.database.connection import get_db
from backend.database.models import Book, ChapterSummary as ChapterDB, ReadingSchedule
from backend.models.schemas import (
    BookResponse, BookWithChapters, ChapterSummary, ChapterSummaryCreate,
    BookUploadResponse, GenerateSummaryRequest, SearchRequest, SearchResult,
)
from backend.services.excel_parser import parse_excel_books, search_books_by_regex
from backend.services.ai_summarizer import summarizer

router = APIRouter(prefix="/api/books", tags=["Books"])

UPLOAD_DIR = Path(__file__).parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=BookUploadResponse)
async def upload_books(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "Only Excel files (.xlsx, .xls) are supported")

    dest_path = UPLOAD_DIR / f"{Path(file.filename).stem}_{int(__import__('time').time())}{Path(file.filename).suffix}"
    try:
        content = await file.read()
        dest_path.write_bytes(content)
        parsed_books = parse_excel_books(str(dest_path))
    except Exception as e:
        if dest_path.exists():
            dest_path.unlink(missing_ok=True)
        raise HTTPException(400, f"Failed to parse Excel file: {e}")

    if not parsed_books:
        if dest_path.exists():
            dest_path.unlink(missing_ok=True)
        raise HTTPException(400, "No books found in the Excel file")

    books_added = 0
    books_skipped = 0
    book_names = []
    existing_titles = {b.title.strip().lower() for b in db.query(Book).all()}

    for book_data in parsed_books:
        title = book_data["title"].strip()
        title_lower = title.lower()
        if title_lower in existing_titles:
            book_names.append(f"{title} (already exists)")
            books_skipped += 1
            continue

        db_book = Book(
            title=title,
            author=book_data.get("author"),
            isbn=book_data.get("isbn"),
            total_chapters=book_data.get("total_chapters", 0) or 0,
            price=book_data.get("price", 0.0),
            stock_quantity=book_data.get("stock_quantity", 50),
            is_digital=False,
            is_active=True,
            source_file=str(dest_path),
        )
        db.add(db_book)
        existing_titles.add(title_lower)
        books_added += 1
        book_names.append(title)

    db.commit()
    return BookUploadResponse(
        message=f"Found {len(parsed_books)} books: added {books_added} new, skipped {books_skipped} duplicates",
        books_found=len(parsed_books),
        books_added=books_added,
        books=book_names,
    )


@router.get("/", response_model=List[BookResponse])
async def list_books(
    search: Optional[str] = Query(None),
    regex: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    query = db.query(Book).filter(Book.is_active == True)

    if search:
        all_books = query.all()
        book_dicts = [{"title": b.title, "author": b.author, "id": b.id} for b in all_books]
        matched = search_books_by_regex(book_dicts, search, use_regex=regex)
        matched_ids = {m["id"] for m in matched}
        if not matched_ids:
            return []
        query = db.query(Book).filter(Book.id.in_(matched_ids), Book.is_active == True)

    total = query.count()
    books = query.order_by(Book.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return books


@router.get("/{book_id}", response_model=BookWithChapters)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")
    return book


@router.get("/{book_id}/chapters", response_model=List[ChapterSummary])
async def get_book_chapters(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")
    chapters = db.query(ChapterDB).filter(ChapterDB.book_id == book_id).order_by(ChapterDB.chapter_number).all()
    return chapters


@router.post("/generate", response_model=ChapterSummary)
async def generate_chapter_summary(req: GenerateSummaryRequest, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == req.book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")

    existing = db.query(ChapterDB).filter(
        ChapterDB.book_id == req.book_id,
        ChapterDB.chapter_number == req.chapter_number,
    ).first()
    if existing:
        return existing

    result = summarizer.generate_summary(
        book_title=book.title,
        chapter_number=req.chapter_number,
        chapter_title=req.chapter_title,
        book_author=book.author,
        context=req.book_context,
    )

    chapter = ChapterDB(
        book_id=req.book_id,
        chapter_number=req.chapter_number,
        chapter_title=req.chapter_title,
        summary=result.get("summary", ""),
        key_points=result.get("key_points", []),
        reading_time_minutes=result.get("reading_time_minutes", 5),
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


@router.delete("/{book_id}")
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")
    db.delete(book)
    db.commit()
    return {"message": "Book deleted"}
