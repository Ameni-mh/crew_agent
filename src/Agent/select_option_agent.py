import json
from crewai import Agent, Task,  LLM
from config.config import settings
import os
from Tool.redis_tool import change_option_status_hotel_offer, get_all_rooms_from_key, get_room_search_payload_from_key, get_selected_rooms_from_key, is_selected_option_from_key, save_hotel_search_options, save_hotelDetails_room_options
from Tool.tool import detect_language_tool
from schema.hotel_details_request_schema import HotelDetailsRequest
basic_llm = LLM(model="gpt-4o", temperature=0, api_key=settings.openai_api_key)
output_dir = "./ai-agent-output"
os.makedirs(output_dir, exist_ok=True)


Hotel_selector_room_booking_agent = Agent(
    role="Hotel Selector and room booking",
    goal="\n".join([
        "You are a helpful and multilingual AI assistant specialized in hotel selection and room booking.",
        "Your job is to guide users through the process of selecting hotels and rooms, detecting their choices, and confirming their booking",
        "respond with the detected language.",
    ]),
    backstory="This agent specializes in Hotel Selector and room booking before look up Hotels based on user preferences and previously saved search options.",
    llm=basic_llm,
    verbose=True,
    tools=[
        get_all_rooms_from_key, #
        detect_language_tool, #
        save_hotelDetails_room_options, 
        change_option_status_hotel_offer, 
        is_selected_option_from_key, #
        get_room_search_payload_from_key, 
        get_selected_rooms_from_key],
    reasoning=False,
    max_execution_time=60
    
)


Hotel_selector_room_booking_task = Task(
    description="\n".join([
    "Core Responsibilities:",
    " Follow the logic below to interact with the user, detect their intentions, and respond with appropriate room and hotel booking information.",
    "",
    "Process Flow:",
    "- You need user id {user_id} and {convo_id} to interact with the hotel details and room options.",
    "- Analyze the user's input to detect if they are selecting a hotel option or a room option.",
    "",
    "- If the user selects a hotel option:",
    "   1. Change the status of the selected hotel option to 'selected' using `change_option_status_hotel_offer`.",
    "   2. Detect the selected hotel option using `is_selected_option_from_key` and extract the hotel ID.",
    "   3. Get the room_search_payload detail with `get_room_search_payload_from_key`."
    "   4. use the following pydantic model to get the hotel details and room options from Gds.",
    json.dumps(HotelDetailsRequest.model_json_schema(), indent=2, ensure_ascii=False),
    "   5 . Call `search_details_specific_hotel` to get the hotel details and room options.",
    "   6. Save the hotel details and room options using `save_hotelDetails_room_options`.",
    "   7. Return a summary of the available room options.",
    "",
    "- If the user want to selects a room option:",
    "   1. Extract this option and and number of selected "
    "   2. Mark this option selected using `mark_rooms_selected`",
    "   2. return a polite message to user.",
    "",
    "- If the user requests to see all available rooms for a selected hotel:",
    "   1. Retrieve all available rooms using `get_all_rooms_from_key`.",
    "   2. Return a summary of the available room options.",
    "",
    "- If the user requests to see their selected room options:",
    "    Retrieve the selected room options using `get_selected_rooms_from_key`.",
    "",
    "If the user want to confirm option selected : use `send_shortlink_request_hotelBooking`"
    
    "6. Handle language preferences:",
    "   - Use `detect_language_tool` for language detection from user input.",
    "   - Respond in detected language",
    "",
    "Begin!",
    "Question: {input}",
    "answer:"
]),
    expected_output="A natural, friendly language message ",
    output_file=os.path.join(output_dir, "hotel_selector_output.json"),
    agent=Hotel_selector_room_booking_agent, 
)