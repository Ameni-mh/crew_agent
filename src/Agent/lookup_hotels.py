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
    agent_context: Annotated[AgentContext, InjectedState]
    date = config["configurable"].get("date")
    thread_id = config["configurable"].get("thread_id")
    user_id = config["configurable"].get("user_id")
    context = ""
    #agent_context["current_state"]

    system_msg = "\n".join([
       "You are an advanced customer support assistant for Vialink, designed to provide comprehensive and accurate assistance to users.",
       "Your role is to help users with their queries related to  bookings, company policies, and other relevant services.",
       "You have access to various tools and databases to search for and retrieve information, and you should utilize them effectively.",
       "",
       "When conducting searches:",
       "- Be thorough and persistent. If initial searches yield no results, broaden your search parameters.",
       "- Prioritize finding relevant, up-to-date information.",
       "- Only conclude a search after exhausting all available options.",
       "",
       "When a list of items is returned from the GDS (e.g., hotels, hotel rooms, flights, cars),",
        "- Format the list in a clear, user-friendly way.",
        "- Prompt the user to select one option to proceed with the next step (e.g., booking, confirmation, or viewing details).",
        "",
        "If any important information appears to be missing due to summarized context or memory loss,",
        "- Use the `gds_data_from_memory` tool to retrieve the full GDS data.",
        "",
        "Provide responses that are clear, concise, and directly address the user's needs.",
        "If uncertain, inform the user that you're unable to find the specific information, rather than providing potentially incorrect details.",
        "",
        "CONTEXT",
        f"{context}",
        "IMPORTANT:",
        "- Do not accept any past dates.",
        f"- Current date: {date}",
        f"- For some tools, you will need the conversation ID: {thread_id} and user ID: {user_id}",
        "",
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












            
    

