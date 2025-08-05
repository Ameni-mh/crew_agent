from config.config import settings
import os
from Tool.redis_tool import change_option_status_hotel_offer, get_all_rooms_from_key, get_room_search_payload_from_key, get_selected_rooms_from_key,  save_hotel_search_options, save_hotelDetails_room_options, selected_option_from_key
from Tool.gds_hotel_service import Search_Details_Specific_Hotel, Search_Hotels_From_GDS, send_shortlink_request_hotelBooking
from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langmem.short_term import SummarizationNode, RunningSummary
from langchain_core.messages.utils import count_tokens_approximately


class State(AgentState):
    # NOTE: we're adding this key to keep track of previous summary information
    # to make sure we're not summarizing on every LLM call
    context: dict[str, RunningSummary]

model = ChatOpenAI(model="gpt-4o", temperature=0.0, api_key=settings.openai_api_key)

def prompt(state: AgentState, config: RunnableConfig) -> list[AnyMessage]: 

    date = config["configurable"].get("date")

    system_msg = "\n".join([
       "You are an advanced customer support assistant for Vialink, designed to provide comprehensive and accurate assistance to users.",
       "Your role is to help users with their queries related to  bookings, company policies, and other relevant services.",
       "You have access to various tools and databases to search for information, and you should utilize them effectively.",
       "",
       "When conducting searches:",
       "- Be thorough and persistent. If initial searches yield no results, broaden your search parameters.",
       "- Prioritize finding relevant, up-to-date information.",
       "- Only conclude a search after exhausting all available options.",
       "",
        "Provide responses that are clear, concise, and directly address the user's needs.",
        "When you are uncertain, it's better to inform the user that you're unable to find the specific information rather than provide incorrect details.",
        "IMPORTANT:",
        "- Do not accept any past dates.",
        "- Current date: {date}",
        "- For some tools, you will need the conversation ID: {thread_id} and user ID: {user_id}",
        "user messages: {messages}",
        "",
        "Your Response:"
])
    print("=========================")
    print("state message : ", state["messages"])
    print("==================================")
    return [{"role": "system", "content": system_msg}] + state["messages"]

tools = [Search_Hotels_From_GDS, Search_Details_Specific_Hotel, send_shortlink_request_hotelBooking ]



checkpointer = InMemorySaver()

summarization_node = SummarizationNode( 
    token_counter=count_tokens_approximately,
    model=model,
    max_tokens=384,
    max_summary_tokens=128,
    output_messages_key="llm_input_messages",
)

agent = create_react_agent(
    model=model,
    tools=tools,
    prompt=prompt,
    verbose=True,
    checkpointer=checkpointer,
    pre_model_hook= summarization_node,
    state_schema=State
    )











            
    

