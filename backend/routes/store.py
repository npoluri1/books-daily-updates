from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timezone
import random
import string

from backend.database.connection import get_db
from backend.database.models import (
    CartItem, Order, OrderItem, Book, ShippingAddress, User,
    ShippingZone, Country, CurrencyRate,
)
from backend.models.schemas import (
    CartItemResponse, CartResponse, OrderResponse,
    ShippingAddressCreate, ShippingAddressResponse,
    CheckoutRequest, ShippingZoneResponse, CountryResponse,
    CurrencyRateResponse, ShippingEstimate,
)
from backend.services.shipping_service import (
    calculate_shipping, convert_currency, get_all_zones, seed_shipping_zones,
    SHIPPING_ZONES, COUNTRY_NAMES,
)

router = APIRouter(prefix="/api/store", tags=["Store"])


def _generate_order_number():
    ts = datetime.now().strftime("%Y%m%d")
    rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"BD-{ts}-{rand}"


@router.get("/cart", response_model=CartResponse)
async def get_cart(
    user_id: int = Query(1),
    currency: str = Query("USD"),
    db: Session = Depends(get_db),
):
    items = db.query(CartItem).options(
        joinedload(CartItem.book).joinedload(Book.images)
    ).filter(CartItem.user_id == user_id).all()

    subtotal = 0.0
    cart_items = []
    for item in items:
        price = item.book.price if item.book else 0
        converted = convert_currency(price, "USD", currency)
        subtotal += converted * item.quantity
        book_dict = None
        if item.book:
            cols = {c.name: getattr(item.book, c.name) for c in Book.__table__.columns}
            from backend.models.schemas import BookResponse
            cols["images"] = item.book.images
            cols["categories"] = []
            book_dict = BookResponse.model_validate(cols)
        cart_items.append(CartItemResponse(
            id=item.id, book_id=item.book_id,
            quantity=item.quantity, is_digital=item.is_digital,
            book=book_dict,
        ))

    return CartResponse(
        items=cart_items,
        total_items=sum(i.quantity for i in items),
        subtotal=round(subtotal, 2),
        currency=currency,
    )


@router.post("/cart/add")
async def add_to_cart(
    book_id: int,
    quantity: int = Query(1, ge=1),
    user_id: int = Query(1),
    db: Session = Depends(get_db),
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")

    existing = db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.book_id == book_id,
    ).first()

    if existing:
        existing.quantity += quantity
    else:
        item = CartItem(
            user_id=user_id, book_id=book_id,
            quantity=quantity, is_digital=book.is_digital,
        )
        db.add(item)

    db.commit()
    return {"message": f"Added '{book.title}' to cart", "quantity": quantity}


@router.put("/cart/{item_id}")
async def update_cart_item(
    item_id: int, quantity: int = Query(1, ge=1),
    user_id: int = Query(1), db: Session = Depends(get_db),
):
    item = db.query(CartItem).filter(
        CartItem.id == item_id, CartItem.user_id == user_id
    ).first()
    if not item:
        raise HTTPException(404, "Cart item not found")
    item.quantity = quantity
    db.commit()
    return {"message": "Cart updated"}


@router.delete("/cart/{item_id}")
async def remove_from_cart(
    item_id: int, user_id: int = Query(1),
    db: Session = Depends(get_db),
):
    item = db.query(CartItem).filter(
        CartItem.id == item_id, CartItem.user_id == user_id
    ).first()
    if not item:
        raise HTTPException(404, "Cart item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item removed from cart"}


@router.post("/checkout", response_model=OrderResponse)
async def checkout(
    req: CheckoutRequest,
    user_id: int = Query(1),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    cart_items = db.query(CartItem).options(
        joinedload(CartItem.book)
    ).filter(CartItem.user_id == user_id).all()

    if not cart_items:
        raise HTTPException(400, "Cart is empty")

    shipping_address_id = req.shipping_address_id
    country_code = "US"
    if req.shipping_address and not shipping_address_id:
        addr = ShippingAddress(user_id=user_id, **req.shipping_address.model_dump())
        db.add(addr)
        db.commit()
        db.refresh(addr)
        shipping_address_id = addr.id
        country_code = req.shipping_address.country
    elif shipping_address_id:
        addr = db.query(ShippingAddress).filter(ShippingAddress.id == shipping_address_id).first()
        if addr:
            country_code = addr.country

    subtotal = 0.0
    order_items_data = []

    for ci in cart_items:
        if not ci.book:
            continue
        price = ci.book.price
        converted = convert_currency(price, "USD", req.currency)
        subtotal += converted * ci.quantity
        order_items_data.append({
            "book_id": ci.book_id,
            "quantity": ci.quantity,
            "unit_price": converted,
            "is_digital": ci.book.is_digital,
        })

    shipping_cost = 0.0
    has_physical = any(not oi["is_digital"] for oi in order_items_data)
    if has_physical:
        shipping_info = calculate_shipping(db, country_code, subtotal=subtotal)
        if shipping_info:
            shipping_cost = shipping_info["total_shipping"]
        else:
            shipping_cost = 5.99

    tax_rate = 0.08
    tax = round(subtotal * tax_rate, 2)
    total = round(subtotal + shipping_cost + tax, 2)

    estimated_delivery = "Instant access (digital)"
    if has_physical:
        shipping_info = calculate_shipping(db, country_code, subtotal=subtotal)
        if shipping_info:
            estimated_delivery = f"{shipping_info['estimated_days']} business days via {shipping_info['zone_name']}"

    order = Order(
        order_number=_generate_order_number(),
        user_id=user_id,
        shipping_address_id=shipping_address_id,
        status="confirmed",
        subtotal=round(subtotal, 2),
        shipping_cost=shipping_cost,
        tax=tax,
        total=total,
        currency=req.currency,
        payment_method=req.payment_method,
        payment_status="paid",
        notes=req.notes,
        estimated_delivery=estimated_delivery,
    )
    db.add(order)
    db.flush()

    for oi_data in order_items_data:
        oi = OrderItem(order_id=order.id, **oi_data)
        db.add(oi)
        book = db.query(Book).filter(Book.id == oi_data["book_id"]).first()
        if book and book.stock_quantity > 0:
            book.stock_quantity -= oi_data["quantity"]

    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()
    db.refresh(order)

    return db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.book).joinedload(Book.images),
    ).filter(Order.id == order.id).first()


@router.get("/orders", response_model=List[OrderResponse])
async def list_orders(
    user_id: int = Query(1),
    db: Session = Depends(get_db),
):
    return db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.book).joinedload(Book.images),
    ).filter(Order.user_id == user_id).order_by(
        Order.created_at.desc()
    ).all()


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int, user_id: int = Query(1),
    db: Session = Depends(get_db),
):
    order = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.book).joinedload(Book.images),
    ).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    return order


@router.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: int, user_id: int = Query(1), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    order.status = "cancelled"
    db.commit()
    return {"message": "Order cancelled"}


@router.get("/addresses", response_model=List[ShippingAddressResponse])
async def list_addresses(user_id: int = Query(1), db: Session = Depends(get_db)):
    return db.query(ShippingAddress).filter(
        ShippingAddress.user_id == user_id
    ).all()


@router.post("/addresses", response_model=ShippingAddressResponse)
async def create_address(
    address: ShippingAddressCreate, user_id: int = Query(1),
    db: Session = Depends(get_db),
):
    if address.is_default:
        db.query(ShippingAddress).filter(
            ShippingAddress.user_id == user_id
        ).update({"is_default": False})
    addr = ShippingAddress(user_id=user_id, **address.model_dump())
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return addr


@router.delete("/addresses/{address_id}")
async def delete_address(
    address_id: int, user_id: int = Query(1),
    db: Session = Depends(get_db),
):
    addr = db.query(ShippingAddress).filter(
        ShippingAddress.id == address_id,
        ShippingAddress.user_id == user_id,
    ).first()
    if not addr:
        raise HTTPException(404, "Address not found")
    db.delete(addr)
    db.commit()
    return {"message": "Address deleted"}


@router.get("/shipping-zones", response_model=List[ShippingZoneResponse])
async def list_shipping_zones(db: Session = Depends(get_db)):
    return get_all_zones(db)


@router.get("/shipping-estimate")
async def estimate_shipping(
    country_code: str = Query("US"),
    subtotal: float = Query(0.0),
    db: Session = Depends(get_db),
):
    info = calculate_shipping(db, country_code, subtotal=subtotal)
    if not info:
        raise HTTPException(404, "No shipping available for this country")
    return info


@router.get("/currencies", response_model=List[CurrencyRateResponse])
async def list_currencies(db: Session = Depends(get_db)):
    return db.query(CurrencyRate).filter(CurrencyRate.is_active == True).all()


@router.get("/countries")
async def list_countries(db: Session = Depends(get_db)):
    countries = db.query(Country).filter(Country.is_active == True).all()
    result = {}
    for c in countries:
        zone = db.query(ShippingZone).filter(ShippingZone.id == c.zone_id).first()
        zone_name = zone.name if zone else "Unknown"
        if zone_name not in result:
            result[zone_name] = []
        result[zone_name].append({
            "id": c.id, "code": c.code, "name": c.name,
            "currency_code": c.currency_code,
        })
    return result
