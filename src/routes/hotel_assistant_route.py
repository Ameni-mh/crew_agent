from fastapi import FastAPI, APIRouter
from datetime import datetime
from fastapi.responses import JSONResponse
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai import  Crew, Process
from config.config import settings
from Agent.lookup_hotels import booking_agent, boking_task, create_crew
from crewai.memory import LongTermMemory, ShortTermMemory
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from crewai.utilities.paths import db_storage_path
from crewai.memory.storage.rag_storage import RAGStorage
import chromadb
import os
import fcntl

custom_storage_path = "./storage"
os.makedirs(custom_storage_path, exist_ok=True)
storage_path = db_storage_path()
os.environ["CREWAI_STORAGE_DIR"] = str(storage_path )

hotel_router = APIRouter(
    prefix="/api/v1",
    tags= ["api_v1"],
)

messages= []
@hotel_router.post("/hotels")
async def hotel_assistant(query: str):
    # Reset specific memory types

    print("CREWAI_STORAGE_DIR:", os.getenv("CREWAI_STORAGE_DIR"))
    print("Current working directory:", os.getcwd())
    print("Computed storage path:", db_storage_path())
    storage_path = db_storage_path()
    lock_file = os.path.join(storage_path, ".crewai.lock")

    with open(lock_file, 'w') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Your CrewAI code here

    
    print(f"Storage path: {storage_path}")
    print(f"Path exists: {os.path.exists(storage_path)}")
    print(f"Is writable: {os.access(storage_path, os.W_OK) if os.path.exists(storage_path) else 'Path does not exist'}")

    # Create with proper permissions
    if not os.path.exists(storage_path):
        os.makedirs(storage_path, mode=0o755, exist_ok=True)
        print(f"Created storage directory: {storage_path}")

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

    
  
    crew = create_crew()
    #crew.reset_memories(command_type='short')     # Short-term memory
    #crew.reset_memories(command_type='long')      # Long-term memory
    #crew.reset_memories(command_type='entity')    # Entity memory
    #crew.reset_memories(command_type='knowledge')
    
    message = {"Human" : query }
    messages.append(message)
    
    
    crew_results = await crew.kickoff_async(
    inputs={
        "today_date": datetime.now().strftime("%Y-%m-%d"),
        "input": query,
        
    })
    #"chat_history": messages

    result = crew_results

    return {"result": result}