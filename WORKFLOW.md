# 🔄 LangGraph Workflow Documentation

deployment is on port 8503




This document explains exactly how the LangGraph nodes and edges interact in the Agentic Research System.

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [State Schema](#state-schema)
3. [Node Definitions](#node-definitions)
4. [Edge Configuration](#edge-configuration)
5. [Conditional Routing](#conditional-routing)
6. [Execution Flow](#execution-flow)

---

## Core Concepts

### What is LangGraph?

LangGraph is a library for building **stateful, multi-agent workflows** as graphs. Key components:

| Concept | Description |
|---------|-------------|
| **StateGraph** | The main graph class that defines the workflow |
| **Nodes** | Functions that process and modify state |
| **Edges** | Connections that define flow between nodes |
| **Conditional Edges** | Dynamic routing based on state values |
| **State** | TypedDict that persists across all nodes |

### Why LangGraph for This Project?

```
Traditional Chain:  A → B → C → END (linear, no loops)

LangGraph:          A → B → C ─┬→ END (supports cycles!)
                         ↑    │
                         └────┘
```

Our critic-revision loop **requires cycles**, which LangGraph handles natively.

---

## State Schema

```python
# graph/state.py

class AgentState(TypedDict):
    topic: str                              # User's research topic
    research_data: str                      # Synthesized research notes
    draft_content: str                      # Current blog post draft
    critique_feedback: str                  # Critic's assessment
    revision_count: int                     # Loop counter (max 3)
    quality_status: str                     # "Acceptable" or "Revision Needed"
    messages: Annotated[list[str], add]     # Agent logs (accumulates)
```

### Why `Annotated[list[str], add]`?

The `add` operator tells LangGraph to **accumulate** messages across nodes instead of replacing them. Each agent can append to the message log.

---

## Node Definitions

### 1. Researcher Node

```python
workflow.add_node("researcher", research_node)
```

**Input State:**
- `topic` - The user's query

**Operations:**
1. Query Tavily Search API (5 results)
2. Format raw search results
3. Use Gemini to synthesize into structured notes

**Output State Updates:**
- `research_data` - Structured research notes
- `messages` - Log entry

---

### 2. Writer Node

```python
workflow.add_node("writer", writer_node)
```

**Input State:**
- `topic` - Context
- `research_data` - Source material
- `critique_feedback` - For revisions (empty on first pass)
- `revision_count` - Determines initial vs revision mode

**Operations:**
- If `revision_count == 0`: Create initial draft
- If `revision_count > 0`: Revise based on feedback

**Output State Updates:**
- `draft_content` - New or revised blog post
- `messages` - Log entry

---

### 3. Critic Node

```python
workflow.add_node("critic", critic_node)
```

**Input State:**
- `draft_content` - The blog post to evaluate
- `research_data` - For fact-checking

**Operations:**
1. Evaluate on 5 criteria (1-10 each)
2. Calculate average score
3. Determine if acceptable (≥7.5) or needs revision

**Output State Updates:**
- `critique_feedback` - Detailed feedback
- `quality_status` - "Acceptable" or "Revision Needed"
- `revision_count` - Incremented by 1
- `messages` - Log entry

---

## Edge Configuration

### Static Edges

```python
# Entry point
workflow.add_edge(START, "researcher")

# Linear flow
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", "critic")
```

```
START ──▶ researcher ──▶ writer ──▶ critic
```

### Conditional Edge

```python
workflow.add_conditional_edges(
    "critic",                    # Source node
    route_critique,              # Routing function
    {
        "writer": "writer",      # If returns "writer" → go to writer
        "end": END               # If returns "end" → terminate
    }
)
```

---

## Conditional Routing

### The Routing Function

```python
def route_critique(state: AgentState) -> str:
    quality_status = state.get("quality_status", "Revision Needed")
    
    if quality_status == "Acceptable":
        return "end"    # → END node
    else:
        return "writer" # → Writer node for revision
```

### Decision Logic

```
                    ┌──────────────────┐
                    │   Critic Node    │
                    │                  │
                    │  Score < 7.5?    │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              │              ▼
       ┌──────────┐          │       ┌──────────┐
       │  "writer"│          │       │   "end"  │
       │          │          │       │          │
       └────┬─────┘          │       └────┬─────┘
            │                │            │
            ▼                │            ▼
     ┌──────────┐            │      ┌──────────┐
     │  Writer  │            │      │   END    │
     │  Node    │◀───────────┘      │          │
     └──────────┘                   └──────────┘
```

### Revision Limit

The critic node enforces a maximum of 3 revisions:

```python
if new_revision_count >= 3 and quality_status == "Revision Needed":
    quality_status = "Acceptable"  # Force exit after 3 attempts
```

---

## Execution Flow

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌───────┐    ┌────────────┐    ┌────────┐    ┌────────┐      │
│  │ START │───▶│ Researcher │───▶│ Writer │───▶│ Critic │      │
│  └───────┘    └────────────┘    └────────┘    └───┬────┘      │
│                                       ▲           │            │
│                                       │           │            │
│                                       │    ┌──────▼──────┐     │
│                                       │    │ route_crit- │     │
│                                       │    │   ique()    │     │
│                                       │    └──────┬──────┘     │
│                                       │           │            │
│                              ┌────────┴───┐ ┌─────▼─────┐      │
│                              │  "writer"  │ │   "end"   │      │
│                              └────────────┘ └─────┬─────┘      │
│                                                   │            │
│                                                   ▼            │
│                                              ┌────────┐        │
│                                              │  END   │        │
│                                              └────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Example Execution Trace

```
Step 1: START → researcher
        State: {topic: "AI in Healthcare", ...}
        
Step 2: researcher → writer
        State: {research_data: "Key findings...", ...}
        
Step 3: writer → critic
        State: {draft_content: "# Blog Post...", revision_count: 0}
        
Step 4: critic → route_critique() → "writer" (score: 6.5)
        State: {quality_status: "Revision Needed", revision_count: 1}
        
Step 5: writer → critic
        State: {draft_content: "# Improved Blog...", revision_count: 1}
        
Step 6: critic → route_critique() → "end" (score: 8.2)
        State: {quality_status: "Acceptable", revision_count: 2}
        
Step 7: END
        Final output: polished blog post
```

---

## Interview Talking Points

1. **Why LangGraph over LangChain chains?**
   - Supports cycles (revision loops)
   - Explicit state management
   - Visual graph representation
   - Better debugging and observability

2. **How does state persistence work?**
   - TypedDict flows through all nodes
   - Each node receives full state
   - Nodes return partial updates (merged automatically)
   - `Annotated` with `add` for list accumulation

3. **How do you prevent infinite loops?**
   - `revision_count` tracks iterations
   - Force exit after 3 revisions
   - Critic scoring threshold (≥7.5 = acceptable)

4. **How would you extend this?**
   - Add parallel research nodes
   - Include human-in-the-loop approval
   - Add fact-checking node
   - Implement caching for API calls
