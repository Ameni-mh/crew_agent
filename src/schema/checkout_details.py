from typing import Optional
from pydantic import BaseModel, Field

class CheckoutDetails(BaseModel):
    """
    Represents the details of a checkout process.
    """
    hotel_id: str = Field(..., description="The unique identifier for the hotel.")
    hotel_name: str = Field(..., description="The name of the hotel.")
    room_option: str = Field(..., description="The selected room option for the booking.")
    room_count: int = Field(..., ge=1, description="The number of rooms booked.")