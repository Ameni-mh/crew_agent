#from langchain_core.pydantic_v1 import BaseModel
from datetime import datetime

from pydantic import BaseModel, Field,  model_validator


class HotelSearchRequest(BaseModel):
    # Required fields (values provided)
    city: str = Field(
        ..., description="Search query city, e.g., 'dubai'"
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
    module_name: str  = Field(None, description="Module name, e.g., 'hotels'")
    rating: int  = Field(None, description="Hotel rating filter")
    user_type: str  = Field(None, description="")

    model_config = {
        "populate_by_name": True,
        "extra": "forbid"
    }

    @model_validator(mode="before")
    def validate_dates(cls, values):
        checkin = values.get('checkin')
        checkout = values.get('checkout')

        try:
            datetime.strptime(checkin, '%d-%m-%Y')
            
        except ValueError:
            raise ValueError('Date must be in DD-MM-YYYY format')

        try:
            datetime.strptime(checkout, '%d-%m-%Y')
            
        except ValueError:
            raise ValueError('Date must be in DD-MM-YYYY format')

        if checkin and checkout:
            if checkout < checkin:
                raise ValueError("Return date cannot be before departure date.")
        return values

    @model_validator(mode="before")
    def validate_room(cls, values): 
      adults = values.get('adults')
      childs = values.get('childs')
      rooms = values.get('rooms')
      
      if ((adults and adults > 1) or (childs and childs > 0)) and rooms == 1:
        raise ValueError("should ask for how many rooms you need for your group")
      return values

    @model_validator(mode="before")
    def validate_child_age(cls, values):
      childs = values.get('childs')
      child_age = values.get('child_age')

      if (childs == 0 and child_age != 0) or (childs != 0 and child_age == 0):
            raise ValueError("valid child age (should be 0 if there are no children)")
      if childs > 0 and (child_age < 0 or child_age > 17):
            raise ValueError("a child age between 0 and 17")
      
      return values

    @model_validator(mode="before")
    def validate_price(cls, values):
      price_from = values.get('price_from')
      price_to = values.get('price_to')

      if price_from > price_to:
        raise ValueError("a maximum price that is higher than the minimum price")
  
    

    
