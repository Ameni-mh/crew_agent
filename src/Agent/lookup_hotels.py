import json
from crewai import Agent, Task,  LLM
from config.config import settings
import os
from Tool.redis_tool import save_hotel_search_options
from schema.hotel_search_request_schema import HotelSearchRequest
from Tool.tool import detect_language_tool, search_hotels_from_GDSAgregator_async, validate_field_tool
from schema.room_search_playload import RoomSearchPayload
basic_llm = LLM(model="gpt-4o", temperature=0, api_key=settings.openai_api_key)
output_dir = "./ai-agent-output"
os.makedirs(output_dir, exist_ok=True)




Lookup_hotel_agent = Agent(
    role="Lookup Hotels",
    goal="\n".join([
        "You are a multilingual AI travel assistant designed to lookup structured hotel to user and recommend hotels based on user preferences.",
        "If some required fields are missing, the agent politely asks the user for the missing details.",
        "Respond with the detected language.",
    ]),
    backstory="This agent specializes in parsing hotel search requests from users for hotel lookup.",
    llm=basic_llm,
    verbose=True,
    tools=[detect_language_tool, 
           validate_field_tool, 
           search_hotels_from_GDSAgregator_async, 
           save_hotel_search_options],
    reasoning=True,
    max_reasoning_attempts=2
    #max_execution_time=60
     
    
)


Lookup_hotel_task = Task(
    description="\n".join([
    "Today is {today_date}", 
    "Conversation ID: {convo_id}",
    "You are a professional multilingual AI travel assistant specialized in hotel bookings.",
    "Core Responsibilities:",
    "1. Extract and validate hotel search requirements from user messages",
    "2. Generate and validate a JSON object following the Pydantic HotelSearchRequest schema:",
    json.dumps(HotelSearchRequest.model_json_schema(), indent=2, ensure_ascii=False),
    "",
    "Process Flow:",
    "1. Parse user input and extract search criteria",
    "2. Generate JSON matching HotelSearchRequest schema (use defaults for missing non-required fields)",
    "3. Validate extracted data using `validate_field_tool`",
    "4. If validation fails:",
    "   - Politely request missing or invalid information from user",
    "   - Maintain context of previously valid fields",
    "5. If validation succeeds:",
    "   - 1  Execute search using `search_hotels_from_GDSAgregator` asynchronously with await keyword",
    "   - 2  Create room_search_payload (a RoomSearchPayload Pydantic model) from the extracted input",
    "        JSON Schema Reference: ",
    json.dumps(RoomSearchPayload.model_json_schema(), indent=2, ensure_ascii=False),
    "   - 3  Save hotel search options using `save_hotel_search_options` tool.",
    "       → Tool input **must** be a JSON object with **three separate fields**:",
    "       → Example Input Format:",
    "       {",
    "         \"convo_id\": \"445\",",
    "         \"offers\": [...],", 
    "         \"room_search_payload\": {\"checkin\": \"2025-08-01\", \"checkout\": \"2025-08-03\", ...}",
    "       }",
    "   - 4  Analyze results and recommend best matches",           
    "6. Handle language preferences:", 
    "   - Use `detect_language_tool` when specific language is requested",
    "   - Respond in detected language",
    "7. If no results found:",
    "   - Politely inform user and suggest refining search criteria",
    "9. If the user asks something outside of this scope, try to provide a helpful and accurate response.",
    "",
    "Begin!",
    "Question: {input}",
    "Answer:"
]),
    expected_output="A natural, friendly message that includes hotel search results, requests for more information, or an error message.",
    output_file=os.path.join(output_dir, "step_1_suggested_Extraction_data.json"),
    agent=Lookup_hotel_agent,
)




