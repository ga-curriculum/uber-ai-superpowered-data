<h1>
  <span>

  ![alt text](../assets/ga-logo.png)

  </span>
  <span class="subhead">SOX Foundations & Where AI Fits</span>
</h1>

**Learning objective:** 
- Apply SOX principles to identify where AI can support but not replace deterministic controls. 
- Discuss strategies for designing audit-ready workflows that preserve evidence integrity and meet compliance standards.

## **What this lesson covers:** 
- Where AI fits in SOX workflows (and where it absolutely doesn't) 
- Risks AI introduces to audit evidence integrity - Design principles for compliance-ready AI systems 
- How regulators view AI in financial reporting 

### **Why it matters:** 
When AI touches financial data, control testing, or audit evidence, it becomes part of your compliance framework. Building it wrong means audit failures. Building it right means automating tedious work while strengthening controls. 

### Developer mindset shift: 
- **Before:** Deterministic systems where input → output is predictable and testable 
- **After:** Probabilistic AI constrained by deterministic guardrails that satisfy audit standards

## Opening Activity: Risk Spotting

**Instructions:** Read the three AI outputs below. For each, identify:

1. Is this output auditable? Why or why not?
2. What evidence is missing?
3. What could go wrong if we used this in a SOX workpaper?

**Output A:**

> "Control PAY-002 (Payables Approval) is operating effectively. AI analyzed 1,247 transactions and found no exceptions."


**Output B:**

> "Control PAY-002 (Payables Approval) tested across 1,247 payables transactions on 2025-03-15. Deterministic check identified 3 exceptions: invoices #8291, #8405, #8512 missing VP approval per control criteria. AI classified exceptions as: missing approver (3), wrong tier approval (0), duplicate approval (0). Evidence stored in workpaper PAY-002-Q1-2025.json."
> 

**Output C:**

> "Based on my analysis, everything looks good with the payables controls. I didn't see any major issues. The system seems to be working as intended."


<details>
<summary><strong>Click to see answers</strong></summary>

**Output A:** ❌ Not auditable

- Missing: How was it analyzed? What criteria? What was checked?
- Risk: No audit trail. Can't reproduce. "AI says so" isn't evidence.

**Output B:** ✅ Potentially auditable

- Has: Date, count, specific exceptions, deterministic check, evidence pointer
- Still needs: Human review to confirm, access to source data

**Output C:** ❌ Not auditable

- Missing: Everything. Vague, subjective, no facts
- Risk: Hallucination, no evidence, can't verify

**Key insight:** In SOX, specificity and traceability = auditability.

</details>


## Why SOX Exists

**2002:** Enron and WorldCom collapse due to accounting fraud. Investors lose billions. Congress acts.

**Sarbanes-Oxley Act (SOX) created two critical requirements:**

- **Section 302:** Management must certify the accuracy of financial statements
- **Section 404:** Companies must test and document internal controls over financial reporting

**Translation for you:** Every control that touches financial data must be:

1. **Designed properly** (does the control make sense?)
2. **Operating effectively** (is it actually working?)

SOX doesn't care about your tech stack. It cares about **evidence integrity**.



## Where AI Actually Helps

AI is a **workflow accelerator**, not a decision-maker. Here's the reality:

| **Control Testing Step** | **Traditional Approach**                     | **AI-Augmented Approach**                                                |
| ------------------------ | -------------------------------------------- | ------------------------------------------------------------------------ |
| Gather evidence          | SQL queries, manual Excel exports            | AI agents call APIs → retrieve & structure logs automatically            |
| Identify exceptions      | Manual rules, statistical sampling           | AI summarizes patterns, classifies violations at scale (full population) |
| Map to controls          | Auditor judgment on which control ID applies | AI suggests likely control IDs with explainable reasoning                |
| Draft narrative          | Auditor writes workpaper summary             | LLM generates first-draft text from structured data                      |
| Review & approve         | Senior auditor re-performs spot checks       | Reviewer agent + human re-checks deterministically                       |

---

### What AI Should Not Do

**1. AI cannot decide compliance.**

- Only deterministic checks + human reviewers conclude pass/fail
- AI can flag, summarize, suggest—never judge

**2. AI cannot invent evidence.**

- Hallucinations = audit failure
- Every AI output must anchor to real, traceable data

**3. AI cannot replace independence.**

- SOX requires separation: preparer ≠ reviewer
- Multi-agent design must mirror this (Evidence Agent ≠ Reviewer Agent)

**Remember:** *AI augments → humans decide.*

---

### SOX-Relevant Use Cases for Data Engineers

**What you'll actually build:**

| **Use Case** | **What It Does**                          | **Example**                                                         |
| ------------ | ----------------------------------------- | ------------------------------------------------------------------- |
| Summarizer   | Condense 200 exceptions into exec summary | “15% of payables missing VP approval, concentrated in EMEA region”  |
| Classifier   | Bucket violations by type                 | Missing approver (12), duplicate approver (3), wrong tier (8)       |
| Mapper       | Link transactions to control IDs          | “These 47 journal entries relate to JE-005 based on account codes”  |
| Assistant    | Draft workpapers in consistent format     | Generate audit memo template with placeholders for evidence         |
| Orchestrator | Connect multi-agent workflow              | Evidence Agent → Classifier Agent → Reviewer Agent → Human sign-off |

## Core Principle: Deterministic First, AI Second

This is your design mantra:

```text
1. Deterministic checks generate the FACTS
2. AI generates the NARRATIVE and workflow support
3. Every AI output must be ANCHORED to deterministic evidence
```

**Example workflow:**

```python
*# Step 1: Deterministic check (facts)*
exceptions = sql_query("""
    SELECT invoice_id, amount, approver_id, approval_date
    FROM payables
    WHERE amount > 5000 AND approver_tier != 'VP'
""")  # ← This is your SOURCE OF TRUTH# Step 2: AI augmentation (narrative)*
summary = llm_summarize(
    prompt=f"Summarize these {len(exceptions)} approval violations in 3 sentences",
    data=exceptions
)  # ← This adds clarity# Step 3: Logging (audit trail)*
log_audit_entry(
    check_type="deterministic_sql",
    exceptions_found=len(exceptions),
    ai_summary=summary,
    evidence_pointer="payables_q1_2025_exceptions.json"
)
```

**Why this works:**

- Facts come from SQL (reproducible, auditable)
- AI adds human-readable context
- Logs tie everything together

---

## Scenario Exercise: Design a Compliant AI Workflow

**Your task:** You're building an AI system to test Control "AP-127: All expenses >$5K require VP approval."

**Current manual process:**

- Finance analyst runs SQL query → 12,000 transactions
- Manually reviews 200-transaction sample
- Documents findings in Excel
- Takes 8 hours, narratives inconsistent

**Your AI mission:**

1. Automate exception detection
2. Classify violation types
3. Generate draft workpaper
4. Ensure external auditors (Deloitte) accept it

**Questions to answer (work in pairs, 5 min):**

1. What runs first: AI or deterministic check? Why?
2. What does the AI do in this workflow?
3. What must be logged for audit trail?
4. How would you validate the AI's output?

<details>
<summary><strong>Sample Solution</strong></summary>

**Workflow design:**

```text
1. Deterministic SQL check (facts)
   → Query all expenses >$5K
   → Flag transactions WHERE approver_tier != 'VP'
   → Output: exceptions.json (3,247 violations found)

2. AI classification (narrative)
   → LLM buckets violations:
      - Missing approver (2,100)
      - Wrong tier approval (980) 
      - Duplicate approval (167)
   → Output: classification_summary.txt

3. AI draft workpaper (documentation)
   → Generate memo: "Control AP-127 tested across 12,000 
      expenses. 3,247 exceptions identified (27% failure rate)."

4. Logging (audit trail)
   → Log: SQL query, row counts, AI prompt, AI output, timestamp
   → Store: Raw exceptions + AI summary + source query

5. Human review (approval)
   → Reviewer validates: row counts match, classifications accurate
   → Signs off on workpaper
```

**Validation approach:**

- Run SQL check twice → should get identical exceptions
- Spot-check 10 random AI classifications → manual verification
- Compare AI summary to raw data → facts must align

</details>


## Key Takeaways (1A)

<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

1. **AI belongs in SOX as the assistant**: great for summarizing, mapping, drafting, but deterministic checks and human judgment remain foundational
2. **Think: deterministic backbone + AI polish**: facts from code, clarity from AI
3. **Every AI output needs an anchor**: trace AI summaries back to source data
4. **Design for independence**: preparer ≠ reviewer, even in agent workflows
   
</aside>
