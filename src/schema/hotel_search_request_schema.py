#from langchain_core.pydantic_v1 import BaseModel
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    nationality: str = Field(..., description="Nationality code (ISO 3166-1 alpha-2), e.g., 'PK' for Pakistan")
    adults: Optional[int] = Field(default=1, ge=1, description="Number of adult guests")
    childs: Optional[int]  = Field(default=0, ge=0, description="Number of children")
    rooms: Optional[int]  = Field(default=1, ge=1, description="Number of rooms to book")
    language: Optional[str]  = Field(default="en", description="Language code (ISO 639-1), e.g., 'en' for English")
    currency: Optional[str]  = Field(default="USD", description="Currency code (ISO 4217), e.g., 'PHP' for Philippine Peso")
    child_age: Optional[int]  = Field(default=0, ge=0, description="Age of child (0 if none)")
    pagination: Optional[int]  = Field(default=1, ge=1, description="Pagination page number")
    price_from: Optional[int]  = Field(default=0, description="Minimum price filter")
    price_to: Optional[int]  = Field(default=5000000, description="Maximum price filter")
    ip: Optional[str]  = Field(default="0.0.0.0", description="ip") 

    # Optional fields (no value provided)
    module_name: Optional[str]   = Field("hotels", description="Module name, e.g., 'hotels'")
    rating: Optional[int]  = Field(default=None, description="Hotel rating filter")
    user_type: Optional[str]   = Field(default=None, description="") 

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"  # This allows extra fields from CrewAI
    )


    @model_validator(mode="after")
    def validate_dates(cls, values):
        checkin = values.get('checkin')
        checkout = values.get('checkout')

        try:
            datetime.strptime(checkin, '%d-%m-%Y')
        
        except ValueError:
            return "Date must be in DD-MM-YYYY format"

        try:
            datetime.strptime(checkout, '%d-%m-%Y')
            
        except ValueError:
            return "Date must be in DD-MM-YYYY format"

        if checkin and checkout:
            if checkout < checkin:
                return "Return date cannot be before departure date."
        return values

    @model_validator(mode="after")
    def validate_room(cls, values):
      adults = values.get('adults')
      childs = values.get('childs')
      rooms = values.get('rooms')

      if ((adults and adults > 1) or (childs and childs > 0)) and rooms == 1:
        return "should ask for how many rooms you need for your group"
      return values

    @model_validator(mode="after")
    def validate_child_age(cls, values):
      childs = values.get('childs')
      child_age = values.get('child_age')

      if (childs == 0 and child_age != 0) or (childs != 0 and child_age == 0):
            return "valid child age (should be 0 if there are no children)"
      if childs > 0 and (child_age < 0 or child_age > 17):
            return "a child age between 0 and 17"

      return values

    @model_validator(mode="after")
    def validate_price(cls, values):
      price_from = values.get('price_from')
      price_to = values.get('price_to')

      if price_from > price_to:
        return "a maximum price that is higher than the minimum price"





    

    
