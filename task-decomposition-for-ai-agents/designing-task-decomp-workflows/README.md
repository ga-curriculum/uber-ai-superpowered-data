<h1>
  <span>

  ![alt text](../assets/ga-logo.png)

  </span>
  <span class="subhead">Decomposition Framework & Case Study</span>
</h1>

**Learning objective:** Explain how to break down complex compliance questions into clear, verifiable steps that combine precise checks with AI-generated summaries.

## Practical Decomposition Framework

Here's a step-by-step process for decomposing any compliance task:

### Step 1: Identify the Goal

**Question:** What is the user really asking for?

**Example:**

- Surface question: "Check PAY-002 compliance"
- Real goal: "Verify all high-value payables had dual approval + produce audit evidence"

### Step 2: List Required Information

**Question:** What data or knowledge is needed?

**Example:**

- Payables data for specific period
- PAY-002 policy text
- Approval records
- Threshold values

### Step 3: Separate Deterministic and Probabilistic

**Question:** Which parts require precision vs narrative?

**Example - Deterministic:**

- Pull payables: SQL query
- Filter by amount: Python logic
- Check approval status: Database lookup
- Count violations: Arithmetic

**Example - Probabilistic:**

- Explain policy: LLM interpretation
- Summarize findings: LLM synthesis
- Suggest next steps: LLM reasoning

### Step 4: Design the Workflow

**Question:** What's the sequence of operations?

**Example:**

```
User Query: "Check PAY-002 compliance for July"
    │
    ▼
[Step 1: Retrieve policy] ← Deterministic (fetch from knowledge base)
    │
    ▼
[Step 2: Pull July payables] ← Deterministic (SQL query)
    │
    ▼
[Step 3: Filter amount > $1000] ← Deterministic (Python filter)
    │
    ▼
[Step 4: Check each for dual approval] ← Deterministic (lookup)
    │
    ▼
[Step 5: Collect violations] ← Deterministic (list building)
    │
    ▼
[Step 6: Generate summary] ← Probabilistic (LLM narrative)
    │
    ▼
[Step 7: Log all steps] ← Deterministic (write to log)
    │
    ▼
Final Output: Audit-ready summary + evidence

```

### Step 5: Define Success Criteria

**Question:** How do we know it worked?

**Example:**

- [ ] All transactions in period were checked
- [ ] Violations include transaction IDs
- [ ] Summary cites PAY-002 explicitly
- [ ] All steps are logged
- [ ] Output includes both evidence and narrative


## Decomposition in Action: PAY-002 Case Study

Let's walk through a complete example.

### The Scenario

**User query:** "Did we comply with PAY-002 in July? Show me any issues."

**Policy PAY-002:** All payments over $1,000 require dual approval before processing.

### Bad Decomposition (Human-Style)

```
❌ Step 1: Ask LLM to check compliance
❌ Step 2: LLM generates answer
❌ Step 3: Return answer to user
```

**What goes wrong:**

- LLM has no access to transaction data
- LLM might hallucinate compliance status
- No evidence trail
- Can't verify results

## Good Decomposition (AI-Native)

```python
# STEP 1: Retrieve policy (Deterministic)
def get_policy():
    policy = knowledge_base.search("PAY-002")
    return {
        "name": "PAY-002",
        "description": "Dual Approval Control",
        "threshold": 1000,
        "requirement": "Two approvers required for payments > $1000"
    }

# STEP 2: Pull July payables (Deterministic)
def get_july_payables():
    query = """
        SELECT
            transaction_id,
            amount,
            vendor_name,
            transaction_date,
            approver_1_id,
            approver_1_date,
            approver_2_id,
            approver_2_date
        FROM payables
        WHERE transaction_date >= '2025-07-01'
          AND transaction_date <= '2025-07-31'
    """
    return database.execute(query)

# STEP 3: Identify transactions requiring dual approval (Deterministic)
def filter_high_value(transactions):
    return [txn for txn in transactions if txn.amount > 1000]

# STEP 4: Check each transaction (Deterministic)
def check_compliance(transactions):
    violations = []
    compliant = []

    for txn in transactions:
        if txn.amount > 1000:
            has_dual_approval = (
                txn.approver_1_id is not None and
                txn.approver_2_id is not None
            )

            if not has_dual_approval:
                violations.append({
                    "transaction_id": txn.transaction_id,
                    "amount": txn.amount,
                    "vendor": txn.vendor_name,
                    "issue": "Missing dual approval"
                })
            else:
                compliant.append(txn.transaction_id)

    return violations, compliant

# STEP 5: Generate narrative (Probabilistic)
def generate_summary(policy, total_tested, violations, compliant_ids):
    prompt = f"""
    You are writing an audit workpaper entry.

    Control tested: {policy['name']} - {policy['description']}
    Requirement: {policy['requirement']}

    Testing scope:
    - Period: July 2025
    - Transactions tested: {total_tested}
    - Threshold: ${policy['threshold']}

    Results:
    - Compliant: {len(compliant_ids)} transactions
    - Violations: {len(violations)} transactions

    Violation details:
    {json.dumps(violations, indent=2)}

    Write a 3-paragraph summary:
    1. Scope and methodology
    2. Findings (include specific transaction IDs)
    3. Conclusion on control effectiveness

    Use professional audit language.
    """

    return llm.generate(prompt)

# ORCHESTRATOR: Puts it all together
def check_pay002_compliance(period: str):
    # Log start
    log("Starting PAY-002 compliance check", period=period)

    # Step 1: Get policy
    policy = get_policy()
    log("Policy retrieved", policy=policy)

    # Step 2: Get data
    transactions = get_july_payables()
    log("Transactions retrieved", count=len(transactions))

    # Step 3: Filter
    high_value = filter_high_value(transactions)
    log("High-value transactions identified", count=len(high_value))

    # Step 4: Check compliance
    violations, compliant = check_compliance(high_value)
    log("Compliance check complete",
        violations=len(violations),
        compliant=len(compliant))

    # Step 5: Generate summary
    summary = generate_summary(
        policy=policy,
        total_tested=len(high_value),
        violations=violations,
        compliant_ids=compliant
    )
    log("Summary generated")

    # Return structured output
    return {
        "summary": summary,
        "evidence": {
            "transactions_tested": len(high_value),
            "violations": violations,
            "compliant_count": len(compliant)
        },
        "logs": get_session_logs()
    }

```

### Why This Works

1. **Clear steps:** Each function has one job
2. **Verifiable evidence:** Tools produce precise outputs
3. **Appropriate use of LLM:** Only for narrative synthesis
4. **Complete audit trail:** Every step logged
5. **Reproducible:** Same input → same output

## Common Decomposition Mistakes

Avoid these pitfalls:

### Mistake 1: Asking LLM to Do Everything

```python
❌ BAD:
def check_compliance(query: str):
    prompt = f"{query}. Check our database and tell me if we're compliant."
    return llm.generate(prompt)

```

**Why it fails:** LLM has no database access, will hallucinate.

> **Fix:** Decompose into tools (data) + LLM (narrative).

---

### Mistake 2: Vague Tool Instructions

```python
❌ BAD:
def get_transactions():
    # What period? What filters? What fields?
    return database.query("SELECT * FROM transactions")

```

**Why it fails:** Ambiguity leads to wrong data retrieval.

> **Fix:** Be explicit about parameters, filters, date ranges.

---

### Mistake 3: Mixing Deterministic and Probabilistic

```python
❌ BAD:
def analyze_compliance(transactions):
    # This uses LLM to count violations - WRONG!
    prompt = f"Count violations in: {transactions}"
    return llm.generate(prompt)

```

**Why it fails:** Counting is deterministic, shouldn't use LLM.

> **Fix:** Use tools for precision, LLM for narrative only.

---

### Mistake 4: No Evidence Trail

```python
❌ BAD:
def quick_check():
    result = run_compliance_check()
    return "Looks compliant"  # Where's the proof?

```

**Why it fails:** No evidence for auditors to review.

> **Fix:** Always return data + logs + narrative.
