from config.config import settings
import os
from Tool.redis_tool import change_option_status_hotel_offer, get_all_rooms_from_key, get_room_search_payload_from_key, get_selected_rooms_from_key,  save_hotel_search_options, save_hotelDetails_room_options, selected_option_from_key
from Tool.searchHotelToolGDS import SearchHotelsFromGDS
from Tool.DetailHotel_tool import SearchDetailsSpecificHotel
from Tool.gds_hotel_service import Search_Details_Specific_Hotel, Search_Hotels_From_GDS, send_shortlink_request_hotelBooking
from langchain_community.llms import OpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory

model = ChatOpenAI(model="gpt-4o", temperature=0.0, api_key=settings.openai_api_key)

agnent_prompt = "\n".join([
       "Your role is to help users with their queries related to Hotel bookings",
        "You have access to various tools and databases to search for information, and you should utilize them effectively.",
        "You are an advanced customer support assistant for Vialink, designed to provide comprehensive and accurate assistance to users.",
        "",
        "When conducting searches:",
        "- Be thorough and persistent. If initial searches yield no results, broaden your search parameters.",
        "- Prioritize finding relevant, up-to-date information.",
        "- Only conclude a search after exhausting all available options.",
        "",
        "If a query is unclear or lacks sufficient information, ask the user for clarification.",
        "Provide responses that are clear, concise, and directly address the user's needs.",
        "When you are uncertain, it's better to inform the user that you're unable to find the specific information rather than provide incorrect details",
        "",
        "Chat history:\n{chat_history}",
        "Current time:",
        "{today_date}",
        "Question: {input}",
        "Thought:{agent_scratchpad}",
        "",
        "Your Response:"
])

tools = [Search_Hotels_From_GDS, Search_Details_Specific_Hotel, send_shortlink_request_hotelBooking ]

prompt = PromptTemplate.from_template(agnent_prompt)

memory = ConversationBufferMemory(
    memory_key="chat_history",   # must match the {chat_history} slot
    return_messages=True         # so that memory returns full Message objects
)

agent = create_react_agent(llm=model, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=True)











            
    

