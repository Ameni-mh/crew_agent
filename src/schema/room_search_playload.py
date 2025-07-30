from pydantic import BaseModel, Field 

class RoomSearchPayload(BaseModel):
    """Payload for room search request."""
    checkin: str = Field(..., description="chekin date of HotelSearchRequest")
    checkout: str = Field(..., description="Check-out date of HotelSearchRequest")
    adults: int = Field(..., ge=1, description="Number of adults of HotelSearchRequest")
    childs: int = Field(..., ge=0, description="Number of children of HotelSearchRequest")
    child_age: int = Field(..., ge=0, description="Age of the child of of HotelSearchRequest")
    rooms: int = Field(..., ge=1, description="Number of rooms of HotelSearchRequest")
    currency: str = Field(..., description="Currency code of HotelSearchRequest")
    nationality: str = Field(..., description="")