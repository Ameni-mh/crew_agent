from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
import agentops

from pydantic import BaseModel, Field
from typing import List
from src.config.config import settings



import os
import json

from schema.hotel_details_request_schema import HotelSearchRequest

basic_llm = LLM(model="gpt-4o", temperature=0, api_key=settings.openai_api_key)
output_dir = "./ai-agent-output"
os.makedirs(output_dir, exist_ok=True)

search_queries_recommendation_agent = Agent(
    role="Field Extractor",
    goal="\n".join([
        "You are a multilingual AI travel assistant designed to extract structured hotel search information from a user's message.",
        "You can understand and process messages in multiple languages.",
        "If any required fields are missing, you detect them and respond appropriately."
    ]),
    backstory="This agent specializes in parsing hotel search requests from users, identifying key information such as city, travel dates, and preferences. If some required fields are missing, the agent politely asks the user for the missing details.",
    llm=basic_llm,
    verbose=True,
    
    
)


Extract_filed_task = Task(
    description="""
    TODAY is {today}.
    Extract structured hotel search data from the user's message.

    Rules:
    - All dates must be in DD-MM-YYYY format.
    - Convert nationality to its ISO 3166-1 alpha-2 country code (e.g., "TN" for Tunisia).
    - Convert language to its ISO 639-1 code (e.g., "en" for English, "fr" for French).
    - Convert currency to its ISO 4217 code (e.g., "USD" for US dollars, "EUR" for euros, "PHP" for Philippine pesos).
    - f the user says phrases like **"no children"**, **"no childs"**, **"without children"**, set `"childs": 0` in the output JSON.
    - If a required field is missing, do not guess or hallucinate values.
    - If 'childs' > 0, 'child_age' must be between 0 and 18 else 'child_age' = 0.
    - If more than one child age is provided, return only the highest age (e.g., for "children aged 10, 7, and 5", set "child_age": 10)
    - Only include fields in the output if they are provided or can be inferred with certainty.
    - Do not return empty or null values for fields that are not provided.

   

    Message: {message}
    """,
    expected_output="A JSON object containing a list of extracted information.",
    output_json=HotelSearchRequest,
    output_file=os.path.join(output_dir, "step_1_suggested_Extraction_data.json"),
    agent=search_queries_recommendation_agent
)

missing_filed_task = Task(
    description= """
      Your task is to verify whether the user's message contains all the required fields for initiating a hotel search.

      The required fields are:
      - City (destination)
      - Check-in date
      - Check-out date

      If any of these fields are missing or if the message contains invalid values (e.g., an unrecognized city). Ensure your reply:
      - Is conversational and polite.
      - Avoids repeating or confirming already provided details.
      - Uses the same language as the user's input (language is detected by a tool).
      - Is suitable for a multilingual travel assistant helping users with hotel bookings.

      Do not proceed with any hotel search or confirmation. Your only goal is to validate and collect all required fields.
      """,
    expected_output="A natural language message that politely asks the user to provide the missing fields.",
    output_file=os.path.join(output_dir, "step_1_task2_missing_filed.json"),
    agent=search_queries_recommendation_agent
)


