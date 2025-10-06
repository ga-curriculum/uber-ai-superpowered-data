<h1>
   <span>

   ![alt text](./assets/ga-logo.png)

   </span>
   <span class="subhead">Concepts: A Mindset Shift in Approach</span>
</h1>

**Learning objective:**  Explain the difference between deterministic and probabilistic systems.

## Why This Matters

**Scenario: Material Weakness in the Audit**

Last quarter, an external auditor flagged 57 vendor payments missing dual approval. The audit report stated: "Control PAY-002 failed due to systematic override of approval workflows."

Your manager asks: "Can we automate PAY-002 testing going forward?"

You think: "Easy, I'll use an LLM to read payment memos and check for approvals."

But here's the problem: LLMs don't count. They interpret. And in compliance, the difference between 1 approver and 2 approvers is the difference between a clean audit and a material weakness.


## A Brief History: From Rules to Models

### The Deterministic Era (1950s–2010s)

For decades, software engineering was fundamentally deterministic. You wrote explicit rules, and the computer followed them exactly:

```python
# 1960s: COBOL accounting system
IF PAYMENT-AMOUNT > 1000
    IF APPROVER-COUNT < 2
        MOVE "REJECTED" TO PAYMENT-STATUS
    END-IF
END-IF.

```

**The trade-off:** Every edge case required a new rule. Systems became brittle. A 2015 study found that enterprise rule engines at large banks contained over 10,000 rules, and 30% had conflicting logic.

### The Probabilistic Shift (2012–Present)

The rise of machine learning introduced a fundamentally different paradigm: instead of writing rules, you train models on data.

**Key milestones:**

- 2012: Deep learning proves effective for image recognition (AlexNet)
- 2017: Transformers architecture enables language models (BERT, GPT)
- 2022: Large Language Models (ChatGPT, Claude) demonstrate emergent reasoning capabilities

**What changed:** Instead of asking "What rule covers this case?", we now ask "What patterns did the model learn from millions of examples?"

```python
# 2025: LLM-based classification
prompt = "Does this payment memo indicate dual approval?"
response = llm.generate(prompt)  # Could return different answers each run

```

**The trade-off:** Models are flexible and scale to ambiguous inputs, but they're non-deterministic. The same input can produce different outputs.

### Why Finance Is Still Catching Up

The regulatory gap: SOX (2002), Basel III (2010), and most compliance frameworks were written assuming deterministic systems. They require:

- Reproducible test results
- Explicit control documentation
- Audit trails that prove exactly what happened

The challenge: How do you reconcile "this model is 94% accurate" with "this control must operate effectively 100% of the time"?

**The answer:** Hybrid systems. Use deterministic logic for evidence, probabilistic models for interpretation.

## Deterministic Systems

### Definition

A deterministic system follows explicit rules to transform inputs into outputs. The same input produces the same output across every execution.

Core property: f(x) = y always, no exceptions.

### Properties

| Property | Description |
| --- | --- |
| Rule-based logic | Every decision follows an if-then-else path |
| Predictable | Output is known before execution |
| Reproducible | Run it 1,000 times, get 1,000 identical results |
| Zero ambiguity | No interpretation required |

### Examples in Finance Workflows

1. **Financial Calculation**

```python
def calculate_withholding(gross_amount: float, tax_rate: float) -> float:
    """
    Calculate tax withholding.
    Same inputs always produce same output.
    """
    return gross_amount * tax_rate

# Always returns 150.0
withholding = calculate_withholding(1000.0, 0.15)

```

Why deterministic matters here: Tax agencies require exact calculations. An error of $0.01 can compound to millions in penalties across thousands of employees.

2. **SQL Validation Query**

```sql
-- Control PAY-002: Dual approval for payments > $1000
SELECT
    p.payable_id,
    p.amount,
    p.posting_date,
    COUNT(a.approver_id) AS approver_count
FROM payables p
LEFT JOIN approvals a ON p.payable_id = a.payable_id
WHERE p.amount > 1000
  AND p.posting_date BETWEEN '2025-07-01' AND '2025-07-31'
GROUP BY p.payable_id, p.amount, p.posting_date
HAVING COUNT(a.approver_id) < 2;

```

Why deterministic matters here: This query is your SOX evidence. Auditors will re-run it. If it returns different results, your control fails.

3. **Rule Engine Implementation**

```python
class PAY002Validator:
    """
    Validates dual approval control.
    Implements explicit business rules.
    """
    THRESHOLD = 1000.0
    REQUIRED_APPROVERS = 2

    def validate(self, payable: dict) -> dict:
        """
        Returns pass/fail status with reason.
        Fully deterministic logic.
        """
        if payable["amount"] <= self.THRESHOLD:
            return {
                "status": "PASS",
                "reason": "Below threshold"
            }

        if payable["approver_count"] >= self.REQUIRED_APPROVERS:
            return {
                "status": "PASS",
                "reason": "Sufficient approvals"
            }

        return {
            "status": "FAIL",
            "reason": f"Missing approvals: {payable['approver_count']}/{self.REQUIRED_APPROVERS}"
        }

# Same input always produces same output
validator = PAY002Validator()
result = validator.validate({"amount": 1500, "approver_count": 1})
# Always returns: {"status": "FAIL", "reason": "Missing approvals: 1/2"}

```

### Strengths

- Precision: No rounding errors, no interpretation gaps
- Auditability: Every decision can be traced to a specific rule
- Reproducibility: Perfect for compliance testing
- Debuggability: When something fails, you know exactly which rule triggered

### Limitations

- Brittle with ambiguity: Cannot handle "the CFO verbally approved this"
- Hard to scale: Unstructured inputs (emails, PDFs, chat logs) require custom parsers
- Maintenance burden: Every new edge case means new rules and growing complexity
- Cannot learn: Rules do not improve from experience

Real-world example: A vendor sends an email saying "Per our call, Jane and Bob both approved the $5K office furniture payment." A deterministic system cannot extract "Jane" and "Bob" as approvers without someone writing a parser for every possible email phrasing.

## Probabilistic Systems and LLMs

### Definition

A probabilistic system generates outputs by sampling from a probability distribution learned from data. With identical inputs, outputs can vary.

Core property: f(x) = y₁ on run 1, f(x) = y₂ on run 2, where y₁ ≈ y₂.

### How LLMs Work (Simplified)

When you prompt an LLM:

- **Input encoding:** Your text becomes a sequence of numbers (tokens)
- **Probability distribution:** The model predicts likely next tokens based on patterns learned from training data
- **Sampling:** The model selects from high-probability options, not always the single highest probability option

Analogy: Imagine autocomplete on your phone, but for entire paragraphs. It predicts what sounds right based on billions of examples, not what is factually correct.

### The Role of Temperature

Temperature controls how much randomness is injected into the model's output.

```python
# Lower temperature = more predictable
response = llm.generate(
    prompt="Summarize the violations",
    temperature=0.3  # Conservative sampling
)

# Higher temperature = more creative
response = llm.generate(
    prompt="Write a haiku about compliance",
    temperature=1.2  # Wild sampling
)

```

### Temperature Scale

| Range   | Behavior                                                                                                      | Use Case                               |
| ------- | ------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| 0.0     | Near-deterministic phrasing (picks highest probability tokens). Not truly deterministic, still some variation |                                        |
| 0.3–0.5 | Low variance, focused, consistent                                                                             | Compliance summaries, audit narratives |
| 0.7–0.9 | Balanced creativity and coherence                                                                             | Marketing copy, brainstorming          |
| 1.0–1.5 | High variance, creative, sometimes incoherent                                                                 | Creative writing, idea generation      |

For compliance workflows: prefer temperature ≤ 0.5.

## Quick Lab: Why Temperature Matters

**Exploring same prompt at different temperatures:**

### **Setup**

```python
prompt = """
Summarize the PAY-002 violations found in July 2025.

Facts:
- 57 violations identified
- All exceeded $1000 threshold
- All had fewer than 2 approvers
"""

```

### Results

| Temperature | Output                                                                                                              | Analysis                                                          |
| ----------- | ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| 0.3         | "57 payments in July 2025 lacked dual approval for amounts exceeding $1000, violating control PAY-002."             | Precise, factual, audit-ready                                     |
| 0.7         | "Several payments in July appear to have missed the approval requirement, with 57 cases flagged."                   | Vague ("appear to have"), hedging language                        |
| 1.2         | "A concerning pattern emerged: payments slipped through the system, raising questions about control effectiveness." | Subjective ("concerning"), invented narrative ("slipped through") |

<aside style="background-color:#2a2a2a; padding: 1.3rem 2rem .33rem; border-radius: .5rem">

**Key Insight:** Higher temperature yields vaguer language that is harder to audit

💡 **Rule of thumb:** If an auditor would ask "How many?" or "Which ones?", use temperature ≤ 0.5.

</aside>

## Risks in Compliance Contexts

1. **Hallucination**
    
   > ❓ What it is: The model invents details that sound plausible but are not in the input data.

   Example:

   > Input: "57 violations in July 2025"

   > Hallucinated output: "57 violations in July 2025, primarily from the IT and Facilities departments."
    
   <br>

2. **Inconsistency** 
    
   > ❓ What it is: The model gives contradictory answers across runs.

   Example:

   > Run 1: "Control PAY-002 was not operating effectively"

   > Run 2: "Control PAY-002 operated effectively with minor exceptions"
        
   <br>
   
3. **Ambiguity**

   > ❓ What it is: Vague language that does not support audit conclusions.

   Example:

   > Bad: "Several issues were identified"

   > Good: "57 violations were identified"
    

## Mini-Exercise: Spot the Hallucination

You ran a SQL query and got these facts:

- 57 violations
- Period: July 2025
- Control: PAY-002 (dual approval for payments > $1000)
- Method: SQL query against approvals table

You ask three different LLMs to summarize. Which summaries introduce unsupported details?

**Summary A:**

"In July 2025, 57 payments exceeded the $1000 threshold without dual approval, primarily from the Facilities and IT departments."

**Summary B:**

"57 vendor payments in July 2025 lacked required dual approval for amounts over $1000, violating control PAY-002."

**Summary C:**

"The audit identified 57 high-risk payments in July, including 3 emergency purchases that bypassed the approval workflow."

[PAUSE HERE - Discuss with a partner before scrolling]

<details>
<summary><b>Click to reveal answer</b></summary>

Summary A invents:

- "primarily from the Facilities and IT departments" (not in input)

Summary B:

- Faithful to the facts, only restates what was provided

Summary C invents:

- "high-risk" (subjective characterization not in input)
- "3 emergency purchases" (specific claim not in input)
- "bypassed the approval workflow" (explanation not in input)

Key takeaway: LLMs fill gaps with plausible-sounding details. In compliance, plausible is not admissible.

</details>
