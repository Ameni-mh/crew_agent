from fastapi import  APIRouter
from datetime import datetime

from Agent.lookup_hotels import agent



hotel_router = APIRouter(
    prefix="/api/v1",
    tags= ["api_v1"],
)



@hotel_router.post("/hotels")
async def hotel_assistant(query: str, user_id:str, con_id: str):
    config = {"configurable": {"thread_id":con_id, 
                               "date": datetime.now().strftime("%d-%m-%y"),
                               "user_id": user_id}}
    
    input={
        "role" : "user",
        "content" : query,
    }
    
    result = await  agent.ainvoke({"messages":[input]},config=config)
    

    responce =  result["messages"][-1].content
    
    print(result)

    return {"result": responce}