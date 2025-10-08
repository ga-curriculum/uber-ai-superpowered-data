
<h1>
  <span style="display:flex; gap:20px; text-align:middler; font-size:">

  ![](/assets/ga-logo.png)

  </span> 
  <span class="headline">Develop a Single-Agent System</span>
</h1>

## About

Now let's put all the pieces together. Participants will decomposed tasks and selected models to assemble a functional single agent.

## Module Objectives
- Develop a functional single agent by assembling core components, including an orchestrator and a RAG-based tool.
- Test the final agent's performance against a set of requirements and justify the design choices made during its construction.
  
# Creating a Single Agent Lab

## Background

This 3-part lab series builds a **SOX Audit Copilot**: an AI assistant that helps finance teams generate and validate audit evidence for SOX controls. Think of it as an automated auditor that can:

1. **Read financial data** (like journal entries)
2. **Apply audit rules** (like "all payments over $1000 need two approvers")  
3. **Find violations** automatically
4. **Write professional audit reports** in plain English

You'll combine deterministic checks (Python logic) with generative AI (LLM) to produce audit-ready outputs.

---

## Prerequisites

**Required Knowledge:**
- Python fundamentals (functions, dictionaries, list comprehensions)
- Basic familiarity with LangChain concepts (agents, tools, chains)
- Understanding of how LLMs work at a high level

**Environment Setup:**
```bash
# Navigate to the module directory
cd modules/develop-a-single-agent-system/solution

# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell

# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your-key-here" > .env
```

**Dependencies Used (from Pipfile):**
- `langchain` (~=0.3.0) — Agent framework and tool decorators
- `langchain-openai` (~=0.2.0) — OpenAI LLM integration
- `langchain-core` (~=0.3.0) — Core LangChain components
- `langgraph` (~=0.2.0) — Graph-based workflows (for future labs)
- `pandas` (~=2.2.0) — CSV data manipulation
- `python-dotenv` (~=1.0.0) — Environment variable management
- `openai` (~=1.55.0) — OpenAI API client
- `jupyter` — Notebook environment
- Python 3.11 required

**Verify your setup:**
```python
import os
from dotenv import load_dotenv
load_dotenv()
assert os.getenv("OPENAI_API_KEY"), "Missing OPENAI_API_KEY"
```

---

## What Does the Evidence Agent Do?

The **Evidence Agent** is like a junior auditor that:

1. **Gets assigned a control to test** (e.g., "PAY-002: Dual Approval for Payables")
2. **Looks up the policy** ("All payables over $1000 require dual approval")
3. **Examines the financial data** (journal entries from July 2024)
4. **Finds violations** (entries missing second approver)
5. **Writes a professional summary** for the audit workpapers

The agent orchestrates these steps automatically, calling different "tools" to:
- Get policy text
- Run compliance checks  
- Generate narrative summaries

---

## Architecture Overview

Here's how the Evidence Agent components fit together:

```
┌─────────────────────────────────────────────────────────────┐
│                      Evidence Agent                          │
│                   (LLM Orchestrator)                         │
│                                                              │
│  "Produce audit result for PAY-002 in 2024-07..."          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Agent decides which tools to call and in what order │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│         ┌───────────────┼───────────────┐                   │
│         │               │               │                   │
│         ▼               ▼               ▼                   │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────┐       │
│  │  Tool 1  │   │  Tool 2  │   │     Tool 3       │       │
│  │ Policy   │   │ Check    │   │   Narrative      │       │
│  │ Lookup   │   │ Runner   │   │   Generator      │       │
│  └──────────┘   └──────────┘   └──────────────────┘       │
│       │              │                  │                   │
└───────┼──────────────┼──────────────────┼───────────────────┘
        │              │                  │
        ▼              ▼                  ▼
   "PAY-002:      ┌─────────────┐    (LLM writes
    All payables  │   CSV Data  │     narrative)
    over $1000... │  July 2024  │         
                  └─────────────┘         
                   violations_found: 2
                   entry_ids: [1002, 1003]
```

**Key Concepts:**

1. **Agent** = LLM that orchestrates tool calls based on the task
2. **Tools** = Python functions wrapped with `@tool` decorator that the agent can invoke
3. **Deterministic Layer** = Business logic (checks, filters) that never hallucinates
4. **Generative Layer** = LLM that writes professional narratives from facts

**Data Flow:**
```
User Request → Agent → Tool 1 (policy) → facts
                    → Tool 2 (check CSV) → facts  
                    → Tool 3 (narrative from facts) → text
             Agent → Assembles JSON payload
```

---

## Lab Structure: Progressive Build (1A → 1B → 1C)

This lab is broken into three progressive folders to help you build incrementally:

### 📁 Part 1A: Single Tool (Deterministic Check)
**Focus**: Learn the `@tool` decorator and wrap your first Python function

**What you build**:
- `sox_copilot/tools.py` with just `run_deterministic_check` tool
- This tool loads CSV, runs the PAY-002 logic, returns facts

**Learning goal**: Understand the bridge between "boring Python" and AI reasoning

---

### 📁 Part 1B: Multiple Tools (Add Policy + Narrative)
**Focus**: Add tools that provide context (policy) and LLM generation (narrative)

**What you build**:
- Add `get_policy_summary` tool (simple dictionary lookup)
- Add `generate_narrative` tool (LLM chain that writes from facts)

**Learning goal**: See how to combine deterministic + generative tools

---

### 📁 Part 1C: Full Agent Orchestrator
**Focus**: Build the agent that intelligently calls all tools in sequence

**What you build**:
- `sox_copilot/evidence_agent.py` with prompt and agent executor
- The agent decides when/how to call tools based on instructions

**Learning goal**: Understand agent orchestration and structured output

---

**Recommended Approach:**
1. Complete 1A fully before moving to 1B
2. Test each tool individually before adding agent orchestration
3. Use the `solution/` folder for reference, not copy-paste
4. The notebooks provide test harnesses for each stage

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

**What the check does**:
1. Filter to Accounts Payable entries > $1000
2. Check if both `approver_1` AND `approver_2` are present
3. Flag violations where either approver is missing
4. Count total violations and capture entry IDs

**Expected violations in our test data**:
- Entry 1002: $2500, missing `approver_2` ❌
- Entry 1003: $1500, missing `approver_1` ❌  
- Entry 1004: $3000, both approvers present ✅

---

## Goal of This Lab

Build a **single agent (Evidence Agent)** that:

* Takes a control ID (PAY-002) and period (2024-07)
* Connects to pre-written deterministic checks
* Wraps these checks as **LangChain tools**
* Produces a structured **JSON payload** with:
  * Violations found (count)
  * Entry IDs of violations  
  * Policy summary
  * Population size/criteria tested
  * Concise LLM-generated audit narrative

The output should be professional enough to include in actual audit workpapers.

---

## Notebook Structure

The `sox_copilot_lab.ipynb` notebook is structured in sequential cells:

**Cell 0: Environment Setup**
```python
import os
from dotenv import load_dotenv

load_dotenv()

assert os.getenv("OPENAI_API_KEY"), "❌ OPENAI_API_KEY missing from .env file"

print("✅ Environment variables loaded successfully!")
```

**Cell 1: Data Exploration**
```python
import pandas as pd

df = pd.read_csv("data/journal_entries.csv")

print(f"📊 Loaded {len(df)} journal entries")
print(f"📋 Columns: {list(df.columns)}")
print("\n🔍 First few rows:")
df.head()
```

**Cell 2: Build Agent**
```python
from sox_copilot.evidence_agent import build_evidence_agent

agent = build_evidence_agent()

print("🤖 Agent built successfully!")
```

**Cell 3: Run Agent**
```python
import json 

control_id = "PAY-002"
period = "2024-07"
csv_path = "data/journal_entries.csv"

print("🚀 Running end-to-end evidence agent...")
res = agent.invoke({
    "control_id": control_id,
    "period": period,
    "csv_path": csv_path,
})

raw = res["output"]
report = json.loads(raw)
report
```

**Cell 4: Validation**
```python
required = {"control_id","period","violations_found","violation_entries","policy_summary","population","narrative"}
missing = required - set(report)
assert not missing, f"Missing fields: {missing}"
assert len(report["violation_entries"]) == report["violations_found"]
print("Checks have passed")
```

---

## Supporting Files Overview

Before implementing the tools and agent, you should understand the supporting files that are already provided.

### Deterministic Checks (`sox_copilot/checks.py`)

These functions provide the "boring Python" business logic that powers the PAY-002 control:

```python
import csv
from typing import List, Dict

def load_logs(path: str) -> List[Dict]:
    """Load CSV into a list[dict]; coerce numeric fields as needed."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            # normalize a few fields; students can add more later
            r["amount"] = float(r.get("amount") or 0.0)
            rows.append(r)
        return rows

def filter_payables_over_threshold(logs: List[Dict], amount_threshold: float) -> List[Dict]:
    """Return AP entries with amount > threshold."""
    return [
        r for r in logs
        if r.get("account", "").lower().startswith("accounts payable")
        and float(r.get("amount") or 0) > amount_threshold
    ]

def find_dual_approval_violations(ap_entries: List[Dict]) -> List[Dict]:
    """Return entries missing either approver_1 or approver_2."""
    return [r for r in ap_entries if not (r.get("approver_1") and r.get("approver_2"))]

def summarize_violations(violations: List[Dict]) -> Dict:
    """Return a lightweight summary (count + entry_ids as strings)."""
    return {"count": len(violations), "entry_ids": [str(v.get("entry_id")) for v in violations]}
```

These functions are **deterministic** — they never hallucinate or make mistakes. This is the "hybrid workflow" pattern in action: Python handles precise logic, LLMs handle natural language.

### Configuration File (`sox_copilot/config.py`)

Before implementing the tools and agent, ensure you have the correct configuration in `sox_copilot/config.py`:

```python
# Central knobs for teachability & stability
MODEL_NAME = "gpt-4o-mini"   # OpenAI chat model for both agent & narrative chain
MODEL_TEMP = 0.2             # Narrative chain (slight variance okay)
AGENT_TEMP = 0.0             # Tools-agent should be deterministic-ish
MAX_ITER = 3                 # Bound agent autonomy
AMOUNT_THRESHOLD = 1000.0    # PAY-002 threshold (can be changed in class)
PROMPT_VERSION = "v1"        # Bump when prompt text changes
```

This configuration:
- Uses `gpt-4o-mini` for cost efficiency
- Sets low temperature (0.0) for the agent to make it deterministic
- Allows slightly higher temperature (0.2) for narrative generation
- Limits agent to 3 iterations for safety
- Defines the $1000 threshold for PAY-002 control

---

## Step-by-Step Implementation Guide

### Step 1: Build Your First Tool (1A)

**Goal**: Wrap the deterministic PAY-002 check as a LangChain tool.

**What you're building**:
A single `@tool` decorated function that bridges Python business logic with LLM reasoning.

**File**: `sox_copilot/tools.py`

**Implementation Pattern**:
```python
from typing import Dict, Any
from langchain.tools import tool
from .checks import (
    load_logs,
    filter_payables_over_threshold,
    find_dual_approval_violations,
    summarize_violations,
)
from .config import AMOUNT_THRESHOLD

@tool("run_deterministic_check", return_direct=False)
def run_deterministic_check(control_id: str, period: str, csv_path: str) -> Dict[str, Any]:
    """
    Run a single control check and return ONLY the facts we need in 1A.

        control_id: e.g., "PAY-002" (passed through for future parts)
        period:     e.g., "2024-07"  (passed through for future parts)
        csv_path:   path to journal entries CSV

    Returns:
        {
            "violations_found": int,
            "violation_entries": list[str],
            "population": {"tested_count": int, "criteria": str}
        }
    """

    rows = load_logs(csv_path)

    ap_over = filter_payables_over_threshold(rows, AMOUNT_THRESHOLD)
    violations = find_dual_approval_violations(ap_over)
    summary = summarize_violations(violations)


    return {
        "violations_found": summary["count"],           # How many violations found
        "violation_entries": summary["entry_ids"],     # Which specific entries failed
        "population": {                                # Context about what was tested
            "tested_count": len(ap_over),
            "criteria": f"Accounts Payable entries with amount > {AMOUNT_THRESHOLD:.2f}",
        },
    }
```

**Why this matters**: 
- The `@tool` decorator makes this function callable by an LLM agent
- The docstring is critical — the LLM reads it to understand what the tool does
- Type hints help the LLM understand parameters and return types
- The deterministic logic (load → filter → check → summarize) never hallucinates

**Test it** (in notebook):
```python
from sox_copilot.tools import run_deterministic_check

result = run_deterministic_check.invoke({
    "control_id": "PAY-002",
    "period": "2024-07",
    "csv_path": "data/journal_entries.csv"
})

print(result)
# Should show: violations_found: 2, violation_entries: ['1002', '1003']
```

**✅ Checkpoint**: Can you call the tool directly and get structured JSON with violations?

---

### Step 2: Add Policy Lookup Tool (1B)

**Goal**: Add a tool that provides business context about what the control means.

**File**: `sox_copilot/tools.py`

**Implementation Pattern**:
```python
POLICY_TEXT: Dict[str, str] = {
    "PAY-002": "All payables over $1000 require dual approval.",
    "REV-001": "All revenue recognition entries must be approved by a manager.",
}

@tool("get_policy_summary", return_direct=False)
def get_policy_summary(control_id: str) -> str:
    """
    Return a short policy summary string for a SOX control ID.
    
    This gives the agent business context about what the control is testing.
    Essential for generating meaningful audit narratives that explain violations
    in business terms that stakeholders can understand.
    
    Args:
        control_id: SOX control identifier (e.g., "PAY-002", "REV-001")
        
    Returns:
        Human-readable policy description or "Unknown control" for invalid IDs
    """

    return POLICY_TEXT.get(control_id, "Unknown control.")
```

**Why this matters**:
- Agents need context to write meaningful narratives
- This is a simple lookup, but in production might query a policy database
- Even simple tools benefit from clear docstrings

**Test it**:
```python
from sox_copilot.tools import get_policy_summary

policy = get_policy_summary.invoke({"control_id": "PAY-002"})
print(policy)  # "All payables over $1000 require dual approval."
```

**✅ Checkpoint**: Does the tool return the correct policy text for PAY-002?

---

### Step 3: Add Narrative Generation Tool (1B)

**Goal**: Use an LLM chain to write professional audit narratives from facts.

**File**: `sox_copilot/tools.py`

**Implementation Pattern**:
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .config import MODEL_NAME, MODEL_TEMP

NARRATIVE_SYSTEM_PROMPT = (
    "You write concise audit narratives (<150 words). "
    "Never invent facts. Only use the provided policy summary and facts JSON. "
    "If violations exist, mention the entry IDs and briefly state the issue. "
    "If none, state the control operated effectively. "
    "Tone: neutral, professional, suitable for workpapers."
)
NARRATIVE_USER_PROMPT = (
    "Compose the narrative for control {control_id} in {period}.\n"
    "Policy summary: {policy_summary}\n"
    "Facts JSON: {facts_json}"
)

@tool("generate_narrative", return_direct=False)
def generate_narrative(control_id: str, period: str, policy_summary: str, facts_json: str) -> str:
    """
    Generate a concise audit narrative from provided policy + facts JSON.
    
    This tool demonstrates the "LLM chain" pattern - using a specialized LLM
    for professional writing while the main agent focuses on orchestration.
    
    Args:
        control_id: SOX control being tested (e.g., "PAY-002")
        period: Audit period (e.g., "2024-07")
        policy_summary: Business rule description
        facts_json: Technical violation data as JSON string
        
    Returns:
        Professional audit narrative suitable for workpapers
    """
    llm = ChatOpenAI(model=MODEL_NAME, temperature=MODEL_TEMP, max_tokens=220)

    prompt = ChatPromptTemplate.from_messages([
        ("system", NARRATIVE_SYSTEM_PROMPT),  # Sets AI behavior/personality
        ("user", NARRATIVE_USER_PROMPT),      # The actual task/request
    ])

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({
        "control_id": control_id,
        "period": period,
        "policy_summary": policy_summary,
        "facts_json": facts_json,
    }).strip()
```

**Why this matters**:
- This demonstrates the "LLM chain" pattern — a specialized LLM for one task
- The main agent orchestrates, this tool generates professional prose
- By passing `facts_json` as a string, we force the LLM to use only provided facts

**Test it**:
```python
facts = '{"violations_found": 2, "violation_entries": ["1002", "1003"]}'
narrative = generate_narrative.invoke({
    "control_id": "PAY-002",
    "period": "2024-07",
    "policy_summary": "All payables over $1000 require dual approval.",
    "facts_json": facts
})
print(narrative)
# Should be professional prose mentioning entries 1002 and 1003
```

**✅ Checkpoint**: Does the narrative mention specific entry IDs and avoid hallucinating?

---

### Step 4: Build the Agent Orchestrator (1C)

**Goal**: Create an agent that intelligently calls all tools in the right sequence.

**File**: `sox_copilot/evidence_agent.py`

**Implementation Pattern**:
```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.agents import create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .config import MODEL_NAME, AGENT_TEMP, MAX_ITER
from .tools import run_deterministic_check, get_policy_summary, generate_narrative

SYSTEM_GUIDANCE = f"""
You are a precise audit assistant for SOX controls.
- You MUST call tools to get policy, facts, and the narrative. Do not guess.
- Use counts and entry IDs EXACTLY as returned by tools.
- If a tool returns an error, include the error and do not fabricate results.
- Return ONLY one JSON object (no prose, no backticks).
""".strip()


PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_GUIDANCE),
    ("user",
     """Produce the audit result for control {control_id} in {period} using data at {csv_path}.
Required steps:
1) get_policy_summary(control_id) -> policy_summary
2) run_deterministic_check(control_id, perimod, csv_path) -> facts_json
3) generate_narrative(control_id, period, policy_summary, facts_json=<exact JSON from step 2>) -> narrative

Return ONLY this JSON:
{{
  "control_id": "{control_id}",
  "period": "{period}",
  "violations_found": <int from facts>,
  "violation_entries": <list[str] from facts>,
  "policy_summary": "<string from policy>",
  "population": {{
    "tested_count": <int from facts>,
    "criteria": "<string from facts>"
  }},
  "narrative": "<string from narrative>"
}}
"""),
    MessagesPlaceholder("agent_scratchpad"),
])

def build_evidence_agent() -> AgentExecutor:
    llm = ChatOpenAI(model=MODEL_NAME, temperature=AGENT_TEMP)
    # Adding more tools
    tools = [run_deterministic_check, get_policy_summary, generate_narrative]

    agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=PROMPT)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=MAX_ITER,           # Safety: prevent runaway agents
        handle_parsing_errors=True,       # Graceful error handling
        verbose=True,                    # More verbose output for testing
    )
```

**Why this matters**:
- The prompt provides explicit instructions for tool calling sequence
- `MessagesPlaceholder("agent_scratchpad")` stores tool call history
- `AgentExecutor` handles the loop: think → act → observe → repeat
- `verbose=True` lets you see the agent's reasoning process

**Test it** (in notebook):
```python
from sox_copilot.evidence_agent import build_evidence_agent
import json 

agent = build_evidence_agent()

control_id = "PAY-002"
period = "2024-07"
csv_path = "data/journal_entries.csv"

print("🚀 Running end-to-end evidence agent...")
res = agent.invoke({
    "control_id": control_id,
    "period": period,
    "csv_path": csv_path,
})

raw = res["output"]
report = json.loads(raw)
report
```

**✅ Checkpoint**: 
- Does the agent call all three tools?
- Is the final JSON properly structured?
- Do violation counts match entry list length?

---

### Step 5: Validate Your Output

**File**: Notebook validation cell

**Validation checks**:
```python
import json

# Parse the output
report = json.loads(result["output"])

# Check required fields
required = {"control_id","period","violations_found","violation_entries","policy_summary","population","narrative"}
missing = required - set(report)
assert not missing, f"Missing fields: {missing}"

# Check internal consistency
assert len(report["violation_entries"]) == report["violations_found"]

print("Checks have passed")
```

**Expected output for PAY-002**:
```json
{
  "control_id": "PAY-002",
  "period": "2024-07",
  "violations_found": 2,
  "violation_entries": ["1002", "1003"],
  "policy_summary": "All payables over $1000 require dual approval.",
  "population": {
    "tested_count": 3,
    "criteria": "Accounts Payable entries with amount > 1000.00"
  },
  "narrative": "Testing of PAY-002 for July 2024 identified 2 violations out of 3 payable entries exceeding $1000. Entry 1002 ($2500) is missing approver_2, and entry 1003 ($1500) is missing approver_1. These exceptions indicate a breakdown in the dual approval control."
}
```

---


## Common Pitfalls

### Important Note: Typo in Solution Code
**Note**: The solution code contains an intentional typo in `evidence_agent.py` line 25: `perimod` instead of `period`. This is present in the reference solution to demonstrate that even production code can have minor issues that still function (the LLM agent may still work despite this typo). You can either keep it as-is to match the solution exactly, or fix it in your implementation.

### Pitfall 1: Agent Hallucinating Violation Counts
**Problem**: Agent returns wrong number of violations

**Cause**: Agent isn't using tool results; it's guessing

**Solution**: 
- Make prompt very explicit: "Use counts EXACTLY as returned by tools"
- Lower agent temperature to 0
- Add validation that checks tool call history

### Pitfall 2: JSON Formatting Issues
**Problem**: Output includes markdown backticks like `\`\`\`json` or extra prose

**Cause**: LLM defaults to markdown code block formatting

**Solution**:
- Prompt must explicitly say "Return ONLY one JSON object (no prose, no backticks)"
- Use `handle_parsing_errors=True` to retry on parse failures
- Consider structured output mode (OpenAI's JSON mode)

### Pitfall 3: Tool Not Being Called
**Problem**: Agent skips calling a tool

**Cause**: Tool signature or docstring is unclear

**Solution**:
- Write clear, specific docstrings that explain what the tool does
- Include type hints for all parameters
- Test tool directly before adding to agent

### Pitfall 4: Narrative Inventing Facts
**Problem**: Narrative mentions violations that don't exist

**Cause**: `generate_narrative` LLM isn't constrained to use only provided facts

**Solution**:
- Pass `facts_json` as a string to force LLM to reference it
- System prompt must say "Never invent facts"
- Lower narrative LLM temperature to 0.1-0.3

### Pitfall 5: Missing Dependencies
**Problem**: Import errors or missing packages

**Cause**: Environment not set up correctly

**Solution**:
```bash
cd modules/develop-a-single-agent-system/solution
pipenv install
pipenv shell
```

### Pitfall 6: API Key Issues
**Problem**: OpenAI API errors

**Cause**: Missing or invalid `OPENAI_API_KEY`

**Solution**:
```bash
# Check .env file exists
cat .env

# Verify key is loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```
---

## Deliverables

* `sox_copilot/evidence_agent.py` - The main agent orchestrator
* `sox_copilot/tools.py` - LangChain tools for policy lookup, checks, and narrative generation
* `sox_copilot/config.py` - Configuration constants for models and thresholds
* `sox_copilot/checks.py` - Deterministic business logic functions (provided)
* `sox_copilot_lab.ipynb` - Jupyter notebook with test harness and validation
* `.env` - Environment variables (OPENAI_API_KEY)

---
