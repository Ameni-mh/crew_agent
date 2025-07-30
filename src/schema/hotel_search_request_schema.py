#from langchain_core.pydantic_v1 import BaseModel
from datetime import datetime

from pydantic import BaseModel, Field  


class HotelSearchRequest(BaseModel):
    # Required fields (values provided)
    city: str = Field(
        ..., description="The city to search for hotels in, e.g., 'Dubai'. If not provided, prompt the user for it."
    )
    checkin: str  = Field(
        ...,
        description="Check-in date (DD-MM-YYYY)",
        pattern=r"^\d{2}-\d{2}-\d{4}$",
    )
    checkout: str  = Field(
        ...,
        description="Check-out date (DD-MM-YYYY)",
        pattern=r"^\d{2}-\d{2}-\d{4}$",
    )
    adults: int = Field(default=1, ge=1, description="Number of adult guests")
    childs: int = Field(default=0, ge=0, description="Number of children")
    rooms: int = Field(default=1, ge=1, description="Number of rooms to book")
    nationality: str = Field(
        default=None, description="Nationality code, e.g., 'pk'"
    )
    language: str = Field(default="en", description="Language code, e.g., 'en'")
    currency: str = Field(default="USD", description="Currency code, e.g., 'php'")
    child_age: int = Field(default=0, ge=0, description="Age of child (0 if none)")
    pagination: int = Field(default=1, ge=1, description="Pagination page number")
    price_from: int = Field(default=0, description="Minimum price filter")
    price_to: int = Field(default=5000000, description="Maximum price filter")
    ip: str = Field(default="0.0.0.0", description="ip") 

    # Optional fields (no value provided)
    module_name: str  = Field("hotels", description="Module name, e.g., 'hotels'")
    rating: int = Field(None, description="Hotel rating filter")
    user_type: str  = Field(None, description="") 
    

    
