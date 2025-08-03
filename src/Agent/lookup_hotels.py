import json
from crewai import Agent, Crew, Process, Task,  LLM
from config.config import settings
import os
from Tool.redis_tool import change_option_status_hotel_offer, get_all_rooms_from_key, get_room_search_payload_from_key, get_selected_rooms_from_key,  save_hotel_search_options, save_hotelDetails_room_options, selected_option_from_key
from Tool.searchHotelToolGDS import SearchHotelsFromGDS
from Tool.DetailHotel_tool import SearchDetailsSpecificHotel
from Tool.gds_hotel_service import send_shortlink_request_hotelBooking
from pathlib import Path
from crewai.memory import LongTermMemory, ShortTermMemory
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai.memory.storage.rag_storage import RAGStorage


os.environ["OPENAI_API_KEY"] = settings.openai_api_key

output_dir = "./ai-agent-output"
os.makedirs(output_dir, exist_ok=True)

# Ensure storage directory exists with proper permissions
custom_storage_path = "./storage"
os.makedirs(custom_storage_path, exist_ok=True)

basic_llm = LLM(model="gpt-4o", temperature=0, api_key=settings.openai_api_key)

booking_agent = Agent(
    role="Hotel Booking Specialist",
    goal="\n".join([
        "Your role is to help users with their queries related to Hotel bookings",
        "You have access to various tools and databases to search for information, and you should utilize them effectively.",
    ]),
    backstory="\n".join([
        "You are an advanced customer support assistant for Vialink, designed to provide comprehensive and accurate assistance to users.",
    ]),
    llm=basic_llm,
    verbose=True,
    tools=[ 
             
            SearchHotelsFromGDS(),
            SearchDetailsSpecificHotel(),
            send_shortlink_request_hotelBooking,            
           ],
    reasoning=True,
    max_reasoning_attempts=2,
    memory= True, 
    max_execution_time=30   
)


boking_task = Task(
    description="\n".join([
    "When conducting searches:",
    "- Be thorough and persistent. If initial searches yield no results, broaden your search parameters.",
    "- Prioritize finding relevant, up-to-date information.",
    "- Only conclude a search after exhausting all available options.",
    "",
    "If a query is unclear or lacks sufficient information, ask the user for clarification.",
    "Provide responses that are clear, concise, and directly address the user's needs.",
    "When you are uncertain, it's better to inform the user that you're unable to find the specific information rather than provide incorrect details",
    "",
    "Current time:",
    "{today_date}",
    "Question: {input}",
    "",
    "Your Response:"
    ]),
    expected_output="\n".join([
        "A comprehensive, user-friendly response that:",
        "- Addresses the user's hotel booking needs",
        "- Provides relevant hotel options or booking assistance", 
        "- Includes clear next steps or calls-to-action",
        "- Maintains a helpful, professional tone",
        "- Uses the user's preferred language"
    ]),
    output_file=os.path.join(output_dir, "step_1_suggested_Extraction_data.json"),
    agent=booking_agent,
)


def create_crew():
    """Create crew with fallback options if memory fails"""
    
    about_company = "Vialink is a company that provides AI solutions to help Travels booking hotel, flighet."
    company_context = StringKnowledgeSource(content=about_company)
    
    try:
            # Ensure database is writable
            ltm_db_path = f"{custom_storage_path}/memory.db"
            stm_path = f"{custom_storage_path}/short_memory"
            
            #ensure_database_writable(ltm_db_path)
            
            crew = Crew(
                agents=[booking_agent],
                tasks=[boking_task],
                process=Process.sequential,
                planning=True,
                memory=True,
                knowledge_sources=[company_context],
            )
            return crew
            
    except Exception as memory_error:
            print(f"Failed to create crew with memory: {memory_error}")
            print("Falling back to crew without persistent memory...")
    
    crew = Crew(
                agents=[booking_agent],
                tasks=[boking_task],
                process=Process.sequential,
                planning=True,
                memory=False,
                knowledge_sources=[company_context],
            )
    return crew

            
    

