<h1>
  <span>

  ![alt text](/assets/ga-logo.png)

  </span>
  <span class="subhead">Risks & Standards Context</span>
</h1>

**Learning objective:** Evaluate AI risks in SOX workflows and apply standards to ensure evidence integrity and reproducibility.

## The Core Question

Once AI enters SOX workflows, regulators ask:

> "Does this technology preserve audit evidence integrity?"

The answer depends on understanding **what can go wrong** and **what regulators expect**.

## Key Risks When AI Meets SOX

| **Risk**                 | **What It Looks Like**                                           | **Why It Breaks SOX**                                                                      |
| ------------------------ | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Hallucination**        | AI fabricates approver names or transaction IDs that don’t exist | Invalidates evidence → audit failure. You can’t rely on made-up data.                      |
| **Traceability gaps**    | No record of what prompt/data produced an output                 | Breaks audit trail. PCAOB requires reproducibility — “show me how you got this answer.”    |
| **Bias / inconsistency** | Same query yields different outputs on two runs                  | Undermines control testing reliability. If results aren’t stable, they aren’t trustworthy. |
| **Over-reliance**        | Management signs off on AI summary without checking source data  | Violates independence. AI can’t be the final authority — humans must validate.             |

> ⚠️ **The most dangerous failures are subtle:** Outputs that *look* plausible but aren't reproducible or traceable.

## Real-World Example: The Hallucination Problem

**Scenario:** Your AI agent generates this workpaper:

> "Control JE-005 (Journal Entry Review) tested on 2025-03-15. Reviewer John Smith approved 847 entries. No exceptions identified."

**Problem:** John Smith was on vacation that week. The AI hallucinated his involvement.

**Impact:** External auditors flag this as unreliable evidence. Your SOX 404 testing is now in question.

**Prevention:**

```python
# Always validate AI outputs against source data*
ai_output = llm.generate_workpaper(data)

# Deterministic validation*
actual_reviewer = db.query("SELECT reviewer FROM approvals WHERE date = '2025-03-15'")
if ai_output.reviewer != actual_reviewer:
    raise AuditException("AI output doesn't match source data")
```

## Regulatory & Standards Landscape

**PCAOB (Public Company Accounting Oversight Board):**

- July 2024 Spotlight Report on GenAI in audits
- Key finding: Firms using AI still require **human judgment and supervision** for all outputs
- Standard: Technology-assisted analysis acceptable ONLY if evidence is **complete, accurate, reproducible**
- Warning: "AI said so" is not audit documentation

**SEC (Securities and Exchange Commission):**

- No AI-specific SOX rules (yet)
- Focus: Risk disclosure, governance, management responsibility
- Expectation: Management certifies accuracy—AI doesn't change that duty

**AICPA / CAQ (Audit Standards Bodies):**

- Encourage AI experimentation
- Stress: Human oversight is non-negotiable
- Guidance: AI as assistive tool, not authoritative source

**Big 4 Audit Firms:**

- Running AI pilots: EY Helix, PwC Halo, Deloitte AI Lab
- Positioning: AI speeds evidence prep, but **auditors still validate**
- Internal policy: AI outputs always reviewed by qualified personnel

**The universal message:** *No regulator has blessed AI outputs as audit evidence on their own.*


## What This Means

**Three compliance questions that must always be answered:**

1. **Can we re-perform the AI's steps deterministically?**
    - If you can't reproduce results, they're not audit evidence
    - Solution: Log inputs, versions, parameters
2. **Do we have a logged trail of input → output?**
    - Audit trail must show: what data went in, what prompt was used, what came out
    - Solution: Structured logging at every AI interaction
3. **Would an external auditor accept this evidence?**
    - Test: Could Deloitte look at your logs and workpapers and trace your conclusion?
    - Solution: Treat AI outputs as supporting analysis, not final evidence

## Exercise: Risk Identification & Mitigation

**Instructions:** For each scenario below, identify:

1. What SOX risk is present?
2. How would you mitigate it?

**Scenario A:**
Your AI agent pulls transaction logs and classifies exceptions. You run it twice on the same data and get different results:

- Run 1: 47 exceptions
- Run 2: 52 exceptions

**Scenario B:**
An LLM generates a workpaper stating: "All segregation-of-duties controls are effective based on my analysis of user access logs."

**Scenario C:**
Your evidence-gathering agent has access to production financial systems. It retrieves data by directly querying databases. No one monitors what it accesses.

<details>
<summary><strong>Solutions</strong></summary>

**Scenario A: Inconsistency Risk**

- **Risk:** Bias/inconsistency—non-deterministic outputs undermine reliability
- **Mitigation:**
    - Use temperature=0 for classification tasks (makes LLM deterministic)
    - Implement validation: if classifications differ, flag for human review
    - Consider rule-based classifier instead of LLM for this task

**Scenario B: Hallucination + Over-reliance Risk**

- **Risk:** AI making compliance judgment without showing evidence
- **Mitigation:**
    - Require AI to cite specific log entries for each claim
    - Have human reviewer spot-check 10% of cited evidence
    - Rewrite prompt: "List specific SoD violations found" vs. "assess effectiveness"

**Scenario C: Security & Traceability Risk**

- **Risk:** Unmonitored access could expose sensitive data or create audit trail gaps
- **Mitigation:**
    - Log every database query the agent executes
    - Implement least-privilege access (agent only queries specific tables)
    - Add approval workflow for sensitive data access

</details>

---

### Code Example: Audit Trail Logging Pattern

Here's an example pattern for logging AI interactions:

```python
import json
from datetime import datetime
from hashlib import sha256

class AuditLogger:
    """Log every AI interaction for SOX compliance."""
    
    def log_ai_step(self, step_type, input_data, prompt, output, model_version):
        """
        Create auditable record of AI processing.
        
        Args:
            step_type: Type of operation (e.g., 'summarization', 'classification')
            input_data: Source data used (dict or dataframe info)
            prompt: Exact prompt sent to AI
            output: AI's response
            model_version: Model identifier (e.g., 'gpt-4-0613')
        """
        # Create reproducible hash of input data*
        input_hash = sha256(
            json.dumps(input_data, sort_keys=True).encode()
        ).hexdigest()
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "step_type": step_type,
            "input_hash": input_hash,
            "input_row_count": len(input_data) if isinstance(input_data, list) else 1,
            "prompt": prompt,
            "output": output,
            "model": model_version,
            "reproducible": True,
            "reviewed": False,  *# Flag for human review*
            "reviewer_id": None
        }
        
        # Store in audit database*
        self.save_to_audit_trail(audit_entry)
        return audit_entry
    
    def validate_reproducibility(self, original_entry_id):
        """Re-run AI step and verify same output."""
        original = self.get_entry(original_entry_id)
        
        # Re-run with same inputs*
        new_output = self.run_ai_step(
            original['input_data'],
            original['prompt'],
            original['model']
        )
        
        if new_output != original['output']:
            raise AuditException(
                f"Non-reproducible output detected for entry {original_entry_id}"
            )

# Usage in your workflow*
logger = AuditLogger()

# Step 1: Deterministic check*
exceptions = deterministic_payables_check()

# Step 2: AI summarization*
summary = llm_summarize(exceptions)

# Step 3: Log everything*
logger.log_ai_step(
    step_type="exception_summary",
    input_data=exceptions,
    prompt="Summarize these payables exceptions in 3 sentences",
    output=summary,
    model_version="gpt-4-turbo-2024"
)
```

**Why this works for SOX:**

- ✅ Timestamps every interaction
- ✅ Creates reproducible hash of inputs
- ✅ Logs exact prompt and output
- ✅ Tracks model version (important for consistency)
- ✅ Includes review flags for human oversight
- ✅ Enables validation re-runs

---

## Key Takeaways 

<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

1. **AI introduces risks**: hallucination, traceability gaps, inconsistency, over-reliance
1. **Regulators' stance is clear**: AI may assist, not replace, audit evidence. Complete, accurate, reproducible evidence is non-negotiable.
1. **Your responsibility**: Build audit trails that show how AI reached conclusions. Log inputs, prompts, outputs, versions.
1. **Human oversight required**: PCAOB, SEC, and audit firms all require qualified personnel to review and approve AI outputs

</aside>
