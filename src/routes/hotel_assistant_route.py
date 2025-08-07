from typing import Annotated
import uuid
from fastapi import  APIRouter, Request
from datetime import datetime
from langgraph.store.base import BaseStore
from langgraph.graph import  MessagesState
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.prebuilt import InjectedState
from Agent.lookup_hotels import AgentContext



hotel_router = APIRouter(
    prefix="/api/v1",
    tags= ["api_v1"],
)



@hotel_router.post("/hotels")
async def hotel_assistant(request:Request ,query: str, user_id:str, con_id: str):
    store: BaseStore = request.app.store
    state: MessagesState
    agent_state : AgentContext
    agent_context: Annotated[AgentContext, InjectedState]
    config = {"configurable": {"thread_id":con_id, 
                               "date": datetime.now().strftime("%d-%m-%y"),
                               "user_id": user_id}}
    
    namespace = ("memories", user_id)
    #await store.aput(namespace, str(uuid.uuid4()), {"data":query})

    input={
        "role" : "user",
        "content" : query,
    }
    
    result = await  request.app.agent.ainvoke({"messages":[input]},config=config)
    #await store.aput(namespace, str(uuid.uuid4()), {"data":result["messages"][-1].content})


    #print( "agent state :",agent_context["current_state"])

    responce =  result["messages"][-1].content
    
    print(result)

    return {"result": responce}