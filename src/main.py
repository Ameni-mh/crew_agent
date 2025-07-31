from fastapi import FastAPI, APIRouter
from datetime import datetime
from fastapi.responses import JSONResponse
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai import  Crew, Process
import agentops
from config.config import settings
from Agent.lookup_hotels import Lookup_hotel_agent, Lookup_hotel_task
from Agent.select_option_agent import Hotel_selector_room_booking_agent, Hotel_selector_room_booking_task
from routes.hotel_assistant_route import hotel_router


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


    agentops.init(
    api_key=settings.agentops_api_key,
    skip_auto_end_session=True,
    default_tags=['crewai']
    )
  
    rankyx_crew = Crew(
    agents=[
        Lookup_hotel_agent
    ],
    tasks=[
        Lookup_hotel_task,
        ],
    process=Process.sequential,
    knowledge_sources=[company_context]
)
    crew_results = await rankyx_crew.kickoff_async(
    inputs={
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


@base_router.post("/hotel_selector")
async def hotel_selector(query: str, convo_id, user_id):
    try:

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
app.include_router(hotel_router)