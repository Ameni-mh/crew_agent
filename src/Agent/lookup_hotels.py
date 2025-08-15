from config.config import settings
from Tool.gds_hotel_service import Search_Details_Specific_Hotel, Search_Hotels_From_GDS, get_current_date, memory_gds_data, policy_cancellation_informations, send_shortlink_request_hotelBooking
from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage
from langgraph.prebuilt.chat_agent_executor import AgentState
from langmem.short_term import SummarizationNode
from langchain_core.messages.utils import count_tokens_approximately




model = ChatOpenAI(model="gpt-4o", temperature=0.0, api_key=settings.openai_api_key)

def prompt(state:AgentState) -> list[AnyMessage]: 

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
        "If a tool returns an error or exception:",
        "- Reformulate the response as a polite, user-friendly message.",
        "- Do not reveal technical details or internal errors.",
        "If unsure, say you cannot find the information rather than guessing.",
        "Your Response:"
])
    return [{"role": "system", "content": system_msg}] + state["messages"]

tools = [Search_Hotels_From_GDS,
        Search_Details_Specific_Hotel,
        send_shortlink_request_hotelBooking,
        memory_gds_data,
        get_current_date,
        policy_cancellation_informations
        ]



summarization_node = SummarizationNode( 
    token_counter=count_tokens_approximately,
    model=model,
    max_tokens=384,
    max_summary_tokens=128,
    output_messages_key="llm_input_messages",
)












            
    

