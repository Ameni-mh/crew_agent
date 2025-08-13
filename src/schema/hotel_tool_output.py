from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict


class HotelRequestOutput(BaseModel):
    hotel_id: int
    img: str
    name: str
    location: str
    address: str
    stars: str
    rating: str
    latitude: str
    longitude: str
    actual_price: float
    actual_price_per_night: float
    markup_price: float
    markup_price_per_night: float
    currency: str
    booking_currency: str
    service_fee: str
    supplier_name: str
    supplier_id: int
    redirect: str
    booking_data: Dict
    color: str
    option: int
    status: str# List of offers available for the hotel