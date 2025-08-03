from fastapi import FastAPI, APIRouter
from datetime import datetime
from fastapi.responses import JSONResponse
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai import  Crew, Process
import agentops
from config.config import settings
from Agent.lookup_hotels import booking_agent, boking_task
from crewai.memory import LongTermMemory, ShortTermMemory
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from crewai.utilities.paths import db_storage_path
from crewai.memory.storage.rag_storage import RAGStorage
import chromadb
import os 

custom_storage_path = "./storage"
os.makedirs(custom_storage_path, exist_ok=True)

hotel_router = APIRouter(
    prefix="/api/v1",
    tags= ["api_v1"],
)


@hotel_router.post("/hotels")
async def hotel_assistant(query: str, convo_id, user_id):
    # Connect to CrewAI's ChromaDB
    storage_path = db_storage_path()
    chroma_path = os.path.join(storage_path, "short_term")

    if os.path.exists(chroma_path):
        client = chromadb.PersistentClient(path=chroma_path)
        collections = client.list_collections()

        print("ChromaDB Collections:")
        for collection in collections:
            print(f"  - {collection.name}: {collection.count()} documents")
    else:
        print("No ChromaDB storage found")

    about_company = "Vialink is a company that provides AI solutions to help Travels booking hotel, flighet."

    company_context = StringKnowledgeSource(
        content=about_company
    )

    

    agentops.init(
    api_key=settings.agentops_api_key,
    skip_auto_end_session=True,
    default_tags=['crewai']
    )
  
    rankyx_crew = Crew(
    agents=[
        booking_agent,  
    ],
    tasks=[
        boking_task,
        ],
    process=Process.sequential,
    planning=True,
    memory=True,
    long_term_memory=LongTermMemory(
        storage=LTMSQLiteStorage(
            db_path=f"{custom_storage_path}/memory.db"
        )
    ),
    short_term_memory=ShortTermMemory(
        storage=RAGStorage(
            type="short_term",
            allow_reset=True,
        ),
        path=f"{custom_storage_path}/short_memory"
        ),
    
    knowledge_sources=[company_context],
    
)
    crew_results = await rankyx_crew.kickoff_async(
    inputs={
        "user_id": user_id,
        "convo_id": convo_id,
        "today_date": datetime.now().strftime("%Y-%m-%d"),
        "input": query
    })

    result = crew_results

    return {"result": result}