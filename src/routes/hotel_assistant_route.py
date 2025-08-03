from fastapi import  APIRouter
from datetime import datetime

from Agent.lookup_hotels import agent_executor



hotel_router = APIRouter(
    prefix="/api/v1",
    tags= ["api_v1"],
)

config = {"configurable": {"thread_id":"ab22"}}
messages = []
@hotel_router.post("/hotels")
async def hotel_assistant(query: str):
    
    
    
    inputs={
        "today_date": datetime.now().strftime("%Y-%m-%d"),
        "input": query,
        "chat_history": messages
    }
    
    result = await agent_executor.ainvoke(inputs,
        config=config
        )
    messages.append({"human": query, "ai": result["messages"][-1].content})


    response = result['messages'][-1].content

    return {"result": response}