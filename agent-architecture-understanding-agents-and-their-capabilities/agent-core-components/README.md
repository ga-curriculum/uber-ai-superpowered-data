<h1>
  <span>

  ![alt text](../assets/ga-logo.png)

  </span>
  <span class="subhead">Core Components of Agentic Systems</span>
</h1>

**Learning objective:** Identify the core components of an agentic system.

## The Four Core Components of an Agentic System

Every well-designed agentic system has four essential components. Let's break them down:

### 1. **Orchestrator** (The Brain)

**What it does:** Decides what actions to take and in what order.

The orchestrator is like the senior auditor who:

- Reads the query
- Decides which tests to run
- Determines the sequence of procedures
- Combines results into a conclusion

**Example in code (conceptual):**

```python
def orchestrator(query: str):
    # Step 1: Understand the query
    intent = parse_query(query)

    # Step 2: Decide which tools to use
    if "compliance" in intent:
        tools = [get_transactions, check_policy_violations]

    # Step 3: Execute tools in order
    results = []
    for tool in tools:
        result = tool.execute()
        results.append(result)

    # Step 4: Generate final output
    return generate_summary(results)

```

**Real-world trigger:** User asks, *"Show me Q3 dual-approval violations."*

**Orchestrator's plan:**

1. Pull Q3 transactions
2. Filter for amounts > $1,000
3. Check approval records
4. Identify violations
5. Summarize findings

---

### 2. **Tools** (The Hands)

**What they are:** Deterministic functions that perform specific actions.

**Why they matter:** Tools provide **precise, verifiable evidence**. They don't "hallucinate"; they execute logic.

**Examples of tools:**

```python
# Tool 1: Query database
def get_payables(period: str, min_amount: float):
    """Pull payables from accounting system."""
    query = f"""
        SELECT transaction_id, amount, vendor, date, approver_1, approver_2
        FROM payables
        WHERE period = '{period}' AND amount >= {min_amount}
    """
    return database.execute(query)

# Tool 2: Check compliance rule
def check_dual_approval(transaction):
    """Verify PAY-002 compliance."""
    if transaction.amount > 1000:
        return (transaction.approver_1 is not None and
                transaction.approver_2 is not None)
    return True

# Tool 3: Generate evidence list
def list_violations(transactions):
    """Return list of non-compliant transaction IDs."""
    violations = []
    for txn in transactions:
        if not check_dual_approval(txn):
            violations.append(txn.transaction_id)
    return violations

```

**Key principle:** Tools do the **deterministic work** (math, lookups, filters). The LLM does the **narrative work** (summarizing, explaining).

---

### 3. **Memory** (The Notebook)

**What it does:** Keeps track of context, past actions, and intermediate results.

**Two types of memory:**

| Type           | Purpose                          | Example                                          |
| -------------- | -------------------------------- | ------------------------------------------------ |
| **Short-term** | Remember within a single session | "I already checked July, now checking August"    |
| **Long-term**  | Recall across sessions           | "User always wants violations grouped by vendor" |

**Why it matters in compliance:**

- Avoid redundant checks
- Track which controls have been tested
- Remember user preferences for report formats

**Conceptual example:**

```python
class AgentMemory:
    def __init__(self):
        self.conversation_history = []
        self.facts_collected = {}
        self.user_preferences = {}

    def remember_fact(self, key, value):
        """Store a piece of evidence."""
        self.facts_collected[key] = value

    def recall_fact(self, key):
        """Retrieve previously collected evidence."""
        return self.facts_collected.get(key)

```

---

### 4. **Logging/Tracing** (The Audit Trail)

**What it does:** Records every step the agent takes.

**Why it's critical for SOX:**

- Auditors need to see **how** conclusions were reached
- Regulators require **evidence** of control testing
- Teams need to **debug** when things go wrong

**What gets logged:**

- Query received
- Tools selected and called
- Data retrieved (or errors encountered)
- LLM prompts and responses
- Final output delivered

**Example log structure:**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-07-15T14:32:00Z",
  "query": "Check PAY-002 compliance for July",
  "steps": [
    {
      "step": 1,
      "action": "tool_call",
      "tool": "get_payables",
      "params": {"period": "2025-07", "min_amount": 1000},
      "result": "142 transactions retrieved"
    },
    {
      "step": 2,
      "action": "tool_call",
      "tool": "check_dual_approval",
      "result": "8 violations found",
      "violation_ids": ["PAY-2025-1847", "PAY-2025-1923", ...]
    },
    {
      "step": 3,
      "action": "llm_generation",
      "prompt": "Summarize findings citing PAY-002...",
      "response": "Testing revealed 8 instances..."
    }
  ],
  "final_output": "Testing revealed 8 instances where..."
}

```

> Ah-ha Moment: Logging isn't just for debugging — it's your workpaper documentation. Every agent interaction should produce a traceable record.
> 

---

## Putting It Together: Component Interaction

Here's how the components work together:

```
┌─────────────────────────────────────────────────────┐
│  USER QUERY: "Did we comply with PAY-002 in July?"  │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │   ORCHESTRATOR       │ ← Decides: Need to check payables
            │   (The Brain)        │   then generate summary
            └──────────┬───────────┘
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
    ┌─────────┐                 ┌─────────┐
    │  TOOLS  │                 │ MEMORY  │
    │  (Hands)│                 │(Notebook)│
    └────┬────┘                 └────┬────┘
         │                           │
         │ Executes:                 │ Recalls:
         │ - get_payables()          │ - Policy text
         │ - check_dual_approval()   │ - Previous tests
         │                           │
         └─────────────┬─────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  LOGGING/TRACING     │ ← Records every step
            │  (Audit Trail)       │
            └──────────┬───────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │  FINAL OUTPUT:              │
         │  "Testing of 142 July       │
         │  payables revealed 8        │
         │  violations of PAY-002..."  │
         └─────────────────────────────┘

```
