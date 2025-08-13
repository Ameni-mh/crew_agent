

from browserbase import BaseModel
from sqlalchemy.future import select

from model.db_schemas.hotel_preferences import HotelPreferences



class HotelPreferencesModel(BaseModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance
    
    async def create_hotel_preferences(self, hotel_preferences: HotelPreferences):

        async with self.db_client() as session:
            async with session.begin():
                session.add(hotel_preferences)
            await session.commit()
            await session.refresh(hotel_preferences)
        return hotel_preferences
    
    async def get_hotelPreferences_perUser(self, hotel_user_id: int):

        async with self.db_client() as session:
            stmt = select(HotelPreferences).where(
                HotelPreferences.hotel_user_id == hotel_user_id
            )
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
        return record