from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import datetime, timezone

from backend.database.connection import get_db
from backend.database.models import PodcastEpisode, Book
from backend.models.schemas import PodcastEpisodeResponse

router = APIRouter(prefix="/api/podcasts", tags=["Podcasts"])


@router.get("/", response_model=List[PodcastEpisodeResponse])
async def list_podcasts(
    platform: Optional[str] = Query(None),
    book_id: Optional[int] = Query(None),
    is_featured: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(PodcastEpisode)
    if platform:
        query = query.filter(PodcastEpisode.platform == platform)
    if book_id:
        query = query.filter(PodcastEpisode.book_id == book_id)
    if is_featured is not None:
        query = query.filter(PodcastEpisode.is_featured == is_featured)
    return query.order_by(PodcastEpisode.published_date.desc().nullslast()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()


@router.get("/platforms", response_model=List[str])
async def list_podcast_platforms(db: Session = Depends(get_db)):
    results = db.query(PodcastEpisode.platform).distinct().all()
    return [r[0] for r in results]


@router.get("/{podcast_id}", response_model=PodcastEpisodeResponse)
async def get_podcast(podcast_id: int, db: Session = Depends(get_db)):
    episode = db.query(PodcastEpisode).filter(PodcastEpisode.id == podcast_id).first()
    if not episode:
        raise HTTPException(404, "Podcast episode not found")
    episode.listen_count = (episode.listen_count or 0) + 1
    db.commit()
    return episode
