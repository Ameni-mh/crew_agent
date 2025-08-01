from pydantic import BaseModel, Field
from typing import List, Optional, Union
from decimal import Decimal


class RoomOption(BaseModel):
    """Model for room booking options"""
    id: str
    currency: str
    price: str
    per_day: str
    markup_price: str
    markup_price_per_night: str
    service_fee: int
    quantity: int
    adults: int
    child: int
    children_ages: str
    bookingurl: str
    booking_data: str
    extrabeds_quantity: int
    extrabed_price: int
    cancellation: str
    breakfast: str
    room_booked: bool


class Room(BaseModel):
    """Model for hotel room details"""
    id: str
    name: str
    actual_price: str
    actual_price_per_night: str
    markup_price: str
    markup_price_per_night: str
    service_fee: int
    currency: str
    refundable: str
    refundable_date: str
    img: List[str]
    amenities: List[str]
    options: List[RoomOption]


class HotelDetailsData(BaseModel):
    """Main hotel model"""
    id: int
    name: str
    city: str
    country: str
    address: str
    stars: str
    ratings: int
    longitude: str
    latitude: str
    desc: str
    img: List[str]
    amenities: List[str]
    supplier_name: str
    supplier_id: Optional[str] = None
    rooms: List[Room]
    checkin: str
    checkout: str
    policy: str
    booking_age_requirement: int
    cancellation: str
    tax_percentage: str
    hotel_phone: Optional[str] = None
    hotel_email: Optional[str] = None
    hotel_website: Optional[str] = None
    discount: int


