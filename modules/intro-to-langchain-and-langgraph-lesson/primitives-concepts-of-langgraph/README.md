<h1>
  <span>
  
  ![](/assets/ga-logo.png)

  </span>
  <span class="subhead">Primitives & Concepts of LangGraph</span>
</h1>

**Learning objective:** Explain the core primitives of LangGraph and analyze how they compose into and production-ready workflows.

## The Core Primitives

### 1. Node

A **node** is a unit of work — often a Python function, but in LangGraph it can be *any callable* (sync, async, or even another subgraph).

Key characteristics:

- Takes in the current state as input
- Performs some operation (LLM call, database query, validation check, etc.)
- Returns an updated state dictionary
- Should be focused on a single responsibility

Examples in a financial context:

- **Evidence Agent Node**: Runs a control check against financial data
- **Reviewer Agent Node**: Validates evidence for completeness and accuracy
- **Retrieval Node**: Fetches relevant documents from a vector database
- **Decision Node**: Makes a final determination based on accumulated evidence

**Code example (simplified):**

```python
def evidence_agent_node(state: AgentState) -> AgentState:
    """Node that generates audit evidence"""
    control_id = state["control_id"]

    # Call LLM to generate evidence
    evidence = llm.invoke(f"Generate evidence for control {control_id}")

    # Update state with results
    return {
        **state,
        "evidence": evidence,
        "timestamp": datetime.now()
    }

```

---

### 2. Edge

An **edge** is a connection between nodes that determines the flow of execution through your graph.

Types of edges:

- **Unconditional edges**
    
    Always flow to the next specified node.
    
    Example: Evidence collection always goes to validation.
    
- **Conditional edges**
    
    Include routing logic that decides the next path based on the state.
    
    Example: If validation fails → error handler; if passes → continue.
    

**Code example (using `StateGraph`):**

```python
graph = StateGraph(AuditState)

# Unconditional edge
graph.add_edge("evidence_node", "validation_node")

# Conditional edge with routing function
def route_validation(state: AgentState) -> str:
    if state["validation_passed"]:
        return "approval_node"
    else:
        return "error_handler_node"

graph.add_conditional_edges(
    "validation_node",
    route_validation,
    {
        "approval_node": "approval_node",
        "error_handler_node": "error_handler_node"
    }
)

```

---

### 3. State

The **state** is a dictionary-like object that persists across the entire graph execution — it’s the *memory* of your workflow.

Key characteristics:

- Contains all relevant data as execution progresses
- Often typed with `TypedDict` or `Pydantic` to enforce schema and catch errors early
- Makes runs auditable, debuggable, and reproducible
- Can include metadata like timestamps, user context, and execution history

Why strong typing matters in production:

- Prevents runtime errors from unexpected data shapes
- Makes code self-documenting
- Enables better IDE support and auto-completion
- Critical for compliance environments where data integrity is paramount

**Example state definition:**

```python
from typing import TypedDict, List, Optional

class AuditState(TypedDict):
    control_id: str
    evidence: Optional[str]
    validation_status: str
    reviewer_notes: List[str]
    timestamp: str
    confidence_score: float
    requires_human_review: bool

```

---

### 4. Graph

The **graph** is the directed graph structure that connects all nodes and edges — it defines the overall workflow of your agent system.

Think of it as:

- The “blueprint” or orchestration layer for your agents
- A state machine that explicitly defines all possible execution paths
- A visual representation of your business logic

Key capabilities:

- Can handle parallel execution of multiple nodes
- Supports cyclic flows (nodes can loop back for retries)
- Enables sub-graphs for modular design
- Supports persistence and checkpointing **via a checkpointer integration** (not automatic)

---

### 5. Start / End

LangGraph requires you to define where the graph begins and ends. These aren’t literal nodes, but designated entry/finish points in the `StateGraph`.

- **Start (Entry Point):**
    
    Where execution begins — often where you initialize state with input parameters.
    
- **End (Finish Point):**
    
    Where execution terminates — returns final state to the caller.
    

Example:

```python
graph.set_entry_point("start_node")
graph.set_finish_point("end_node")

```

---

## Why Graphs Instead of Chains?

| Benefit            | Why It Matters                                                                              | Example in Practice                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| **Transparency**   | See every step of execution with explicit state transitions                                 | Replay and inspect exactly how evidence was generated for Control 123 — critical during audits   |
| **Control**        | Add guards, retries, fallbacks, and alternate execution paths                               | Route failed JSON parsing → error handler node with retry logic                                  |
| **Auditability**   | Replay historical runs, inspect state at each node, generate execution traces               | Prove to auditors that controls executed correctly                                               |
| **Scalability**    | Branching logic, parallel execution, multi-agent orchestration                              | Evidence Agent → Reviewer Agent → Decision Agent, with parallel lookups to multiple data sources |
| **Error Handling** | Explicit failure modes and recovery strategies (not automatic, but modeled in graph design) | If LLM returns invalid format → retry with stricter prompt → escalate to human                   |
| **Testability**    | Each node can be unit tested in isolation                                                   | Test evidence generation separately from validation logic                                        |

💡 **LangChain** was about chaining steps sequentially; **LangGraph** is about managing complex systems with explicit control flow.

---

## Example Flow: Audit Control Verification

**Diagram-in-Text:**

```
      ┌─────────────┐
      │    START    │
      └──────┬──────┘
             │
             ▼
      ┌─────────────┐
      │  Classify   │
      │  Control    │
      └──────┬──────┘
             │
             ▼
      ┌─────────────┐
      │   Router    │
      │ (decides    │
      │  pathway)   │
      └──┬─────┬────┘
         │     │
 ┌───────┘     └───────┐
 ▼                     ▼
┌─────────────┐   ┌─────────────┐
│ Exec Node   │   │ Audit Node  │
│ (automated) │   │ (detailed)  │
└──────┬──────┘   └──────┬──────┘
       │                 │
       └───────┬─────────┘
               │
               ▼
        ┌─────────────┐
        │     END     │
        └─────────────┘

```

How it works:

- State flows through nodes, accumulating information
- Router decides which branch to take (e.g., high-risk → detailed audit path)
- Each node updates state (evidence, validation results, timestamps)
- Final state contains a complete audit trail


## Comparison: LangChain vs LangGraph

| Feature            | LangChain                         | LangGraph                                             |
| ------------------ | --------------------------------- | ----------------------------------------------------- |
| **Primary model**  | Chains (linear, sequential flows) | Graphs (nodes + edges + state)                        |
| **State handling** | Implicit, passed ad-hoc           | Explicit, typed, persisted via `TypedDict`/`Pydantic` |
| **Routing**        | Limited branching                 | Conditional edges with routing functions              |
| **Error handling** | Try/except in steps               | Explicit error nodes & retry patterns                 |
| **Debugging**      | Logging or LangSmith tracing      | State inspection and execution trace built in         |
| **Visualization**  | Text diagrams / optional tools    | Directed graph visualization (Mermaid export)         |
| **Best use case**  | Prototypes, demos                 | Production systems, compliance workflows              |
| **Learning curve** | Gentler                           | Steeper, but pays off for complex systems             |


## Interactive Prompt (2–3m Discussion)

👉 If you were designing a financial control system with multiple agents (evidence gathering, review, approval), which primitive (Node, Edge, State, Graph) do you think is most important to get right from day one? Why?

Suggested prompts:

- What happens if your State schema changes mid-project?
- How would poor Edge design impact your audit trail?
- Can you recover from errors if Node boundaries aren’t clear?

💡 **Facilitator note:** Highlight that **State** is usually most critical for auditability — it’s your permanent record of what happened and why.



## Key Takeaway

LangGraph isn’t just “LangChain v2” — it’s a fundamentally different abstraction: a **state machine for LLM-powered agents**.

Once you grasp **nodes, edges, and state**, you can model almost any agent system:

- Simple: A chatbot with conversation memory
- Moderate: A customer support agent with escalation paths
- Complex: An auditable compliance workflow with multiple specialized agents

<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

💡 **The power isn’t in the primitives themselves** — it’s in how they compose to create transparent, controllable, and auditable AI systems.

</aside>