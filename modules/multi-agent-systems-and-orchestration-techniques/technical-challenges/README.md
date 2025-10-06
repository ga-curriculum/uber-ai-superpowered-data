<h1>
  <span>

  ![alt text](./assets/ga-logo.png)
  
  </span>
  <span class="subhead">Technical Challenges</span>
</h1>

**Learning objective:** Identify challenges in multi-agent workflows by examining concrete failure cases in state management, context handoffs, and error propagation. Develop debugging strategies for each challenge type.

---

## Overview

When multi-agent systems fail, it's rarely because "the LLM gave a bad answer."

The failures happen in the **engineering layer**:
- **Handoffs:** Passing structured data between agents
- **State management:** Preserving context as tasks progress
- **Error propagation:** How one agent's failure infects downstream agents
- **Auditability:** Ensuring every decision can be traced and explained

**In this section:** We'll examine real failure modes you'll encounter today (and in production), and strategies to prevent them.

---

## **Why This Matters: A Real Bug from Production**

**Scenario:** Finance team deploys multi-agent SOX checker for PAY-002. It runs for 3 months. Auditor reviews outputs in October.

**Auditor:** "Why did July show PASS when August showed 3 violations with similar patterns?"

**Engineering investigation reveals:**
- Evidence Agent ran correctly in July (found 2 violations)
- But output was `{"violations": "2"}` (string)
- Reviewer Agent expected integer, got string, **failed silently**
- Silently returned `{"review_status": "PASS"}` (default value when error)
- Decision Agent saw "PASS" from Reviewer → marked control as PASS

**Root cause:** Schema mismatch in handoff. Cost: Loss of auditor trust, 3 months of invalid results.

**Lesson:** The bugs that matter aren't "bad AI reasoning." They're **bad plumbing**.

---

## **Challenge 1: Handoffs (Schema Mismatches)**

### **Definition:** Passing structured data from one agent to another.

Agents must "speak" in a **common language** (usually JSON or typed objects). Even minor mismatches break the pipeline.

### **Common Failure Modes:**

**Type Mismatch:**
```python
# Evidence Agent outputs
{"violations_found": "2"}  # String

# Reviewer Agent expects
class ReviewInput(BaseModel):
    violations_found: int  # Integer
    
# Result: Pydantic validation error → pipeline crashes
```

**Field Name Mismatch:**
```python
# Evidence outputs
{"violations_found": 2}

# Reviewer expects
{"violations_count": int}

# Result: Reviewer receives None, silently fails or uses default
```

**Missing Required Field:**
```python
# Evidence outputs
{"violations_found": 2}  # Missing "transaction_ids"

# Reviewer expects
class ReviewInput(BaseModel):
    violations_found: int
    transaction_ids: List[str]  # Required
    
# Result: Validation error → pipeline crashes
```

**Date Format Mismatch:**
```python
# Evidence outputs
{"check_date": "2025-07-15"}  # ISO format

# Reviewer expects
{"check_date": "07/15/2025"}  # US format

# Result: Reviewer fails to parse date, logic breaks
```

---

### **SOX Example: The Silent Killer**

**Evidence Agent:**
```python
def check_segregation_of_duties(month):
    violations = find_sod_violations(month)
    return {
        "violations": len(violations),  # Returns integer ✅
        "details": violations
    }
```

**Reviewer Agent:**
```python
class ReviewInput(BaseModel):
    violations_found: int  # Expects "violations_found" ❌
    details: List[Dict]

def review(evidence: ReviewInput):
    # evidence.violations_found is None (field mismatch)
    # Reviewer thinks "no violations" → returns PASS
    ...
```

**Result:** Control with 2 violations marked as PASS. Auditor discovers 3 months later.

---

### **Best Practices:**

1. **Enforce Pydantic schemas everywhere:**
```python
from pydantic import BaseModel, Field

class EvidenceOutput(BaseModel):
    """Schema for Evidence Agent output"""
    violations_found: int = Field(..., ge=0, description="Number of violations")
    transaction_ids: List[str] = Field(default_factory=list)
    check_timestamp: datetime
    evidence_summary: str

class ReviewInput(BaseModel):
    """Schema for Reviewer Agent input (MUST match EvidenceOutput)"""
    violations_found: int
    transaction_ids: List[str]
    check_timestamp: datetime
    evidence_summary: str
```

2. **Fail fast on schema violations:**
```python
try:
    evidence = EvidenceOutput(**evidence_agent_output)
except ValidationError as e:
    return {"status": "FAIL", "reason": f"Evidence schema invalid: {e}"}
```

3. **Use type hints and validate in tests:**
```python
def test_evidence_to_reviewer_handoff():
    """Ensure Evidence output matches Reviewer input schema"""
    evidence = evidence_agent.run(control_id="PAY-002", month="July")
    
    # This should not raise ValidationError
    reviewer_input = ReviewInput(**evidence.dict())
    assert reviewer_input.violations_found >= 0
```

---

## **Challenge 2: State Management (Context Loss)**

### **Definition:** Keeping track of shared context as tasks progress through the pipeline.

In single-agent systems, state lives inside the agent (the LLM maintains context within a conversation). In multi-agent systems, **state must be passed explicitly**—and it's easy to lose.

### **Common Failure Modes:**

**State Not Passed:**
```python
# Evidence Agent checks July data
evidence = evidence_agent.run(control_id="PAY-002", month="July")

# Developer forgets to pass "month" to Reviewer
review = reviewer_agent.run(evidence)  # What month is this reviewing?

# Reviewer defaults to "current month" (October) → validates wrong data
```

**Partial State Passed:**
```python
# Evidence Agent collects rich context
evidence = {
    "violations_found": 2,
    "transaction_ids": ["TXN-4721", "TXN-4838"],
    "month": "July",
    "total_transactions_checked": 847,
    "check_methodology": "SQL query on payroll.transactions"
}

# Developer only passes violations to Reviewer
review = reviewer_agent.run(violations=evidence["violations_found"])

# Reviewer can't verify methodology, can't re-check same transactions
```

**State Mutated Unexpectedly:**
```python
# Evidence Agent outputs state
state = {"violations": [tx1, tx2]}

# Reviewer modifies state in-place
reviewer_agent.run(state)  # Adds "review_notes" key to state dict

# Decision Agent sees modified state, can't distinguish Evidence vs Review data
```

---

### **SOX Example: The "Wrong Month" Bug**

**Scenario:** Control PAY-002 for July

**Evidence Agent:**
```python
def generate_evidence(control_id, month):
    # Checks July payroll data
    violations = query_payroll(month="July")
    return {"violations_found": len(violations), "month": "July"}
```

**Orchestration (buggy):**
```python
def run_check(control_id, month):
    evidence = evidence_agent.generate_evidence(control_id, month)
    
    # BUG: Doesn't pass "month" to Reviewer
    review = reviewer_agent.verify(evidence)
    
    return decision_agent.finalize(evidence, review)
```

**Reviewer Agent:**
```python
def verify(evidence):
    # No "month" in input → defaults to current month
    month = datetime.now().strftime("%B")  # "October"
    
    # Re-checks October data (different month!)
    violations = query_payroll(month=month)
    return {"confirmed": len(violations) == evidence["violations_found"]}
```

**Result:**
- Evidence checked July (2 violations)
- Reviewer checked October (0 violations)
- Reviewer says "Confirmed: 2 violations" (FALSE)
- System outputs FAIL for July (by coincidence correct, but reasoning is wrong)

**Worse:** If October also had 2 violations, system would mark PASS incorrectly.

---

### **Best Practices:**

1. **Use a central State object (e.g., LangGraph State):**
```python
from typing import TypedDict

class AuditState(TypedDict):
    """Shared state across all agents"""
    control_id: str
    month: str
    evidence: Optional[EvidenceOutput]
    review: Optional[ReviewOutput]
    decision: Optional[str]
    errors: List[str]

# Each agent updates and returns the full state
def evidence_node(state: AuditState) -> AuditState:
    evidence = generate_evidence(state["control_id"], state["month"])
    state["evidence"] = evidence
    return state

def reviewer_node(state: AuditState) -> AuditState:
    # State includes month, control_id, evidence automatically
    review = verify_evidence(state["evidence"], state["month"])
    state["review"] = review
    return state
```

2. **Make state immutable (return new state, don't mutate):**
```python
def reviewer_node(state: AuditState) -> AuditState:
    # Create new state dict instead of modifying input
    new_state = state.copy()
    new_state["review"] = verify_evidence(state["evidence"], state["month"])
    return new_state
```

3. **Log state at each transition:**
```python
def log_state_transition(from_node: str, to_node: str, state: AuditState):
    logger.info(f"Transition {from_node} → {to_node}", extra={
        "control_id": state["control_id"],
        "month": state["month"],
        "state_keys": list(state.keys())
    })
```

---

## **Challenge 3: Error Propagation (Silent Failures)**

### **Definition:** How one agent's failure spreads through the system.

In a sequential pipeline, if Agent A fails but doesn't raise an error, Agent B might produce nonsense output—and the system looks like it "worked."

### **Common Failure Modes:**

**Silent Failure with Default Values:**
```python
def evidence_agent(control_id, month):
    try:
        violations = check_violations(control_id, month)
    except Exception as e:
        # BUG: Returns default instead of raising
        return {"violations_found": 0, "status": "success"}  # Should be "error"
```

**Downstream Agent Doesn't Check for Errors:**
```python
evidence = evidence_agent.run()  # Fails silently, returns {"violations": 0}
review = reviewer_agent.run(evidence)  # Blindly accepts, validates 0 violations
# System outputs PASS (wrong!)
```

**Partial Errors Not Caught:**
```python
def evidence_agent(control_id, month):
    results = []
    for transaction in get_transactions(month):
        try:
            results.append(check_transaction(transaction))
        except Exception:
            # BUG: Skips failed transactions, continues
            pass
    
    # Returns partial results without indicating some checks failed
    return {"violations": sum(results)}
```

---

### **SOX Example: The "File Not Found" Bug**

**Scenario:** Evidence Agent needs to load July payroll CSV

**Evidence Agent (buggy):**
```python
def generate_evidence(control_id, month):
    try:
        df = pd.read_csv(f"payroll_{month}.csv")
    except FileNotFoundError:
        # BUG: Returns empty result instead of failing
        return {"violations_found": 0, "status": "success"}
    
    violations = check_segregation(df)
    return {"violations_found": len(violations), "status": "success"}
```

**What Happens:**
- File doesn't exist (maybe filename was `payroll_july_2025.csv`)
- Evidence Agent returns `{"violations_found": 0, "status": "success"}`
- Reviewer validates "0 violations" (technically correct given the empty data)
- System marks PASS
- **Reality:** Control was never tested at all

**Auditor discovers:** "You marked July as PASS, but I don't see any evidence in your logs that you checked July data."

---

### **Best Practices:**

1. **Fail closed, not open:**
```python
def evidence_agent(control_id, month):
    try:
        df = pd.read_csv(f"payroll_{month}.csv")
    except FileNotFoundError as e:
        # FAIL immediately, don't continue
        return {
            "status": "FAIL",
            "reason": f"Unable to load data: {e}",
            "violations_found": None  # Explicit null
        }
    
    violations = check_segregation(df)
    return {
        "status": "SUCCESS",
        "violations_found": len(violations),
        "evidence": violations
    }
```

2. **Downstream agents check upstream status:**
```python
def reviewer_agent(evidence):
    # ALWAYS check if upstream agent succeeded
    if evidence.get("status") != "SUCCESS":
        return {
            "status": "FAIL",
            "reason": f"Cannot review: Evidence agent failed with reason: {evidence.get('reason')}"
        }
    
    # Only proceed if evidence is valid
    review = verify_evidence(evidence)
    return {"status": "SUCCESS", "review": review}
```

3. **Use exceptions for control flow in critical paths:**
```python
class EvidenceGenerationError(Exception):
    """Raised when evidence cannot be generated"""
    pass

def evidence_agent(control_id, month):
    try:
        df = pd.read_csv(f"payroll_{month}.csv")
    except FileNotFoundError as e:
        raise EvidenceGenerationError(f"Data file not found: {e}")
    
    violations = check_segregation(df)
    return {"violations_found": len(violations)}

# Orchestrator catches and handles
try:
    evidence = evidence_agent.run()
except EvidenceGenerationError as e:
    return {"status": "FAIL", "reason": str(e)}
```

---

## **Challenge 4: Auditability (Black Box Decisions)**

### **Definition:** Ability to explain *why* the system reached its decision.

For SOX compliance, **"the AI said so"** is never an acceptable explanation. Auditors need:
- What checks were performed
- What data was examined
- What results were produced
- Who (which agent) validated what

Without logging, the system is a black box—and black boxes fail audits.

### **Common Failure Modes:**

**No Logging:**
```python
def run_audit(control_id, month):
    evidence = evidence_agent.run(control_id, month)
    review = reviewer_agent.run(evidence)
    decision = decision_agent.run(evidence, review)
    return decision  # No trace of intermediate steps
```

**Insufficient Logging:**
```python
def run_audit(control_id, month):
    logger.info("Starting audit")
    evidence = evidence_agent.run(control_id, month)
    logger.info("Evidence generated")  # What evidence? What values?
    review = reviewer_agent.run(evidence)
    logger.info("Review complete")  # What was the outcome?
    return decision
```

**Logging Without Context:**
```python
logger.info(f"Violations found: {violations_count}")
# Missing: What control? What month? What methodology? Who found them?
```

---

### **SOX Example: The "Trust Me" Audit**

**Scenario:** Auditor reviews Q3 SOX results

**Auditor:** "Show me how you determined PAY-002 was compliant in July."

**Your logs:**
```
2025-07-15 10:23:45 - INFO - Starting audit
2025-07-15 10:23:52 - INFO - Evidence generated
2025-07-15 10:24:01 - INFO - Review complete
2025-07-15 10:24:03 - INFO - Decision: PASS
```

**Auditor:** "What evidence? What did the reviewer check?"

**You:** "The system marked it as PASS."

**Auditor:** 🚩 "This is insufficient. I need to see the actual checks performed."

---

### **Best Practices:**

1. **Log structured artifacts at each step:**
```python
import json
import logging

def evidence_agent(control_id, month):
    violations = check_violations(control_id, month)
    
    evidence = {
        "control_id": control_id,
        "month": month,
        "violations_found": len(violations),
        "transaction_ids": [v["id"] for v in violations],
        "check_timestamp": datetime.now().isoformat(),
        "methodology": "SQL query: SELECT * FROM payroll WHERE created_by = approved_by",
        "total_transactions_checked": get_total_count(month)
    }
    
    # Log the full evidence artifact
    logging.info("Evidence generated", extra={
        "control_id": control_id,
        "evidence": json.dumps(evidence)
    })
    
    return evidence
```

2. **Create audit trails that look like workpapers:**
```python
def create_audit_workpaper(control_id, month, evidence, review, decision):
    """Generate human-readable audit artifact"""
    workpaper = f"""
    SOX Control Testing Workpaper
    ============================
    Control: {control_id}
    Period: {month} 2025
    Test Date: {datetime.now().strftime("%Y-%m-%d")}
    
    Evidence Phase:
    ---------------
    Methodology: {evidence["methodology"]}
    Transactions Tested: {evidence["total_transactions_checked"]}
    Violations Found: {evidence["violations_found"]}
    Violation IDs: {", ".join(evidence["transaction_ids"])}
    
    Review Phase:
    -------------
    Independent Verification: {review["independent_check_result"]}
    Reviewer Confidence: {review["confidence"]}
    Discrepancies: {review.get("discrepancies", "None")}
    
    Final Decision:
    ---------------
    Status: {decision["status"]}
    Rationale: {decision["rationale"]}
    
    Performed by: AI Multi-Agent System v2.1
    Reviewed by: {review["reviewer_agent_version"]}
    """
    
    # Save to artifact store
    save_workpaper(workpaper, control_id, month)
    return workpaper
```

3. **Include version and config information:**
```python
evidence = {
    "violations_found": len(violations),
    "agent_version": "evidence_agent_v1.2",
    "model_used": "claude-sonnet-4-5",
    "prompt_version": "PAY002_v3",
    "config": {
        "threshold": 0,
        "date_range": f"{month}-01 to {month}-31"
    }
}
```

---

## **Debugging Multi-Agent Systems: A Workflow**

When your pipeline fails today (and it will!), use this process:

### **Step 1: Identify Which Agent Failed**
```python
# Check logs to see where pipeline stopped
# Look for: Which agent's output is None/invalid?
```

### **Step 2: Check the Handoff**
```python
# Print the output of the failing agent
print(json.dumps(evidence, indent=2))

# Compare to the schema of the next agent
print(ReviewInput.schema())

# Look for: Type mismatches, missing fields, wrong field names
```

### **Step 3: Verify State**
```python
# Check if context was passed correctly
print(f"Month in evidence: {evidence.get('month')}")
print(f"Month in state: {state.get('month')}")

# Look for: Missing context, wrong values, stale data
```

### **Step 4: Check Error Handling**
```python
# Did the agent fail silently?
if evidence.get("status") == "SUCCESS" but evidence.get("violations_found") is None:
    print("🚩 Agent returned SUCCESS but data is invalid")
```

### **Step 5: Review Audit Trail**
```python
# Can you explain the decision to an auditor?
# If not, add more logging
```

---

## **Putting It All Together**

The four big challenges and their solutions:

| Challenge | Failure Mode | Prevention Strategy |
|-----------|--------------|---------------------|
| **Handoffs** | Schema mismatches, type errors | Enforce Pydantic schemas, fail fast on validation errors |
| **State Management** | Context loss, wrong data checked | Use central State object, log state transitions |
| **Error Propagation** | Silent failures, default values accepted | Fail closed, check upstream status before proceeding |
| **Auditability** | Black box decisions, no trace | Log structured artifacts, create workpapers, include versioning |

<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

👉 **Key Message**: In SOX systems, the failure modes aren't "bad AI answers." *They're orchestration failures.* Building reliable multi-agent systems means engineering the pipes as carefully as the agents themselves—and **today's hands-on will intentionally break those pipes so you learn to fix them.**

</aside>

