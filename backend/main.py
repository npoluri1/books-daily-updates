from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, joinedload
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import settings
from backend.database.connection import init_db, get_db
from backend.tasks.scheduler import start_scheduler

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    init_db()
    start_scheduler()
    try:
        from backend.data.seed_catalog import seed
        seed()
    except Exception as e:
        print(f"Seed skipped: {e}")
    try:
        from backend.database.connection import SessionLocal
        db = SessionLocal()
        seed_shipping_zones(db)
        db.close()
    except Exception as e:
        print(f"Shipping seed skipped: {e}")
    try:
        from backend.database.connection import SessionLocal
        db = SessionLocal()
        books = db.query(Book).filter(Book.is_active == True).all()
        book_dicts = [{"id": b.id, "title": b.title, "author": b.author or "",
                       "description": b.description or "", "price": b.price or 0,
                       "isbn": b.isbn or ""} for b in books]
        if book_dicts:
            count = vector_search.index_books(book_dicts)
            print(f"Indexed {count} books in vector DB")
        db.close()
    except Exception as e:
        print(f"Vector index skipped: {e}")


from backend.routes import books, reading, users, catalog, media, store, podcasts, videos, search as search_route, cricfy
app.include_router(books.router)
app.include_router(reading.router)
app.include_router(users.router)
app.include_router(catalog.router)
app.include_router(media.router)
app.include_router(store.router)
app.include_router(podcasts.router)
app.include_router(videos.router)
app.include_router(search_route.router)
app.include_router(cricfy.router)

from backend.services.vector_search import vector_search
from backend.database.models import Book

from backend.services.shipping_service import seed_shipping_zones
from backend.database.models import (
    Book, Category, ReadingSchedule, ChapterSummary, CartItem,
    Order, OrderItem, MediaContent, PodcastEpisode, PlaylistVideo,
    CricfyMatch,
)
from backend.models.schemas import DashboardStats, BookResponse


@app.get("/api/dashboard", response_model=DashboardStats)
async def get_dashboard(user_id: int = Query(1), db: Session = Depends(get_db)):
    total_books = db.query(Book).filter(Book.is_active == True).count()
    total_categories = db.query(Category).count()
    active_schedules = db.query(ReadingSchedule).filter(
        ReadingSchedule.user_id == user_id, ReadingSchedule.is_active == True
    ).count()
    chapters_read = db.query(ChapterSummary).filter(
        ChapterSummary.is_sent == True
    ).count()
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).count()
    total_orders = db.query(Order).filter(Order.user_id == user_id).count()
    total_media = db.query(MediaContent).count()
    total_podcasts = db.query(PodcastEpisode).count()
    total_videos = db.query(PlaylistVideo).count()
    live_matches = db.query(CricfyMatch).filter(CricfyMatch.status == "live").count()
    total_cricfy_matches = db.query(CricfyMatch).count()

    featured = db.query(Book).options(
        joinedload(Book.images), joinedload(Book.categories)
    ).filter(Book.is_active == True, Book.stock_quantity > 0).order_by(
        Book.created_at.desc()
    ).limit(8).all()
    featured_list = []
    for b in featured:
        d = {c.name: getattr(b, c.name) for c in Book.__table__.columns}
        d["images"] = b.images
        d["categories"] = b.categories
        featured_list.append(BookResponse.model_validate(d))

    recent_orders = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.book).joinedload(Book.images),
    ).filter(Order.user_id == user_id).order_by(
        Order.created_at.desc()
    ).limit(5).all()

    return DashboardStats(
        total_books=total_books, total_categories=total_categories,
        active_schedules=active_schedules, chapters_read=chapters_read,
        cart_items=cart_items, total_orders=total_orders,
        total_media=total_media, total_podcasts=total_podcasts,
        total_videos=total_videos,
        live_matches=live_matches, total_cricfy_matches=total_cricfy_matches,
        featured_books=featured_list, recent_orders=recent_orders,
    )


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }


frontend_dir = Path(__file__).parent.parent / "frontend" / "build"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

static_dir = Path(__file__).parent / "static"
app.mount("/backend-static", StaticFiles(directory=str(static_dir)), name="static")


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
