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
Same as Parts 1 & 2:
```bash
cd modules/lab-orchestrating-and-evaluating-the-sox-copilot/solution
pipenv install
pipenv shell
```

The Pipfile already includes `langgraph ~=0.2.0`.

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
from typing import List
from pydantic import BaseModel, Field

class Population(BaseModel):
    tested_count: int = Field(ge=0)
    criteria: str

class EvidencePayload(BaseModel):
    control_id: str
    period: str
    violations_found: int = Field(ge=0)
    violation_entries: List[str]
    policy_summary: str
    population: Population
    narrative: str

class ReviewPayload(BaseModel):
    reviewed_control_id: str
    period: str
    evidence_valid: bool
    issues: List[str]
    review_notes: str
```

**Why this matters**:
- **Runtime Validation**: Pydantic catches schema violations immediately
- **Type Safety**: IDE autocomplete and type checking  
- **Clean Serialization**: Easy conversion to/from dicts and JSON
- **Field Constraints**: `Field(ge=0)` ensures non-negative values

**Test it**:
```python
from sox_copilot.models import EvidencePayload, Population
from pydantic import ValidationError

# Valid evidence
evidence = EvidencePayload(
    control_id="PAY-002",
    period="2024-07",
    violations_found=2,
    violation_entries=["1002", "1003"],
    policy_summary="All payables over $1000 require dual approval.",
    population=Population(tested_count=3, criteria="AP > $1000"),
    narrative="Testing identified 2 violations in the audit period."
)
print(evidence.model_dump())  # Serializes to dict

# Invalid evidence (negative violations)
try:
    bad = EvidencePayload(
        control_id="PAY-002",
        violations_found=-1,  # Invalid! Must be >= 0
        violation_entries=[],
        policy_summary="...",
        population=Population(tested_count=0, criteria="..."),
        narrative="..."
    )
except ValidationError as e:
    print("Caught validation error:", e)
```

**✅ Checkpoint**: Do the Pydantic models catch negative values and missing required fields?

---

### Step 2: Define Graph State Schema

**Goal**: Create a typed state dictionary that flows through the graph.

**File**: `sox_copilot/graph_evidence_review.py`

**Implementation Pattern**:
```python
from typing import TypedDict, Optional
from .models import EvidencePayload, ReviewPayload

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
    
    # Evidence phase intermediates
    policy_summary: str
    facts: dict            # {"violations_found": int, "violation_entries": [...], "population": {...}}
    facts_json: str
    narrative: str
    
    # Validated outputs
    evidence: EvidencePayload
    evidence_errors: str   # serialized pydantic errors if any
    
    # Review phase intermediates
    comparison: dict       # {"reviewed_control_id":..., "period":..., "evidence_valid":..., "issues":[...]}
    review_notes: str
    
    # Final
    review: ReviewPayload
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
    get_policy_summary,
    run_deterministic_check,
    generate_narrative,
    recount_and_compare,
    generate_review_notes,
)
from .models import EvidencePayload, ReviewPayload
import json

def node_get_policy(state: GraphState) -> GraphState:
    """Node: Fetch policy summary for the control"""
    summary = get_policy_summary.invoke({"control_id": state["control_id"]})
    return {"policy_summary": summary}

def node_run_check(state: GraphState) -> GraphState:
    """Node: Run deterministic PAY-002 check"""
    facts = run_deterministic_check.invoke({
        "control_id": state["control_id"],
        "period": state["period"],
        "csv_path": state["csv_path"],
    })
    return {"facts": facts, "facts_json": json.dumps(facts)}

def node_generate_narrative(state: GraphState) -> GraphState:
    """Node: Generate audit narrative from policy + facts"""
    nar = generate_narrative.invoke({
        "control_id": state["control_id"],
        "period": state["period"],
        "policy_summary": state["policy_summary"],
        "facts_json": state["facts_json"],
    })
    return {"narrative": nar}

def node_assemble_and_validate_evidence(state: GraphState) -> GraphState:
    """
    Node: Validate evidence payload using Pydantic.
    
    This is a validation gate - if schema is invalid, set evidence_errors.
    """
    try:
        payload = EvidencePayload.model_validate({
            "control_id": state["control_id"],
            "period": state["period"],
            "violations_found": state["facts"]["violations_found"],
            "violation_entries": state["facts"]["violation_entries"],
            "policy_summary": state["policy_summary"],
            "population": state["facts"]["population"],
            "narrative": state["narrative"],
        })
        return {"evidence": payload, "evidence_errors": None}
    except Exception as e:
        return {"evidence_errors": str(e)}

def node_recount_and_compare(state: GraphState) -> GraphState:
    """Node: Independently recount and compare to evidence"""
    comparison = recount_and_compare.invoke({
        "csv_path": state["csv_path"],
        "evidence_json": state["evidence"].model_dump_json(),
    })
    return {"comparison": comparison}

def node_generate_review_notes(state: GraphState) -> GraphState:
    """Node: Generate reviewer notes from validation results"""
    notes = generate_review_notes.invoke({
        "control_id": state["comparison"]["reviewed_control_id"],
        "period": state["comparison"]["period"],
        "evidence_valid": state["comparison"]["evidence_valid"],
        "issues": state["comparison"]["issues"],
    })
    return {"review_notes": notes}

def node_assemble_and_validate_review(state: GraphState) -> GraphState:
    """Node: Validate review payload using Pydantic"""
    try:
        review = ReviewPayload.model_validate({
            "reviewed_control_id": state["comparison"]["reviewed_control_id"],
            "period": state["comparison"]["period"],
            "evidence_valid": state["comparison"]["evidence_valid"],
            "issues": state["comparison"]["issues"],
            "review_notes": state["review_notes"],
        })
        return {"review": review}
    except Exception as e:
        return {"review": None}
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
def route_evidence_valid(state: GraphState) -> str:
    """
    Router: Decide whether to continue to review or stop.
    
    If evidence validation failed (evidence_errors is set), stop early.
    Otherwise, proceed to independent recount.
    """
    return "ok" if not state.get("evidence_errors") else "invalid"
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
from langgraph.graph import StateGraph, START, END

def build_evidence_review_graph():
    """
    Build the complete evidence + review pipeline graph.
    
    Flow:
    START → get_policy → run_check → write_narrative → evidence_validate
                                                            ↓
                                    (if ok) recount_compare → write_review_notes → review_validate → END
                                    (if invalid) → END (early exit)
    """
    # Initialize graph with state schema
    g = StateGraph(GraphState)
    
    # Add evidence path nodes
    g.add_node("get_policy", node_get_policy)
    g.add_node("run_check", node_run_check)
    g.add_node("write_narrative", node_generate_narrative)
    g.add_node("evidence_validate", node_assemble_and_validate_evidence)
    
    # Add review path nodes
    g.add_node("recount_compare", node_recount_and_compare)
    g.add_node("write_review_notes", node_generate_review_notes)
    g.add_node("review_validate", node_assemble_and_validate_review)
    
    # Edges: Evidence sequence
    g.add_edge(START, "get_policy")
    g.add_edge("get_policy", "run_check")
    g.add_edge("run_check", "write_narrative")
    g.add_edge("write_narrative", "evidence_validate")
    
    # Conditional: evidence validation gate
    g.add_conditional_edges(
        "evidence_validate",
        route_evidence_valid,
        {
            "ok": "recount_compare",      # proceed to reviewer flow
            "invalid": END,               # stop early; evidence schema failed
        },
    )
    
    # Review sequence
    g.add_edge("recount_compare", "write_review_notes")
    g.add_edge("write_review_notes", "review_validate")
    g.add_edge("review_validate", END)
    
    return g.compile()
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
print("🧭 Graph compiled")

# Run the pipeline
inputs = {
    "control_id": "PAY-002",
    "period": "2024-07",
    "csv_path": "data/journal_entries.csv",
}
final = app.invoke(inputs)

# Extract validated models
evidence = final.get("evidence")
review = final.get("review")

print("✅ Evidence validated" if evidence else "❌ Evidence failed validation")
print("✅ Review validated" if review else "❌ Review failed validation")

# Pretty print
if evidence:
    print("\n--- Evidence ---")
    print(evidence.model_dump())
if review:
    print("\n--- Review ---")
    print(review.model_dump())
```

**✅ Checkpoint**: 
- Does the graph compile without errors?
- Does the pipeline execute all nodes in order?
- Are both evidence and review payloads Pydantic models in the final state?

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

## Notebook Structure

The `sox_copilot_lab.ipynb` notebook demonstrates the complete LangGraph pipeline:

**Cell 0-1: Setup and Data Exploration**
- Load environment variables
- Import pandas and explore journal entries CSV

**Cell 2: Build Graph**
```python
from sox_copilot.graph_evidence_review import build_evidence_review_graph
app = build_evidence_review_graph()
print("🧭 Graph compiled")
```

**Cell 3-4: Visualize Graph Structure**
- Use `app.get_graph().draw_mermaid_png()` to generate visual diagram
- Shows node connections and conditional routing

**Cell 5-6: Test Validation Gates**
- Test valid `EvidencePayload` creation
- Test parity error catching (violations_found != len(violation_entries))
- Test missing required field detection

**Cell 7-8: Verify Early Exit Logic**
- Confirm graph has conditional routing from `evidence_validate`
- Routes to `recount_compare` if valid, END if invalid

**Cell 9-10: Stream Pipeline Execution**
```python
for i, step in enumerate(app.stream(inputs), 1):
    node_name = list(step.keys())[0]
    node_output = step[node_name]
    print(f"📍 Step {i}: {node_name}")
    # Display intermediate state changes
```

**Cell 11-12: Inspect Final State**
```python
final_state = app.invoke(inputs)
# Trace data flow through all phases
print("Evidence:", final_state.get('evidence'))
print("Review:", final_state.get('review'))
```

**Cell 13-14: Standard Execution**
```python
final = app.invoke(inputs)
evidence = final.get("evidence")
review = final.get("review")
if evidence:
    print(evidence.model_dump())
if review:
    print(review.model_dump())
```

**Cell 15-16: Save Results**
```python
import json, os
os.makedirs("out", exist_ok=True)
if evidence: 
    with open("out/evidence.json","w") as f: 
        json.dump(evidence.model_dump(), f, indent=2)
if review:
    with open("out/review.json","w") as f: 
        json.dump(review.model_dump(), f, indent=2)
```

---

## Testing Your Implementation

### Unit Testing Individual Nodes

```python
from sox_copilot.graph_evidence_review import node_get_policy, node_run_check

# Test policy node
state = {"control_id": "PAY-002", "period": "2024-07", "csv_path": "data/journal_entries.csv"}
new_state = node_get_policy(state)
assert "policy_summary" in new_state
assert "dual approval" in new_state["policy_summary"].lower()

# Test check node
state_with_policy = {**state, **new_state}
state_with_facts = node_run_check(state_with_policy)
assert "facts" in state_with_facts
assert "facts_json" in state_with_facts
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
assert result.get("evidence_errors") is None, f"Unexpected validation error: {result.get('evidence_errors')}"
assert "evidence" in result
assert "review" in result
assert result["evidence"].violations_found == 2
assert result["review"].evidence_valid == True
```

### Testing Validation Gates

```python
# Test that negative values are caught
from sox_copilot.models import EvidencePayload, Population
from pydantic import ValidationError

try:
    bad_evidence = EvidencePayload(
        control_id="PAY-002",
        period="2024-07",
        violations_found=-1,  # Invalid! Must be >= 0
        violation_entries=[],
        policy_summary="All payables over $1000 require dual approval.",
        population=Population(tested_count=0, criteria="AP > $1000"),
        narrative="Some text"
    )
    assert False, "Should have raised ValidationError"
except ValidationError as e:
    print(f"✓ Validation error caught: {e}")
```

### Debugging Tips

**If nodes aren't executing:**
- Check that entry point uses START: `g.add_edge(START, "get_policy")`
- Verify all edges are added between nodes
- Use `app.stream(inputs)` to see intermediate state changes

**If conditional routing doesn't work:**
- Check router function return values match edge mapping keys exactly
- Router returns `"ok"` or `"invalid"` to match edge mapping
- Add print statements in routers to see which path is taken

**If Pydantic validation always fails:**
- Check that state fields match model field names exactly
- Verify types (e.g., list vs tuple, int vs string)
- Use `model.model_dump()` to serialize (Pydantic v2), not `dict()`
- Use `model.model_validate()` to validate dicts (Pydantic v2)

---

## Common Pitfalls

### Pitfall 1: Returning Full State vs Partial Updates
**Problem**: Nodes can return just the fields they're updating (partial state)

**Both work, but partial is cleaner:**
```python
# Good: Return only what changed
def good_node(state: GraphState) -> GraphState:
    return {"new_field": "value"}  # Partial update

# Also works: Return full state
def also_good_node(state: GraphState) -> GraphState:
    return {**state, "new_field": "value"}  # Full state
```

**Why partial is better:**
- More concise
- Clearer intent (shows what changed)
- LangGraph merges it automatically

### Pitfall 2: Missing Conditional Edge Mappings
**Problem**: Router returns a key that doesn't exist in edge mapping

**Bad:**
```python
def router(state):
    return "unknown_key"  # Not in mapping!

g.add_conditional_edges(
    "node",
    router,
    {"ok": "next", "invalid": END}  # Missing "unknown_key"
)
```

**Good:**
```python
def router(state):
    return "ok" if not state.get("error") else "invalid"  # Matches mapping

g.add_conditional_edges(
    "node",
    router,
    {"ok": "next", "invalid": END}  # Keys match router returns
)
```

### Pitfall 3: Not Handling Validation Errors
**Problem**: ValidationError crashes the pipeline

**Bad:**
```python
def validate_node(state):
    payload = EvidencePayload.model_validate(state)  # Can raise ValidationError
    return {"evidence": payload}
```

**Good:**
```python
def validate_node(state):
    try:
        payload = EvidencePayload.model_validate({
            "control_id": state["control_id"],
            "period": state["period"],
            # ... other fields
        })
        return {"evidence": payload, "evidence_errors": None}
    except Exception as e:
        return {"evidence_errors": str(e)}
```

### Pitfall 4: Forgetting to Compile the Graph
**Problem**: Trying to invoke an uncompiled workflow

**Bad:**
```python
g = StateGraph(GraphState)
# ... add nodes and edges ...
result = g.invoke({...})  # Error!
```

**Good:**
```python
g = StateGraph(GraphState)
# ... add nodes and edges ...
app = g.compile()  # Compile first!
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

* `sox_copilot/graph_evidence_review.py` — The LangGraph pipeline with nodes, routing logic, and graph builder
* `sox_copilot/models.py` — Pydantic models for `EvidencePayload`, `ReviewPayload`, and `Population`
* `sox_copilot/tools.py` — Reused tools from Parts 1 & 2 (`run_deterministic_check`, `get_policy_summary`, `generate_narrative`, `recount_and_compare`, `generate_review_notes`)
* `sox_copilot/checks.py` — Deterministic business logic (reused from Parts 1 & 2)
* `sox_copilot/config.py` — Configuration constants (reused from Parts 1 & 2)
* `sox_copilot_lab.ipynb` — Complete notebook demonstrating graph visualization, streaming, validation gates, and final execution
* `out/` directory — Saved evidence.json and review.json outputs

