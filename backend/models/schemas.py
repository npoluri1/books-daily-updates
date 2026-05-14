from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime, time, date


class BookBase(BaseModel):
    title: str
    author: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    pages: Optional[int] = None
    language: str = "English"
    total_chapters: int = 0
    price: float = 0.0
    currency: str = "USD"
    stock_quantity: int = 0
    is_digital: bool = True
    product_type: str = "book"
    brand: Optional[str] = None
    specifications: dict = {}
    source_file: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookImageResponse(BaseModel):
    id: int
    url: str
    alt_text: Optional[str] = None
    is_primary: bool = False

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int = 0

    class Config:
        from_attributes = True


class BookResponse(BookBase):
    id: int
    current_chapter: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    images: List[BookImageResponse] = []
    categories: List[CategoryResponse] = []

    class Config:
        from_attributes = True


class BookReviewResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    rating: int
    title: Optional[str] = None
    comment: Optional[str] = None
    is_verified: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class BookReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None


class MediaContentResponse(BaseModel):
    id: int
    book_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    media_type: str
    platform: str
    url: str
    embed_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    author: Optional[str] = None
    tags: List[str] = []
    is_featured: bool = False
    view_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class MediaContentCreate(BaseModel):
    book_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    media_type: str
    platform: str
    url: str
    embed_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    author: Optional[str] = None
    tags: List[str] = []
    is_featured: bool = False


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
    reviews: List[BookReviewResponse] = []
    media: List[MediaContentResponse] = []
    podcast_episodes: List["PodcastEpisodeResponse"] = []

    class Config:
        from_attributes = True


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


class ShippingAddressCreate(BaseModel):
    label: str = "Home"
    full_name: str
    street: str
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str
    phone: Optional[str] = None
    is_default: bool = False


class ShippingAddressResponse(BaseModel):
    id: int
    user_id: int
    label: str
    full_name: str
    street: str
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str
    phone: Optional[str] = None
    is_default: bool = False

    class Config:
        from_attributes = True


class CartItemResponse(BaseModel):
    id: int
    book_id: int
    quantity: int
    is_digital: bool = True
    book: Optional[BookResponse] = None

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_items: int
    subtotal: float
    currency: str = "USD"


class OrderItemResponse(BaseModel):
    id: int
    book_id: int
    quantity: int
    unit_price: float
    is_digital: bool
    book: Optional[BookResponse] = None

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: int
    status: str
    subtotal: float
    shipping_cost: float
    tax: float
    total: float
    currency: str
    payment_method: Optional[str] = None
    payment_status: str
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    items: List[OrderItemResponse] = []
    shipping_zone: Optional[str] = None

    class Config:
        from_attributes = True


class CheckoutRequest(BaseModel):
    shipping_address_id: Optional[int] = None
    shipping_address: Optional[ShippingAddressCreate] = None
    payment_method: str = "card"
    currency: str = "USD"
    notes: Optional[str] = None
    shipping_zone_id: Optional[int] = None


class CatalogFilter(BaseModel):
    category: Optional[str] = None
    search: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    in_stock: bool = True
    is_digital: Optional[bool] = None
    sort_by: str = "title"
    sort_order: str = "asc"
    page: int = 1
    page_size: int = 20


class ShippingZoneResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    base_rate: float = 0.0
    rate_per_kg: float = 0.0
    free_shipping_min: Optional[float] = None
    estimated_days_min: int = 5
    estimated_days_max: int = 14
    is_active: bool = True
    country_count: int = 0

    class Config:
        from_attributes = True


class CountryResponse(BaseModel):
    id: int
    code: str
    name: str
    zone_id: int
    currency_code: str = "USD"
    is_active: bool = True

    class Config:
        from_attributes = True


class PodcastEpisodeResponse(BaseModel):
    id: int
    book_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    host: Optional[str] = None
    platform: str
    audio_url: Optional[str] = None
    embed_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    episode_number: Optional[int] = None
    season_number: Optional[int] = None
    tags: List[str] = []
    is_featured: bool = False
    listen_count: int = 0
    published_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PlaylistVideoResponse(BaseModel):
    id: int
    playlist_id: int
    title: str
    description: Optional[str] = None
    url: str
    embed_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    platform: str
    view_count: int = 0
    sort_order: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class VideoPlaylistResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    platform: str
    channel_name: Optional[str] = None
    channel_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_featured: bool = False
    sort_order: int = 0
    videos: List[PlaylistVideoResponse] = []

    class Config:
        from_attributes = True


class CurrencyRateResponse(BaseModel):
    id: int
    code: str
    name: str
    symbol: str
    rate_to_usd: float = 1.0
    is_default: bool = False

    class Config:
        from_attributes = True


class ShippingEstimate(BaseModel):
    zone_id: int
    zone_name: str
    base_rate: float
    rate_per_kg: float
    estimated_days: str
    total_shipping: float


class CricfyMatchResponse(BaseModel):
    id: int
    title: str
    team1: str
    team2: str
    team1_logo: Optional[str] = None
    team2_logo: Optional[str] = None
    match_date: date
    match_time: Optional[str] = None
    status: str = "upcoming"
    series_name: Optional[str] = None
    venue: Optional[str] = None
    live_url: Optional[str] = None
    embed_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    platform: str = "youtube"
    score_team1: Optional[str] = None
    score_team2: Optional[str] = None
    overs_team1: Optional[float] = None
    overs_team2: Optional[float] = None
    match_result: Optional[str] = None
    is_featured: bool = False
    view_count: int = 0

    class Config:
        from_attributes = True


class CricfyMatchCreate(BaseModel):
    title: str
    team1: str
    team2: str
    team1_logo: Optional[str] = None
    team2_logo: Optional[str] = None
    match_date: date
    match_time: Optional[str] = None
    status: str = "upcoming"
    series_name: Optional[str] = None
    venue: Optional[str] = None
    live_url: Optional[str] = None
    embed_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    platform: str = "youtube"
    is_featured: bool = False


class DashboardStats(BaseModel):
    total_books: int
    total_categories: int
    active_schedules: int
    chapters_read: int
    cart_items: int
    total_orders: int
    total_media: int
    total_podcasts: int
    total_videos: int
    live_matches: int = 0
    total_cricfy_matches: int = 0
    featured_books: List[BookResponse] = []
    recent_orders: List[OrderResponse] = []
