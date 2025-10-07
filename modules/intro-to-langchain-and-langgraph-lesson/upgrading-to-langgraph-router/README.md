<h1>
  <span>

  ![](/assets/ga-logo.png)



  </span>
  <span class="subhead">Tutorial Part 2: Upgrading to LangGraph Router</span>
</h1>

**Learning objective:** Implement a LangGraph workflow that defines state, implements nodes, and applies conditional routing to produce transparent and auditable outputs.


## Activity Overview

Take our **LangChain narrative generator** and upgrade it to **LangGraph.**
  
**By the end, you’ll:**
  - Define state explicitly.
  - Create nodes for Exec + Audit narratives.
  - Add a router for branching.
  - Run the graph and compare results.

> 💡 *This shows why LangGraph is better for enterprise: transparency, auditability, scalability.*

</aside>

## Workflow
### **Step 1. Define State**

```python
from typing import TypedDict, Literal
from typing_extensions import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]   # store user + model messages
    audience: Literal["exec","audit"] | None # flag for routing
    narrative: str | None                     # output narrative

```

- **State = single source of truth.**
- Keeps track of messages, audience flag, and narrative.
- Explicit typing = auditability + validation.

---

### **Step 2. Define Nodes**

```python
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

llm = init_chat_model(model="gpt-4o-mini")

def exec_node(state: State) -> State:
    msgs = [SystemMessage(EXEC_SYSTEM), HumanMessage(state["messages"][-1].content)]
    out = llm.invoke(msgs)
    return {"narrative": out.content, "messages": [out]}

def audit_node(state: State) -> State:
    msgs = [SystemMessage(AUDIT_SYSTEM), HumanMessage(state["messages"][-1].content)]
    out = llm.invoke(msgs)
    return {"narrative": out.content, "messages": [out]}

```

- Each node = **unit of work.**
- Exec node → 3-sentence leadership summary.
- Audit node → terse bullet points with policy references.

---

### **Step 3. Add a Router**

```python
def router(state: State):
    # simple routing: check the audience flag
    return "exec" if state.get("audience") == "exec" else "audit"

```

- Router decides the path based on `audience`.
- Could be extended later with **more complex logic** (confidence scores, fallback routes, etc).

---

### **Step 4. Build the Graph**

```python
g = StateGraph(State)

# Add nodes
g.add_node("Exec", exec_node)
g.add_node("Audit", audit_node)

# Add conditional edges
g.add_conditional_edges(START, router, {"exec": "Exec", "audit": "Audit"})
g.add_edge("Exec", END)
g.add_edge("Audit", END)

graph = g.compile()

```

- Graph = **nodes + edges.**
- Router = conditional edge.
- End = explicit termination.

**Visual Representation**

```jsx
     START
       ↓
    [router] ← checks state["audience"]
       ↓
   ┌───┴───┐
   ↓       ↓
 Exec    Audit
   ↓       ↓
   └───┬───┘
       ↓
      END
```

---

### **Step 5. Run the Graph**

```python
evidence = """PAY-002: Dual approval required > $1,000.
Entries 1002, 1015, 1021 lacked second approver.
Policy section: AP-7.3."""

initial = {
    "messages": [{"role": "user", "content": evidence}],
    "audience": "audit",  # change to "exec" to test
    "narrative": None
}

final = graph.invoke(initial)
print({"audience": initial["audience"], "narrative": final["narrative"]})

```

---

### **Expected Output**

- If **audience = "exec"** → 3-sentence leadership-style summary.
- If **audience = "audit"** → terse bullet points with policy reference.



## **Your Turn (Exercise)**

1. Change the `audience` flag and rerun.
2. Try new evidence text.
3. Discuss:
    - How is this different from Microlesson 3?
    - Why is explicit routing + state valuable in **enterprise or audit contexts**?


## Key Takeaway:

<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

💡 *We’ve upgraded from a **Python if-statement** → a **LangGraph state machine.***

*This gives us:*

- ***Transparency** → we can visualize the graph.*
- ***Auditability** → state is tracked at each node.*
- ***Reusability** → easy to extend with new nodes.*

</aside>