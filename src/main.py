from datetime import date
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from langchain.agents import tool
from config.config import settings
from Agent.extarct_field import agent_executor

app = FastAPI()

base_router = APIRouter(
    prefix="/api/v1",
    tags= ["api_v1"],
)

@base_router.post("/")
async def welcome(query: str):

    
  
   
    result = agent_executor.invoke({"input": query, "today_date": date.today()})

    return JSONResponse(
            content={
                "signal": "success",
                "result": result if result else "No results found",
            }
        )



app.include_router(base_router)