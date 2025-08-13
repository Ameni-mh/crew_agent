from typing import List, Optional
from pydantic import BaseModel


class RoomOption(BaseModel):
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


class HotelDetailsRequestOutput(BaseModel):
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
    supplier_id: Optional[str]
    rooms: List[Room]
    checkin: str
    checkout: str
    policy: str
    booking_age_requirement: int
    cancellation: str
    tax_percentage: str
    hotel_phone: Optional[str]
    hotel_email: Optional[str]
    hotel_website: Optional[str]
    discount: int
