from typing import Annotated
from langgraph.prebuilt.chat_agent_executor import AgentState
from langmem.short_term import  RunningSummary
from langgraph.types import Command
from langgraph.prebuilt import InjectedState


class AgentContext(AgentState):
    # NOTE: we're adding this key to keep track of previous summary information
    # to make sure we're not summarizing on every LLM call
    context: dict[str, RunningSummary]
    current_state : str = "Focus on hotel search parameters, preferences, and results."

             
             
def update_agent_context(context:str) -> Command:
    agent_context: Annotated[AgentContext, InjectedState]
    return Command(update={agent_context["current_state"]: context})