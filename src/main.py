from fastapi import FastAPI, APIRouter
from datetime import datetime
from fastapi.responses import JSONResponse
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai import  Crew, Process
import agentops
from config.config import settings
from Agent.extarct_field import search_queries_recommendation_agent, Extract_filed_task, missing_filed_task
import json

app = FastAPI()

base_router = APIRouter(
    prefix="/api/v1",
    tags= ["api_v1"],
)

@base_router.post("/")
async def welcome(query: str):

    about_company = "Vialink is a company that provides AI solutions to help websites refine their search and recommendation systems."

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
        search_queries_recommendation_agent
    ],
    tasks=[
        Extract_filed_task,
        missing_filed_task


    ],
    process=Process.sequential,
    knowledge_sources=[company_context]
)
    crew_results = rankyx_crew.kickoff(
    inputs={
        "today": datetime.now().strftime("%Y-%m-%d"),
        "message": query ,

    })

    result = crew_results.to_dict()

    return JSONResponse(
            content={
                "signal": "success",
                "result": result if result else "No results found",
            }
        )



app.include_router(base_router)