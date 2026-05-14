from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import threading

from backend.database.connection import get_db
from backend.database.models import Book, Order, OrderItem
from backend.models.schemas import BookResponse
from backend.services.vector_search import vector_search
from backend.services.recommender import recommender

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.get("/semantic")
async def semantic_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    results = vector_search.search(q, n_results=limit)
    if not results:
        return []

    book_ids = [r["id"] for r in results]
    books = db.query(Book).options(
        joinedload(Book.images), joinedload(Book.categories)
    ).filter(Book.id.in_(book_ids), Book.is_active == True).all()

    book_map = {b.id: b for b in books}
    output = []
    for r in results:
        b = book_map.get(r["id"])
        if b:
            d = {c.name: getattr(b, c.name) for c in Book.__table__.columns}
            d["images"] = b.images
            d["categories"] = b.categories
            output.append(BookResponse.model_validate(d))
    return output


@router.get("/similar/{book_id}")
async def similar_books(
    book_id: int,
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db),
):
    results = vector_search.get_similar_books(book_id, n_results=limit)
    if not results:
        return []

    book_ids = [r["id"] for r in results]
    books = db.query(Book).options(
        joinedload(Book.images), joinedload(Book.categories)
    ).filter(Book.id.in_(book_ids), Book.is_active == True).all()

    book_map = {b.id: b for b in books}
    output = []
    for r in results:
        b = book_map.get(r["id"])
        if b:
            d = {c.name: getattr(b, c.name) for c in Book.__table__.columns}
            d["images"] = b.images
            d["categories"] = b.categories
            output.append(BookResponse.model_validate(d))
    return output


@router.get("/recommendations")
async def get_recommendations(
    user_id: int = Query(1),
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db),
):
    from backend.database.models import User, ReadingSchedule

    user = db.query(User).filter(User.id == user_id).first()
    user_profile = {
        "liked_categories": [],
        "liked_authors": [],
        "budget_max": 100,
    }

    active_schedules = db.query(ReadingSchedule).filter(
        ReadingSchedule.user_id == user_id, ReadingSchedule.is_active == True
    ).all()
    for s in active_schedules:
        book = db.query(Book).filter(Book.id == s.book_id).first()
        if book:
            if book.author:
                user_profile["liked_authors"].append(book.author)

    recent_orders = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.book).joinedload(Book.images),
    ).filter(Order.user_id == user_id).order_by(
        Order.created_at.desc()
    ).limit(5).all()

    available = db.query(Book).options(
        joinedload(Book.images), joinedload(Book.categories)
    ).filter(Book.is_active == True, Book.stock_quantity > 0).all()

    available_list = []
    for b in available:
        d = {c.name: getattr(b, c.name) for c in Book.__table__.columns}
        d["images"] = b.images
        d["categories"] = b.categories
        available_list.append(BookResponse.model_validate(d))

    recommended = recommender.recommend_for_user(
        user_profile=user_profile,
        available_books=available_list,
        recent_orders=recent_orders,
    )
    return recommended[:limit]


@router.post("/reindex")
async def reindex_books(db: Session = Depends(get_db)):
    def _reindex():
        from backend.database.connection import SessionLocal
        s = SessionLocal()
        try:
            books = s.query(Book).filter(Book.is_active == True).all()
            book_dicts = [
                {"id": b.id, "title": b.title, "author": b.author or "",
                 "description": b.description or "", "price": b.price or 0,
                 "isbn": b.isbn or ""}
                for b in books
            ]
            count = vector_search.reindex(book_dicts)
            print(f"Reindexed {count} books")
        finally:
            s.close()

    thread = threading.Thread(target=_reindex, daemon=True)
    thread.start()
    return {"message": "Reindex started"}


@router.get("/status")
async def search_status():
    return {
        "indexed_books": vector_search.count,
        "chroma_db_path": str(CHROMA_DIR),
    }


from backend.services.vector_search import CHROMA_DIR
