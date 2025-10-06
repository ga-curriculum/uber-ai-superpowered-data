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
from typing import Dict, Any
from langchain.tools import tool
from .checks import load_logs, filter_payables_over_threshold, 
                    find_dual_approval_violations, summarize_violations
from .config import AMOUNT_THRESHOLD

@tool("recount_and_compare", return_direct=False)
def recount_and_compare(evidence_json: str, csv_path: str) -> Dict[str, Any]:
    """
    Independently recount violations and compare to the submitted evidence.
    
    This is a VALIDATION tool - it doesn't trust the evidence, it verifies it.
    
    Args:
        evidence_json: JSON string of the evidence payload to validate
        csv_path: Path to the original CSV data
        
    Returns:
        {
          "evidence_valid": bool,
          "issues": list[str],
          "recount": {"violations_found": int, "violation_entries": list[str]},
          "submitted": {"violations_found": int, "violation_entries": list[str]}
        }
    """
    # Parse the evidence that was submitted
    evidence = json.loads(evidence_json)
    
    # Extract what the Evidence Agent claimed
    submitted_count = evidence.get("violations_found", 0)
    submitted_entries = set(evidence.get("violation_entries", []))
    
    # INDEPENDENT RECOUNT: Same logic as Evidence Agent, but fresh
    rows = load_logs(csv_path)
    ap_over = filter_payables_over_threshold(rows, AMOUNT_THRESHOLD)
    violations = find_dual_approval_violations(ap_over)
    summary = summarize_violations(violations)
    
    recount_count = summary["count"]
    recount_entries = set(summary["entry_ids"])
    
    # COMPARISON LOGIC: Find discrepancies
    issues = []
    
    # Parity check: Does the count match the list length in submitted evidence?
    if submitted_count != len(evidence.get("violation_entries", [])):
        issues.append(
            f"Parity issue: violations_found ({submitted_count}) != "
            f"len(violation_entries) ({len(evidence.get('violation_entries', []))})"
        )
    
    # Count comparison: Does our recount match their count?
    if recount_count != submitted_count:
        issues.append(
            f"Count mismatch: Recount found {recount_count}, "
            f"evidence claims {submitted_count}"
        )
    
    # Entry ID comparison: Are the violation lists identical?
    missing_in_evidence = recount_entries - submitted_entries
    extra_in_evidence = submitted_entries - recount_entries
    
    if missing_in_evidence:
        issues.append(
            f"Missing violations in evidence: {sorted(missing_in_evidence)}"
        )
    if extra_in_evidence:
        issues.append(
            f"Extra violations in evidence: {sorted(extra_in_evidence)}"
        )
    
    # Determine validity
    evidence_valid = len(issues) == 0
    
    return {
        "evidence_valid": evidence_valid,
        "issues": issues,
        "recount": {
            "violations_found": recount_count,
            "violation_entries": sorted(recount_entries),
        },
        "submitted": {
            "violations_found": submitted_count,
            "violation_entries": sorted(submitted_entries),
        },
    }
```

**Why this matters**:
- **Independent Verification**: Doesn't trust the Evidence Agent; recalculates everything
- **Comprehensive Validation**: Checks both counts AND entry IDs
- **Parity Checks**: Catches internal inconsistencies in the evidence itself
- **Detailed Issues**: Provides specific discrepancies for debugging

**Test it**:
```python
from sox_copilot.tools import recount_and_compare

# Create a valid evidence JSON (from Part 1)
evidence = json.dumps({
    "control_id": "PAY-002",
    "period": "2024-07",
    "violations_found": 2,
    "violation_entries": ["1002", "1003"],
    # ... other fields
})

result = recount_and_compare.invoke({
    "evidence_json": evidence,
    "csv_path": "data/journal_entries.csv"
})

print(result)
# Should show: evidence_valid: True, issues: []

# Test with INVALID evidence
bad_evidence = json.dumps({
    "violations_found": 3,  # Wrong count!
    "violation_entries": ["1002", "1003"]
})

result2 = recount_and_compare.invoke({
    "evidence_json": bad_evidence,
    "csv_path": "data/journal_entries.csv"
})

print(result2)
# Should show: evidence_valid: False, issues: ["Count mismatch: ..."]
```

**✅ Checkpoint**: 
- Does the tool catch count mismatches?
- Does it detect missing or extra violation entries?
- Does it flag parity issues (count != list length)?

---

### Step 2: Build the Review Notes Generator Tool

**Goal**: Use an LLM to write professional reviewer notes based on validation results.

**File**: `sox_copilot/tools.py`

**Implementation Pattern**:
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .config import MODEL_NAME, MODEL_TEMP

REVIEW_NOTES_SYSTEM_PROMPT = (
    "You write concise reviewer notes (<100 words) for audit workpapers. "
    "Based on validation results, state whether evidence is valid or not. "
    "If valid, briefly confirm findings match. "
    "If invalid, list specific issues found. "
    "Tone: professional, factual, suitable for senior reviewer signature."
)

@tool("generate_review_notes", return_direct=False)
def generate_review_notes(control_id: str, period: str, 
                          validation_results: str) -> str:
    """
    Generate professional reviewer notes from validation results.
    
    Args:
        control_id: e.g., "PAY-002"
        period: e.g., "2024-07"
        validation_results: JSON string from recount_and_compare tool
        
    Returns:
        Professional review notes suitable for audit workpapers
    """
    llm = ChatOpenAI(model=MODEL_NAME, temperature=MODEL_TEMP, max_tokens=150)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", REVIEW_NOTES_SYSTEM_PROMPT),
        ("user", "Write reviewer notes for control {control_id} in {period}.\n"
                 "Validation results: {validation_results}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({
        "control_id": control_id,
        "period": period,
        "validation_results": validation_results,
    }).strip()
```

**Why this matters**:
- **Professional Writing**: LLM converts technical validation results to audit language
- **Constrained Generation**: Short notes focused only on validation outcomes
- **Separation of Logic**: Validation is deterministic, writing is generative

**Test it**:
```python
from sox_copilot.tools import generate_review_notes

validation = json.dumps({
    "evidence_valid": True,
    "issues": [],
    "recount": {"violations_found": 2}
})

notes = generate_review_notes.invoke({
    "control_id": "PAY-002",
    "period": "2024-07",
    "validation_results": validation
})

print(notes)
# Should say something like: "Evidence validated. Independent recount confirms..."
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

REVIEWER_SYSTEM_GUIDANCE = """
You are an independent audit reviewer for SOX controls.
- You MUST call tools to validate evidence. Never trust submitted evidence without verification.
- First, recount violations independently using recount_and_compare.
- Then, generate professional review notes using generate_review_notes.
- Return ONLY one JSON object (no prose, no backticks).
""".strip()

REVIEWER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", REVIEWER_SYSTEM_GUIDANCE),
    ("user",
     """Review the submitted evidence for control {control_id} in {period}.

Evidence to review: {evidence_json}
CSV path for recount: {csv_path}

Required steps:
1) recount_and_compare(evidence_json, csv_path) -> validation_results
2) generate_review_notes(control_id, period, validation_results=<JSON from step 1>) -> notes

Return ONLY this JSON:
{{
  "reviewed_control_id": "{control_id}",
  "period": "{period}",
  "evidence_valid": <bool from validation>,
  "issues": <list[str] from validation>,
  "review_notes": "<string from notes>"
}}"""),
    MessagesPlaceholder("agent_scratchpad"),
])

def build_reviewer_agent() -> AgentExecutor:
    llm = ChatOpenAI(model=MODEL_NAME, temperature=AGENT_TEMP)
    tools = [recount_and_compare, generate_review_notes]
    
    agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=REVIEWER_PROMPT)
    
    return AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=MAX_ITER,
        handle_parsing_errors=True,
        verbose=True,
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

# Step 1: Generate evidence
evidence_agent = build_evidence_agent()
evidence_result = evidence_agent.invoke({
    "control_id": "PAY-002",
    "period": "2024-07",
    "csv_path": "data/journal_entries.csv"
})
evidence_json = evidence_result["output"]

# Step 2: Review the evidence
reviewer_agent = build_reviewer_agent()
review_result = reviewer_agent.invoke({
    "control_id": "PAY-002",
    "period": "2024-07",
    "evidence_json": evidence_json,
    "csv_path": "data/journal_entries.csv"
})

review = json.loads(review_result["output"])
print(json.dumps(review, indent=2))
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
# Use real Evidence Agent output
evidence_agent = build_evidence_agent()
evidence = evidence_agent.invoke({
    "control_id": "PAY-002",
    "period": "2024-07",
    "csv_path": "data/journal_entries.csv"
})

reviewer_agent = build_reviewer_agent()
review = reviewer_agent.invoke({
    "control_id": "PAY-002",
    "period": "2024-07",
    "evidence_json": evidence["output"],
    "csv_path": "data/journal_entries.csv"
})

review_payload = json.loads(review["output"])
assert review_payload["evidence_valid"] == True
assert len(review_payload["issues"]) == 0
print("✅ Valid evidence passed review")
```

**Test Case 2: Invalid Evidence (Simulated Hallucination)**
```python
# Simulate an Evidence Agent that hallucinated
fake_evidence = json.dumps({
    "control_id": "PAY-002",
    "period": "2024-07",
    "violations_found": 5,  # Wrong! Should be 2
    "violation_entries": ["1002", "1003", "9999"],  # Entry 9999 doesn't exist
    "policy_summary": "All payables over $1000 require dual approval.",
    "population": {"tested_count": 3, "criteria": "..."},
    "narrative": "Found 5 violations..."
})

reviewer_agent = build_reviewer_agent()
review = reviewer_agent.invoke({
    "control_id": "PAY-002",
    "period": "2024-07",
    "evidence_json": fake_evidence,
    "csv_path": "data/journal_entries.csv"
})

review_payload = json.loads(review["output"])
assert review_payload["evidence_valid"] == False
assert len(review_payload["issues"]) > 0
print("✅ Invalid evidence caught by reviewer")
print("Issues found:", review_payload["issues"])
```

**Expected Issues Detected**:
- "Count mismatch: Recount found 2, evidence claims 5"
- "Extra violations in evidence: ['9999']"

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

### Pitfall 3: Set Comparison Issues
**Problem**: Comparison logic doesn't handle duplicates or ordering

**Solution**:
```python
# Convert to sets for proper comparison
recount_entries = set(summary["entry_ids"])
submitted_entries = set(evidence.get("violation_entries", []))

# Use set operations
missing = recount_entries - submitted_entries
extra = submitted_entries - recount_entries
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

## Deliverables

* `sox_copilot/reviewer_agent.py` — The main agent orchestrator for review
* `sox_copilot/tools.py` — Reviewer tools: `recount_and_compare`, `generate_review_notes`
* Notebook section: Part 2 — Reviewer Agent demonstration
