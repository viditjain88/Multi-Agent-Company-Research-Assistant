from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage

from research_assistant.graph.state import AgentState
from research_assistant.agents.clarity import ClarityAgent
from research_assistant.agents.research import ResearchAgent
from research_assistant.agents.validator import ValidatorAgent
from research_assistant.agents.synthesis import SynthesisAgent
from research_assistant.utils.llm_factory import get_llm

def create_graph():
    llm = get_llm()
    
    # Initialize Agents
    clarity_agent = ClarityAgent(llm)
    research_agent = ResearchAgent(llm)
    validator_agent = ValidatorAgent(llm)
    synthesis_agent = SynthesisAgent(llm)

    # Initialize Graph
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("clarity_node", clarity_agent.run)
    workflow.add_node("research_node", research_agent.run)
    workflow.add_node("validator_node", validator_agent.run)
    workflow.add_node("synthesis_node", synthesis_agent.run)

    # Entry Point
    workflow.set_entry_point("clarity_node")

    # Conditional Edges

    def route_clarity(state: AgentState):
        if state["clarity_status"] == "clear":
            return "research_node"
        else:
            return END 

    def route_research(state: AgentState):
        # Research always goes to validator to check quality
        return "validator_node"

    def route_validator(state: AgentState):
        validation = state.get("validation_result", "insufficient")
        attempts = state.get("attempts", 0)
        
        # If sufficient or we've tried 3 times, go to synthesis
        if validation == "sufficient" or attempts >= 3:
            return "synthesis_node"
        else:
            # Loop back to research
            return "research_node"

    workflow.add_conditional_edges(
        "clarity_node",
        route_clarity,
        {
            "research_node": "research_node",
            END: END
        }
    )

    workflow.add_edge("research_node", "validator_node")
    
    workflow.add_conditional_edges(
        "validator_node",
        route_validator,
        {
            "synthesis_node": "synthesis_node",
            "research_node": "research_node"
        }
    )
    
    workflow.add_edge("synthesis_node", END)

    # Checkpointer
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
