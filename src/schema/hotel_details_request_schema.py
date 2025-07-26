from pydantic import BaseModel, Field,  model_validator

class HotelSearchRequest(BaseModel):
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
        default=None, description="ISO 3166-1 alpha-2 country code"
    )
    language: str = Field( description="Language code, ISO 639-1 language code, Use detected language en default")
    currency: str = Field(default="USD", description="ISO 4217 currency code")
    child_age: int = Field(default=0, ge=0, description="Age of child (0 if none)")
    pagination: int = Field(default=1, ge=1, description="1 if requested, otherwise 0")
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