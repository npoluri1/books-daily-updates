from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import datetime, timezone

from backend.database.connection import get_db
from backend.database.models import VideoPlaylist, PlaylistVideo, MediaContent
from backend.models.schemas import (
    VideoPlaylistResponse, PlaylistVideoResponse, MediaContentResponse,
)

router = APIRouter(prefix="/api/videos", tags=["Videos"])


@router.get("/playlists", response_model=List[VideoPlaylistResponse])
async def list_playlists(
    platform: Optional[str] = Query(None),
    is_featured: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(VideoPlaylist).options(
        joinedload(VideoPlaylist.videos)
    )
    if platform:
        query = query.filter(VideoPlaylist.platform == platform)
    if is_featured is not None:
        query = query.filter(VideoPlaylist.is_featured == is_featured)
    return query.order_by(VideoPlaylist.sort_order).all()


@router.get("/playlists/{playlist_id}", response_model=VideoPlaylistResponse)
async def get_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = db.query(VideoPlaylist).options(
        joinedload(VideoPlaylist.videos)
    ).filter(VideoPlaylist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(404, "Playlist not found")
    return playlist


@router.get("/channels")
async def list_channels(db: Session = Depends(get_db)):
    results = db.query(
        VideoPlaylist.platform,
        VideoPlaylist.channel_name,
        VideoPlaylist.channel_url,
        VideoPlaylist.thumbnail_url,
    ).distinct().all()
    
    channels = []
    seen = set()
    for platform, name, url, thumb in results:
        key = f"{platform}:{name}"
        if key not in seen and name:
            seen.add(key)
            channels.append({
                "platform": platform,
                "channel_name": name,
                "channel_url": url,
                "thumbnail_url": thumb,
            })
    
    all_media = db.query(MediaContent).filter(
        MediaContent.media_type.in_(["video", "podcast"])
    ).all()
    seen_platforms = set()
    for m in all_media:
        key = f"{m.platform}:{m.author}"
        if key not in seen and m.author:
            seen.add(key)
            channel_entry = {
                "platform": m.platform,
                "channel_name": m.author,
                "channel_url": None,
                "thumbnail_url": None,
            }
            for c in channels:
                if c["channel_name"] == m.author:
                    channel_entry["channel_url"] = c["channel_url"]
                    break
            channels.append(channel_entry)
    
    return channels


@router.get("/platforms")
async def list_video_platforms(db: Session = Depends(get_db)):
    playlists = db.query(VideoPlaylist.platform).distinct().all()
    media = db.query(MediaContent.platform).filter(
        MediaContent.media_type == "video"
    ).distinct().all()
    platforms = set()
    for p in playlists:
        platforms.add(p[0])
    for p in media:
        platforms.add(p[0])
    return sorted(platforms)


@router.post("/{video_id}/view")
async def increment_video_view(video_id: int, db: Session = Depends(get_db)):
    video = db.query(PlaylistVideo).filter(PlaylistVideo.id == video_id).first()
    if not video:
        raise HTTPException(404, "Video not found")
    video.view_count = (video.view_count or 0) + 1
    db.commit()
    return {"view_count": video.view_count}
