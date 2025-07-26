import json
from typing import List
from config.config import settings
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.agents import tool
from langchain_core.prompts import BasePromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain import hub
from langchain_core.tools import BaseTool
from schema.hotel_details_request_schema import HotelSearchRequest
from langchain.memory import ConversationBufferMemory
from Tool.tool import detect_language_tool, search_hotels_from_GDSAgregator, validate_field_tool

basic_llm = ChatOpenAI(model="gpt-4o", temperature=0.0, api_key=settings.openai_api_key)
# First, fix the tools list initialization
tools_list: List[BaseTool] = [
    detect_language_tool,
    validate_field_tool,
    search_hotels_from_GDSAgregator
]
tool_names = [tool.name for tool in tools_list]
tools = [tool.description  for tool in tools_list]


base_prompt = "\n".join([
    "To day is {today_date}", 
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
    "Thought:{agent_scratchpad}"
])




prompt = PromptTemplate(template=base_prompt,
                        input_variables=["input", "today_date"],
                        partial_variables={"tool_names": ", ".join(tool_names)})

lookup_hotels_agent = create_react_agent(llm = basic_llm, tools=tools_list, prompt=prompt)



agent_executor = AgentExecutor(
        agent=lookup_hotels_agent,
        tools=[tool],
        verbose=True,
        handle_parsing_errors=True,
        max_iterations = 5, 
        )






