from typing import Annotated, Optional
from langgraph.prebuilt.chat_agent_executor import AgentState
from langmem.short_term import  RunningSummary
from langgraph.types import Command
from langgraph.prebuilt import InjectedState


class AgentContext(AgentState):
    # NOTE: we're adding this key to keep track of previous summary information
    # to make sure we're not summarizing on every LLM call
    context: Optional[dict[str, RunningSummary]]
    hotels: Optional[str] 
    room_search_payload: Optional[dict] 

             
             
