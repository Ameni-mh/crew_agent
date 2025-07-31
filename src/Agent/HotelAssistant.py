from crewai import Agent, Task,  LLM
from config.config import settings
import os

basic_llm = LLM(model="gpt-4o", temperature=0, api_key=settings.openai_api_key)
output_dir = "./ai-agent-output"
os.makedirs(output_dir, exist_ok=True)

Hotel_assistant_agent = Agent(
    role="Hotel Task Manager",
    goal="\n".join([
        "Oversee all hotel-related user queries.",
        "Delegate tasks such as `Lookup_hotel_task` and `Hotel_selector_room_booking_task` according to the user's message.",
        "Ensure the user receives the most accurate and timely response to their hotel booking needs."
    ]),
    backstory=(
        "You are a multilingual AI assistant specializing in travel. "
        "You coordinate a team of sub-agents that handle hotel search, selection, and booking tasks. "
        "You are efficient, responsive, and goal-driven."
    ),    
    llm=basic_llm,
    verbose=True,
    allow_delegation=True,
    reasoning=True,
    max_execution_time=60,   
)

