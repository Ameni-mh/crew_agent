import uuid
from fastapi import  APIRouter, Request
from datetime import datetime
from langgraph.store.base import BaseStore
from langgraph.prebuilt.chat_agent_executor import AgentState




hotel_router = APIRouter(
    prefix="/api/v1",
    tags= ["api_v1"],
)


@hotel_router.post("/hotels")
async def hotel_assistant(request:Request ,query: str, accound_id:str, con_id: str):
    
    config = {"configurable": {"thread_id":con_id, 
                               "date": datetime.now().strftime("%d-%m-%Y")}}
    
    

    input={
        "role" : "user",
        "content" : query,
    }
    
    result = await  request.app.agent.ainvoke({"messages":[input],"account_id": accound_id,
                                               "conversation_id": con_id},
                                               config=config)
    

    responce =  result["messages"][-1].content
    
    print(result)

    return {"result": responce}