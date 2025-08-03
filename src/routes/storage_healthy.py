from fastapi import FastAPI, APIRouter, HTTPException
from datetime import datetime
from fastapi.responses import JSONResponse
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai import Crew, Process
import agentops
from config.config import settings
from Agent.lookup_hotels import booking_agent, boking_task
from crewai.memory import LongTermMemory, ShortTermMemory
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from crewai.utilities.paths import db_storage_path
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.utilities.errors import DatabaseOperationError
import chromadb
import os
import sqlite3
from pathlib import Path
import tempfile

# Ensure storage directory exists with proper permissions
custom_storage_path = "./storage"
storage_path = Path(custom_storage_path)
storage_path.mkdir(parents=True, exist_ok=True)

# Set proper permissions for the storage directory
try:
    storage_path.chmod(0o755)
except Exception as e:
    print(f"Warning: Could not set directory permissions: {e}")

health_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)

def ensure_database_writable(db_path: str):
    """Ensure the database file is writable"""
    db_file = Path(db_path)
    
    # If database exists, check if it's writable
    if db_file.exists():
        try:
            # Test write access
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE IF NOT EXISTS test_write (id INTEGER)")
            conn.execute("DROP TABLE IF EXISTS test_write")
            conn.close()
            return True
        except sqlite3.OperationalError as e:
            if "readonly database" in str(e).lower():
                print(f"Database {db_path} is readonly, attempting to fix...")
                try:
                    # Try to change file permissions
                    db_file.chmod(0o666)
                    # Test again
                    conn = sqlite3.connect(db_path)
                    conn.execute("CREATE TABLE IF NOT EXISTS test_write (id INTEGER)")
                    conn.execute("DROP TABLE IF EXISTS test_write")
                    conn.close()
                    print(f"Successfully fixed permissions for {db_path}")
                    return True
                except Exception as fix_error:
                    print(f"Could not fix database permissions: {fix_error}")
                    # Delete the problematic database file
                    try:
                        db_file.unlink()
                        print(f"Deleted problematic database: {db_path}")
                        return True
                    except Exception as del_error:
                        print(f"Could not delete database: {del_error}")
                        return False
            else:
                raise e
    return True





# Optional: Add a health check endpoint
@health_router.get("/health")
async def health_check():
    """Check if storage is properly configured"""
    try:
        storage_check = {
            "storage_directory_exists": os.path.exists(custom_storage_path),
            "storage_writable": os.access(custom_storage_path, os.W_OK),
        }
        
        # Test database creation
        test_db_path = f"{custom_storage_path}/test.db"
        try:
            conn = sqlite3.connect(test_db_path)
            conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER)")
            conn.close()
            os.remove(test_db_path)
            storage_check["database_writable"] = True
        except Exception as e:
            storage_check["database_writable"] = False
            storage_check["database_error"] = str(e)
        
        return {"status": "healthy", "storage": storage_check}
    
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}