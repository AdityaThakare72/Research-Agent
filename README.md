# 🔬 Agentic Research System

A production-ready multi-agent AI system built with **LangGraph** and **LangChain** that researches topics, drafts blog posts, and iteratively refines them through collaborative AI agents.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agentic Research System                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│    ┌──────────┐     ┌──────────┐     ┌──────────┐          │
│    │Researcher│────▶│  Writer  │────▶│  Critic  │          │
│    │  Agent   │     │  Agent   │     │  Agent   │          │
│    └──────────┘     └──────────┘     └──────────┘          │
│         │                ▲                │                 │
│         │                │   Revision     │                 │
│         │                └────────────────┤                 │
│         │                                 │                 │
│         │                          ┌──────▼─────┐          │
│         │                          │ Acceptable? │          │
│         │                          └──────┬─────┘          │
│         ▼                                 ▼                 │
│    ┌──────────┐                     ┌──────────┐          │
│    │  Tavily  │                     │   END    │          │
│    │  Search  │                     │  Output  │          │
│    └──────────┘                     └──────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd Agentic_Research
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Edit .env with your API keys:
# GOOGLE_API_KEY=your_google_api_key
# TAVILY_API_KEY=your_tavily_api_key
```

### 3. Run the Application

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## 📁 Project Structure

```
Agentic_Research/
├── agents/                 # AI Agent implementations
│   ├── __init__.py
│   ├── researcher.py      # Tavily search + synthesis
│   ├── writer.py          # Blog post drafting
│   └── critic.py          # Quality evaluation
├── graph/                  # LangGraph workflow
│   ├── __init__.py
│   ├── state.py           # TypedDict state schema
│   └── workflow.py        # StateGraph definition
├── app.py                  # Streamlit UI
├── requirements.txt        # Dependencies
├── Dockerfile             # Container deployment
├── WORKFLOW.md            # Technical workflow docs
└── README.md              # This file
```

## 🤖 The Agents

### 🔍 Researcher Agent
- Uses **Tavily Search API** to gather web information
- Synthesizes search results using **Gemini** into structured research notes
- Extracts key facts, themes, expert opinions, and sources

### ✍️ Writer Agent
- Drafts engaging blog posts from research data
- Handles revision cycles by incorporating critic feedback
- Uses **Gemini** with higher temperature for creative writing

### 🎯 Critic Agent
- Evaluates drafts on: Accuracy, Clarity, Engagement, Completeness, Structure
- Returns JSON-formatted scores and actionable feedback
- Triggers revision loop or approves for final output

## 🔄 Workflow

See [WORKFLOW.md](WORKFLOW.md) for detailed technical documentation on how LangGraph nodes and edges interact.

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t agentic-research .

# Run with environment variables
docker run -p 8501:8501 \
  -e GOOGLE_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  agentic-research
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Orchestration | LangGraph (StateGraph) |
| LLM | Google Gemini (gemini-2.5-flash) |
| Search | Tavily Search API |
| UI | Streamlit |
| LLM Framework | LangChain |

## 📝 License

MIT License - feel free to use this project for learning and production.
