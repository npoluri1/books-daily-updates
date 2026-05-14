from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from backend.database.connection import get_db
from backend.database.models import MediaContent, Book
from backend.models.schemas import MediaContentResponse, MediaContentCreate

router = APIRouter(prefix="/api/media", tags=["Media"])


@router.get("/", response_model=List[MediaContentResponse])
async def list_media(
    media_type: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    book_id: Optional[int] = Query(None),
    is_featured: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(MediaContent)
    if media_type:
        query = query.filter(MediaContent.media_type == media_type)
    if platform:
        query = query.filter(MediaContent.platform == platform)
    if book_id:
        query = query.filter(MediaContent.book_id == book_id)
    if is_featured is not None:
        query = query.filter(MediaContent.is_featured == is_featured)
    return query.order_by(MediaContent.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()


@router.post("/", response_model=MediaContentResponse)
async def create_media(media: MediaContentCreate, db: Session = Depends(get_db)):
    if media.book_id:
        book = db.query(Book).filter(Book.id == media.book_id).first()
        if not book:
            raise HTTPException(404, "Book not found")
    db_media = MediaContent(**media.model_dump())
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media


@router.get("/platforms", response_model=List[str])
async def list_platforms(db: Session = Depends(get_db)):
    results = db.query(MediaContent.platform).distinct().all()
    return [r[0] for r in results]


@router.get("/types", response_model=List[str])
async def list_media_types(db: Session = Depends(get_db)):
    results = db.query(MediaContent.media_type).distinct().all()
    return [r[0] for r in results]


@router.post("/{media_id}/view")
async def increment_view(media_id: int, db: Session = Depends(get_db)):
    media = db.query(MediaContent).filter(MediaContent.id == media_id).first()
    if not media:
        raise HTTPException(404, "Media not found")
    media.view_count = (media.view_count or 0) + 1
    db.commit()
    return {"view_count": media.view_count}
