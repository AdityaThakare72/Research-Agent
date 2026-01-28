"""Writer Agent - Drafts blog posts from research data.

This agent takes research data from the state and creates an engaging
blog post. On revision cycles, it incorporates critique feedback to
improve the draft.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import AgentState


def writer_node(state: AgentState) -> dict:
    """Execute writing phase to create or revise blog post.
    
    Args:
        state: Current agent state with research_data and optional feedback
        
    Returns:
        Updated state with draft_content and status message
    """
    topic = state["topic"]
    research_data = state["research_data"]
    critique_feedback = state.get("critique_feedback", "")
    revision_count = state.get("revision_count", 0)
    
    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.7  # Higher creativity for writing
    )
    
    # Determine if this is initial draft or revision
    if revision_count == 0 or not critique_feedback:
        # Initial draft
        writing_prompt = [
            SystemMessage(content="""You are an expert blog writer known for creating engaging, 
informative, and well-structured content. Write a compelling blog post based on the research provided.

Your blog post should:
1. Have a catchy, SEO-friendly title
2. Start with a hook that grabs attention
3. Use clear subheadings to organize content
4. Include relevant facts and statistics from the research
5. Maintain a conversational yet authoritative tone
6. End with a thought-provoking conclusion or call-to-action
7. Be approximately 800-1200 words

Format the output in Markdown."""),
            HumanMessage(content=f"Topic: {topic}\n\nResearch Notes:\n{research_data}")
        ]
        action = "Created initial draft"
    else:
        # Revision based on feedback
        current_draft = state.get("draft_content", "")
        writing_prompt = [
            SystemMessage(content="""You are an expert blog writer revising your work based on 
editorial feedback. Carefully address each point of criticism while maintaining the 
overall quality and flow of the article.

Preserve what works well, fix what needs improvement, and ensure the revised version
is polished and ready for publication."""),
            HumanMessage(content=f"""Topic: {topic}

Current Draft:
{current_draft}

Critique Feedback:
{critique_feedback}

Please revise the blog post to address this feedback.""")
        ]
        action = f"Revised draft (attempt {revision_count + 1})"
    
    # Generate content
    response = llm.invoke(writing_prompt)
    draft_content = response.content
    
    return {
        "draft_content": draft_content,
        "messages": [f"✍️ **Writer Agent**: {action} for '{topic}'."]
    }
