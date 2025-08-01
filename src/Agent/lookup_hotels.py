import json
from crewai import Agent, Task,  LLM
from config.config import settings
import os
from Tool.redis_tool import change_option_status_hotel_offer, get_all_rooms_from_key, get_room_search_payload_from_key, get_selected_rooms_from_key, is_selected_option_from_key, save_hotel_search_options, save_hotelDetails_room_options
from schema.hotel_search_request_schema import HotelSearchRequest
from Tool.tool import detect_language_tool, search_hotels_from_GDSAgregator_async, validate_field_tool
from schema.room_search_playload import RoomSearchPayload
from schema.hotel_details_request_schema import HotelDetailsRequest
basic_llm = LLM(model="gpt-4o", temperature=0, api_key=settings.openai_api_key)
output_dir = "./ai-agent-output"
os.makedirs(output_dir, exist_ok=True)




booking_agent = Agent(
    role="Lookup Hotels",
    goal="\n".join([
        "You are a multilingual AI travel assistant designed to hotel booking",
        "Respond with the detected language.",
    ]),
    backstory="This agent specializes in booking hotel  requests.",
    llm=basic_llm,
    verbose=True,
    tools=[ 
            validate_field_tool, 
            search_hotels_from_GDSAgregator_async, 
            save_hotel_search_options,
            get_all_rooms_from_key, #
            detect_language_tool, #
            save_hotelDetails_room_options, 
            change_option_status_hotel_offer, 
            is_selected_option_from_key, #
            get_room_search_payload_from_key, 
            get_selected_rooms_from_key
           ],
    max_reasoning_attempts=2
    #max_execution_time=60
     
    
)


boking_task = Task(
    description="\n".join([
    "Today is {today_date}", 
    "Conversation ID: {convo_id}",
    "User ID: {user_id}",
    "There is a schema for hotel search request that can you need to follow.",
    json.dumps(HotelSearchRequest.model_json_schema(), indent=2, ensure_ascii=False),
    "There is a schema for room Search payload that can you need to follow.",
    json.dumps(RoomSearchPayload.model_json_schema(), indent=2, ensure_ascii=False),
    "There is a schema for hotel Details that can you need to follow.",
    json.dumps(HotelDetailsRequest.model_json_schema(), indent=2, ensure_ascii=False),

    "Help the user search for, select, and book hotels based on tool ",
    "chouse the appropriate tool based on the user's input.",
    "Ensure responses are friendly, clear, and directly help the user move forward with their hotel booking.",
    
    "Begin!",
    "Question: {input}",
    "Answer:"
]),
    expected_output="A natural, friendly message that includes hotel search results, requests for more information, or an error message.",
    output_file=os.path.join(output_dir, "step_1_suggested_Extraction_data.json"),
    agent=booking_agent,
)




