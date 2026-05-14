from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float,
    ForeignKey, JSON, Table, UniqueConstraint, Date
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone, date

Base = declarative_base()

book_categories = Table(
    "book_categories", Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    author = Column(String(300), nullable=True)
    isbn = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    publisher = Column(String(300), nullable=True)
    publication_year = Column(Integer, nullable=True)
    pages = Column(Integer, nullable=True)
    language = Column(String(50), default="English")
    total_chapters = Column(Integer, default=0)
    current_chapter = Column(Integer, default=0)
    price = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    stock_quantity = Column(Integer, default=0)
    is_digital = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    product_type = Column(String(50), default="book")
    brand = Column(String(200), nullable=True)
    specifications = Column(JSON, default=dict)
    source_file = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc))

    chapters = relationship("ChapterSummary", back_populates="book", cascade="all, delete-orphan")
    schedules = relationship("ReadingSchedule", back_populates="book", cascade="all, delete-orphan")
    images = relationship("BookImage", back_populates="book", cascade="all, delete-orphan")
    categories = relationship("Category", secondary=book_categories, back_populates="books")
    reviews = relationship("BookReview", back_populates="book", cascade="all, delete-orphan")
    media = relationship("MediaContent", back_populates="book", cascade="all, delete-orphan")


class BookImage(Base):
    __tablename__ = "book_images"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    url = Column(String(1000), nullable=False)
    alt_text = Column(String(500), nullable=True)
    is_primary = Column(Boolean, default=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    book = relationship("Book", back_populates="images")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    slug = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    books = relationship("Book", secondary=book_categories, back_populates="categories")
    children = relationship("Category", backref="parent", remote_side=[id])


class BookReview(Base):
    __tablename__ = "book_reviews"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    title = Column(String(300), nullable=True)
    comment = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    book = relationship("Book", back_populates="reviews")
    user = relationship("User", backref="reviews")


class MediaContent(Base):
    __tablename__ = "media_content"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    media_type = Column(String(50), nullable=False)
    platform = Column(String(50), nullable=False)
    url = Column(String(1000), nullable=False)
    embed_url = Column(String(1000), nullable=True)
    thumbnail_url = Column(String(1000), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    author = Column(String(300), nullable=True)
    tags = Column(JSON, default=list)
    is_featured = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    book = relationship("Book", back_populates="media")


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
    phone = Column(String(50), nullable=True)
    avatar_url = Column(String(500), nullable=True)
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
    addresses = relationship("ShippingAddress", back_populates="user", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")


class ShippingAddress(Base):
    __tablename__ = "shipping_addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    label = Column(String(100), default="Home")
    full_name = Column(String(300), nullable=False)
    street = Column(String(500), nullable=False)
    city = Column(String(200), nullable=False)
    state = Column(String(200), nullable=True)
    postal_code = Column(String(50), nullable=False)
    country = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="addresses")
    orders = relationship("Order", back_populates="shipping_address")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    quantity = Column(Integer, default=1)
    is_digital = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="cart_items")
    book = relationship("Book")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shipping_address_id = Column(Integer, ForeignKey("shipping_addresses.id"), nullable=True)
    status = Column(String(50), default="pending")
    subtotal = Column(Float, default=0.0)
    shipping_cost = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    payment_method = Column(String(50), nullable=True)
    payment_status = Column(String(50), default="pending")
    notes = Column(Text, nullable=True)
    tracking_number = Column(String(200), nullable=True)
    estimated_delivery = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="orders")
    shipping_address = relationship("ShippingAddress", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    is_digital = Column(Boolean, default=True)

    order = relationship("Order", back_populates="items")
    book = relationship("Book")


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


class ShippingZone(Base):
    __tablename__ = "shipping_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    base_rate = Column(Float, default=0.0)
    rate_per_kg = Column(Float, default=0.0)
    free_shipping_min = Column(Float, nullable=True)
    estimated_days_min = Column(Integer, default=5)
    estimated_days_max = Column(Integer, default=14)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    countries = relationship("Country", back_populates="zone", cascade="all, delete-orphan")


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(5), nullable=False, unique=True)
    name = Column(String(200), nullable=False)
    zone_id = Column(Integer, ForeignKey("shipping_zones.id"), nullable=False)
    currency_code = Column(String(5), default="USD")
    is_active = Column(Boolean, default=True)

    zone = relationship("ShippingZone", back_populates="countries")


class PodcastEpisode(Base):
    __tablename__ = "podcast_episodes"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    host = Column(String(300), nullable=True)
    platform = Column(String(50), nullable=False)
    audio_url = Column(String(1000), nullable=True)
    embed_url = Column(String(1000), nullable=True)
    thumbnail_url = Column(String(1000), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    episode_number = Column(Integer, nullable=True)
    season_number = Column(Integer, nullable=True)
    tags = Column(JSON, default=list)
    is_featured = Column(Boolean, default=False)
    listen_count = Column(Integer, default=0)
    published_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    book = relationship("Book", backref="podcast_episodes")


class VideoPlaylist(Base):
    __tablename__ = "video_playlists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    platform = Column(String(50), nullable=False)
    channel_name = Column(String(300), nullable=True)
    channel_url = Column(String(1000), nullable=True)
    thumbnail_url = Column(String(1000), nullable=True)
    is_featured = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    videos = relationship("PlaylistVideo", back_populates="playlist", cascade="all, delete-orphan")


class PlaylistVideo(Base):
    __tablename__ = "playlist_videos"

    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("video_playlists.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(1000), nullable=False)
    embed_url = Column(String(1000), nullable=True)
    thumbnail_url = Column(String(1000), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    platform = Column(String(50), nullable=False)
    view_count = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    playlist = relationship("VideoPlaylist", back_populates="videos")


class CricfyMatch(Base):
    __tablename__ = "cricfy_matches"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    team1 = Column(String(200), nullable=False)
    team2 = Column(String(200), nullable=False)
    team1_logo = Column(String(1000), nullable=True)
    team2_logo = Column(String(1000), nullable=True)
    match_date = Column(Date, nullable=False)
    match_time = Column(String(20), nullable=True)
    status = Column(String(20), default="upcoming")
    series_name = Column(String(300), nullable=True)
    venue = Column(String(300), nullable=True)
    live_url = Column(String(1000), nullable=True)
    embed_url = Column(String(1000), nullable=True)
    thumbnail_url = Column(String(1000), nullable=True)
    platform = Column(String(50), default="youtube")
    score_team1 = Column(String(50), nullable=True)
    score_team2 = Column(String(50), nullable=True)
    overs_team1 = Column(Float, nullable=True)
    overs_team2 = Column(Float, nullable=True)
    match_result = Column(String(500), nullable=True)
    is_featured = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CurrencyRate(Base):
    __tablename__ = "currency_rates"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(5), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    symbol = Column(String(10), nullable=False)
    rate_to_usd = Column(Float, default=1.0)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
