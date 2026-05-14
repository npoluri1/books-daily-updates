from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timezone

from backend.database.connection import get_db
from backend.database.models import CricfyMatch
from backend.models.schemas import CricfyMatchResponse, CricfyMatchCreate

router = APIRouter(prefix="/api/cricfy", tags=["Cricfy TV"])


@router.get("/", response_model=List[CricfyMatchResponse])
async def list_matches(
    status: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    series: Optional[str] = Query(None),
    is_featured: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(CricfyMatch)
    if status:
        query = query.filter(CricfyMatch.status == status)
    if platform:
        query = query.filter(CricfyMatch.platform == platform)
    if series:
        query = query.filter(CricfyMatch.series_name.ilike(f"%{series}%"))
    if is_featured is not None:
        query = query.filter(CricfyMatch.is_featured == is_featured)
    return query.order_by(CricfyMatch.match_date.desc(), CricfyMatch.sort_order).all()


@router.get("/{match_id}", response_model=CricfyMatchResponse)
async def get_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(CricfyMatch).filter(CricfyMatch.id == match_id).first()
    if not match:
        raise HTTPException(404, "Match not found")
    return match


@router.post("/", response_model=CricfyMatchResponse)
async def create_match(data: CricfyMatchCreate, db: Session = Depends(get_db)):
    match = CricfyMatch(**data.model_dump())
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


@router.put("/{match_id}/score", response_model=CricfyMatchResponse)
async def update_score(
    match_id: int,
    score_team1: Optional[str] = None,
    score_team2: Optional[str] = None,
    overs_team1: Optional[float] = None,
    overs_team2: Optional[float] = None,
    status: Optional[str] = None,
    match_result: Optional[str] = None,
    db: Session = Depends(get_db),
):
    match = db.query(CricfyMatch).filter(CricfyMatch.id == match_id).first()
    if not match:
        raise HTTPException(404, "Match not found")
    if score_team1 is not None:
        match.score_team1 = score_team1
    if score_team2 is not None:
        match.score_team2 = score_team2
    if overs_team1 is not None:
        match.overs_team1 = overs_team1
    if overs_team2 is not None:
        match.overs_team2 = overs_team2
    if status is not None:
        match.status = status
    if match_result is not None:
        match.match_result = match_result
    db.commit()
    db.refresh(match)
    return match


@router.post("/{match_id}/view")
async def increment_match_view(match_id: int, db: Session = Depends(get_db)):
    match = db.query(CricfyMatch).filter(CricfyMatch.id == match_id).first()
    if not match:
        raise HTTPException(404, "Match not found")
    match.view_count = (match.view_count or 0) + 1
    db.commit()
    return {"view_count": match.view_count}


@router.delete("/{match_id}")
async def delete_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(CricfyMatch).filter(CricfyMatch.id == match_id).first()
    if not match:
        raise HTTPException(404, "Match not found")
    db.delete(match)
    db.commit()
    return {"message": "Match deleted"}


@router.get("/series/list")
async def list_series(db: Session = Depends(get_db)):
    series = db.query(CricfyMatch.series_name).distinct().filter(
        CricfyMatch.series_name.isnot(None)
    ).all()
    return sorted(set(s[0] for s in series if s[0]))


@router.get("/platforms/list")
async def list_platforms(db: Session = Depends(get_db)):
    platforms = db.query(CricfyMatch.platform).distinct().all()
    return sorted(set(p[0] for p in platforms))
