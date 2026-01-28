"""Researcher Agent - Gathers information using Tavily Search.

This agent takes a topic from the state, performs web research using
Tavily's search API, and synthesizes the findings into structured
research data for the writer agent.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import AgentState


def research_node(state: AgentState) -> dict:
    """Execute research phase using Tavily Search.
    
    Args:
        state: Current agent state containing the topic
        
    Returns:
        Updated state with research_data and status message
    """
    topic = state["topic"]
    
    # Initialize Tavily search tool
    tavily_tool = TavilySearchResults(
        max_results=5,
        include_answer=True,
        include_raw_content=False
    )
    
    # Initialize Gemini LLM for synthesis
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )
    
    # Perform search
    search_results = tavily_tool.invoke({"query": topic})
    
    # Format search results
    formatted_results = []
    for i, result in enumerate(search_results, 1):
        formatted_results.append(
            f"**Source {i}:** {result.get('url', 'N/A')}\n"
            f"**Content:** {result.get('content', 'No content available')}\n"
        )
    
    raw_research = "\n---\n".join(formatted_results)
    
    # Synthesize research into structured notes
    synthesis_prompt = [
        SystemMessage(content="""You are a research analyst. Synthesize the given search results 
into well-organized research notes that will help a writer create an engaging blog post.

Structure your output as:
1. **Key Facts & Statistics** - Important data points
2. **Main Themes** - Core concepts and ideas
3. **Expert Opinions** - Notable quotes or perspectives
4. **Recent Developments** - Latest news or updates
5. **Sources** - List the URLs for citation

Be thorough but concise. Focus on actionable insights for the writer."""),
        HumanMessage(content=f"Topic: {topic}\n\nSearch Results:\n{raw_research}")
    ]
    
    synthesis_response = llm.invoke(synthesis_prompt)
    research_data = synthesis_response.content
    
    return {
        "research_data": research_data,
        "messages": [f"🔍 **Researcher Agent**: Completed research on '{topic}'. Found {len(search_results)} sources and synthesized key insights."]
    }
