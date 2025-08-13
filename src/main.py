from fastapi import FastAPI
from routes.hotel_assistant_route import hotel_router
from langgraph.checkpoint.redis import AsyncRedisSaver
from langgraph.prebuilt import create_react_agent
from config.config import settings
from Agent.lookup_hotels import  model, prompt,  summarization_node
from langgraph.store.redis.aio import AsyncRedisStore
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from config.config import settings
from schema.agent_context import AgentContext
from langchain_mcp_adapters.client import MultiServerMCPClient
from routes.data import data_router
import os
from Agent.lookup_hotels import tools
from model.db_schemas.travel_base import SQLAlchemyBase

@asynccontextmanager
async def lifespan(app: FastAPI):

    postgres_conn = f"postgresql+asyncpg://{settings.postgres_username}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_main_database}"
    app.db_engine = create_async_engine(postgres_conn, echo=True)
    app.db_client = sessionmaker(
        app.db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with app.db_engine.begin() as conn:
        print("Creating database tables...")
        await conn.run_sync(SQLAlchemyBase.metadata.create_all)
        print("✅ Database tables created successfully!")

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
            tools=tools,
            verbose=False,
            checkpointer=checkpointer,
            store=store,
            pre_model_hook= summarization_node,
            state_schema=AgentContext,
            prompt=prompt,
            )    
    yield 
    app.db_engine.dispose() 

app = FastAPI(lifespan=lifespan)


app.include_router(hotel_router)
app.include_router(data_router)