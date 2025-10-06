<h1>
  <span>

  ![alt text](/assets/ga-logo.png)

  </span>
  <span class="subhead">Part 3 - Add State and Guardrails with LangGraph</span>
</h1>

## Goal

Wrap the pipeline in LangGraph with explicit state management and add an automatic groundedness check.

## Why LangGraph?

So far, we've built a simple pipeline with sequential steps. But production systems need:

1. **State management**: Track what we've retrieved, generated, and validated
2. **Conditional logic**: Take different actions based on validation results
3. **Observability**: Log every decision for debugging and auditing

**LangGraph** gives you a state machine abstraction for complex LLM workflows. Think of it as a flowchart that executes itself!

## The Workflow

Here's what we're building:

```
┌─────────────┐
│   RETRIEVE  │  Fetch relevant chunks
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  GENERATE   │  Draft an answer
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    GRADE    │  Check if answer is grounded
└──────┬──────┘
       │
    ┌──┴──┐
    │ PASS? │
    └──┬──┘
  Yes  │  No
       │  ▼
       │  ┌──────────────┐
       │  │ FAIL_CLOSED  │  Return safe response
       │  └──────────────┘
       ▼
     [END]
```

This workflow has **4 nodes** and **1 conditional edge**. The answer only returns if it passes the grounding check!

## Steps

### 1. Define state

State is the "memory" passed between nodes in the graph.

```python
from typing import List, Optional
from pydantic import BaseModel, Field

class QAState(BaseModel):
    """State object for our RAG workflow."""
    
    # Input
    question: str = Field(description="User's question")
    
    # Retrieval
    contexts: List[str] = Field(default_factory=list, description="Retrieved text chunks")
    citations: List[str] = Field(default_factory=list, description="Source references")
    
    # Generation
    draft_answer: Optional[str] = Field(default=None, description="LLM-generated answer")
    
    # Validation
    passed: Optional[bool] = Field(default=None, description="Did answer pass grounding check?")
    reason: Optional[str] = Field(default=None, description="Grading explanation")

```

### 2. Create a groundedness grader

Now we need a way to **verify** that the answer is actually supported by the context. We'll use an LLM as a judge:

```python
grade_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a strict fact-checker. Check if the answer is FULLY supported by the provided context. "
     "Reply with 'PASS' or 'FAIL' on the first line, then a short reason explaining your decision. "
     "Be strict: if the answer makes any claims not in the context, even minor ones, mark it as FAIL."),
    ("human", "Answer:\n{answer}\n\nContext:\n{context}")
])

grade_chain = grade_prompt | llm | StrOutputParser()
```

**Why use an LLM for grading?**

- **Semantic understanding**: Can detect paraphrasing and implications
- **Flexible**: Works for any domain without custom rules
- **Reliable**: Better than regex or keyword matching for nuanced text

A rule-based system might miss that "requires approval from both..." means the same as "dual approval needed by...". The LLM understands these are semantically equivalent.

### 3. Define graph nodes

Each node is a function that takes state, does something, and returns updated state. Think of nodes as steps in your workflow.

```python
from langgraph.graph import StateGraph, START, END

def retrieve_node(state: QAState) -> QAState:
    """Retrieve relevant documents."""
    docs = retriever.invoke(state.question)
    state.contexts = [doc.page_content for doc in docs]
    state.citations = [f"doc{i+1}" for i in range(len(docs))]
    print(f"Retrieved {len(docs)} chunks")
    return state

def generate_node(state: QAState) -> QAState:
    """Generate answer from context."""
    # Format context with citations
    joined = "\n\n---\n\n".join([
        f"[{state.citations[i]}]: {ctx}"
        for i, ctx in enumerate(state.contexts)
    ])
    
    state.draft_answer = answer_chain.invoke({
        "question": state.question,
        "context": joined
    })
    print(f"Generated draft answer ({len(state.draft_answer)} chars)")
    return state

def grade_node(state: QAState) -> QAState:
    """Check if answer is grounded in context."""
    joined = "\n\n---\n\n".join(state.contexts)
    verdict = grade_chain.invoke({
        "answer": state.draft_answer,
        "context": joined
    })
    
    state.passed = verdict.strip().upper().startswith("PASS")
    state.reason = verdict
    print(f"Grading: {'PASS' if state.passed else 'FAIL'}")
    return state

def fail_closed_node(state: QAState) -> QAState:
    """Fallback when grounding check fails."""
    state.draft_answer = "Insufficient evidence to answer confidently."
    print("Fail-closed response triggered")
    return state
```

**Note:**  
Each node:

- Receives the current state
- Updates specific fields
- Prints progress (for observability)
- Returns the updated state

The state flows through: `retrieve → generate → grade → (pass or fail_closed) → END`

### 4. Wire the graph

Now let's connect these nodes into a workflow:

```python

# Initialize graph with our state schema
wf = StateGraph(QAState)

# Add nodes
wf.add_node("retrieve", retrieve_node)
wf.add_node("generate", generate_node)
wf.add_node("grade", grade_node)
wf.add_node("fail_closed", fail_closed_node)

# Define edges (flow)
wf.set_entry_point("retrieve")
wf.add_edge("retrieve", "generate")
wf.add_edge("generate", "grade")

# Conditional routing based on grading result
wf.add_conditional_edges(
    "grade",
    lambda state: "pass" if state.passed else "fail",
    {
        "pass": END,              # Success path
        "fail": "fail_closed"     # Failure path
    }
)

wf.add_edge("fail_closed", END)

# Compile into runnable
app = wf.compile()
```

**What's happening here?**

1. **Set entry point**: Start at "retrieve"
2. **Linear edges**: retrieve → generate → grade (always happen)
3. **Conditional edge**: After grading, route based on `state.passed`:
   - If `True` → END (answer is good!)
   - If `False` → fail_closed (override with safe response)
4. **Compile**: Turn the graph definition into a runnable application

**Test it!** Add this quick test:

```python
# Quick test of the graph
test_state = QAState(question="What is the dual approval threshold for PAY-002?")
result = app.invoke(test_state)

print("\n" + "="*60)
print("GRAPH TEST RESULT")
print("="*60)
print(f"Answer: {result['draft_answer']}")
print(f"Passed: {result['passed']}")
print("="*60 + "\n")
```

Run it and you should see all the progress prints as it flows through the graph!

**Checkpoint:** You have a LangGraph workflow that automatically validates answers and fails closed when grounding is insufficient.

