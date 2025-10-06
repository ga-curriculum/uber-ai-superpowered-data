<h1>
  <span>

  ![alt text](./assets/ga-logo.png)
  
  </span>
  <span class="subhead">Hybrid Workflow Mindset</span>
</h1>

**Learning objectives:** 
- Distinguish between deterministic evidence and probabilistic narratives.
- Design hybrid workflows that ensure audit-ready outputs with clear boundaries, safeguards, and traceability.

## Hybrid Engineering Mindset

> **Core Principle: Evidence first, narrative second.**

Break your workflow into two layers:

- **Deterministic layer:** SQL queries and validation scripts produce exact facts, IDs, and counts
- **Probabilistic layer:** LLMs explain findings based on validated input, but never create the findings

Analogy: Think of a murder trial. The detective (deterministic system) collects fingerprints, timestamps, and DNA evidence. The prosecutor (LLM) weaves that evidence into a narrative for the jury. The prosecutor does not invent evidence, they interpret it.

## SOX Connection: Why This Matters for Audit

Under SOX Section 404, you must maintain evidence that controls are operating effectively.

### **What Auditors Test**

| Component               | Audit Approach                                     | Why It Matters                                                          |
| ----------------------- | -------------------------------------------------- | ----------------------------------------------------------------------- |
| Deterministic evidence  | Re-run SQL queries, validate schemas, inspect logs | This is your audit trail. Must be reproducible.                         |
| Probabilistic narrative | Read workpaper summaries, validate tone            | Explains findings but does not prove findings. Not tested for accuracy. |

### **In Practice**

```python
# THIS is your SOX evidence
violations = execute_sql("""
    SELECT payable_id, amount, approver_count
    FROM payables
    WHERE amount > 1000 AND approver_count < 2
""")

# THIS is your workpaper narrative
summary = llm.generate(f"Summarize these {len(violations)} violations")

```

### **Critical distinction:**

- Auditors will re-run the SQL query
- Auditors will read the LLM summary

If the SQL query returns different results when the auditor runs it, the control fails.

If the LLM summary is poorly worded, that is workpaper cleanup, not a control failure.

### **Fail-Safe Requirement**

Fail-closed means the system stops processing when it encounters invalid input, rather than guessing or proceeding with bad data.

```python
if violations_df['amount'].min() < 0:
    raise ValueError("Negative amounts detected - data quality issue")
    # Do not let the LLM "interpret" what a negative amount means

```

Why this matters: SOX requires documented controls. If your system proceeds with garbage data and the LLM smooths over the errors, you've created an undetected control failure.

## Implementation Pattern

### Step 1: Deterministic Evidence Extraction

```python
def get_pay002_violations(start_date: str, end_date: str) -> list[dict]:
    """
    Extracts PAY-002 violations using SQL.
    Returns exact list of violations with IDs.

    This function is DETERMINISTIC - same inputs = same outputs.
    """
    query = """
        SELECT
            p.payable_id,
            p.vendor_name,
            p.amount,
            p.posting_date,
            COUNT(a.approver_id) as approver_count
        FROM payables p
        LEFT JOIN approvals a ON p.payable_id = a.payable_id
        WHERE p.amount > 1000
          AND p.posting_date BETWEEN %(start)s AND %(end)s
        GROUP BY p.payable_id
        HAVING COUNT(a.approver_id) < 2
    """

    results = db.execute(query, {"start": start_date, "end": end_date})
    return results.fetchall()

```

Why this step is deterministic: The SQL engine follows explicit rules. Run it twice, get the same results.

### Step 2: Schema Enforcement

```python
from pydantic import BaseModel, Field, validator
from typing import List
from datetime import datetime

class Violation(BaseModel):
    """
    Strict schema for a single violation.
    Enforces data types and business rules.
    """
    payable_id: str
    vendor_name: str
    amount: float = Field(..., gt=0)  # Must be positive
    posting_date: str  # ISO format: YYYY-MM-DD
    approver_count: int = Field(..., ge=0)  # Can't be negative

    @validator('posting_date')
    def validate_date_format(cls, v):
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid date format: {v}")

class PAY002Report(BaseModel):
    """
    Wrapper for the full report.
    Enforces report-level constraints.
    """
    period: str  # e.g., "July 2025"
    threshold: float = Field(default=1000.0, gt=0)
    violations: List[Violation]

    @validator('violations')
    def check_non_empty(cls, v):
        # Fail-closed: empty violations might indicate query failure
        if len(v) == 0:
            raise ValueError("No violations found - verify query logic")
        return v

# Usage
raw_data = get_pay002_violations("2025-07-01", "2025-07-31")
report = PAY002Report(
    period="July 2025",
    violations=[Violation(**row) for row in raw_data]
)
# If any row has invalid data, Pydantic raises an error immediately

```

Why schema enforcement matters:

- Catches data quality issues before they reach the LLM
- Documents expected data structure (crucial for audits)
- Implements fail-closed behavior

### Step 3: Constrained Narrative Generation

```python
def generate_audit_narrative(report: PAY002Report, temperature: float = 0.3) -> str:
    """
    Generates workpaper summary using LLM.

    Key constraints:
    - Temperature ≤ 0.5 for consistency
    - Prompt explicitly states "use only the facts provided"
    - Includes sample violations for specificity
    """
    # Select first 3 violations as examples
    sample_violations = [
        {"id": v.payable_id, "amount": v.amount}
        for v in report.violations[:3]
    ]

    prompt = f"""
Write a two to three sentence workpaper summary for an audit.

**Control**: PAY-002 (Dual Approval Required)
**Period**: {report.period}
**Threshold**: ${report.threshold:,.2f}

**Facts**:
- Total violations: {len(report.violations)}
- Example violations: {sample_violations}

**Instructions**:
- Use only the facts provided above
- Do not invent vendor names, departments, or explanations
- State counts precisely (not "several" or "many")
- Maintain neutral, factual tone
"""

    response = llm.generate(
        prompt=prompt,
        temperature=temperature,  # Low variance
        max_tokens=200
    )

    return response

# Usage
narrative = generate_audit_narrative(report)
print(narrative)
# Output: "57 vendor payments in July 2025 exceeded the $1000 threshold
# without required dual approval, violating control PAY-002. Examples include
# payables PAY-5471 ($1,250) and PAY-5833 ($2,100). All violations were
# identified via SQL query against the approvals table."

```

**Why this step is probabilistic:**
- Run it twice, get slightly different wording
- Constraints keep it factual and audit-appropriate

## Key Takeaways

<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

💡 **Engineering implications for building hybrid systems:**

| Component                | Purpose                                 | Example                                                   |
| ------------------------ | --------------------------------------- | --------------------------------------------------------- |
| Schemas and contracts    | Define boundaries between layers        | Pydantic models, OpenAPI specs                            |
| Evaluation harness       | Test outputs against golden datasets    | Unit tests comparing LLM output to known-good summaries   |
| Fail-closed behavior     | Stop processing when inputs are invalid | Raise errors for negative amounts, null IDs               |
| Logging and traceability | Record every step for audit trail       | Log SQL queries, LLM prompts, and outputs with timestamps |

</aside>
