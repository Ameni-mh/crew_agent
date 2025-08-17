from typing import Optional, List
from pydantic import BaseModel, Field

class RoomOption(BaseModel):
    room_name: str = Field(..., description="The name of the room option.")
    count: int = Field(..., ge=1, description="The number of rooms booked.")

class CheckoutDetails(BaseModel):
    """
    Represents the details of a checkout process.
    """
    hotel_id: str = Field(..., description="The unique identifier for the hotel.")
    hotel_name: str = Field(..., description="The name of the hotel.")
    room_options: List[RoomOption] = Field(..., description="The selected room option for the booking.")
    