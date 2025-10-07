<h1>
  <span>

  ![](/assets/ga-logo.png)

  </span>
  <span class="subhead">Tutorial Part 1: Narrative Styles in LangChain</span>
</h1>

**Learning objective:** Apply tailored prompts and branching in LangChain to generate executive and audit narratives from the same evidence.

## Activity Overview

In this walkthrough, we'll demonstrate how to use **LangChain** to produce different **narrative styles** (executive vs audit) from the **same evidence input.** 

You will also be able to see how **prompt design + simple branching** shape outputs.

> **Objective: One set of facts → two very different narratives, depending on the audience.**

## **Setup**

- Framework: **LangChain’s chat model interface**
- Model: `gpt-4o-mini` (or any LLM: Claude, Gemini, etc.)
- Two **system prompts:**
    - **Executive style** → crisp, high-level communication.
    - **Audit style** → terse, specific, control-focused.

## Workflow

### **Step 1. Define the Prompts**

```python
EXEC_SYSTEM = """You are a crisp executive communicator.
Write 3 short sentences: impact, key risk, next step.
Avoid jargon and keep it high-level."""

AUDIT_SYSTEM = """You are an audit reviewer.
Be terse and specific. Cite the policy section by ID if provided.
Return 3 bullet points: Finding, Evidence, Policy reference."""

```

- **Executive style**: impact → risk → next step.
- **Audit style**: finding → evidence → policy reference.

---

### **Step 2. Create a Simple LangChain Model**

```python
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

# Choose a model you have access to
llm = init_chat_model(model="gpt-4o-mini")

def write_narrative(evidence: str, audience: str):
    system = EXEC_SYSTEM if audience == "exec" else AUDIT_SYSTEM
    msgs = [SystemMessage(system), HumanMessage(evidence)]
    resp = llm.invoke(msgs)
    return {"audience": audience, "narrative": resp.content}

```

- `init_chat_model` → initializes an LLM.
- `SystemMessage` sets the style (exec vs audit).
- `HumanMessage` provides the evidence.
- Output = structured dict → audience + narrative.

---

### **Step 3. Test With an Example**

```python
evidence = """PAY-002: Dual approval required > $1,000.
Entries 1002, 1015, 1021 lacked second approver.
Policy section: AP-7.3."""

print(write_narrative(evidence, "exec"))
print(write_narrative(evidence, "audit"))

```

---

### **Expected Output**

**Executive Style**

```
Payments above threshold lacked proper approval.
This creates financial control risk.
Next step: reinforce dual approval process.
```

**Audit Style**

```
Finding: Missing dual approval for entries 1002, 1015, 1021
Evidence: Ledger entries show only one approver
Policy reference: AP-7.3
```

## **Your Turn (Exercise)**

1. Replace the `evidence` string with your own text.
    - Example: *“Revenue entries not reviewed by manager in Q3.”*
2. Generate both versions (`exec` and `audit`).
3. Compare:
    - How do the outputs differ?
    - Which would you present to leadership?
    - Which belongs in an audit committee workpaper?

## ****Key Takeaway**:**

<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

💡 LangChain makes it easy to produce different styles with **simple prompt branching.**

  **But:**
  - Routing logic is **hidden** in our Python function.
  - There’s **no explicit state or auditability yet.**
    
</aside>