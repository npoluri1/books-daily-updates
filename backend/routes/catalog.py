from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import datetime, timezone

from backend.database.connection import get_db
from backend.database.models import (
    Book, Category, BookImage, BookReview, MediaContent,
    book_categories
)
from backend.models.schemas import (
    BookResponse, BookWithChapters, BookReviewResponse, BookReviewCreate,
    CategoryResponse, MediaContentResponse, CatalogFilter,
)

router = APIRouter(prefix="/api/catalog", tags=["Catalog"])


@router.get("/", response_model=List[BookResponse])
async def list_catalog(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    in_stock: bool = Query(True),
    is_digital: Optional[bool] = Query(None),
    sort_by: str = Query("title"),
    sort_order: str = Query("asc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Book).options(
        joinedload(Book.images), joinedload(Book.categories)
    ).filter(Book.is_active == True)

    if category:
        query = query.join(Book.categories).filter(Category.slug == category)

    if search:
        q = f"%{search}%"
        query = query.filter(
            Book.title.ilike(q) | Book.author.ilike(q) | Book.description.ilike(q)
        )

    if min_price is not None:
        query = query.filter(Book.price >= min_price)
    if max_price is not None:
        query = query.filter(Book.price <= max_price)
    if in_stock:
        query = query.filter(Book.stock_quantity > 0)
    if is_digital is not None:
        query = query.filter(Book.is_digital == is_digital)

    sort_col = getattr(Book, sort_by, Book.title)
    if sort_order == "desc":
        sort_col = sort_col.desc()
    else:
        sort_col = sort_col.asc()
    query = query.order_by(sort_col)

    total = query.count()
    books = query.offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for b in books:
        d = {c.name: getattr(b, c.name) for c in Book.__table__.columns}
        d["images"] = b.images
        d["categories"] = b.categories
        d["specifications"] = b.specifications or {}
        result.append(BookResponse.model_validate(d))
    return result


@router.get("/product-types")
async def list_product_types(db: Session = Depends(get_db)):
    types = db.query(Book.product_type).filter(Book.is_active == True).distinct().all()
    return sorted([t[0] for t in types])


@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(
    parent_id: Optional[int] = Query(None),
    top_level: bool = Query(False),
    db: Session = Depends(get_db),
):
    query = db.query(Category)
    if top_level:
        query = query.filter(Category.parent_id == None)
    elif parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    return query.order_by(Category.sort_order, Category.name).all()


@router.get("/categories/tree")
async def category_tree(db: Session = Depends(get_db)):
    parents = db.query(Category).filter(Category.parent_id == None).order_by(Category.sort_order).all()
    tree = []
    for p in parents:
        children = db.query(Category).filter(Category.parent_id == p.id).order_by(Category.name).all()
        tree.append({
            "id": p.id, "name": p.name, "slug": p.slug,
            "description": p.description, "icon": p.icon,
            "children": [
                {"id": c.id, "name": c.name, "slug": c.slug, "icon": c.icon}
                for c in children
            ]
        })
    return tree


@router.get("/featured", response_model=List[BookResponse])
async def get_featured_books(limit: int = Query(8, le=20), db: Session = Depends(get_db)):
    books = db.query(Book).options(
        joinedload(Book.images), joinedload(Book.categories)
    ).filter(Book.is_active == True, Book.stock_quantity > 0).order_by(
        Book.created_at.desc()
    ).limit(limit).all()
    result = []
    for b in books:
        d = {c.name: getattr(b, c.name) for c in Book.__table__.columns}
        d["images"] = b.images
        d["categories"] = b.categories
        result.append(BookResponse.model_validate(d))
    return result


@router.get("/{book_id}", response_model=BookWithChapters)
async def get_book_detail(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).options(
        joinedload(Book.images), joinedload(Book.categories),
        joinedload(Book.chapters), joinedload(Book.reviews),
        joinedload(Book.media),
    ).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")
    return book


@router.post("/{book_id}/reviews", response_model=BookReviewResponse)
async def create_review(
    book_id: int, review: BookReviewCreate,
    user_id: int = Query(1), db: Session = Depends(get_db),
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")
    db_review = BookReview(
        book_id=book_id, user_id=user_id,
        rating=review.rating, title=review.title, comment=review.comment,
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@router.get("/{book_id}/reviews", response_model=List[BookReviewResponse])
async def get_book_reviews(book_id: int, db: Session = Depends(get_db)):
    return db.query(BookReview).filter(
        BookReview.book_id == book_id
    ).order_by(BookReview.created_at.desc()).all()
