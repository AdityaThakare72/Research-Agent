"""LangGraph Workflow - State machine orchestrating the research agents.

This module implements the cyclic workflow:
Research -> Writer -> Critic -> (Revision Loop or END)

The conditional edge from Critic determines whether to loop back
for revision or proceed to completion.
"""

from langgraph.graph import StateGraph, END, START

from graph.state import AgentState
from agents.researcher import research_node
from agents.writer import writer_node
from agents.critic import critic_node


def route_critique(state: AgentState) -> str:
    """Conditional routing function for the critique node.
    
    Determines whether to loop back to writer for revision
    or proceed to END for final output.
    
    Args:
        state: Current agent state with quality_status
        
    Returns:
        "writer" to continue revision, "end" to complete
    """
    quality_status = state.get("quality_status", "Revision Needed")
    
    if quality_status == "Acceptable":
        return "end"
    else:
        return "writer"


def create_workflow() -> StateGraph:
    """Create and compile the LangGraph workflow.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize the state graph with our state schema
    workflow = StateGraph(AgentState)
    
    # Add nodes - each node is an agent function
    workflow.add_node("researcher", research_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("critic", critic_node)
    
    # Add edges - define the flow between nodes
    # START -> researcher: Begin with research
    workflow.add_edge(START, "researcher")
    
    # researcher -> writer: Pass research to writer
    workflow.add_edge("researcher", "writer")
    
    # writer -> critic: Submit draft for review
    workflow.add_edge("writer", "critic")
    
    # critic -> (writer OR end): Conditional routing
    # If quality is acceptable, end; otherwise, loop back to writer
    workflow.add_conditional_edges(
        "critic",
        route_critique,
        {
            "writer": "writer",  # Loop back for revision
            "end": END           # Complete the workflow
        }
    )
    
    # Compile and return the graph
    return workflow.compile()


def run_workflow(topic: str):
    """Execute the workflow for a given topic.
    
    Args:
        topic: The research topic to process
        
    Yields:
        State updates as the workflow progresses
    """
    # Create the compiled workflow
    app = create_workflow()
    
    # Initialize the starting state
    initial_state = {
        "topic": topic,
        "research_data": "",
        "draft_content": "",
        "critique_feedback": "",
        "revision_count": 0,
        "quality_status": "",
        "messages": []
    }
    
    # Stream the execution
    for output in app.stream(initial_state):
        yield output


# For testing
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    test_topic = "The Future of Renewable Energy"
    print(f"Running workflow for topic: {test_topic}\n")
    
    for step in run_workflow(test_topic):
        for node_name, state_update in step.items():
            print(f"[{node_name}] completed")
            if "messages" in state_update:
                for msg in state_update["messages"]:
                    print(f"  {msg}")
        print()
