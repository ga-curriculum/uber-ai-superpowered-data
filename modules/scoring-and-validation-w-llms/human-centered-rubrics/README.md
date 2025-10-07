<h1>
  <span>

  ![alt text](/assets/ga-logo.png)

  </span>
  <span class="subhead">Human Rubrics & Hybrid Evaluation</span>
</h1

**Learning objective:** Learn about human-centered approach to evaluation

## What Humans Can Judge That Machines Can't

Automated checks handle structure and facts. But they can't assess:

- **Clarity:** Is this narrative easy to understand?
- **Professional tone:** Does it sound audit-appropriate?
- **Contextual appropriateness:** Does it address the auditor's needs?
- **Completeness:** Does it cover all relevant aspects?

> This is where **human rubrics** come in.

---

## A Human Evaluation Rubric for Audit Narratives

Use this rubric to score outputs on a Pass/Fail basis (or 1-5 scale if you want granularity):

| Dimension                | Question to Ask                                | Pass Example                                                      | Fail Example                                   |
| ------------------------ | ---------------------------------------------- | ----------------------------------------------------------------- | ---------------------------------------------- |
| **Faithfulness**         | Does it match deterministic checks?            | "Entries 1002 and 1003 lacked dual approval (2 violations)"       | "Three entries lacked approvals" (wrong count) |
| **Clarity**              | Is it unambiguous and easy to read?            | "PAY-002 was not fully followed in July, with 2 exceptions noted" | "Some issues occurred with the control"        |
| **Professional Tone**    | Does it sound neutral and audit-ready?         | "The control operated effectively with no exceptions identified"  | "Everything looks totally fine to me"          |
| **Compliance Alignment** | Does it cite control ID and period explicitly? | "For PAY-002 in July 2024, testing revealed..."                   | "This control showed some problems"            |

## How to Apply the Rubric

**Step 1:** Read the narrative without looking at scores

**Step 2:** Rate each dimension independently

**Step 3:** Only approve if ALL dimensions pass

**Step 4:** Document failure reasons for any dimension that fails


## Hybrid Validation in Practice

Neither programmatic nor human evaluation alone is sufficient. You need both.

### Pattern: Two-Gate Approval

```
LLM Output
    ↓
Gate 1: Automated (Programmatic)
    ├─ Schema validation ✅
    ├─ Grounding checks ✅
    └─ Guardrails ✅
    ↓
Gate 2: Human Rubric
    ├─ Faithfulness ✅
    ├─ Clarity ⚠️  (needs revision)
    ├─ Tone ✅
    └─ Compliance ✅
    ↓
Status: NEEDS REVISION

```

**Decision logic:**

- If Gate 1 fails → Reject immediately (don't even send to human)
- If Gate 1 passes but Gate 2 fails → Send back for revision
- If both pass → Approved for workpapers


## Case Study: When Gates Disagree

**Scenario:** LLM produces this output:

```json
{
  "control_id": "PAY-002",
  "period": "2024-07",
  "violations_found": 2,
  "violation_entries": ["1002", "1003"],
  "policy_summary": "Payables over $1000 require dual approval.",
  "population": {"tested_count": 50},
  "narrative": "PAY-002 was reviewed for July. There were 2 violations
               (entries 1002 and 1003). Overall, the control showed weaknesses."
}

```

**Gate 1 (Programmatic):** ✅ PASS

- Schema valid
- Count matches (2 = len([1002, 1003]))
- Control ID cited

**Gate 2 (Human Rubric):**

- Faithfulness: ✅
- Clarity: ✅
- Tone: ⚠️ "showed weaknesses" is vague—what kind of weaknesses?
- Compliance: ✅

**Decision:** Needs revision. Prompt LLM to be more specific about the nature of violations.

**Revised narrative:**

```
"PAY-002 was tested for July 2024. Out of 50 transactions over $1000,
2 violated the dual approval requirement (entries 1002 and 1003).
Both transactions were approved by a single person rather than two
authorized approvers as required by policy."

```

Now both gates pass. ✅


## LLM-as-Judge: Using AI to Scale Human Evaluation

**Concept:** Use a second LLM to evaluate the first LLM's output against a rubric.

### When to Use LLM-as-Judge

- **Good for:** Scaling evaluation across many outputs (100s or 1000s)
- **Requires:** Clear rubric, calibration against human judgments
- **Risk:** Judge LLM can have its own biases or errors

### Implementation Pattern

```python
def llm_judge(output: str, rubric: str) -> dict:
    """Use GPT-4 to evaluate an output against a rubric"""

    judge_prompt = f"""
You are an audit quality reviewer. Evaluate this AI-generated audit narrative
against the rubric below. Output your assessment as JSON.

RUBRIC:
{rubric}

NARRATIVE TO EVALUATE:
{output}

Provide your evaluation in this format:
{{
  "faithfulness": {{"pass": true/false, "reason": "..."}},
  "clarity": {{"pass": true/false, "reason": "..."}},
  "tone": {{"pass": true/false, "reason": "..."}},
  "compliance": {{"pass": true/false, "reason": "..."}}
}}
"""

    judge_response = llm_api_call(judge_prompt)
    return json.loads(judge_response)

```

## Putting This in Your Pipeline

**Real-world integration diagram:**

```
[Source Data]
    ↓
[Deterministic Checks] → violations list, counts
    ↓
[LLM Agent] → generates narrative + JSON
    ↓
[Validation Layer]
    ├─ Schema check (Pydantic)
    ├─ Grounding check (counts match)
    ├─ Guardrails (tone, length)
    └─ [Optional: LLM Judge]
    ↓
[Human Approval] → for any flagged cases
    ↓
[Audit Workpapers]

```

Validation should be a **stage in the pipeline**, not an afterthought.

## SOX Documentation Requirements

For SOX compliance, document your validation approach:

**Control Documentation Template:**

```md
## AI Validation Control: LLM-Generated Audit Evidence

### Control ID: VAL-001
### Purpose: Ensure LLM outputs meet audit quality standards

### Validation Steps:
1. **Automated Checks (Deterministic)**
   - Schema validation via Pydantic model AuditEvidence
   - Grounding: violations_found = len(violation_entries)
   - Guardrails: no banned phrases, control ID cited

2. **Human Review (Qualitative)**
   - Rubric: faithfulness, clarity, tone, compliance
   - Reviewer: Senior Auditor or Finance Manager
   - Frequency: 100% of outputs OR sample-based (10% minimum)

3. **Approval Workflow**
   - If automated checks fail → reject immediately
   - If rubric fails → return for revision
   - If both pass → approved for workpapers
   - Approval logged in [audit system]

### Audit Trail:
- Validation results stored in validation_log table
- Includes: output_id, timestamp, automated_result, human_review, approver, final_status

```

## Key Takeaway:

<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

💡 Human rubrics ensure outputs are not only correct but also clear, professional, and compliant. The strongest systems use both programmatic checks and human judgment — and document both for SOX.

</aside>