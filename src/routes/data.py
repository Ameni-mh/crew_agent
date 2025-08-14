# main.py
from fastapi import FastAPI, Depends, HTTPException, Request, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import uuid
from fastapi.responses import JSONResponse
from model.db_schemas.user import User
from model.userModel import UserModel
from model.db_schemas.general_travel_preferences import GeneralPreferences
from model.generalModel import GeneralPreferencesModel

data_router= APIRouter(
    prefix="/api/v1/profil",
    tags= ["api_v1"],
)


# Response schema
class UserResponse(BaseModel):
    user_id: int
    user_uuid: uuid.UUID
    username: str
    general_user_id: int
    hotel_user_id: int

    class Config:
        orm_mode = True

@data_router.post("/users", response_model=UserResponse)
async def create_user_endpoint(request: Request, user_name:str):
    user_model = await UserModel.create_instance(db_client=request.app.db_client)

    db_user = User(
        username=user_name,
    )

    try:
        created_user = await user_model.create_user(db_user)
        return {"message": "User created successfully"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
    
@data_router.post("/users/{user_id}")
async def create_general_preferences(request: Request, user_id:str, currencies: str, budget: int):
    general_pref_model = await GeneralPreferencesModel.create_instance(db_client=request.app.db_client)

    general_pref = GeneralPreferences(currencies=currencies, budget=budget, general_user_id=int(user_id))

    try:
        created_genral = await general_pref_model.create_general_preferences(general_pref)
        return {"message": "User created successfully"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
