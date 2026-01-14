from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import MessagesState

class AgentState(MessagesState):
    """
    State for the research assistant graph.
    Inherits from MessagesState to include 'messages' automatically.
    """
    query: str
    clarity_status: str  # "clear" or "needs_clarification"
    company_name: Optional[str]
    research_findings: Optional[Dict[str, Any]]
    confidence_score: float
    validation_result: str  # "sufficient" or "insufficient"
    attempts: int
    summary: Optional[str]
