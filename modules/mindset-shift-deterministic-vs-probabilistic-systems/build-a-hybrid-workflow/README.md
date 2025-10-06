<h1>
   <span>
 
   ![alt text](./assets/ga-logo.png)
   
   </span>
  <span class="subhead">Activity: Build a Hybrid Workflow</span>
</h1>

**Learning objective:** Design and peer-review a hybrid workflow that combines deterministic evidence checks with probabilistic narratives for audit-ready outputs.

## Design Activity: Build a Hybrid Workflow

**Scenario**

You must verify 10,000 vendor payments against a dual approval policy:

- Payments over $1,000 require 2 approvers
- You have SQL access to payables and approvals tables
- You need to produce an audit workpaper

**Part 1: Individual Design**

Fill in the template below.

- **Step 1 - Deterministic Evidence**:
    
    Tool or script: [What will you use? SQL? Python?]
    
    Output: [What does it return? Be specific about data structure]
    
    Why deterministic: [Why must this step be reproducible?]
    
- **Step 2 - Validation**:
    
    Schema or checks: [How will you validate the output from Step 1?]
    
    Fail conditions: [What errors should stop the workflow?]
    
- **Step 3 - Probabilistic Narrative**:
    
    LLM task: [What should the LLM do with the validated data?]
    
    Temperature: [What temperature and why?]
    
    Prompt constraints: [What guardrails will you include in the prompt?]
    
- **Guardrails**:
    
    [List 3–5 constraints that prevent the LLM from inventing details]
    

**Part 2: Peer Review**

Pair up with a neighbor. Review each other's designs and discuss:

- Hallucination risk: Where could the LLM invent unsupported details?
- Failure modes: What happens if the SQL query times out? Returns 0 rows? Returns null values?
- Schema strictness: Is the validation schema tight enough to catch bad data?

**Part 3: Debrief**

Instructor will share common pitfalls from peer reviews.

<details>
<summary><b>Example Solution (click to reveal)</b></summary>

```
Step 1 - Deterministic Evidence:
  Tool: SQL query against payables and approvals tables
  Output: List of dicts with payable_id, vendor_name, amount, posting_date, approver_count
  Why deterministic: Auditors will re-run this query. Must return identical results.

Step 2 - Validation:
  Schema: Pydantic model with:
  - amount > 0 (no negative payments)
  - approver_count >= 0 (can't be null or negative)
  - posting_date in ISO format
  Fail conditions:
  - If any row has negative amount → raise ValueError
  - If SQL returns 0 rows → log warning (might be no violations, or query bug)
  - If any required field is null → raise ValueError

Step 3 - Probabilistic Narrative:
  LLM task: Summarize findings in 2–3 sentences for audit workpaper
  Temperature: 0.3 (low variance for consistency)
  Prompt constraints:
  - "Use only the facts provided"
  - Provide exact count: {len(violations)}
  - Include 2–3 example payable IDs with amounts
  - "Do not invent vendor names or departments"

Guardrails:
  - Prompt explicitly forbids inventing details
  - Low temperature (0.3) reduces creative deviation
  - Structured prompt with clear sections (Facts, Instructions)
  - Max tokens limit (200) prevents rambling
  - Post-generation check: Does output mention the exact violation count?

```

</details>

---

## Decision Matrix: When to Use Each Approach

Use this table as a quick reference guide:

| Task | Deterministic? | Probabilistic? | Recommended Pattern |
| --- | --- | --- | --- |
| Count records | Yes | No | SQL `COUNT(*)` |
| Extract structured fields | Yes | Cautious | Regex or SQL for known formats; LLM for unstructured text |
| Calculate amounts | Yes | No | Python or SQL math operations |
| Validate data structure | Yes | No | Pydantic, JSON Schema |
| Rule-based classification | Yes (if rules are clear) | Cautious (if rules are ambiguous) | Deterministic for binary rules; LLM for gray-area cases with human review |
| Summarize for humans | Template only | Yes, grounded in facts | Hybrid: SQL for facts → LLM for prose |
| Explain root causes | Limited | Yes, interpret patterns | LLM with validated input data |
| Process unstructured text | Brittle | Yes | LLM with schema validation on output |
| Generate audit narratives | Too stiff | Yes, when grounded | Hybrid: deterministic evidence → LLM narrative (temp ≤ 0.5) |

### Golden Rule

**Facts are deterministic. Explanations are probabilistic.** 
- If an auditor would ask "prove it", use deterministic logic. 
- If an auditor would ask "what does this mean?", use an LLM.

---

## Summary & Key Takeaways

1. Deterministic systems are rule-based, predictable, and reproducible. Perfect for evidence collection and calculations.
2. Probabilistic systems (LLMs) are model-based and variable. Excellent for interpretation and summarization, but risky for facts.
3. Hybrid workflows are the standard for compliant AI. The deterministic layer extracts evidence, the probabilistic layer explains it.
4. Temperature matters. For compliance work, use ≤ 0.5 to minimize hallucination and variance.
5. SOX compliance requires reproducible evidence. Your SQL queries and validation logs are what auditors test, not your LLM summaries.
6. Fail-closed design prevents bad data from propagating. If validation fails, stop the workflow and alert humans.

**Aha Moments**

- The LLM is a prosecutor, not a detective. It interprets evidence but does not collect it.
- Temperature is a risk dial. Higher temperature increases hallucination risk.
- Same facts, different words do not mean different facts. LLM variance in phrasing is acceptable; variance in numbers is not.
- Schema enforcement is your firewall. Invalid data should never reach the LLM.

---

## Reflection & Discussion Questions

### Individual Reflection


1. **Identify a deterministic component in your current workflows**
    - What is one process you already rely on that is fully deterministic?
    - What makes it reliable?
2. **Spot the rule maintenance burden**
    - Where do you spend the most time writing rules for edge cases?
    - Could an LLM handle the ambiguity if you fixed the facts first?
3. **Find an interpretation opportunity**
    - What part of your workflow requires human interpretation today?
    - Could you automate it if the underlying facts were validated deterministically?

### Optional: Pair Share

Discuss with a partner:

- What is one workflow you could redesign as a hybrid system?
- Where is the deterministic or probabilistic boundary?

