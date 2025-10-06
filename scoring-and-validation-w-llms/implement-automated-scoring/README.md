<h1>
  <span>

  ![alt text](../assets/ga-logo.png)

  </span>
  <span class="subhead">Programmatic Validation</span>
</h1>

**Learning objective:**  Integrate automated checks with human feedback to holistically judge whether an AI system is production-ready.

## The First Line of Defense

Programmatic validation = automated checks that run on **every single output**, before humans ever see it. Think of these as unit tests for AI systems.

## Three Categories of Programmatic Checks

### 1. Schema Validation

Enforce that outputs follow a required structure using tools like Pydantic (Python).

**Example Requirement:**

```
Every audit evidence payload must include:
- control_id: string
- period: string (YYYY-MM format)
- violations_found: integer
- violation_entries: list of strings
- policy_summary: string
- population: object with tested_count
- narrative: string
```

### 2. Grounding Checks (Fact Consistency)

Ensure numbers and claims match source data.

**Examples:**

- `violations_found` must equal `len(violation_entries)`
- All entry IDs in `violation_entries` must exist in source CSV
- Period mentioned in narrative must match `period` field

### 3. Guardrails (Style & Safety)

Lightweight rules to enforce professionalism and prevent vague language.

**Examples:**

- Narrative must be < 150 words
- Must not contain banned phrases: "probably", "maybe", "appears to", "seems like"
- Must explicitly cite control ID by name
- Must not include placeholder text like "[TODO]" or "XXX"

---

## Building a Validation System

Let's build a real validation function using Pydantic. Follow along in your own environment.

### Step 1: Define the Schema

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict
import re

class AuditEvidence(BaseModel):
    """Schema for audit evidence outputs"""
    control_id: str = Field(..., pattern=r'^[A-Z]{3}-\d{3}$')
    period: str = Field(..., pattern=r'^\d{4}-\d{2}$')
    violations_found: int = Field(..., ge=0)
    violation_entries: List[str] = Field(...)
    policy_summary: str = Field(..., min_length=10)
    population: Dict[str, int] = Field(...)
    narrative: str = Field(..., min_length=20, max_length=500)

    @field_validator('violations_found')
    @classmethod
    def check_count_matches(cls, v, info):
        """Grounding check: violations_found must match list length"""
        entries = info.data.get('violation_entries', [])
        if v != len(entries):
            raise ValueError(
                f"violations_found ({v}) doesn't match "
                f"violation_entries length ({len(entries)})"
            )
        return v

    @field_validator('narrative')
    @classmethod
    def check_guardrails(cls, v, info):
        """Guardrails: check for banned phrases and control ID citation"""
        banned_phrases = ['probably', 'maybe', 'appears to', 'seems like']
        for phrase in banned_phrases:
            if phrase in v.lower():
                raise ValueError(f"Narrative contains banned phrase: '{phrase}'")

        # Must cite control ID
        control_id = info.data.get('control_id', '')
        if control_id not in v:
            raise ValueError(f"Narrative must cite control ID: {control_id}")

        return v

```

### Step 2: Test Valid Output

```python
# Example: Valid LLM output
valid_output = {
    "control_id": "PAY-002",
    "period": "2024-07",
    "violations_found": 2,
    "violation_entries": ["1002", "1003"],
    "policy_summary": "Payables over $1000 require dual approval.",
    "population": {"tested_count": 50, "violations": 2},
    "narrative": "Control PAY-002 was not fully followed in July 2024. "
                 "Entries 1002 and 1003 were processed without required dual approval, "
                 "representing 2 violations out of 50 transactions tested."
}

try:
    evidence = AuditEvidence(**valid_output)
    print("✅ Validation PASSED")
    print(f"Evidence for {evidence.control_id} is audit-ready")
except Exception as e:
    print(f"❌ Validation FAILED: {e}")

```

**Output:**

```
✅ Validation PASSED
Evidence for PAY-002 is audit-ready
```

### Step 3: Test Invalid Outputs

**Test Case 1: Count Mismatch**

```python
invalid_count = {
    "control_id": "PAY-002",
    "period": "2024-07",
    "violations_found": 3,  # Wrong!
    "violation_entries": ["1002", "1003"],  # Only 2 entries
    "policy_summary": "Payables over $1000 require dual approval.",
    "population": {"tested_count": 50},
    "narrative": "Control PAY-002 had 3 violations in July 2024."
}

try:
    evidence = AuditEvidence(**invalid_count)
except Exception as e:
    print(f"❌ Count Mismatch: {e}")

```

**Output:**

```
❌ Count Mismatch: violations_found (3) doesn't match violation_entries length (2)
```

**Test Case 2: Banned Phrase**

```python
invalid_tone = {
    "control_id": "PAY-002",
    "period": "2024-07",
    "violations_found": 2,
    "violation_entries": ["1002", "1003"],
    "policy_summary": "Payables over $1000 require dual approval.",
    "population": {"tested_count": 50},
    "narrative": "Control PAY-002 probably had violations, maybe around 2 entries."
}

try:
    evidence = AuditEvidence(**invalid_tone)
except Exception as e:
    print(f"❌ Banned Phrase: {e}")

```

**Output:**

```
❌ Banned Phrase: Narrative contains banned phrase: 'probably'
```



## Practice: Complete the Validator (10 minutes)

**Exercise:** Add a validator to check that all `violation_entries` IDs exist in a source CSV.

```python
# Starter code
import pandas as pd

# Assume source_logs.csv contains columns: entry_id, amount, approver_count
source_df = pd.read_csv('source_logs.csv')
valid_entry_ids = set(source_df['entry_id'].astype(str))

class AuditEvidence(BaseModel):
    # ... previous fields ...

    @field_validator('violation_entries')
    @classmethod
    def check_entries_exist(cls, v):
        """TODO: Verify all entry IDs exist in source data"""
        # YOUR CODE HERE
        # Hint: Check if each ID in v is in valid_entry_ids
        # Raise ValueError if any ID is not found
        pass

```

<details>
<summary>Click for solution</summary>

```python
@field_validator('violation_entries')
@classmethod
def check_entries_exist(cls, v):
    """Verify all entry IDs exist in source data"""
    invalid_ids = [id for id in v if id not in valid_entry_ids]
    if invalid_ids:
        raise ValueError(
            f"Entry IDs not found in source data: {invalid_ids}"
        )
    return v

```

</details>

---

### Real-World Integration Pattern

**How this fits in your pipeline:**

```python
def safe_llm_call(prompt: str, context: dict) -> dict:
    """Wrapper that validates LLM output before returning"""

    # 1. Get LLM response
    raw_response = llm.generate(prompt, context)

    # 2. Parse to dict
    try:
        output_dict = json.loads(raw_response)
    except json.JSONDecodeError:
        logger.error("LLM returned invalid JSON")
        return {"status": "error", "reason": "invalid_json"}

    # 3. Validate with Pydantic
    try:
        validated = AuditEvidence(**output_dict)
        return {
            "status": "success",
            "data": validated.model_dump()
        }
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return {"status": "error", "reason": str(e)}

```



**Fail-closed principle:** If validation fails at any step, return an error—never pass unvalidated output downstream.

## Key Takeaway
<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

💡**Programmatic validation catches structural errors and factual inconsistencies automatically.** 

1. In compliance contexts checks must be fail-closed.
2. If anything doesn't reconcile, it doesn't move forward.

</aside>