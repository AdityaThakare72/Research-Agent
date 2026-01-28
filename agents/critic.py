"""Critic Agent - Evaluates blog post quality and provides feedback.

This agent reviews the draft content for accuracy, clarity, engagement,
and overall quality. It determines whether the post is ready for
publication or needs revision.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import json

from graph.state import AgentState


def critic_node(state: AgentState) -> dict:
    """Execute critique phase to evaluate blog post quality.
    
    Args:
        state: Current agent state with draft_content
        
    Returns:
        Updated state with critique_feedback, quality_status, and revision_count
    """
    topic = state["topic"]
    draft_content = state["draft_content"]
    research_data = state["research_data"]
    revision_count = state.get("revision_count", 0)
    
    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.2  # Lower temperature for analytical tasks
    )
    
    # Critique prompt
    critique_prompt = [
        SystemMessage(content="""You are a senior editor at a major publication. Your job is to 
critically evaluate blog posts for quality, accuracy, and reader engagement.

Evaluate the blog post on these criteria (score 1-10 each):
1. **Accuracy** - Facts align with research, no misinformation
2. **Clarity** - Writing is clear, well-organized, easy to follow
3. **Engagement** - Hooks readers, maintains interest, compelling narrative
4. **Completeness** - Covers topic adequately, nothing crucial missing
5. **SEO & Structure** - Good title, headings, scannable format

Provide your response in this exact JSON format:
{
    "scores": {
        "accuracy": <1-10>,
        "clarity": <1-10>,
        "engagement": <1-10>,
        "completeness": <1-10>,
        "structure": <1-10>
    },
    "average_score": <calculated average>,
    "decision": "Acceptable" or "Revision Needed",
    "strengths": ["list of what works well"],
    "improvements": ["specific actionable improvements needed"],
    "summary": "Brief overall assessment"
}

Rules:
- If average_score >= 7.5, decision should be "Acceptable"
- If average_score < 7.5, decision should be "Revision Needed"
- Be constructive but rigorous in your assessment"""),
        HumanMessage(content=f"""Topic: {topic}

Original Research:
{research_data}

Blog Post Draft:
{draft_content}

Please provide your critique.""")
    ]
    
    # Get critique
    response = llm.invoke(critique_prompt)
    critique_text = response.content
    
    # Parse the JSON response
    try:
        # Extract JSON from response (handle markdown code blocks)
        json_str = critique_text
        if "```json" in critique_text:
            json_str = critique_text.split("```json")[1].split("```")[0]
        elif "```" in critique_text:
            json_str = critique_text.split("```")[1].split("```")[0]
        
        critique_data = json.loads(json_str.strip())
        quality_status = critique_data.get("decision", "Revision Needed")
        average_score = critique_data.get("average_score", 0)
        
        # Format feedback for writer
        improvements = critique_data.get("improvements", [])
        strengths = critique_data.get("strengths", [])
        
        feedback = f"""**Quality Score: {average_score}/10**

**Strengths:**
{chr(10).join(f'- {s}' for s in strengths)}

**Areas for Improvement:**
{chr(10).join(f'- {i}' for i in improvements)}

**Summary:** {critique_data.get('summary', 'N/A')}"""
        
    except (json.JSONDecodeError, IndexError, KeyError):
        # Fallback if JSON parsing fails
        quality_status = "Acceptable" if revision_count >= 2 else "Revision Needed"
        average_score = 7.0 if quality_status == "Acceptable" else 6.0
        feedback = critique_text
    
    # Increment revision count
    new_revision_count = revision_count + 1
    
    # Force acceptance after max revisions
    if new_revision_count >= 3 and quality_status == "Revision Needed":
        quality_status = "Acceptable"
        feedback += "\n\n⚠️ *Max revisions reached. Accepting current draft.*"
    
    # Status message
    status_emoji = "✅" if quality_status == "Acceptable" else "🔄"
    status_msg = (
        f"{status_emoji} **Critic Agent**: Score {average_score}/10 - {quality_status}. "
        f"{'Draft approved for publication!' if quality_status == 'Acceptable' else 'Sending back for revision...'}"
    )
    
    return {
        "critique_feedback": feedback,
        "quality_status": quality_status,
        "revision_count": new_revision_count,
        "messages": [status_msg]
    }
