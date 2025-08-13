from config.config import settings
from Tool.redis_tool import  get_hotel_search_options, get_room_search_payload_from_key
from Tool.gds_hotel_service import Search_Details_Specific_Hotel, Search_Hotels_From_GDS, memory_gds_data, send_shortlink_request_hotelBooking
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import InjectedState
from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt.chat_agent_executor import AgentState
from typing import Annotated
from langmem.short_term import SummarizationNode
from langchain_core.messages.utils import count_tokens_approximately
from schema.agent_context import AgentContext



model = ChatOpenAI(model="gpt-4o", temperature=0.0, api_key=settings.openai_api_key)

def prompt(state:AgentState, config: RunnableConfig) -> list[AnyMessage]: 
    date = config["configurable"].get("date")
    thread_id = config["configurable"].get("thread_id")
    user_id = config["configurable"].get("user_id")

    system_msg = "\n".join([
        "You are Vialink’s advanced customer support assistant. Provide accurate, concise help on bookings, company policies, and related services.",
        "Use available tools and databases to search and retrieve information. Always prefer up-to-date, reliable sources.",
        "When searching:",
        "- Be thorough. If results are empty, broaden criteria.",
        "- Only finish searching after exhausting all options.",
        "- Response length must be ≤ 800 characters, including spaces.",
        "When GDS returns a list (hotels, rooms, flights, cars):",
        "- Present results clearly ",
        "- Ask user to choose one (eg. hotel, fligh, car) or several (eg hotel : room ptions)  for next step (booking, viewing details).",
        "If context is incomplete:",
        "- Retrieve full GDS or payload data from the appropriate memory tool (hotel memory, flight memory, etc.).",
        "If unsure, say you cannot find the information rather than guessing.",
        "IMPORTANT:",
        "- Do not accept past dates.",
        f"- Current date: {date}",
        f"- Some tools require conversation ID: {thread_id} and user ID: {user_id}",
        "Your Response:"
])
    print("=========================")
    print("state message : ", state)
    print("==================================")
    return [{"role": "system", "content": system_msg}] + state["messages"]

tools = [Search_Hotels_From_GDS,
        Search_Details_Specific_Hotel,
        send_shortlink_request_hotelBooking,
        memory_gds_data
        ]



summarization_node = SummarizationNode( 
    token_counter=count_tokens_approximately,
    model=model,
    max_tokens=384,
    max_summary_tokens=128,
    output_messages_key="llm_input_messages",
)












            
    

