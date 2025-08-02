import json
from crewai import Agent, Task,  LLM
from config.config import settings
import os
from Tool.redis_tool import change_option_status_hotel_offer, get_all_rooms_from_key, get_room_search_payload_from_key, get_selected_rooms_from_key,  save_hotel_search_options, save_hotelDetails_room_options, selected_option_from_key
from Tool.searchHotelToolGDS import SearchHotelsFromGDS
from Tool.DetailHotel_tool import SearchDetailsSpecificHotel
basic_llm = LLM(model="gpt-4o", temperature=0, api_key=settings.openai_api_key)

output_dir = "./ai-agent-output"
os.makedirs(output_dir, exist_ok=True)



booking_agent = Agent(
    role="Hotel Booking Specialist",
    goal="\n".join([
        "You are a multilingual AI travel assistant specialized in hotel booking.",
        "Help users search, compare, and book hotels efficiently.",
        "Always respond in the user's detected language.",
        "Provide clear, actionable recommendations based on user preferences."
    ]),
    backstory="\n".join([
        "You are an experienced travel consultant with deep knowledge of global hospitality.",
        "You excel at understanding customer needs and matching them with perfect accommodations.",
        "You have access to comprehensive hotel databases and booking systems."
    ]),
    llm=basic_llm,
    verbose=True,
    tools=[ 
             
            SearchHotelsFromGDS(),
            SearchDetailsSpecificHotel(),
            get_all_rooms_from_key, #
            
            change_option_status_hotel_offer, 
            selected_option_from_key, #
            get_room_search_payload_from_key, 
            get_selected_rooms_from_key,
            
           ],
    reasoning=True,
    max_reasoning_attempts=2,
    memory= True
    #max_execution_time=60
     
    
)


boking_task = Task(
    description="\n".join([
    "=== CONTEXT ===",
    "Today's date: {today_date}",
    "Conversation ID: {convo_id}",
    "User ID: {user_id}",
    "",
    "=== YOUR MISSION ===",
    "Help users with their hotel booking journey from search to confirmation.",
    "Be proactive, friendly, and efficient in your assistance.",
    "",
    "=== RESPONSE GUIDELINES ===",
    "- Always be helpful and encouraging",
    "- Provide specific, actionable information",
    "- Ask clarifying questions when needed",
    "- Use appropriate tools based on user's current step in booking process",
    "- Handle errors gracefully with alternative suggestions",
    "",
    "=== USER INPUT ===",
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




