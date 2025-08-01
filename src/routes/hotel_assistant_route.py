from fastapi import FastAPI, APIRouter
from datetime import datetime
from fastapi.responses import JSONResponse
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai import  Crew, Process
import agentops
from config.config import settings
from Agent.lookup_hotels import booking_agent, boking_task
from Agent.HotelAssistant import Hotel_assistant_agent
from Agent.select_option_agent import Hotel_selector_room_booking_agent, Hotel_selector_room_booking_task


hotel_router = APIRouter(
    prefix="/api/v1",
    tags= ["api_v1"],
)

@hotel_router.post("/hotels")
async def hotel_assistant(query: str, convo_id, user_id):

    about_company = "Vialink is a company that provides AI solutions to help Travels booking hotel, flighet."

    company_context = StringKnowledgeSource(
        content=about_company
    )

    

    agentops.init(
    api_key=settings.agentops_api_key,
    skip_auto_end_session=True,
    default_tags=['crewai']
    )
  
    rankyx_crew = Crew(
    agents=[
        booking_agent,  
    ],
    tasks=[
        boking_task,
        ],
    process=Process.sequential,
    planning=True,
    knowledge_sources=[company_context],
    
)
    crew_results = await rankyx_crew.kickoff_async(
    inputs={
        "user_id": user_id,
        "convo_id": convo_id,
        "today_date": datetime.now().strftime("%Y-%m-%d"),
        "input": query
    })

    result = crew_results.to_dict()

    return JSONResponse(
            content={
                "signal": "success",
                "result": result if result else "No results found",
            }
        )