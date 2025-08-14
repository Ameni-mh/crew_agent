import uuid
from fastapi import  APIRouter, Request
from datetime import datetime
from langgraph.store.base import BaseStore
from langgraph.prebuilt.chat_agent_executor import AgentState

from schema.vialink_webhook_request_schema import VialinkWebhookPayload




hotel_router = APIRouter(
    prefix="/api/v1",
    tags= ["api_v1"],
)


@hotel_router.post("/hotels")
async def hotel_assistant(request:Request , payload: VialinkWebhookPayload):
    accound_id = payload.account.id
    con_id = payload.conversation.id
    message = payload.content
    
    config = {"configurable": {"thread_id":con_id,
                               "account_id": accound_id,
                               "date": datetime.now().strftime("%d-%m-%Y")}}
    
    

    input={
        "role" : "user",
        "content" : message,
    }
    
    result = await  request.app.agent.ainvoke({"messages":[input]}, config=config)
    

    responce =  result["messages"][-1].content
    
    print(result)

    return {"result": responce}