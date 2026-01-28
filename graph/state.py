"""State schema for the Agentic Research System.

Defines the TypedDict that flows through the LangGraph workflow,
carrying all data between the researcher, writer, and critic agents.
"""

from typing import TypedDict, Annotated
from operator import add


class AgentState(TypedDict):
    """State object that persists across all nodes in the graph.
    
    Attributes:
        topic: The user's research topic/query
        research_data: Synthesized research from Tavily search
        draft_content: Current blog post draft
        critique_feedback: Critic's assessment and suggestions
        revision_count: Number of revision iterations (max 3)
        quality_status: "Acceptable" or "Revision Needed"
        messages: Log of agent thoughts for UI display
    """
    topic: str
    research_data: str
    draft_content: str
    critique_feedback: str
    revision_count: int
    quality_status: str
    messages: Annotated[list[str], add]
