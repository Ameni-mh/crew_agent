from model.baseModel import BaseDataModel
from model.db_schemas.user import User
from sqlalchemy.future import select
from sqlalchemy import func

class UserModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance
    
    async def create_user(self, user: User):
        async with self.db_client() as session:
            async with session.begin():
                session.add(user)
            await session.commit()
            await session.refresh(user)
        
        return user
    
    
                
    async def get_all_projects(self):

        async with self.db_client() as session:
            async with session.begin():

                query = select(User)
                users = await session.execute(query).scalars().all()

                return users