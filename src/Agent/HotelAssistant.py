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
        "Delegate tasks such as hotel searching, room selection, and booking to the appropriate agents.",
        "Ensure the user receives the most accurate and timely hotel booking assistance."
    ]),
    backstory="You are a multilingual AI assistant specializing in travel. You coordinate a team of sub-agents that handle hotel search, selection, and booking tasks.",
    llm=basic_llm,
    verbose=True,
    allow_delegation=True,
    reasoning=True,
    max_reasoning_attempts=2
    #tools=[hotel_selector_agent, hotel_lookup_agent, room_booking_agent]
)

