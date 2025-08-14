
from model.db_schemas.travel_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Index
import uuid

class GeneralPreferences(SQLAlchemyBase):
    __tablename__ = "general_preferences"

    general_id = Column(Integer, primary_key=True, autoincrement=True)
    general_uuid = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    hotel_name = Column(String, nullable=True)
    currencies = Column(String, nullable=True)
    budget = Column(Integer, nullable=True)

    general_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    user = relationship("User", back_populates="general_preferences")

    __table_args__ = (
        Index('ix_gneralPreferences_user_id', general_user_id),
    )