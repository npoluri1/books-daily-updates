from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from backend.database.models import ShippingZone, Country, CurrencyRate


SHIPPING_ZONES = {
    "domestic": {"name": "Domestic (US)", "countries": ["US"], "base_rate": 3.99, "rate_per_kg": 0.50, "days": "3-5"},
    "north_america": {"name": "North America", "countries": ["CA", "MX"], "base_rate": 5.99, "rate_per_kg": 1.00, "days": "5-8"},
    "europe": {"name": "Europe", "countries": ["GB", "DE", "FR", "IT", "ES", "NL", "BE", "CH", "SE", "NO", "DK", "FI", "AT", "IE", "PT", "PL", "CZ", "GR", "HU", "RO", "UA"], "base_rate": 8.99, "rate_per_kg": 1.50, "days": "7-12"},
    "asia_pacific": {"name": "Asia Pacific", "countries": ["IN", "SG", "JP", "CN", "KR", "AU", "NZ", "HK", "TW", "MY", "TH", "VN", "PH", "ID"], "base_rate": 9.99, "rate_per_kg": 2.00, "days": "8-14"},
    "middle_east": {"name": "Middle East & Africa", "countries": ["AE", "SA", "QA", "KW", "BH", "OM", "ZA", "NG", "KE", "EG", "IL", "TR"], "base_rate": 12.99, "rate_per_kg": 2.50, "days": "10-18"},
    "south_america": {"name": "South America", "countries": ["BR", "AR", "CL", "CO", "PE", "EC", "UY", "VE"], "base_rate": 14.99, "rate_per_kg": 3.00, "days": "12-20"},
    "rest_of_world": {"name": "Rest of World", "countries": ["RU", "other"], "base_rate": 19.99, "rate_per_kg": 3.50, "days": "14-25"},
}

CURRENCIES = {
    "USD": {"name": "US Dollar", "symbol": "$", "rate": 1.0},
    "EUR": {"name": "Euro", "symbol": "\u20ac", "rate": 0.92},
    "GBP": {"name": "British Pound", "symbol": "\u00a3", "rate": 0.79},
    "INR": {"name": "Indian Rupee", "symbol": "\u20b9", "rate": 83.50},
    "AED": {"name": "UAE Dirham", "symbol": "\u062f.\u0625", "rate": 3.67},
    "SGD": {"name": "Singapore Dollar", "symbol": "S$", "rate": 1.35},
    "AUD": {"name": "Australian Dollar", "symbol": "A$", "rate": 1.54},
    "CAD": {"name": "Canadian Dollar", "symbol": "C$", "rate": 1.36},
    "JPY": {"name": "Japanese Yen", "symbol": "\u00a5", "rate": 151.50},
    "CNY": {"name": "Chinese Yuan", "symbol": "\u00a5", "rate": 7.24},
    "KRW": {"name": "South Korean Won", "symbol": "\u20a9", "rate": 1350.0},
    "BRL": {"name": "Brazilian Real", "symbol": "R$", "rate": 5.05},
    "ZAR": {"name": "South African Rand", "symbol": "R", "rate": 18.50},
    "NGN": {"name": "Nigerian Naira", "symbol": "\u20a6", "rate": 1550.0},
    "MYR": {"name": "Malaysian Ringgit", "symbol": "RM", "rate": 4.72},
}


def seed_shipping_zones(db: Session):
    if db.query(ShippingZone).count() > 0:
        return
    for key, zone in SHIPPING_ZONES.items():
        db_zone = ShippingZone(
            name=zone["name"],
            description=f"Shipping to {zone['name']}",
            base_rate=zone["base_rate"],
            rate_per_kg=zone["rate_per_kg"],
            free_shipping_min=50.0 if key != "rest_of_world" else 100.0,
            estimated_days_min=int(zone["days"].split("-")[0]),
            estimated_days_max=int(zone["days"].split("-")[1]),
        )
        db.add(db_zone)
        db.flush()
        for country_code in zone["countries"]:
            if country_code == "other":
                continue
            country_name = COUNTRY_NAMES.get(country_code, country_code)
            currency = COUNTRY_CURRENCY.get(country_code, "USD")
            db.add(Country(code=country_code, name=country_name, zone_id=db_zone.id, currency_code=currency))
    db.commit()
    seed_currencies(db)


def seed_currencies(db: Session):
    if db.query(CurrencyRate).count() > 0:
        return
    for code, info in CURRENCIES.items():
        db.add(CurrencyRate(
            code=code, name=info["name"], symbol=info["symbol"],
            rate_to_usd=info["rate"], is_default=(code == "USD"),
        ))
    db.commit()


def calculate_shipping(db: Session, country_code: str, total_weight_kg: float = 1.0, subtotal: float = 0.0) -> Optional[Dict]:
    country = db.query(Country).filter(Country.code == country_code).first()
    if not country:
        country = db.query(Country).filter(Country.code == "US").first()
    if not country:
        return None
    zone = db.query(ShippingZone).filter(ShippingZone.id == country.zone_id).first()
    if not zone:
        return None
    if zone.free_shipping_min and subtotal >= zone.free_shipping_min:
        return {
            "zone_id": zone.id, "zone_name": zone.name,
            "base_rate": 0, "rate_per_kg": 0,
            "estimated_days": f"{zone.estimated_days_min}-{zone.estimated_days_max}",
            "total_shipping": 0.0, "free_shipping": True,
        }
    total = zone.base_rate + (zone.rate_per_kg * total_weight_kg)
    return {
        "zone_id": zone.id, "zone_name": zone.name,
        "base_rate": zone.base_rate, "rate_per_kg": zone.rate_per_kg,
        "estimated_days": f"{zone.estimated_days_min}-{zone.estimated_days_max}",
        "total_shipping": round(total, 2), "free_shipping": False,
    }


def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    if from_currency == to_currency:
        return round(amount, 2)
    rates = {c["rate"] for c in CURRENCIES.values()}
    from_rate = CURRENCIES.get(from_currency, {}).get("rate", 1.0)
    to_rate = CURRENCIES.get(to_currency, {}).get("rate", 1.0)
    usd_amount = amount / from_rate
    return round(usd_amount * to_rate, 2)


def get_all_zones(db: Session) -> List[Dict]:
    zones = db.query(ShippingZone).filter(ShippingZone.is_active == True).all()
    result = []
    for z in zones:
        country_count = db.query(Country).filter(Country.zone_id == z.id).count()
        result.append({
            "id": z.id, "name": z.name, "description": z.description,
            "base_rate": z.base_rate, "rate_per_kg": z.rate_per_kg,
            "free_shipping_min": z.free_shipping_min,
            "estimated_days_min": z.estimated_days_min,
            "estimated_days_max": z.estimated_days_max,
            "country_count": country_count,
        })
    return result


COUNTRY_NAMES = {
    "US": "United States", "CA": "Canada", "MX": "Mexico",
    "GB": "United Kingdom", "DE": "Germany", "FR": "France", "IT": "Italy",
    "ES": "Spain", "NL": "Netherlands", "BE": "Belgium", "CH": "Switzerland",
    "SE": "Sweden", "NO": "Norway", "DK": "Denmark", "FI": "Finland",
    "AT": "Austria", "IE": "Ireland", "PT": "Portugal", "PL": "Poland",
    "CZ": "Czech Republic", "GR": "Greece", "HU": "Hungary", "RO": "Romania",
    "UA": "Ukraine",
    "IN": "India", "SG": "Singapore", "JP": "Japan", "CN": "China",
    "KR": "South Korea", "AU": "Australia", "NZ": "New Zealand",
    "HK": "Hong Kong", "TW": "Taiwan", "MY": "Malaysia", "TH": "Thailand",
    "VN": "Vietnam", "PH": "Philippines", "ID": "Indonesia",
    "AE": "UAE", "SA": "Saudi Arabia", "QA": "Qatar", "KW": "Kuwait",
    "BH": "Bahrain", "OM": "Oman", "ZA": "South Africa", "NG": "Nigeria",
    "KE": "Kenya", "EG": "Egypt", "IL": "Israel", "TR": "Turkey",
    "BR": "Brazil", "AR": "Argentina", "CL": "Chile", "CO": "Colombia",
    "PE": "Peru", "EC": "Ecuador", "UY": "Uruguay", "VE": "Venezuela",
    "RU": "Russia",
}

COUNTRY_CURRENCY = {
    "US": "USD", "CA": "CAD", "MX": "MXN",
    "GB": "GBP", "DE": "EUR", "FR": "EUR", "IT": "EUR", "ES": "EUR",
    "NL": "EUR", "BE": "EUR", "CH": "CHF", "SE": "SEK", "NO": "NOK",
    "DK": "DKK", "FI": "EUR", "AT": "EUR", "IE": "EUR", "PT": "EUR",
    "PL": "PLN", "CZ": "CZK", "GR": "EUR", "HU": "HUF", "RO": "RON",
    "UA": "UAH",
    "IN": "INR", "SG": "SGD", "JP": "JPY", "CN": "CNY", "KR": "KRW",
    "AU": "AUD", "NZ": "NZD", "HK": "HKD", "TW": "TWD", "MY": "MYR",
    "TH": "THB", "VN": "VND", "PH": "PHP", "ID": "IDR",
    "AE": "AED", "SA": "SAR", "QA": "QAR", "KW": "KWD", "BH": "BHD",
    "OM": "OMR", "ZA": "ZAR", "NG": "NGN", "KE": "KES", "EG": "EGP",
    "IL": "ILS", "TR": "TRY",
    "BR": "BRL", "AR": "ARS", "CL": "CLP", "CO": "COP", "PE": "PEN",
    "EC": "USD", "UY": "UYU", "VE": "VES", "RU": "RUB",
}
