"""Streamlit UI for the Agentic Research System.

A chat-like interface that displays the agent's thought process
as it researches, writes, critiques, and refines blog posts.
"""

import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Agentic Research System",
    page_icon="🔬",
    layout="wide"
)

# Custom CSS for better aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .agent-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .researcher-msg {
        background-color: #e8f4f8;
        border-left-color: #0ea5e9;
    }
    .writer-msg {
        background-color: #f0fdf4;
        border-left-color: #22c55e;
    }
    .critic-msg {
        background-color: #fef3c7;
        border-left-color: #f59e0b;
    }
    .stSpinner > div {
        text-align: center;
    }
    .final-output {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🔬 Agentic Research System</h1>', unsafe_allow_html=True)
st.markdown("""
<p style="text-align: center; color: #6b7280; font-size: 1.1rem;">
    Multi-agent AI system that researches, writes, and refines blog posts
</p>
""", unsafe_allow_html=True)

st.divider()

# Check for API keys
if not os.getenv("GOOGLE_API_KEY") or not os.getenv("TAVILY_API_KEY"):
    st.warning("Please set your API keys in the `.env` file:")
    st.code("""
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
    """)
    st.stop()

# Input section
col1, col2 = st.columns([4, 1])
with col1:
    topic = st.text_input(
        "Enter your research topic:",
        placeholder="e.g., The Future of Quantum Computing",
        label_visibility="visible"
    )
with col2:
    st.write("")  # Spacer
    st.write("")  # Spacer
    start_button = st.button("🚀 Start Research", type="primary", use_container_width=True)

# Initialize session state
if "workflow_complete" not in st.session_state:
    st.session_state.workflow_complete = False
if "final_draft" not in st.session_state:
    st.session_state.final_draft = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# Run workflow
if start_button and topic:
    # Reset state
    st.session_state.workflow_complete = False
    st.session_state.final_draft = ""
    st.session_state.messages = []
    
    # Import workflow
    from graph.workflow import create_workflow
    
    # Create containers for real-time updates
    progress_container = st.container()
    
    with progress_container:
        st.subheader("🤖 Agent Activity")
        
        # Create the workflow
        app = create_workflow()
        
        # Initial state
        initial_state = {
            "topic": topic,
            "research_data": "",
            "draft_content": "",
            "critique_feedback": "",
            "revision_count": 0,
            "quality_status": "",
            "messages": []
        }
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        messages_container = st.container()
        
        # Run the workflow
        step_count = 0
        final_state = {}
        
        try:
            for output in app.stream(initial_state):
                step_count += 1
                
                for node_name, state_update in output.items():
                    # Update progress
                    progress = min(step_count * 20, 95)  # Cap at 95% until complete
                    progress_bar.progress(progress)
                    status_text.text(f"Currently running: {node_name.title()} Agent...")
                    
                    # Display messages
                    if "messages" in state_update:
                        for msg in state_update["messages"]:
                            with messages_container:
                                # Determine message type for styling
                                if "Researcher" in msg:
                                    st.info(msg)
                                elif "Writer" in msg:
                                    st.success(msg)
                                elif "Critic" in msg:
                                    if "✅" in msg:
                                        st.success(msg)
                                    else:
                                        st.warning(msg)
                    
                    # Store state updates
                    final_state.update(state_update)
            
            # Complete
            progress_bar.progress(100)
            status_text.text("Workflow complete!")
            st.session_state.workflow_complete = True
            st.session_state.final_draft = final_state.get("draft_content", "")
            
        except Exception as e:
            st.error(f"Error during execution: {str(e)}")
            st.exception(e)

# Display final output
if st.session_state.workflow_complete and st.session_state.final_draft:
    st.divider()
    st.subheader("📝 Final Blog Post")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📖 Rendered", "📋 Markdown"])
    
    with tab1:
        st.markdown(st.session_state.final_draft)
    
    with tab2:
        st.code(st.session_state.final_draft, language="markdown")
    
    # Download button
    st.download_button(
        label="📥 Download Blog Post",
        data=st.session_state.final_draft,
        file_name=f"blog_post_{topic.replace(' ', '_').lower()[:30]}.md",
        mime="text/markdown"
    )

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This system uses **three AI agents** working together:
    
    1. **🔍 Researcher** - Searches the web using Tavily
    2. **✍️ Writer** - Drafts engaging blog posts
    3. **🎯 Critic** - Evaluates and requests improvements
    
    The workflow loops until the critic approves the draft
    (or max 3 revisions are reached).
    """)
    
    st.divider()
    
    st.header("🔧 Tech Stack")
    st.markdown("""
    - **LangGraph** - Agent orchestration
    - **LangChain** - LLM integration
    - **Gemini** - Language model
    - **Tavily** - Web search
    - **Streamlit** - UI
    """)
    
    st.divider()
    
    st.header("📊 Workflow")
    st.markdown("""
    ```
    Research → Write → Critique
                  ↑        ↓
                  ← Revise ←
                       ↓
                     [END]
    ```
    """)
