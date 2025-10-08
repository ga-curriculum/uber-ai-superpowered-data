<h1>
  <span class="prefix">

  ![](/assets/ga-logo.png)

  </span> 
  <span class="headline">Building the Reviewer Agent</span>
</h1>

## About

Goal: Add a second, independent Reviewer Agent that validates the Evidence Agent’s outputs.

The challenge is not just building it in isolation, but ensuring it integrates and interacts effectively with the agent from Day 2 to create a complete, functioning system.

**Key takeaway:** Independence + structured validation = *trustable evidence*.

## Module Objectives
- Design the workflow for a 2-agent system.
- Develop the second agent to effectively interact with the agent created on Day 2.
- Implement and test the data handoff between the two agents to create a fully integrated system.

# Building the Reviewer Agent

## Background

In Part 2, you extend the **SOX Audit Copilot** into a multi-agent workflow by adding a **Reviewer Agent**. This agent independently validates the evidence produced by the Evidence Agent to increase assurance and reduce the risk of hallucinations or logic mistakes. The Reviewer Agent will:

1. Recount violations deterministically from the source data
2. Compare counts and entry IDs with the submitted evidence
3. Flag inconsistencies in a structured way
4. Write concise, professional reviewer notes suitable for audit workpapers

You'll combine deterministic validation logic with an LLM that focuses solely on writing short reviewer notes from facts.

---

## Prerequisites

**Required Knowledge:**
- Completion of Part 1 (Evidence Agent)
- Understanding of multi-agent workflows
- Familiarity with validation patterns and data comparison logic


**Key Concepts to Understand:**
- **Independent Validation**: The Reviewer Agent doesn't trust the Evidence Agent; it recounts everything
- **Parity Checks**: Ensuring internal consistency (e.g., count matches list length)
- **Comparison Logic**: Deterministic set operations to find discrepancies
- **Separation of Concerns**: Evidence generation vs. evidence validation

---

## What Does the Reviewer Agent Do?

The **Reviewer Agent** acts like an independent senior reviewer who:

1. Receives the submitted evidence payload (JSON string) for a given control and period
2. Loads the same journal entries CSV used to generate that evidence
3. Independently recounts violations for the tested control
4. Performs parity checks (e.g., `violations_found` equals the length of `violation_entries`)
5. Compares the independent recount to the submitted evidence
6. Produces a concise review note suitable for inclusion in workpapers

The agent orchestrates these steps automatically, calling specialized tools to:
- Recount and compare the evidence to the CSV (`recount_and_compare`)
- Generate a short reviewer note (`generate_review_notes`)

---

## Architecture Overview

Here's how the multi-agent workflow fits together:

```
┌──────────────────────────────────────────────────────────────┐
│                    PART 1: EVIDENCE AGENT                     │
│                                                               │
│  CSV → Tools → Evidence JSON                                 │
│                     │                                         │
│                     ▼                                         │
│  {                                                            │
│    "violations_found": 2,                                     │
│    "violation_entries": ["1002", "1003"],                     │
│    ...                                                        │
│  }                                                            │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            │ Evidence JSON passed as string
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    PART 2: REVIEWER AGENT                     │
│                   (Independent Validator)                     │
│                                                               │
│  "Review this evidence for PAY-002..."                       │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Agent decides which validation tools to call           │  │
│  └────────────────────────────────────────────────────────┘  │
│                         │                                     │
│         ┌───────────────┴──────────────┐                     │
│         ▼                               ▼                     │
│  ┌──────────────────┐          ┌─────────────────┐          │
│  │  Recount Tool    │          │  Review Notes   │          │
│  │  (Deterministic) │          │   Generator     │          │
│  │                  │          │   (LLM Chain)   │          │
│  └──────────────────┘          └─────────────────┘          │
│         │                               │                     │
│         ▼                               ▼                     │
│   CSV → Fresh                     "Evidence validated.        │
│   recount of                       2 violations found         │
│   violations                       match submitted            │
│         │                          evidence."                 │
│         ▼                                                     │
│  Compare to Evidence JSON                                     │
│  - Match? ✅                                                  │
│  - Mismatch? ❌ (flag issues)                                │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Final Review Payload                       │  │
│  │  {                                                      │  │
│  │    "evidence_valid": true,                              │  │
│  │    "issues": [],                                        │  │
│  │    "review_notes": "..."                                │  │
│  │  }                                                      │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

**Key Architectural Patterns:**

1. **Independent Validation**: 
   - Reviewer Agent doesn't trust Evidence Agent's calculations
   - Always recounts from source data
   - Uses same deterministic checks but compares results

2. **Data Contracts**:
   - Evidence Agent produces structured JSON
   - Reviewer Agent consumes and validates that JSON
   - Clear input/output schema between agents

3. **Separation of Concerns**:
   - Evidence Agent: Generate findings
   - Reviewer Agent: Validate findings
   - Each agent has specialized tools for its role

4. **Multi-Agent Workflow**:
   ```
   User → Evidence Agent → Evidence JSON → Reviewer Agent → Review JSON
   ```

**Why This Matters:**
- Catches hallucinations (LLM making up violation counts)
- Detects logic errors (bugs in check functions)
- Provides audit trail (independent verification)
- Mirrors real audit processes (preparer vs. reviewer separation)

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

**What the reviewer re-check does**:
1. Filter to Accounts Payable entries > $1000
2. Recompute whether both `approver_1` AND `approver_2` are present
3. Recount violations and collect entry IDs
4. Compare recount with the submitted evidence payload
5. Flag parity issues (e.g., mismatched counts vs. IDs)

**Expected violations in our test data**:
- Entry 1002: $2500, missing `approver_2` ❌
- Entry 1003: $1500, missing `approver_1` ❌  
- Entry 1004: $3000, both approvers present ✅

---

## Goal of This Lab

Build a **second agent (Reviewer Agent)** that:

* Takes the submitted evidence JSON and the CSV path
* Independently recounts violations for the control under test
* Compares the recount to the evidence and records issues, if any
* Generates a short LLM-written review note
* Produces a structured **JSON payload** with:
  * `reviewed_control_id`
  * `period`
  * `evidence_valid` (true/false)
  * `issues` (list of strings)
  * `review_notes` (concise narrative)

The output should be professional and auditable, clearly stating whether the evidence appears consistent with the source data.

---

## Notebook Structure

The `sox_copilot_lab.ipynb` notebook extends Part 1 with additional cells:

**Cells 0-4: Evidence Agent** (from Part 1)
- Environment setup
- Data exploration
- Build and run Evidence Agent
- Validation

**Cell 5: Build Reviewer Agent**
```python
from sox_copilot.reviewer_agent import build_reviewer_agent
import json

# Ensure we have a JSON string for the reviewer input
evidence_json = json.dumps(report)  # or use `raw` directly if you kept it

reviewer = build_reviewer_agent()
print("🤖 Agent built successfully!")
```

**Cell 6: Run Reviewer Agent**
```python
print("🧮 Running reviewer agent...")
rev_res = reviewer.invoke({
    "evidence": evidence_json,
    "csv_path": "data/journal_entries.csv",
})

rev_raw = rev_res["output"]  # JSON string
print(rev_raw)

# Quick checks
rev = json.loads(rev_raw)
assert set(rev) == {"reviewed_control_id", "period", "evidence_valid", "issues", "review_notes"}
print("✅ Reviewer output shape OK")
rev
```

**Cell 7: Test Valid Evidence**
```python
print("✅ Test Case: Valid Evidence")
print(f"Evidence valid: {rev['evidence_valid']}")
print(f"Issues found: {rev['issues']}")

assert rev['evidence_valid'] == True, "Valid evidence should pass review"
assert len(rev['issues']) == 0, "Valid evidence should have no issues"
print("✅ Valid evidence test PASSED\n")
```

**Cell 8: Empty** (for student experimentation with invalid evidence)

---

## Step-by-Step Implementation Guide

### Step 1: Build the Recount and Compare Tool

**Goal**: Create a tool that independently recounts violations and compares to submitted evidence.

**What you're building**:
A deterministic validation tool that performs three functions:
1. Parse the evidence JSON
2. Recount violations from the CSV (same logic as Evidence Agent)
3. Compare recount to evidence and flag discrepancies

**File**: `sox_copilot/tools.py`

**Implementation Pattern**:
```python
import json
from typing import Dict, Any, List
from langchain.tools import tool
from .checks import count_pay002_violations_from_csv
from .config import AMOUNT_THRESHOLD

@tool("recount_and_compare", return_direct=False)
def recount_and_compare(csv_path: str, evidence_json: str) -> Dict[str, Any]:
    """
    Recount violations independently and compare against the provided evidence payload.

    Args:
        csv_path: Path to the source CSV used to generate evidence
        evidence_json: Evidence payload as a JSON string (dict with control_id, period,
                       violations_found, violation_entries, population, narrative, ...)

    Returns:
        {
          "reviewed_control_id": str,
          "period": str,
          "evidence_valid": bool,
          "issues": list[str]
        }
    """
    issues: List[str] = []

    # Parse the incoming JSON string
    try:
        ev = json.loads(evidence_json)
    except Exception:
        return {
            "reviewed_control_id": "UNKNOWN",
            "period": "UNKNOWN",
            "evidence_valid": False,
            "issues": ["invalid_evidence_json"],
        }

    control_id = ev.get("control_id")
    period = ev.get("period", "UNKNOWN")

    # Basic presence checks
    if control_id is None:
        issues.append("missing_control_id")
    if "violations_found" not in ev:
        issues.append("missing_violations_found")
    if "violation_entries" not in ev:
        issues.append("missing_violation_entries")

    # Parity check: count must match list length
    try:
        if ev.get("violations_found") != len(ev.get("violation_entries", [])):
            issues.append("violations_found != len(violation_entries)")
    except Exception:
        issues.append("failed_parity_check")

    # Independent recount (lab supports PAY-002 only)
    if control_id == "PAY-002":
        recount = count_pay002_violations_from_csv(csv_path, AMOUNT_THRESHOLD)
        if recount != ev.get("violations_found"):
            issues.append(
                f"independent_recount={recount} != evidence_count={ev.get('violations_found')}"
            )
    else:
        issues.append(f"unsupported_control_id={control_id}")

    return {
        "reviewed_control_id": control_id or "UNKNOWN",
        "period": period,
        "evidence_valid": len(issues) == 0,
        "issues": issues,
    }
```

**Why this matters**:
- **Independent Verification**: Doesn't trust the Evidence Agent; recalculates everything from source
- **Simplified Validation**: Focuses on count comparison and parity checks (not detailed entry ID comparison)
- **Error Handling**: Gracefully handles malformed JSON and missing fields
- **Control-Specific Logic**: Uses helper function `count_pay002_violations_from_csv` for focused recounting

**Test it**:
```python
from sox_copilot.tools import recount_and_compare
import json

# Create a valid evidence JSON (from Part 1)
evidence = json.dumps({
    "control_id": "PAY-002",
    "period": "2024-07",
    "violations_found": 2,
    "violation_entries": ["1002", "1003"],
    "policy_summary": "All payables over $1000 require dual approval.",
    "population": {"tested_count": 3, "criteria": "..."},
    "narrative": "..."
})

result = recount_and_compare.invoke({
    "csv_path": "data/journal_entries.csv",
    "evidence_json": evidence
})

print(result)
# Should show: evidence_valid: True, issues: []

# Test with INVALID evidence
bad_evidence = json.dumps({
    "control_id": "PAY-002",
    "period": "2024-07",
    "violations_found": 3,  # Wrong count!
    "violation_entries": ["1002", "1003"]
})

result2 = recount_and_compare.invoke({
    "csv_path": "data/journal_entries.csv",
    "evidence_json": bad_evidence
})

print(result2)
# Should show: evidence_valid: False, issues: ["independent_recount=2 != evidence_count=3"]
```

**✅ Checkpoint**: 
- Does the tool catch count mismatches?
- Does it flag parity issues (count != list length)?
- Does it handle missing fields gracefully?

---

### Step 2: Build the Review Notes Generator Tool

**Goal**: Use an LLM to write professional reviewer notes based on validation results.

**File**: `sox_copilot/tools.py`

**Implementation Pattern**:
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import List
from .config import MODEL_NAME, MODEL_TEMP

REVIEW_NOTES_SYSTEM_PROMPT = (
    "You are a SOX reviewer. Be concise, neutral, and actionable. "
    "Never invent facts. Write <= 100 words suitable for workpapers."
)

REVIEW_NOTES_USER_PROMPT = (
    "Write reviewer notes for the evidence outcome below.\n"
    "Control ID: {control_id}\n"
    "Period: {period}\n"
    "Evidence valid: {evidence_valid}\n"
    "Issues: {issues}\n"
    "Guidance: If 'Issues' is 'None', say the evidence appears consistent. "
    "Avoid extra commentary."
)

@tool("generate_review_notes", return_direct=False)
def generate_review_notes(control_id: str, period: str, evidence_valid: bool, issues: List[str]) -> str:
    """Generate concise reviewer notes from the comparison result."""
    llm = ChatOpenAI(model=MODEL_NAME, temperature=MODEL_TEMP, max_tokens=140)
    prompt = ChatPromptTemplate.from_messages([
        ("system", REVIEW_NOTES_SYSTEM_PROMPT),
        ("user", REVIEW_NOTES_USER_PROMPT),
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({
        "control_id": control_id,
        "period": period,
        "evidence_valid": str(evidence_valid),              # keep it explicit for the prompt
        "issues": ", ".join(issues) if issues else "None",  # compact list -> string
    }).strip()
```

**Why this matters**:
- **Professional Writing**: LLM converts technical validation results to audit language
- **Explicit Parameters**: Takes structured data (not JSON string) for clearer interface
- **Constrained Generation**: Short notes focused only on validation outcomes
- **Separation of Logic**: Validation is deterministic, writing is generative

**Test it**:
```python
from sox_copilot.tools import generate_review_notes

# Test with valid evidence
notes = generate_review_notes.invoke({
    "control_id": "PAY-002",
    "period": "2024-07",
    "evidence_valid": True,
    "issues": []
})

print(notes)
# Should say something like: "Evidence appears consistent with source data..."

# Test with invalid evidence
notes2 = generate_review_notes.invoke({
    "control_id": "PAY-002",
    "period": "2024-07",
    "evidence_valid": False,
    "issues": ["independent_recount=2 != evidence_count=3"]
})

print(notes2)
# Should mention the specific mismatch found
```

**✅ Checkpoint**: Do the notes clearly state whether evidence is valid or invalid?

---

### Step 3: Build the Reviewer Agent

**Goal**: Create an agent that orchestrates validation tools and produces a review payload.

**File**: `sox_copilot/reviewer_agent.py`

**Implementation Pattern**:
```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .config import MODEL_NAME, AGENT_TEMP, MAX_ITER
from .tools import recount_and_compare, generate_review_notes

SYSTEM_GUIDANCE = f"""
You are a SOX Reviewer Agent.
- NEVER invent facts; you must call tools to re-check evidence deterministically.
- Use tool outputs EXACTLY as returned for counts/IDs/flags.
- When calling recount_and_compare, pass the EXACT evidence JSON string you received.
- Write concise, professional review notes (<100 words); no extra commentary.
- Final answer must be a single JSON object only (no extra text, no backticks).
""".strip()

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_GUIDANCE),
    ("user",
     """Review this submitted evidence against the source CSV.

Evidence (JSON string):
{evidence}

CSV path:
{csv_path}

Use tools to:
1) recount_and_compare(csv_path, evidence_json=<the EXACT string above>) -> comparison
2) generate_review_notes(control_id=<from comparison>, period=<from comparison>,
   evidence_valid=<from comparison>, issues=<from comparison>) -> review_notes

Return ONLY this JSON:
{{
  "reviewed_control_id": "<from comparison>",
  "period": "<from comparison>",
  "evidence_valid": true|false,
  "issues": <list of strings from comparison>,
  "review_notes": "<short narrative from tool>"
}}
"""),
    MessagesPlaceholder("agent_scratchpad"),
])

def build_reviewer_agent() -> AgentExecutor:
    llm = ChatOpenAI(model=MODEL_NAME, temperature=AGENT_TEMP)
    tools = [recount_and_compare, generate_review_notes]
    agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=PROMPT)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=MAX_ITER,
        verbose=True,
        handle_parsing_errors=True,
    )
```

**Why this matters**:
- **Multi-Agent Pattern**: Evidence Agent → Reviewer Agent (separation of duties)
- **Independent Verification**: Reviewer doesn't trust evidence, validates everything
- **Clear Workflow**: Explicit tool calling sequence in prompt

**Test it** (in notebook):
```python
from sox_copilot.evidence_agent import build_evidence_agent
from sox_copilot.reviewer_agent import build_reviewer_agent
import json

# Step 1: Generate evidence (from previous lab)
evidence_agent = build_evidence_agent()
res = evidence_agent.invoke({
    "control_id": "PAY-002",
    "period": "2024-07",
    "csv_path": "data/journal_entries.csv"
})

raw = res["output"]
report = json.loads(raw)

# Step 2: Prepare evidence for review
evidence_json = json.dumps(report)

reviewer = build_reviewer_agent()
print("🤖 Agent built successfully!")

# Step 3: Run reviewer
print("🧮 Running reviewer agent...")
rev_res = reviewer.invoke({
    "evidence": evidence_json,
    "csv_path": "data/journal_entries.csv",
})

rev_raw = rev_res["output"]
print(rev_raw)

# Step 4: Validate output
rev = json.loads(rev_raw)
assert set(rev) == {"reviewed_control_id", "period", "evidence_valid", "issues", "review_notes"}
print("✅ Reviewer output shape OK")
rev
```

**✅ Checkpoint**:
- Does the Reviewer Agent call both validation tools?
- Is `evidence_valid` set correctly?
- Do the review notes make sense?

---

### Step 4: Test the Multi-Agent Workflow

**Goal**: Validate that Evidence → Review workflow catches errors.

**Test Case 1: Valid Evidence**
```python
# Test Case: Valid Evidence (from our earlier Evidence Agent run)
print("✅ Test Case: Valid Evidence")
print(f"Evidence valid: {rev['evidence_valid']}")
print(f"Issues found: {rev['issues']}")

assert rev['evidence_valid'] == True, "Valid evidence should pass review"
assert len(rev['issues']) == 0, "Valid evidence should have no issues"
print("✅ Valid evidence test PASSED\n")
```

**Test Case 2: Invalid Evidence (Simulated Hallucination)**
```python
# Test Case 2: Invalid Evidence (simulated bad count)
print("🔍 Test Case: Invalid Evidence")
fake_evidence = json.dumps({
    "control_id": "PAY-002",
    "period": "2024-07",
    "violations_found": 5,  # Wrong! Should be 2
    "violation_entries": ["1002", "1003"],  # Count mismatch
    "policy_summary": "All payables over $1000 require dual approval.",
    "population": {"tested_count": 3, "criteria": "..."},
    "narrative": "Found 5 violations..."
})

rev_res_bad = reviewer.invoke({
    "evidence": fake_evidence,
    "csv_path": "data/journal_entries.csv",
})

rev_bad = json.loads(rev_res_bad["output"])
print(f"Evidence valid: {rev_bad['evidence_valid']}")
print(f"Issues found: {rev_bad['issues']}")

assert rev_bad['evidence_valid'] == False, "Invalid evidence should fail review"
assert len(rev_bad['issues']) > 0, "Invalid evidence should have issues"
print("✅ Invalid evidence test PASSED")
```

**Expected Issues Detected**:
- `"violations_found != len(violation_entries)"` (parity issue)
- `"independent_recount=2 != evidence_count=5"` (count mismatch)

---



## Common Pitfalls

### Pitfall 1: Reviewer Trusts Evidence Without Validation
**Problem**: Reviewer just echoes back the evidence without recounting

**Cause**: Not calling `recount_and_compare` or not using its results

**Solution**:
- Prompt must explicitly say "You MUST call tools to validate"
- Check agent tool call history to ensure validation tool was invoked
- Add assertions that validation results were used in final payload

### Pitfall 2: Parity Checks Not Implemented
**Problem**: Missing internal consistency checks

**Example Bad Evidence**:
```json
{
  "violations_found": 5,
  "violation_entries": ["1002", "1003"]  # Length is 2, not 5!
}
```

**Solution**:
- Add check: `if submitted_count != len(submitted_entries)`
- This catches bugs in the Evidence Agent itself

### Pitfall 3: Parameter Order Issues
**Problem**: Calling `recount_and_compare` with wrong parameter order

**Solution**:
```python
# Correct order: csv_path first, then evidence_json
result = recount_and_compare.invoke({
    "csv_path": "data/journal_entries.csv",
    "evidence_json": evidence_json
})

# NOT: evidence_json first (this is wrong)
```

### Pitfall 4: Not Testing with Invalid Evidence
**Problem**: Only testing the happy path (valid evidence)

**Solution**:
- Create test cases with wrong counts, missing entries, extra entries
- Simulate hallucinations to ensure reviewer catches them
- Test parity issues (count != length)

### Pitfall 5: Review Notes Too Generic
**Problem**: Notes don't mention specific issues found

**Solution**:
- Pass full validation results to review notes generator
- Ensure prompt asks LLM to mention specific discrepancies
- Lower temperature for more factual output

---

## Supporting Files

### Updated `checks.py`
The solution adds a new helper function for the reviewer:

```python
def count_pay002_violations_from_csv(csv_path: str, amount_threshold: float) -> int:
    """Independent recount for PAY-002 given a CSV path."""
    rows = load_logs(csv_path)
    ap_over = filter_payables_over_threshold(rows, amount_threshold)
    violations = find_dual_approval_violations(ap_over)
    return len(violations)
```

This provides a focused recount function that the reviewer tool can call without repeating all the logic.

---

## Deliverables

* `sox_copilot/reviewer_agent.py` — The main agent orchestrator for review
* `sox_copilot/tools.py` — Reviewer tools: `recount_and_compare`, `generate_review_notes`
* `sox_copilot/checks.py` — Updated with `count_pay002_violations_from_csv` helper function
* Notebook section: Part 2 — Reviewer Agent demonstration (Cells 5-8)
