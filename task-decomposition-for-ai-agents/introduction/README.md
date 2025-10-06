<h1>
  <span>

  ![alt text](../assets/ga-logo.png)

  </span>
  <span class="subhead">Concepts: Understanding AI Task Decomposition</span>
</h1>

**Learning objective:** Explain why AI task decomposition differs from human logic; compare deterministic vs AI-native approaches.

## What is Task Decomposition?

### Definition

**Task decomposition** is the process of breaking down a complex goal into smaller, well-defined steps that can be executed reliably.

For AI agents, this means:

- Taking a high-level question or goal
- Breaking it into atomic actions
- Assigning each action to the right executor (tool vs LLM)
- Defining the sequence and dependencies

### Why It Matters for Agents

**Without decomposition:**

- Agents guess at what you want
- Steps get skipped or done in wrong order
- No clear evidence trail
- Outputs vary wildly between runs

**With decomposition:**

- Clear workflow from query to output
- Each step has one job
- Tools handle precision, LLM handles narrative
- Reproducible, auditable results

### The SOX Connection

Remember: SOX requires **evidence + documentation + repeatability**.

Good decomposition ensures:

- **Evidence:** Tools produce verifiable facts
- **Documentation:** Each step is logged
- **Repeatability:** Same query → same process → same result


## Two Approaches to Decomposition

There are two ways to think about breaking down tasks. Understanding the difference is crucial.

### Approach 1: Human-Style Decomposition

**How humans naturally break down tasks:**

**Task:** "Check Q3 compliance with REV-001"

**Human thinking:**

1. "First, I'll review what REV-001 requires"
2. "Then I'll pull some revenue transactions"
3. "I'll spot-check for issues"
4. "I'll write up what I found"

**Why this fails for agents:**

- Too vague ("some transactions" — how many?)
- Relies on intuition ("spot-check" — what criteria?)
- No clear success criteria ("write up" — what format?)
- Mixes deterministic and probabilistic thinking

**The result:** An agent following these instructions will hallucinate, miss steps, or produce unusable output.

---

### Approach 2: AI-Native Decomposition

**How to decompose for agent success:**

**Task:** "Check Q3 compliance with REV-001"

**AI-native breakdown:**

**Step 1 (Deterministic):** Retrieve policy

```python
policy = get_policy_text("REV-001")
requirements = parse_requirements(policy)
# Result: List of specific checks to perform

```

**Step 2 (Deterministic):** Pull relevant data

```python
transactions = get_revenue_transactions(
    start_date="2025-07-01",
    end_date="2025-09-30",
    status="all"
)
# Result: Complete dataset for Q3

```

**Step 3 (Deterministic):** Apply compliance checks

```python
for requirement in requirements:
    violations = check_compliance(transactions, requirement)
    log_results(requirement, violations)
# Result: List of specific violations with transaction IDs

```

**Step 4 (Probabilistic):** Generate narrative

```python
prompt = f"""
Given these findings: {violations}
Write a 3-paragraph compliance summary:
- State total transactions tested
- List violations by type with IDs
- Cite REV-001 requirements
"""
summary = llm.generate(prompt)
# Result: Auditor-ready narrative

```

**Why this works:**

- ✅ Each step is explicit and unambiguous
- ✅ Clear separation: data (tools) vs narrative (LLM)
- ✅ Verifiable outputs at each stage
- ✅ Complete audit trail

## The Core Split: Deterministic vs Probabilistic

The key to good decomposition is knowing **what type of task you're dealing with**.

### Deterministic Tasks (For Tools)

**Definition:** Tasks with ONE correct answer, calculable through logic or rules.

**Characteristics:**

- Precise inputs → Precise outputs
- No ambiguity or interpretation needed
- Must be 100% accurate
- Repeatable with identical results

**Examples:**

| Task | Why Deterministic | Tool to Use |
| --- | --- | --- |
| Count transactions over $1,000 | Simple filter + count | SQL query or Python filter |
| Check if dual approval exists | Boolean logic | Database lookup function |
| Calculate Days Sales Outstanding | Standard formula | Python calculation |
| Find missing approval dates | Data completeness check | Validation function |
| Sum invoice amounts by vendor | Aggregation | SQL GROUP BY |

**Code example:**

```python
def check_dual_approval(transaction_id: str) -> Dict:
    """Deterministic check for PAY-002 compliance."""
    txn = db.get_transaction(transaction_id)

    result = {
        "transaction_id": transaction_id,
        "amount": txn.amount,
        "requires_dual_approval": txn.amount > 1000,
        "approver_1": txn.approver_1,
        "approver_2": txn.approver_2,
        "compliant": False
    }

    if txn.amount > 1000:
        result["compliant"] = (txn.approver_1 is not None and
                               txn.approver_2 is not None)
    else:
        result["compliant"] = True

    return result

```

### Probabilistic Tasks (For LLMs)

**Definition:** Tasks requiring interpretation, synthesis, or natural language generation.

**Characteristics:**

- No single "right" answer
- Requires judgment or creativity
- Needs to sound natural to humans
- Some variation is acceptable (even desirable)

**Examples:**

| Task | Why Probabilistic | LLM Role |
| --- | --- | --- |
| Explain policy in plain language | Needs interpretation + clarity | Generate explanation |
| Summarize findings | Requires synthesis + prioritization | Write narrative |
| Compare to industry standards | Needs contextual knowledge | Provide analysis |
| Suggest remediation steps | Requires reasoning | Generate recommendations |
| Write executive summary | Needs audience adaptation | Craft communication |

**Code example:**

```python
def generate_compliance_summary(violations: List[Dict]) -> str:
    """Probabilistic narrative generation."""
    prompt = f"""
    You are a financial auditor writing a compliance summary.

    Evidence collected:
    - Total transactions tested: {len(all_transactions)}
    - Violations found: {len(violations)}
    - Policy: PAY-002 (Dual Approval for amounts > $1,000)

    Violation details:
    {json.dumps(violations, indent=2)}

    Write a 3-paragraph summary:
    1. Scope of testing
    2. Findings with specific transaction IDs
    3. Compliance conclusion

    Use professional audit language. Cite PAY-002 explicitly.
    """

    return llm.generate(prompt)

```
