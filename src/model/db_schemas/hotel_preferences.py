
from model.db_schemas.travel_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Index
import uuid

class HotelPreferences(SQLAlchemyBase):
    __tablename__ = "hotel_preferences"

    hotel_id = Column(Integer, primary_key=True, autoincrement=True)
    hotel_uuid = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    hotel_name = Column(String, nullable=False)
    room_type = Column(String, nullable=False)
    amenities = Column(String, nullable=True)
    pet_friendly = Column(Boolean, nullable=True)
    view_preference = Column(String, nullable=True)

    hotel_user_id = Column(String, ForeignKey("user.user_id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    user = relationship("User", back_populates="hotelPreferences")

    __table_args__ = (
        Index('ix_hotelPreferences_user_id', hotel_user_id),
    )