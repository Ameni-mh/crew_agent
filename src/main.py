from fastapi import FastAPI
from routes.hotel_assistant_route import hotel_router
from langgraph.checkpoint.redis import AsyncRedisSaver
from langgraph.prebuilt import create_react_agent
from config.config import settings
from Agent.lookup_hotels import model, State, prompt, tools, summarization_node
app = FastAPI()

async def startup_span():
    async with AsyncRedisSaver.from_conn_string(settings.redis_url) as checkpointer:
        #checkpointer.setup()
        app.agent =  create_react_agent(
            model=model,
            tools=tools,
            prompt=prompt,
            verbose=True,
            checkpointer=checkpointer,
            pre_model_hook= summarization_node,
            state_schema=State
            )      

async def shutdown_span():
    pass


app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(hotel_router)