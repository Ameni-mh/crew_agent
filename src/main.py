from fastapi import FastAPI
from routes.hotel_assistant_route import hotel_router
from langgraph.checkpoint.redis import AsyncRedisSaver
from langgraph.prebuilt import create_react_agent
from config.config import settings
from Agent.lookup_hotels import  model, prompt,  summarization_node
from langgraph.store.redis.aio import AsyncRedisStore
from contextlib import asynccontextmanager
from schema.agent_context import AgentContext
from langchain_mcp_adapters.client import MultiServerMCPClient
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = MultiServerMCPClient(
    {
        "hotels": {
            "command": "python",
            "args": ["mcp_server.py"],
            "transport": "stdio",
        },
        
    }
)
    tools_mcp = await client.get_tools()

    os.environ["REDIS_URL"] = settings.redis_url
    async with (
        AsyncRedisSaver.from_conn_string(settings.redis_url) as checkpointer,
        AsyncRedisStore.from_conn_string(settings.redis_url) as store):
        await checkpointer.asetup()
        await store.setup()
        app.store = store
        app.agent =  create_react_agent(
            model=model,
            tools=tools_mcp,
            verbose=False,
            checkpointer=checkpointer,
            store=store,
            pre_model_hook= summarization_node,
            state_schema=AgentContext,
            prompt=prompt,
            )    
    yield  

app = FastAPI(lifespan=lifespan)


app.include_router(hotel_router)