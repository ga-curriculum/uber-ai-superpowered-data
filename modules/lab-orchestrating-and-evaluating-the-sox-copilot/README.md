<h1>
  <span class="prefix">

  ![](/assets/ga-logo.png)

  </span> 
  <span class="headline">Upgrading to LangGraph</span>
</h1>

## About

Learners will connect Evidence + Reviewer Agents into a single orchestrated workflow and evaluate as a system. 

**Key takeaway:** Evaluation is about testing the system as a whole, not just its parts.


## Module Objectives
- Define system-level evaluation criteria for a multi-agent system, covering accuracy, compliance, and efficiency.
- Design an evaluation plan to test a multi-agent system's performance against its business requirements.
- Analyze a system's output to trace errors or inefficiencies back to a specific agent or the handoff between them.

  
# Upgrading to LangGraph

## Background

In Part 3, you evolve the **SOX Audit Copilot** into a **typed, auditable pipeline** using LangGraph. Instead of relying on an LLM to orchestrate steps implicitly, you define an explicit graph with nodes, edges, typed state, and validation gates. This increases determinism, traceability, and ease of debugging.

The pipeline covers the full lifecycle:

1. Get policy context
2. Run deterministic checks to compute facts
3. Generate the audit narrative
4. Validate the evidence payload (schema-gated)
5. Independently recount and compare
6. Generate reviewer notes
7. Validate the review payload (schema-gated)

---

## Prerequisites

**Required Knowledge:**
- Completion of Part 1 (Evidence Agent) and Part 2 (Reviewer Agent)
- Understanding of state machines and directed graphs
- Familiarity with Pydantic for data validation
- Basic knowledge of typed Python (TypedDict or dataclasses)

**Environment Setup:**
Same as Parts 1 & 2, plus:
```bash
# Ensure langgraph is installed
pipenv install langgraph
```

**Key Concepts to Understand:**
- **Nodes**: Individual functions that transform state
- **Edges**: Connections that define execution order
- **State**: Typed dictionary that flows through the graph
- **Conditional Routing**: Decision points based on state values
- **Pydantic Models**: Schema validation for structured data

**Why LangGraph?**
- **Deterministic Flow**: Developer defines execution order, not LLM
- **Type Safety**: Pydantic ensures data contracts between nodes
- **Auditability**: Clear state transformations at each step
- **Debuggability**: Inspect state at any node
- **Conditional Logic**: Route based on validation results (e.g., early exit on errors)

---

## What Does the LangGraph Pipeline Do?

The pipeline acts like an end-to-end auditor workflow where each step is a graph node:

1. Fetch the policy summary for the control
2. Run the PAY-002 deterministic check against the CSV
3. Produce a concise narrative from the policy and facts
4. Assemble and validate a strongly-typed Evidence payload
5. Recount and compare to validate evidence deterministically
6. Produce concise review notes for workpapers
7. Assemble and validate a strongly-typed Review payload

The graph controls tool invocation order, enforces contracts via Pydantic, and conditionally routes on validation results.

---

## Architecture Overview

Here's how the LangGraph pipeline connects all the pieces:

```
                          ┌─────────────────┐
                          │  START: Input   │
                          │  {control_id,   │
                          │   period,       │
                          │   csv_path}     │
                          └────────┬────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │  Node: Policy   │
                          │  Fetch policy   │
                          │  text for       │
                          │  control        │
                          └────────┬────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │  Node: Check    │
                          │  Run            │
                          │  deterministic  │
                          │  PAY-002 check  │
                          └────────┬────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │  Node: Narrative│
                          │  Generate LLM   │
                          │  prose from     │
                          │  facts          │
                          └────────┬────────┘
                                   │
                                   ▼
                     ┌─────────────────────────┐
                     │ Node: Validate Evidence │
                     │ Build EvidencePayload   │
                     │ (Pydantic model)        │
                     └───────────┬─────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
         evidence_valid = False    evidence_valid = True
                    │                         │
                    ▼                         ▼
            ┌──────────────┐        ┌─────────────────┐
            │  END (Error) │        │  Node: Recount  │
            │  "Validation │        │  Compare        │
            │   Failed"    │        │  evidence to    │
            └──────────────┘        │  fresh count    │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌────────────────┐
                                    │ Node: Review   │
                                    │ Notes          │
                                    │ Generate LLM   │
                                    │ reviewer text  │
                                    └────────┬───────┘
                                             │
                                             ▼
                                ┌────────────────────────┐
                                │ Node: Validate Review  │
                                │ Build ReviewPayload    │
                                │ (Pydantic model)       │
                                └────────┬───────────────┘
                                         │
                                         ▼
                                ┌────────────────────┐
                                │  END: Complete     │
                                │  {evidence: {...}, │
                                │   review: {...}}   │
                                └────────────────────┘
```

**Key LangGraph Concepts:**

### 1. State Schema
```python
from typing import TypedDict, Optional

class GraphState(TypedDict):
    # Inputs
    control_id: str
    period: str
    csv_path: str
    
    # Intermediate values
    policy_summary: Optional[str]
    facts: Optional[dict]
    narrative: Optional[str]
    
    # Outputs
    evidence: Optional[dict]
    review: Optional[dict]
    
    # Error handling
    error: Optional[str]
```

State flows through every node, nodes update specific fields.

### 2. Nodes
Each node is a function with signature: `def node_name(state: GraphState) -> GraphState`

```python
def fetch_policy_node(state: GraphState) -> GraphState:
    policy = get_policy_summary(state["control_id"])
    return {**state, "policy_summary": policy}
```

### 3. Edges
Connect nodes in sequence:
```python
graph.add_edge("fetch_policy", "run_check")
graph.add_edge("run_check", "generate_narrative")
```

### 4. Conditional Edges
Route based on state:
```python
def should_continue_to_review(state: GraphState) -> str:
    if state.get("evidence") is None:
        return "error"
    return "continue"

graph.add_conditional_edges(
    "validate_evidence",
    should_continue_to_review,
    {
        "continue": "recount",
        "error": END
    }
)
```

### 5. Pydantic Schema Enforcement
```python
from pydantic import BaseModel, Field

class EvidencePayload(BaseModel):
    control_id: str
    period: str
    violations_found: int = Field(ge=0)  # >= 0
    violation_entries: list[str]
    policy_summary: str
    population: dict
    narrative: str
    
    @validator("violation_entries")
    def check_parity(cls, v, values):
        if len(v) != values.get("violations_found"):
            raise ValueError("Count must match list length")
        return v
```

**Why This Architecture Matters:**
- **No LLM Orchestration**: Graph structure is explicit, not inferred
- **Type Safety**: Pydantic catches schema violations at runtime
- **Early Exit**: Stop pipeline if evidence validation fails
- **Clear Data Flow**: State transformations are transparent
- **Testability**: Test each node independently

---


## The Data We're Working With

### Sample Journal Entries (July 2024)
Our test data contains accounting journal entries with these fields:

| Field | Description | Example |
|-------|-------------|---------|
| `entry_id` | Unique identifier | 1002 |
| `date` | Transaction date | 2024-07-02 |
| `account` | Account type | Accounts Payable |
| `amount` | Dollar amount | 2500 |
| `approver_1` | First approver | j.smith |
| `approver_2` | Second approver | (empty) |
| `notes` | Description | Laptop purchase (missing approver_2) |

### What Makes This Realistic
- **Missing approvals**: Some entries lack required approvers
- **Edge cases**: Same person approving twice, wrong account types
- **Mixed scenarios**: Some compliant, some violations, some edge cases

---

## The Control We're Testing

### PAY-002: Dual Approval for Payables
**Policy**: "All payables over $1000 require dual approval"

**What the deterministic evidence + review flow does**:
1. Filter to Accounts Payable entries > $1000
2. Compute violations and collect entry IDs
3. Generate a concise narrative using only returned facts
4. Validate the Evidence payload against a strict schema
5. Independently recount and compare results to the evidence
6. Generate brief reviewer notes
7. Validate the final Review payload against a strict schema

**Expected violations in our test data**:
- Entry 1002: $2500, missing `approver_2` ❌
- Entry 1003: $1500, missing `approver_1` ❌  
- Entry 1004: $3000, both approvers present ✅

---

## Goal of This Lab

Build an explicit **LangGraph** that:

* Defines typed graph state for inputs, intermediates, and outputs
* Wires nodes for policy, check, narrative, validation, recount/compare, review notes, and final validation
* Routes conditionally on evidence validation (stop early on schema failure)
* Produces two structured, validated payloads:
  * Evidence: counts, entry IDs, policy summary, population, narrative
  * Review: control/period, `evidence_valid`, `issues`, reviewer notes

This graph-centric approach improves determinism, auditability, and replayability.

---

## Step-by-Step Implementation Guide

### Step 1: Define Pydantic Models

**Goal**: Create strongly-typed schemas for Evidence and Review payloads.

**File**: `sox_copilot/models.py`

**Implementation Pattern**:
```python
from pydantic import BaseModel, Field, validator
from typing import List, Dict

class Population(BaseModel):
    """Population metadata for what was tested"""
    tested_count: int = Field(ge=0, description="Number of entries tested")
    criteria: str = Field(description="Filter criteria applied")

class EvidencePayload(BaseModel):
    """Structured evidence output with validation"""
    control_id: str = Field(description="SOX control identifier")
    period: str = Field(description="Audit period (YYYY-MM)")
    violations_found: int = Field(ge=0, description="Count of violations")
    violation_entries: List[str] = Field(description="Entry IDs that violated")
    policy_summary: str = Field(description="Business rule text")
    population: Population
    narrative: str = Field(min_length=50, description="Audit narrative")
    
    @validator("violation_entries")
    def check_parity(cls, v, values):
        """Ensure count matches list length"""
        count = values.get("violations_found", 0)
        if len(v) != count:
            raise ValueError(
                f"Parity error: violations_found={count} but "
                f"violation_entries has {len(v)} items"
            )
        return v

class ReviewPayload(BaseModel):
    """Structured review output with validation"""
    reviewed_control_id: str
    period: str
    evidence_valid: bool = Field(description="Whether evidence passed validation")
    issues: List[str] = Field(default_factory=list, description="Validation issues found")
    review_notes: str = Field(min_length=20, description="Reviewer commentary")
    
    @validator("issues")
    def issues_when_invalid(cls, v, values):
        """If invalid, must have issues listed"""
        if not values.get("evidence_valid") and len(v) == 0:
            raise ValueError("evidence_valid=False requires non-empty issues list")
        return v
```

**Why this matters**:
- **Runtime Validation**: Pydantic catches schema violations immediately
- **Parity Checks**: Custom validators enforce business rules
- **Type Safety**: IDE autocomplete and type checking
- **Self-Documenting**: Field descriptions explain intent

**Test it**:
```python
from sox_copilot.models import EvidencePayload, Population

# Valid evidence
evidence = EvidencePayload(
    control_id="PAY-002",
    period="2024-07",
    violations_found=2,
    violation_entries=["1002", "1003"],
    policy_summary="All payables over $1000 require dual approval.",
    population=Population(tested_count=3, criteria="AP > $1000"),
    narrative="Testing identified 2 violations..."
)
print(evidence.dict())  # Serializes to dict

# Invalid evidence (parity error)
try:
    bad = EvidencePayload(
        violations_found=5,  # Wrong!
        violation_entries=["1002", "1003"],  # Only 2 items
        # ... other fields
    )
except ValidationError as e:
    print("Caught parity error:", e)
```

**✅ Checkpoint**: Do the Pydantic models catch parity errors and missing fields?

---

### Step 2: Define Graph State Schema

**Goal**: Create a typed state dictionary that flows through the graph.

**File**: `sox_copilot/graph_evidence_review.py`

**Implementation Pattern**:
```python
from typing import TypedDict, Optional, Dict, Any

class GraphState(TypedDict, total=False):
    """
    State that flows through the LangGraph pipeline.
    
    Each node reads from and writes to this shared state.
    'total=False' means not all fields are required at initialization.
    """
    # Inputs (provided at start)
    control_id: str
    period: str
    csv_path: str
    
    # Intermediate values (populated by nodes)
    policy_summary: Optional[str]
    facts: Optional[Dict[str, Any]]
    narrative: Optional[str]
    validation_result: Optional[Dict[str, Any]]
    review_notes: Optional[str]
    
    # Final outputs (structured payloads)
    evidence: Optional[Dict[str, Any]]
    review: Optional[Dict[str, Any]]
    
    # Error handling
    error: Optional[str]
```

**Why this matters**:
- **Shared Context**: All nodes access the same state
- **Type Hints**: Helps catch errors during development
- **Clear Data Flow**: See what data is needed at each stage
- **Optional Fields**: State builds up progressively

**✅ Checkpoint**: Does your state schema cover all intermediate values and outputs?

---

### Step 3: Build Graph Nodes

**Goal**: Create node functions that transform state.

**File**: `sox_copilot/graph_evidence_review.py`

**Implementation Pattern**:
```python
from .tools import (
    get_policy_summary as get_policy_tool,
    run_deterministic_check as run_check_tool,
    generate_narrative as generate_narrative_tool,
    recount_and_compare as recount_tool,
    generate_review_notes as review_notes_tool,
)
from .models import EvidencePayload, ReviewPayload
from pydantic import ValidationError
import json

def fetch_policy_node(state: GraphState) -> GraphState:
    """Node: Fetch policy summary for the control"""
    control_id = state["control_id"]
    policy = get_policy_tool(control_id)
    return {**state, "policy_summary": policy}

def run_check_node(state: GraphState) -> GraphState:
    """Node: Run deterministic PAY-002 check"""
    facts = run_check_tool(
        state["control_id"],
        state["period"],
        state["csv_path"]
    )
    return {**state, "facts": facts}

def generate_narrative_node(state: GraphState) -> GraphState:
    """Node: Generate audit narrative from policy + facts"""
    narrative = generate_narrative_tool(
        state["control_id"],
        state["period"],
        state["policy_summary"],
        json.dumps(state["facts"])
    )
    return {**state, "narrative": narrative}

def validate_evidence_node(state: GraphState) -> GraphState:
    """
    Node: Validate evidence payload using Pydantic.
    
    This is a validation gate - if schema is invalid, set error.
    """
    try:
        evidence = EvidencePayload(
            control_id=state["control_id"],
            period=state["period"],
            violations_found=state["facts"]["violations_found"],
            violation_entries=state["facts"]["violation_entries"],
            policy_summary=state["policy_summary"],
            population=state["facts"]["population"],
            narrative=state["narrative"],
        )
        return {**state, "evidence": evidence.dict()}
    except ValidationError as e:
        return {**state, "error": f"Evidence validation failed: {e}"}

def recount_node(state: GraphState) -> GraphState:
    """Node: Independently recount and compare to evidence"""
    evidence_json = json.dumps(state["evidence"])
    validation = recount_tool(evidence_json, state["csv_path"])
    return {**state, "validation_result": validation}

def generate_review_notes_node(state: GraphState) -> GraphState:
    """Node: Generate reviewer notes from validation results"""
    notes = review_notes_tool(
        state["control_id"],
        state["period"],
        json.dumps(state["validation_result"])
    )
    return {**state, "review_notes": notes}

def validate_review_node(state: GraphState) -> GraphState:
    """Node: Validate review payload using Pydantic"""
    try:
        review = ReviewPayload(
            reviewed_control_id=state["control_id"],
            period=state["period"],
            evidence_valid=state["validation_result"]["evidence_valid"],
            issues=state["validation_result"]["issues"],
            review_notes=state["review_notes"],
        )
        return {**state, "review": review.dict()}
    except ValidationError as e:
        return {**state, "error": f"Review validation failed: {e}"}
```

**Why this matters**:
- **Single Responsibility**: Each node does one thing
- **Pure Functions**: Read state, return new state (no mutations)
- **Error Handling**: Validation failures set `error` in state
- **Tool Reuse**: Nodes call the same tools from Parts 1 & 2

**✅ Checkpoint**: Can you call each node function directly with a test state dict?

---

### Step 4: Build Conditional Routing Logic

**Goal**: Add decision points to control graph flow.

**File**: `sox_copilot/graph_evidence_review.py`

**Implementation Pattern**:
```python
def should_continue_after_evidence_validation(state: GraphState) -> str:
    """
    Router: Decide whether to continue to review or stop.
    
    If evidence validation failed, stop early.
    Otherwise, proceed to independent recount.
    """
    if state.get("error"):
        return "error"
    if state.get("evidence") is None:
        return "error"
    return "continue"

def should_continue_after_review_validation(state: GraphState) -> str:
    """
    Router: Check if review validation succeeded.
    """
    if state.get("error"):
        return "error"
    return "success"
```

**Why this matters**:
- **Early Exit**: Stop pipeline if validation fails
- **Explicit Routing**: Developer controls flow, not LLM
- **Error Handling**: Route to error state when needed

**✅ Checkpoint**: Do your router functions return the expected string keys?

---

### Step 5: Assemble the Graph

**Goal**: Wire nodes and edges into a complete pipeline.

**File**: `sox_copilot/graph_evidence_review.py`

**Implementation Pattern**:
```python
from langgraph.graph import StateGraph, END

def build_evidence_review_graph():
    """
    Build the complete evidence + review pipeline graph.
    
    Flow:
    START → policy → check → narrative → validate_evidence
                                            ↓
                                    (if valid) recount → review_notes → validate_review → END
                                    (if invalid) → END (error)
    """
    # Initialize graph with state schema
    workflow = StateGraph(GraphState)
    
    # Add all nodes
    workflow.add_node("fetch_policy", fetch_policy_node)
    workflow.add_node("run_check", run_check_node)
    workflow.add_node("generate_narrative", generate_narrative_node)
    workflow.add_node("validate_evidence", validate_evidence_node)
    workflow.add_node("recount", recount_node)
    workflow.add_node("generate_review_notes", generate_review_notes_node)
    workflow.add_node("validate_review", validate_review_node)
    
    # Set entry point
    workflow.set_entry_point("fetch_policy")
    
    # Add simple edges (always execute in order)
    workflow.add_edge("fetch_policy", "run_check")
    workflow.add_edge("run_check", "generate_narrative")
    workflow.add_edge("generate_narrative", "validate_evidence")
    
    # Conditional edge: only continue to review if evidence is valid
    workflow.add_conditional_edges(
        "validate_evidence",
        should_continue_after_evidence_validation,
        {
            "continue": "recount",
            "error": END  # Stop early if validation fails
        }
    )
    
    # Continue review flow
    workflow.add_edge("recount", "generate_review_notes")
    workflow.add_edge("generate_review_notes", "validate_review")
    
    # Conditional edge: check final review validation
    workflow.add_conditional_edges(
        "validate_review",
        should_continue_after_review_validation,
        {
            "success": END,
            "error": END
        }
    )
    
    # Compile the graph
    return workflow.compile()
```

**Why this matters**:
- **Explicit Structure**: You define the execution graph, not the LLM
- **Validation Gates**: Pydantic models enforce schemas at key points
- **Early Exit**: Stop if evidence validation fails
- **Type Safety**: State schema ensures data contracts

**Test it**:
```python
from sox_copilot.graph_evidence_review import build_evidence_review_graph

app = build_evidence_review_graph()

result = app.invoke({
    "control_id": "PAY-002",
    "period": "2024-07",
    "csv_path": "data/journal_entries.csv"
})

print("Evidence:", result.get("evidence"))
print("Review:", result.get("review"))
print("Error:", result.get("error"))
```

**✅ Checkpoint**: 
- Does the graph execute all nodes in order?
- Is evidence validated before proceeding to review?
- Are both evidence and review payloads in the final state?

---

### Step 6: Visualize the Graph (Optional but Recommended)

**Goal**: Generate a visual representation of your graph for debugging.

**Implementation**:
```python
from IPython.display import Image, display

app = build_evidence_review_graph()

# Generate PNG visualization
try:
    display(Image(app.get_graph().draw_mermaid_png()))
except Exception:
    # If mermaid not available, print the graph structure
    print(app.get_graph().to_json())
```

**Why this matters**:
- **Visual Debugging**: See the actual graph structure
- **Documentation**: Share with team to explain flow
- **Verification**: Confirm edges are wired correctly

---

## Testing Your Implementation

### Unit Testing Individual Nodes

```python
from sox_copilot.graph_evidence_review import fetch_policy_node, run_check_node

# Test policy node
state = {"control_id": "PAY-002", "period": "2024-07", "csv_path": "..."}
new_state = fetch_policy_node(state)
assert "policy_summary" in new_state
assert "dual approval" in new_state["policy_summary"].lower()

# Test check node
state_with_policy = {**new_state}
state_with_facts = run_check_node(state_with_policy)
assert "facts" in state_with_facts
assert state_with_facts["facts"]["violations_found"] == 2
```

### Integration Testing the Full Pipeline

```python
from sox_copilot.graph_evidence_review import build_evidence_review_graph

app = build_evidence_review_graph()

# Test with valid data
result = app.invoke({
    "control_id": "PAY-002",
    "period": "2024-07",
    "csv_path": "data/journal_entries.csv"
})

# Assertions
assert result.get("error") is None, f"Unexpected error: {result.get('error')}"
assert "evidence" in result
assert "review" in result
assert result["evidence"]["violations_found"] == 2
assert result["review"]["evidence_valid"] == True
```

### Testing Validation Gates

```python
# Test that parity errors are caught
from sox_copilot.models import EvidencePayload
from pydantic import ValidationError

try:
    bad_evidence = EvidencePayload(
        control_id="PAY-002",
        period="2024-07",
        violations_found=10,  # Wrong!
        violation_entries=["1002", "1003"],  # Only 2
        policy_summary="...",
        population={"tested_count": 3, "criteria": "..."},
        narrative="Some text"
    )
    assert False, "Should have raised ValidationError"
except ValidationError as e:
    assert "Parity error" in str(e)
```

### Debugging Tips

**If nodes aren't executing:**
- Check that entry point is set: `workflow.set_entry_point("fetch_policy")`
- Verify all edges are added between nodes
- Print state at each node to see transformations

**If conditional routing doesn't work:**
- Check router function return values match edge mapping keys
- Ensure router functions are checking the right state fields
- Add print statements in routers to see which path is taken

**If Pydantic validation always fails:**
- Check that state fields match model field names exactly
- Verify types (e.g., list vs tuple, int vs string)
- Use `model.dict()` to serialize, not raw model instance

---

## Common Pitfalls

### Pitfall 1: Mutating State Instead of Returning New State
**Problem**: Nodes modify state in-place

**Bad:**
```python
def bad_node(state: GraphState) -> GraphState:
    state["new_field"] = "value"  # Mutating!
    return state
```

**Good:**
```python
def good_node(state: GraphState) -> GraphState:
    return {**state, "new_field": "value"}  # New dict
```

### Pitfall 2: Missing Conditional Edge Mappings
**Problem**: Router returns a key that doesn't exist in edge mapping

**Bad:**
```python
def router(state):
    return "unknown_key"  # Not in mapping!

workflow.add_conditional_edges(
    "node",
    router,
    {"continue": "next", "error": END}  # Missing "unknown_key"
)
```

**Solution**: Ensure router only returns keys that exist in the mapping.

### Pitfall 3: Not Handling Validation Errors
**Problem**: ValidationError crashes the pipeline

**Bad:**
```python
def validate_node(state):
    evidence = EvidencePayload(**state)  # Can raise ValidationError
    return {**state, "evidence": evidence.dict()}
```

**Good:**
```python
def validate_node(state):
    try:
        evidence = EvidencePayload(**state)
        return {**state, "evidence": evidence.dict()}
    except ValidationError as e:
        return {**state, "error": str(e)}
```

### Pitfall 4: Forgetting to Compile the Graph
**Problem**: Trying to invoke an uncompiled workflow

**Bad:**
```python
workflow = StateGraph(GraphState)
# ... add nodes and edges ...
result = workflow.invoke({...})  # Error!
```

**Good:**
```python
workflow = StateGraph(GraphState)
# ... add nodes and edges ...
app = workflow.compile()  # Compile first!
result = app.invoke({...})
```

### Pitfall 5: Type Mismatches Between State and Models
**Problem**: State field types don't match Pydantic model

**Example:**
```python
# State has string "2", but model expects int
state["violations_found"] = "2"  # string
evidence = EvidencePayload(violations_found=state["violations_found"])  # ValidationError
```

**Solution**: Ensure state transformations maintain correct types.

---

## Comparison: Agents (Parts 1 & 2) vs. Graph (Part 3)

| Aspect | Agent Approach (Parts 1 & 2) | Graph Approach (Part 3) |
|--------|------------------------------|-------------------------|
| **Orchestration** | LLM decides tool calling order | Developer defines explicit flow |
| **Determinism** | Varies (LLM can choose different paths) | Fixed execution path |
| **Debugging** | Set `verbose=True`, read logs | Inspect state at each node |
| **Type Safety** | Weak (JSON strings) | Strong (Pydantic models) |
| **Validation** | Post-hoc (check final output) | Gate-based (block invalid data) |
| **Flexibility** | LLM can adapt to new scenarios | Must modify graph for new flows |
| **Cost** | Higher (multiple LLM calls for orchestration) | Lower (LLM only for content generation) |
| **Auditability** | Harder (trace through agent logs) | Easier (state transformations are explicit) |

**When to use Agents:**
- Exploratory or dynamic workflows
- User-driven tool selection
- Flexibility > determinism

**When to use LangGraph:**
- Production pipelines requiring consistency
- Compliance/audit scenarios
- Multiple validation gates
- Cost-sensitive applications


---

## Deliverables

* `sox_copilot/graph_evidence_review.py` — The LangGraph pipeline and nodes
* `sox_copilot/models.py` — Pydantic models for `EvidencePayload` and `ReviewPayload`
* `sox_copilot/tools.py` — Reused tools (`run_deterministic_check`, `get_policy_summary`, `generate_narrative`, `recount_and_compare`, `generate_review_notes`)
* Notebook section: Part 3 — LangGraph Evidence + Review

