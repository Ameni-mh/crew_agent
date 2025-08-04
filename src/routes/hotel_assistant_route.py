from fastapi import  APIRouter
from datetime import datetime

from Agent.lookup_hotels import agent



hotel_router = APIRouter(
    prefix="/api/v1",
    tags= ["api_v1"],
)

config = {"configurable": {"thread_id":"1", "date": datetime.now().strftime("%Y-%m-%d")}}
#messages = []
@hotel_router.post("/hotels")
async def hotel_assistant(query: str):
    
    
    
    input={
        "role" : "user",
        "content" : query,
    }
    
    result = await  agent.ainvoke({"messages":[input]},config=config)
    #messages.append(inputs)

    responce =  result["messages"][-1].content
    #response = result['messages'][-1].content
    print(result)

    return {"result": responce}