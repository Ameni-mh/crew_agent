#from langchain_core.pydantic_v1 import BaseModel
from datetime import datetime, date
from typing import Optional, Any


from pydantic import BaseModel, ConfigDict, Field, field_validator


class HotelSearchRequest(BaseModel):
    # Required fields (values provided)
    city: str = Field(
        ..., description="The city to search for hotels in, e.g., 'Dubai'. If not provided, prompt the user for it."
    )
    checkin: str  = Field(
        ...,
        description="Check-in date (DD-MM-YYYY), must not be in the past",
        pattern=r"^\d{2}-\d{2}-\d{4}$",
    )
    checkout: str  = Field(
        ...,
        description="Check-out date (DD-MM-YYYY), does not be less than checkin date or in the past",
        pattern=r"^\d{2}-\d{2}-\d{4}$",
    )
    nationality: str = Field(..., description="Nationality code (ISO 3166-1 alpha-2), e.g., 'PK' for Pakistan")
    adults: Optional[int] = Field(default=1, ge=1, description="Number of adult guests")
    childs: Optional[int]  = Field(default=0, ge=0, description="Number of children")
    rooms: Optional[int]  = Field(default=1, ge=1, description="Number of rooms to book")
    language: Optional[str]  = Field(default="en", description="Language code (ISO 639-1), e.g., 'en' for English")
    currency: Optional[str]  = Field(default="USD", description="Currency code (ISO 4217), e.g., 'PHP' for Philippine Peso")
    child_age: Optional[int] = Field(default=0, ge=0, lt=18, description="Child's age (0–17 years)")
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
        extra="ignore"  
    )

    @field_validator('checkin')
    @classmethod
    def validate_checkin_date(cls, v: str) -> str:
        """Validate that check-in date is not in the past"""
        try:
            # Parse the date string
            checkin_date = datetime.strptime(v, "%d-%m-%Y" ).date()
            today = datetime.now().strftime("%d-%m-%Y")
            today = datetime.strptime(today , "%d-%m-%Y").date()
            
            if checkin_date < today:
                return f"Check-in date {v} cannot be in the past. Today is {datetime.now().strftime('%d-%m-%Y')}"
                
            return v
        except ValueError as e:
            if "time data" in str(e):
                return f"Invalid date format: {v}. Expected DD-MM-YYYY"
            
        
    @field_validator('checkout')
    @classmethod
    def validate_checkout_date(cls, v: str) -> str:
        """Validate that checkout date is not in the past"""
        try:
            # Parse the date string
            checkout_date = datetime.strptime(v, "%d-%m-%Y" ).date()
            today = datetime.now().strftime("%d-%m-%Y")
            today = datetime.strptime(today , "%d-%m-%Y").date()
            if checkout_date < today:
                return f"Check-out date {v} cannot be in the past. Today is {datetime.now().strftime('%d-%m-%Y')}"
                
            return v
        except ValueError as e:
            if "time data" in str(e):
                return f"Invalid date format: {v}. Expected DD-MM-YYYY"
            

    def model_post_init(self, __context: Any) -> None:
            """Additional validation after all fields are set"""
            try:
                checkin_date = datetime.strptime(self.checkin, "%d-%m-%Y").date()
                checkout_date = datetime.strptime(self.checkout, "%d-%m-%Y").date()
                
                if checkout_date <= checkin_date:
                    return f"Check-out date {self.checkout} must be after check-in date {self.checkin}"
                    
            except ValueError as e:
                if "must be after" in str(e):
                    return e
    