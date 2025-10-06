<h1>
  <span>

  ![alt text](./assets/ga-logo.png)

  </span>
  <span class="subhead">Design Principles & Production Readiness</span>
</h1>

**Learning objectives:** 
- Explore design principles to integrate deterministic checks and augmentation in SOX-compliant workflows.
- Implement audit trails and validation harnesses to ensure production readiness.


## The Five Principles for SOX-Compliant AI

You've learned **where AI fits** and **what risks emerge**. Now: design principles that auditors, regulators, and finance teams can trust.

Think of these as your **engineering guardrails**, constraints that keep AI useful without breaking SOX rules.

--- 
### Principle 1: Deterministic First

**Rule:** Evidence MUST be gathered through hard-coded, reproducible checks.

✅ **Acceptable:**

```python
# Deterministic SQL check*
missing_approvals = db.query("""
    SELECT invoice_id, amount
    FROM payables
    WHERE amount > 5000 
      AND approver_tier != 'VP'
      AND status = 'paid'
""")
```

❌ **Not acceptable:**

```python
# AI determining facts*
missing_approvals = llm.query(
    "How many payables were missing VP approval?"
)
```

**Why:** Deterministic checks are reproducible. Run the same SQL twice → same results. AI might give different answers each time.

--- 

### Principle 2: AI for Augmentation

**Rule:** AI's role is to **summarize, classify, map, narrate**—never to replace factual checks.

✅ **Good use:**

```python
# AI adds clarity to facts*
summary = llm.summarize(
    f"Explain these {len(missing_approvals)} violations in plain language for executives"
)
```

❌ **Bad use:**

```python
# AI making compliance decision*
decision = llm.evaluate("Does Control PAY-002 pass or fail?")
```

**Remember:** AI adds efficiency and insight, but humans + deterministic checks make the call.

--- 
### Principle 3: Separation of Concerns

**Rule:** SOX requires **independence** between preparer and reviewer. Multi-agent design must mirror this.

**Traditional SOX workflow:**

```python
Preparer (staff auditor) → gathers evidence, performs test
Reviewer (senior auditor) → independently validates, approves
```

**AI equivalent:**

```python
Evidence Agent → gathers data, runs deterministic checks
Classifier Agent → buckets exceptions, drafts narrative
Reviewer Agent → re-performs validation checks (different logic/tools)
Human Reviewer → final sign-off
```

**Why this matters:** If the same agent (or person) both prepares and reviews, there's no independence. External auditors will flag this.

**Code pattern:**

```python
class EvidenceAgent:
    """Preparer role: gather and check."""
    def gather_exceptions(self, control_id):
        return deterministic_check(control_id)

class ReviewerAgent:
    """Reviewer role: independent validation."""
    def validate_exceptions(self, evidence_agent_output):
        # Re-perform check with different method*
        recheck = alternative_validation(evidence_agent_output)
        if recheck != evidence_agent_output:
            raise IndependenceException("Results don't match")
        return {"validated": True, "reviewer": "agent_v2"}

# Workflow enforces separation*
evidence = EvidenceAgent().gather_exceptions("PAY-002")
validation = ReviewerAgent().validate_exceptions(evidence)
```
--- 
### Principle 4: Audit Trail Everywhere

**Rule:** Every AI-assisted step must be **logged and traceable.**

**What to log:**

- Inputs (data + prompts)
- Outputs (JSON + narratives)
- System version / model used
- Timestamp
- Who/what reviewed it

✅ **Production pattern:**

```python
def compliant_ai_workflow(control_id):
    # Step 1: Deterministic check*
    exceptions = sql_check(control_id)
    
    # Step 2: AI augmentation*
    ai_summary = llm.summarize(exceptions)
    
    # Step 3: Log everything*
    audit_log = {
        "timestamp": datetime.utcnow(),
        "control_id": control_id,
        "check_type": "sql_deterministic",
        "exceptions_count": len(exceptions),
        "ai_model": "gpt-4-turbo",
        "ai_prompt": "Summarize these exceptions...",
        "ai_output": ai_summary,
        "evidence_file": f"{control_id}_exceptions.json",
        "reviewed_by": None  # Awaiting human review*
    }
    
    save_to_audit_db(audit_log)
    
    return {
        "exceptions": exceptions,
        "summary": ai_summary,
        "audit_trail_id": audit_log["id"]
    }
```

**If asked "how did you reach this conclusion?"** → Show the full trail.

❌ **Black-box AI = unacceptable under SOX.**

--- 

### Principle 5: Evaluation Harness

**Rule:** Must be able to **re-run golden test cases** and get consistent results.

**Concept:** Build a test harness that validates AI behavior before using it in production.

```python
class SOXEvaluationHarness:
    """Test suite for AI-augmented SOX controls."""
    
    def __init__(self):
        self.golden_test_cases = [
            {
                "control_id": "PAY-002",
                "test_data": "payables_test_set_1.json",
                "expected_exceptions": 15,
                "expected_classification": {
                    "missing_approver": 10,
                    "wrong_tier": 5
                }
            },
            # ... more test cases*
        ]
    
    def validate_consistency(self, ai_system):
        """Run AI on golden cases, verify reproducibility."""
        for test_case in self.golden_test_cases:
            # Run AI*
            result = ai_system.process(test_case['test_data'])
            
            # Validate deterministic layer*
            assert result['exception_count'] == test_case['expected_exceptions'], \
                "Deterministic check failed—facts don't match"
            
            # Validate AI classification*
            assert result['classification'] == test_case['expected_classification'], \
                "AI classification inconsistent"
        
        return {"status": "validated", "tests_passed": len(self.golden_test_cases)}

# Usage before production deployment*
harness = SOXEvaluationHarness()
harness.validate_consistency(my_ai_system)
```

**In audit terms:** If you can't reproduce it, it doesn't count as evidence.

## Design Challenge: Build a Compliant Workflow

**Scenario:** You're building an AI system to summarize SOX 404 control test results for 500 payables exceptions across 10 business units.

**Requirements:**

- Deterministic exception detection
- AI-powered classification and summarization
- Audit trail for external auditors
- Reproducible results

**Your task (work in pairs):**

1. **Sketch the workflow:** What runs first? What does AI do? Where's the human review?
2. **Identify what gets logged:** List 5-7 items that must be in the audit trail
3. **Design validation:** How would you test this before production?

**Template to fill out:**

```python
WORKFLOW DESIGN:
Step 1 (Deterministic):
Step 2 (AI Augmentation):
Step 3 (Logging):
Step 4 (Review):

AUDIT TRAIL:
1. 
2. 
3. 
4. 
5. 

VALIDATION APPROACH:
- Golden test case 1:
- Golden test case 2:
- Reproducibility check:
```

<details>
<summary><strong>Sample Solution</strong></summary>

```
WORKFLOW DESIGN:

Step 1 (Deterministic):

- Run SQL query across all payables systems
- Flag exceptions: amount > threshold AND missing approval
- Output: 500 exceptions → exceptions_raw.json
- Count by business unit deterministically

Step 2 (AI Augmentation):

- LLM classifies each exception:
    - Missing approver
    - Wrong approval tier
    - Duplicate approval
    - Amount discrepancy
- LLM generates exec summary:
"500 exceptions identified across 10 BUs. EMEA shows highest
concentration (40%). Primary issue: missing VP approval."

Step 3 (Logging):

- Log:
    1. SQL query used
    2. Row count (500 exceptions)
    3. AI model (gpt-4-turbo-2024-04-09)
    4. Exact prompt sent
    5. Classification output
    6. Summary output
    7. Timestamp
    8. Evidence pointer (exceptions_raw.json)

Step 4 (Review):

- Reviewer Agent: Re-runs deterministic check → verifies 500 exceptions
- Human Reviewer: Spot-checks 10 random AI classifications
- Final sign-off: Senior auditor approves workpaper

AUDIT TRAIL (what gets logged):

1. SQL query text + parameters
2. Exception count per business unit
3. AI prompt template + variables
4. AI classification results (JSON)
5. AI summary text
6. Model version identifier
7. Reviewer validation results
8. Human reviewer ID + timestamp

VALIDATION APPROACH:

- Golden test case 1: Known dataset with 15 exceptions
→ AI should find exactly 15
→ Classification should match manual labels
- Golden test case 2: Empty dataset (no exceptions)
→ Should return 0 exceptions (not hallucinate)
- Reproducibility check:
→ Run same data through system 3 times
→ Exception count must be identical
→ AI summary should be semantically equivalent (use embeddings to check)
```

</details>

## Industry Best Practices

Based on PCAOB guidance and Big 4 firm practices:

**1. Human-in-the-Loop (HITL) is mandatory**

- PCAOB: "Firms do not allow AI to replace human judgment or supervision"
- Every AI output must be reviewed by qualified personnel
- Implementation: Add review checkpoints in your workflow

**2. Data governance before AI**

- "Garbage in, garbage out" applies forcefully
- Ensure data quality: completeness, accuracy, consistency
- Reality check: If your source data is 80% reliable, AI will amplify that 20% error

**3. Start with pilots on high-volume tasks**

- Test AI on routine journal entry testing first
- Run parallel validation (AI + manual) initially
- Expand only after proving reliability

**4. Secure tool selection**

- Use SOC 2 / ISO 27001 certified platforms for sensitive data
- Consider private LLM instances for confidential financial data
- Public LLM endpoints (like ChatGPT.com) are generally inappropriate for non-public financial data

**5. Integrate with existing control framework**

- If AI performs a control, it should be in your control matrices
- Apply general IT controls: change management, access control
- Test the AI system like any other automated control


## Takeaways

**Your role:** Build AI systems that are:

- **Summarizers** → Condense 500 exceptions into 3-sentence exec summary
- **Classifiers** → Bucket violations (missing approver, wrong tier, duplicate)
- **Mappers** → Link transactions to control IDs based on patterns
- **Assistants** → Draft workpapers in consistent, audit-ready format

**Not your role:**

- ❌ AI that decides pass/fail
- ❌ AI that fabricates evidence
- ❌ AI that operates without human oversight

**Your deliverables:**

- Python pipelines with deterministic checks as foundation
- LLM integrations for clarity and efficiency
- Comprehensive logging for audit trails
- Evaluation harnesses for reproducibility


## Knowledge Check 

Test your understanding:

**Question 1:** True or False: AI can decide if a SOX control passed or failed.

<details><summary>Answer</summary>
False. Only humans (with deterministic evidence) can make compliance decisions.  
</details>

**Question 2:** What must be logged for every AI-assisted step?

<details><summary>Answer</summary>
Input data (or hash), prompt, output, system version, timestamp, review status  
</details>

**Question 3:** In multi-agent design, what SOX principle does "preparer vs. reviewer" enforce?

<details><summary>Answer</summary>
Independence / separation of concerns. No one entity both prepares and approves evidence.  
</details>

**Question 4:** You run your AI classifier twice on the same exceptions and get different results. Is this a problem? Why?

<details><summary>Answer</summary>
Yes—big problem. Non-deterministic outputs undermine audit reliability. Fix: Use temperature=0, pin model versions, log outputs, and implement validation checks.  
</details>

**Question 5:** Can an LLM-generated summary serve as audit evidence by itself?

<details><summary>Answer</summary>
No. It must be tied to underlying source data and reviewed by a human. AI outputs are supporting analysis, not standalone evidence.  
</details>


## Module Summary & Key Takeaways

<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

1. **AI's role in SOX:** Assistant, not auditor. Augments workflows but doesn’t replace deterministic checks or human judgment.

1. **Where AI helps:** Eexception summarization, classification, workpaper drafting, workflow orchestration.

1. **Where AI fails:** Making compliance decisions, inventing evidence, operating without oversight.

1. **Key risks:** Hallucinations, traceability gaps, inconsistency, over-reliance, data quality issues.

1. **Regulatory stance:** PCAOB expect human oversight, audit trails, and reproducible evidence. No lowering of standards because AI is involved.

1. **Five design principles:**
   - Deterministic first (facts from code)
   - AI for augmentation (clarity from LLMs)
   - Separation of concerns (preparer ≠ reviewer)
   - Audit trail everywhere (log inputs, outputs, versions)
   - Evaluation harness (prove reproducibility)

</aside>


## **Practice & Discussion**

### Discussion Questions

1. **Think about a current manual SOX process in your role.** Where could AI provide the most value? What would be the compliance risks?
2. **If an external auditor asks: "How do you know your AI isn't hallucinating?"** — What would you show them?
3. **What’s the difference between AI summarizing exceptions vs. AI detecting exceptions?** Which is SOX-appropriate?
4. **How would you explain to a finance manager (non-technical) why AI outputs need human review?**


## Lesson references

### **Regulatory Guidance:**

- [PCAOB Spotlight on GenAI (July 2024)](https://pcaobus.org/news-events/speeches/speech-detail/staff-perspectives-on-generative-ai-in-audits)

