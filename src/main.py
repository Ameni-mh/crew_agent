from fastapi import FastAPI, APIRouter
from datetime import datetime
from redis.asyncio import Redis
from fastapi.responses import JSONResponse
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai import  Crew, Process
import agentops
from config.config import settings


from routes.hotel_assistant_route import hotel_router


app = FastAPI()


       
base_router = APIRouter(
    prefix="/api/v1",
    tags= ["api_v1"],
)








app.include_router(base_router)
app.include_router(hotel_router)