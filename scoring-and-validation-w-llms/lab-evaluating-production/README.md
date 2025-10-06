<h1>
  <span>

  ![alt text](./assets/ga-logo.png)

  </span>
  <span class="subhead">Applied Exercise - Scoring Real Outputs</span>
</h1>

**Learning objective:** Evaluate AI-generated audit outputs to decide if they are production-ready, using both automated checks and human review rubrics.

## Exercise Overview

You'll practice the full validation workflow:

1. Review sample LLM-generated audit outputs
2. Run programmatic checks using provided code
3. Apply human rubric scoring
4. Compare results and discuss discrepancies
5. Decide: production-ready or needs revision?


## Materials Provided

### Sample Dataset: `payment_logs.csv`

```csv
entry_id,amount,date,approver_1,approver_2,status
1001,450.00,2024-07-15,Alice,NULL,approved
1002,1250.00,2024-07-18,Bob,NULL,approved
1003,1800.00,2024-07-22,Alice,NULL,approved
1004,950.00,2024-07-25,Charlie,NULL,approved
1005,2100.00,2024-07-28,Bob,Dana,approved
```

**Control:** PAY-002 requires dual approval for payments > $1000

> **Expected violations:** Entries 1002, 1003 (both > $1000 with only one approver)

## Sample Outputs to Evaluate

### Output A: "The Strong One"

```json
{
  "control_id": "PAY-002",
  "period": "2024-07",
  "violations_found": 2,
  "violation_entries": ["1002", "1003"],
  "policy_summary": "All payments exceeding $1000 require dual approval per SOX control PAY-002.",
  "population": {
    "tested_count": 5,
    "over_threshold": 3,
    "violations": 2
  },
  "narrative": "Testing of control PAY-002 for July 2024 identified 2 violations out of 5 transactions tested. Entries 1002 ($1,250) and 1003 ($1,800) were approved by a single approver, violating the dual approval requirement for payments over $1,000. Entry 1005 ($2,100) correctly had dual approval. The control was not operating effectively during the period tested."
}

```

### Output B: "The Hallucinator"

```json
{
  "control_id": "PAY-002",
  "period": "2024-07",
  "violations_found": 2,
  "violation_entries": ["1002", "1003", "1004"],
  "policy_summary": "Payments over $1000 require dual approval.",
  "population": {
    "tested_count": 5
  },
  "narrative": "PAY-002 testing for July 2024 found 3 violations. Entries 1002, 1003, and 1004 all lacked proper approval controls."
}

```

### Output C: "The Vague One"

```json
{
  "control_id": "PAY-002",
  "period": "2024-07",
  "violations_found": 2,
  "violation_entries": ["1002", "1003"],
  "policy_summary": "Dual approval needed for big payments.",
  "population": {
    "tested_count": 5
  },
  "narrative": "The control probably had some issues. It looks like maybe 2 entries didn't follow the rules correctly."
}

```

### Output D: "The Format Breaker"

```json
{
  "control": "PAY-002",
  "month": "July 2024",
  "issues": 2,
  "problem_entries": ["1002", "1003"],
  "summary": "Control PAY-002 had 2 violations in July. Both entries lacked dual approval."
}

```

---

## Step 1: Run Programmatic Validation

**Instructions:** Use the Pydantic validator from earlier to test each output.

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict
import pandas as pd

# Load source data
logs_df = pd.read_csv('payment_logs.csv')
valid_entry_ids = set(logs_df['entry_id'].astype(str))

class AuditEvidence(BaseModel):
    control_id: str = Field(..., pattern=r'^[A-Z]{3}-\d{3}$')
    period: str = Field(..., pattern=r'^\d{4}-\d{2}$')
    violation_entries: List[str]
    violations_found: int = Field(..., ge=0)
    policy_summary: str = Field(..., min_length=10)
    population: Dict[str, int]
    narrative: str = Field(..., max_length=500)

    @field_validator('violations_found')
    @classmethod
    def check_count(cls, v, info):
        entries = info.data.get('violation_entries', [])
        if v != len(entries):
            raise ValueError(f"Count mismatch: {v} vs {len(entries)}")
        return v

    @field_validator('narrative')
    @classmethod
    def check_guardrails(cls, v, info):
        banned = ['probably', 'maybe', 'looks like', 'appears to']
        for phrase in banned:
            if phrase in v.lower():
                raise ValueError(f"Banned phrase: '{phrase}'")

        control_id = info.data.get('control_id', '')
        if control_id not in v:
            raise ValueError(f"Must cite {control_id}")
        return v

# Test each output
outputs = {
    "Output A": output_a_dict,
    "Output B": output_b_dict,
    "Output C": output_c_dict,
    "Output D": output_d_dict
}

for name, output in outputs.items():
    try:
        validated = AuditEvidence(**output)
        print(f"✅ {name}: PASSED programmatic validation")
    except Exception as e:
        print(f"❌ {name}: FAILED - {e}")

```

**Expected Results:**

| Output | Schema | Grounding | Guardrails | Overall |
| --- | --- | --- | --- | --- |
| A | ✅ | ✅ | ✅ | PASS |
| B | ✅ | ❌ Count wrong | ✅ | FAIL |
| C | ✅ | ✅ | ❌ Banned phrases | FAIL |
| D | ❌ Wrong fields | N/A | N/A | FAIL |



## Step 2: Apply Human Rubric

**Instructions:** For outputs that passed Gate 1 (programmatic), apply the human rubric.

**Rubric Scorecard:**

| Output | Faithfulness | Clarity | Tone | Compliance | Overall |
| --- | --- | --- | --- | --- | --- |
| A | ✅ Matches data | ✅ Clear narrative | ✅ Professional | ✅ Cites control | PASS |
| B | ❌ Wrong count (hallucination) | - | - | - | FAIL (Gate 1) |
| C | ✅ Count correct | ⚠️ Vague language | ❌ "probably", "maybe" | ⚠️ Weak citation | FAIL (Gate 1) |
| D | - | - | - | - | FAIL (Gate 1) |

**Only Output A passes both gates.**


## Step 3: Group Discussion

**Discussion Questions:**

1. **Where did automation and human scoring agree?**
    - Both caught Output B's count mismatch
    - Both flagged Output C's banned phrases
2. **Where did they disagree or complement each other?**
    - Output A: Automation said "pass," humans confirmed it's audit-ready
    - Output C: Automation caught banned phrases, humans noticed vague tone
3. **What would you do with each output?**
    - A: Approve for workpapers
    - B: Reject—hallucination is critical
    - C: Send back for revision (remove vague language)
    - D: Reject—doesn't meet schema
4. **How would you improve the validation system?**
    - Add more banned phrases to guardrails?
    - Require minimum detail level in narratives?
    - Add LLM-as-judge to flag vague language automatically?


## Step 4: Production Readiness Decision Matrix (5 min)

For each output, decide its fate:

```
┌─────────────────────────────────────────────────┐
│              VALIDATION DECISION TREE            │
├─────────────────────────────────────────────────┤
│                                                  │
│  Gate 1 (Programmatic) FAIL → REJECT             │
│       ↓                                          │
│  Gate 1 PASS → Gate 2 (Human Rubric)             │
│       ↓                                          │
│  Gate 2 FAIL → REVISE or REJECT                  │
│       ↓                                          │
│  Gate 2 PASS → APPROVE for Workpapers         │
│                                                  │
└─────────────────────────────────────────────────┘

```

**Your decisions:**

- Output A: APPROVE ✅
- Output B: REJECT ❌ (hallucination)
- Output C: REVISE 🔄 (remove vagueness)
- Output D: REJECT ❌ (schema broken)
