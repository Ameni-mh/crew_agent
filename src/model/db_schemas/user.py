
from sqlalchemy import Column, Integer, DateTime, func, String
from model.db_schemas.travel_base import SQLAlchemyBase
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(SQLAlchemyBase):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_uuid = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    username = Column(String, nullable=False, unique=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)