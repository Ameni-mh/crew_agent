from browserbase import BaseModel
from sqlalchemy.future import select
from model.db_schemas.general_travel_preferences import GeneralPreferences


class GeneralPreferencesModel(BaseModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance
    
    async def create_general_preferences(self, general_preferences: GeneralPreferences):

        async with self.db_client() as session:
            async with session.begin():
                session.add(general_preferences)
            await session.commit()
            await session.refresh(general_preferences)
        return general_preferences
    
    async def get_generalPreferences_perUser(self, general_user_id: str, general_id: str):

        async with self.db_client() as session:
            stmt = select(GeneralPreferences).where(
                GeneralPreferences.general_user_id == general_user_id,
                GeneralPreferences.general_id == general_id
            )
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
        return record