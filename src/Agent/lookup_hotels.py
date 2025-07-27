import json
from crewai import Agent, Task,  LLM
from config.config import settings
import os
from src.Tool.redis_tool import save_hotel_search_options
from src.schema.hotel_search_request_schema import HotelSearchRequest
from Tool.tool import detect_language_tool, search_hotels_from_GDSAgregator, validate_field_tool
basic_llm = LLM(model="gpt-4o", temperature=0, api_key=settings.openai_api_key)
output_dir = "./ai-agent-output"
os.makedirs(output_dir, exist_ok=True)




search_queries_recommendation_agent = Agent(
    role="Lookup Hotels",
    goal="\n".join([
        "You are a multilingual AI travel assistant designed to lookup structured hotel to user and recommend hotels based on user preferences.",
        "If some required fields are missing, the agent politely asks the user for the missing details.",
        "Respond with the detected language.",
    ]),
    backstory="This agent specializes in parsing hotel search requests from users for hotel lookup.",
    llm=basic_llm,
    verbose=True,
    tools=[detect_language_tool, validate_field_tool, search_hotels_from_GDSAgregator, save_hotel_search_options],
    
)


Extract_filed_task = Task(
    description="\n".join([
    "Today is {today_date}", 
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
    "   - Execute search using `search_hotels_from_GDSAgregator`",
    "   - Analyze results and recommend best matches",
    "   - Save search options using `save_hotel_search_options`",
    "6. Handle language preferences:",
    "   - Use `detect_language_tool` when specific language is requested",
    "   - Respond in detected language",
    "",
    "Response Format:",
    "Question: the input question you must answer",
    "Thought: you should always think about what to do",
    "Action: the action to take, should be one of [{tool_names}]",
    "Action Input: the input to the action",
    "Observation: the result of the action",
    "... (this Thought/Action/Action Input/Observation can repeat N times)",
    "Thought: I now know the final answer",
    "Final Answer: the final answer to the original input question"
    "",
    "Begin!",
    "Question: {input}",
    "Thought:"
]),
    expected_output="A natural, friendly language message ",
    output_file=os.path.join(output_dir, "step_1_suggested_Extraction_data.json"),
    agent=search_queries_recommendation_agent
)




