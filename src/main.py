from fastapi import FastAPI, APIRouter
from datetime import datetime
from fastapi.responses import JSONResponse
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai import  Crew, Process
import agentops
from config.config import settings
from Agent.lookup_hotels import search_queries_recommendation_agent, Extract_filed_task
from Tool.tool import detect_language_tool, search_hotels_from_GDSAgregator, validate_field_tool
from Agent.select_option_agent import Hotel_selector_room_booking_agent, Hotel_selector_room_booking_task
from Tool.redis_tool import change_option_status_hotel_offer, get_all_rooms_from_key, get_room_search_payload_from_key, get_selected_rooms_from_key, is_selected_option_from_key, save_hotelDetails_room_options
import asyncio

app = FastAPI()

base_router = APIRouter(
    prefix="/api/v1",
    tags= ["api_v1"],
)

@base_router.post("/lookup_hotels")
async def lookup_hotels(query: str):

    about_company = "Vialink is a company that provides AI solutions to help Travels booking hotel, flighet."

    company_context = StringKnowledgeSource(
        content=about_company
    )

    tools_list = [
        detect_language_tool,
        validate_field_tool,
        search_hotels_from_GDSAgregator
    ]
    tool_names = [tool.name for tool in tools_list]
    tools = [tool.description  for tool in tools_list]

    agentops.init(
    api_key=settings.agentops_api_key,
    skip_auto_end_session=True,
    default_tags=['crewai']
    )
  
    rankyx_crew = Crew(
    agents=[
        search_queries_recommendation_agent
    ],
    tasks=[
        Extract_filed_task,
        ],
    process=Process.sequential,
    knowledge_sources=[company_context]
)
    crew_results = rankyx_crew.kickoff(
    inputs={
        "today_date": datetime.now().strftime("%Y-%m-%d"),
        "tool_names": tool_names,
        "input": query ,

    })

    result = crew_results.to_dict()

    return JSONResponse(
            content={
                "signal": "success",
                "result": result if result else "No results found",
            }
        )


@base_router.post("/hotel_selector")
async def hotel_selector(query: str, convo_id, user_id):
    try:

        about_company = "Vialink is a company that provides AI solutions to help Travels booking hotel, flighet."

        company_context = StringKnowledgeSource(
            content=about_company
        )

        tools_list = [
            get_all_rooms_from_key, #
            detect_language_tool, #
            save_hotelDetails_room_options, 
            change_option_status_hotel_offer, 
            is_selected_option_from_key, #
            get_room_search_payload_from_key, 
            get_selected_rooms_from_key]
        tool_names = [tool.name for tool in tools_list]
        

        agentops.init(
        api_key=settings.agentops_api_key,
        skip_auto_end_session=True,
        default_tags=['crewai']
        )
    
        rankyx_crew = Crew(
        agents=[
            Hotel_selector_room_booking_agent 
        ],
        tasks=[
            Hotel_selector_room_booking_task,
            ],
        process=Process.sequential,
        knowledge_sources=[company_context]
    )
        
        
        
        crew_results = await rankyx_crew.kickoff_async(
            inputs={
                "user_id": user_id,
                "convo_id": convo_id,
                "tool_names": tool_names,
                "input": query ,

            })

        result = crew_results.to_dict()

        
        return JSONResponse(
            content={
                "signal": "success",
                "result": result if result else "No results found",
                    }
                )
        
        
    except Exception as e:
        return JSONResponse(
            content={
                "signal": "error",
                "message": str(e)
            },
            status_code=500
        )



app.include_router(base_router)