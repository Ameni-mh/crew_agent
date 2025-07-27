import re
from pydantic import BaseModel, Field, field_validator


class HotelDetailsRequest(BaseModel):
    hotel_id: int = Field(..., description="ID of the hotel")
    checkin: str = Field(
        ...,
        description="Check-in date in format DD-MM-YYYY",
        pattern=r"^\d{2}-\d{2}-\d{4}$",
    )
    checkout: str = Field(
        ...,
        description="Check-out date in format DD-MM-YYYY",
        pattern=r"^\d{2}-\d{2}-\d{4}$",
    )
    adults: int = Field(..., ge=1, description="Number of adults, must be at least 1")
    childs: int = Field(..., ge=0, description="Number of children")
    child_age: int = Field(..., ge=0, description="Age of the child")
    rooms: int = Field(..., ge=1, description="Number of rooms, must be at least 1")
    language: str = Field(..., description="Language code, e.g. 'en'")
    currency: str = Field(..., description="Currency code, e.g. 'usd'")
    nationality: str = Field(..., description="Nationality code, e.g. 'PK'")

    @field_validator("checkin", "checkout")
    def validate_date_format(cls, v):
        if not re.match(r"^\d{2}-\d{2}-\d{4}$", v):
            msg = "Date must be in DD-MM-YYYY format"
            raise ValueError(msg)
        return v
