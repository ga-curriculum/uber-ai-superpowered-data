<h1>
  <span>
  
  ![](/assets/ga-logo.png)

  </span>
  <span class="subhead">Tutorial Part 3: Adding a Classifier with Structured Output</span>
</h1>

**Learning objective:** Implement a classifier node with structured outputs to automate routing, validation, and improve auditability in LangGraph workflows.


## Activity Overview
- Remove the **manual audience flag.**
- Add a **classifier node** that decides automatically whether the narrative should be “exec” or “audit.”
- Introduce **structured outputs (via Pydantic)** and show why typed state = critical in auditable systems.

> 💡 *Instead of guessing or hardcoding routes, the system decides — and validates its decision.*


## Workflow
### **Step 1. Extend State**

```python
from typing import TypedDict, Literal
from typing_extensions import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
    audience: Literal["exec","audit"] | None  # classifier will set this
    narrative: str | None

```

- `audience` now starts as `None`.
- Classifier node will **set it automatically.**

---

### **Step 2. Define the Classifier Schema**

```python
from pydantic import BaseModel, Field

class AudienceChoice(BaseModel):
    audience: Literal["exec","audit"] = Field(
        description="Choose 'exec' for leadership brief; 'audit' for compliance detail."
    )

```

- **Pydantic model** enforces allowed values.
- If model returns invalid text → it fails validation.

💡 *This makes routing decisions typed, safe, and auditable.*

---

### **Step 3. Create a Classifier Node**

```python
from langchain_core.messages import SystemMessage, HumanMessage

def classify_audience(state: State) -> State:
    structured = llm.with_structured_output(AudienceChoice)
    user_msg = state["messages"][-1].content

    system_prompt = (
        "Decide the audience. "
        "If the request asks for high-level summary, risks, or next steps → exec. "
        "If it asks for findings, evidence, or policy refs → audit."
    )

    result: AudienceChoice = structured.invoke([
        SystemMessage(system_prompt),
        HumanMessage(user_msg)
    ])

    return {"audience": result.audience}

```

- Uses **structured output binding** → returns an `AudienceChoice`.
- Classifier node updates state with `audience`.

---

### **Step 4. Rebuild the Graph**

```python
g2 = StateGraph(State)

# Add nodes
g2.add_node("Classify", classify_audience)
g2.add_node("Exec", exec_node)
g2.add_node("Audit", audit_node)

# Add edges
g2.add_edge(START, "Classify")
g2.add_conditional_edges("Classify", lambda s: s["audience"],
                         {"exec": "Exec", "audit": "Audit"})
g2.add_edge("Exec", END)
g2.add_edge("Audit", END)

graph2 = g2.compile()

```

- `Classify` is now the **first step.**
- Routes automatically to `Exec` or `Audit`.

---

### **Step 5. Run Without Audience Flag**

```python
evidence = """PAY-002: Dual approval required > $1,000.
Entries 1002, 1015, 1021 lacked second approver.
Policy section: AP-7.3."""

initial2 = {
    "messages": [{"role": "user", "content": evidence}],
    "audience": None,   # no flag now!
    "narrative": None
}

final2 = graph2.invoke(initial2)
print({"audience": final2["audience"], "narrative": final2["narrative"]})

```

---

### **Expected Output**

- If evidence feels like a **leadership summary request** → Exec narrative.
- If evidence points to **compliance/evidence needs** → Audit narrative.

---

### **Your Turn (Exercise)**

Try 3 examples:

1. *“Summarize the risk exposure for leadership.”* → Should route to **Exec**.
2. *“List the missing approvals with policy citations.”* → Should route to **Audit**.
3. Your own example → See how classifier responds.

**Discuss:**

- Did the classifier route correctly?
- Why is **typed structured output** safer than parsing plain text?
- Where would this matter in compliance or audit systems?


## Key Takeaway:

<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

💡 **With the classifier:**
  - Routing is **automated.**
  - Decisions are **typed and validated.**
  - System is **auditable and production-ready.**

👉 This is the same pattern you’ll use later for **multi-agent orchestration and evaluation.**

</aside>


