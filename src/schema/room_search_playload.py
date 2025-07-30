from pydantic import BaseModel, Field 

class RoomSearchPayload(BaseModel):
    """Payload for room search request."""
    checkin: str = Field(..., description="Hotel check-in date")
    checkout: str = Field(..., description="Hotel check-out date")
    adults: int = Field(..., ge=1, description="Number of adults")
    childs: int = Field(..., ge=0, description="Number of children")
    child_age: int = Field(..., ge=0, description="Age of the child")
    rooms: int = Field(..., ge=1, description="Number of rooms")
    currency: str = Field(..., description="Currency code (e.g., USD, EUR)")
    nationality: str = Field(..., description="Guest's nationality")