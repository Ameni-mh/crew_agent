from fastapi import FastAPI
from routes.hotel_assistant_route import hotel_router


app = FastAPI()

       


app.include_router(hotel_router)