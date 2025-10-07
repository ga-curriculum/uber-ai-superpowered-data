<h1>
  <span>

  ![alt text](/assets/ga-logo.png)

  </span>
  <span class="subhead">Activity: Design Task Decomposition Workflows</span>
</h1>

**Learning objective:** Practice breaking down a compliance-related request into AI-ready steps; discuss outcomes and tradeoffs. 

## Practice Exercise: Decompose This!

Let's apply what you've learned.

### Scenario

**User query:** "Analyze Q3 revenue recognition compliance with REV-001. Are we following the policy? Show me any exceptions."

**REV-001 Policy:** Revenue can only be recognized when:

1. Service has been delivered
2. Customer has been invoiced
3. Approval has been obtained from Finance Manager

### Your Task
Decompose this query into steps. For each step, identify:

1. Is it **deterministic** or **probabilistic**?
2. What **tool or LLM action** is needed?
3. What **output** does it produce?

### Starter Template

Fill this in:

```
Step 1: _______________ [Deterministic/Probabilistic]
Tool/Action: _______________
Output: _______________

Step 2: _______________ [Deterministic/Probabilistic]
Tool/Action: _______________
Output: _______________

[Continue for all necessary steps...]
```

---

### Solution (Expand to See)

<details>
<summary>Click to see solution</summary>

```
Step 1: Retrieve REV-001 policy [Deterministic]
Tool/Action: knowledge_base.get_policy("REV-001")
Output: Policy text with 3 requirements

Step 2: Pull Q3 revenue transactions [Deterministic]
Tool/Action: SQL query for period 2025-07-01 to 2025-09-30
Output: DataFrame with all revenue entries

Step 3: Check Requirement 1 - Service delivered [Deterministic]
Tool/Action: check_service_delivery_status(transactions)
Output: List of transactions with service_delivered = True/False

Step 4: Check Requirement 2 - Invoice issued [Deterministic]
Tool/Action: check_invoice_status(transactions)
Output: List of transactions with invoice_issued = True/False

Step 5: Check Requirement 3 - Finance approval [Deterministic]
Tool/Action: check_finance_approval(transactions)
Output: List of transactions with finance_approval = True/False

Step 6: Identify violations [Deterministic]
Tool/Action: filter_transactions_where_any_requirement_false()
Output: List of violation records with transaction IDs

Step 7: Calculate compliance rate [Deterministic]
Tool/Action: (compliant_count / total_count) * 100
Output: Percentage value

Step 8: Generate executive summary [Probabilistic]
Tool/Action: LLM with prompt containing evidence from Steps 1-7
Output: 3-paragraph narrative citing REV-001

Step 9: Create evidence package [Deterministic]
Tool/Action: compile_results(violations, summary, logs)
Output: Structured report with data + narrative + audit trail

```

**Key insights:**

- Steps 1-7 are deterministic (tools provide evidence)
- Only Step 8 is probabilistic (LLM provides narrative)
- Step 9 packages everything for the auditor
- Clear sequence ensures nothing is missed

</details>


## Decomposition Checklist

Use this checklist when designing agent workflows:

### Before You Start

- [ ]  Clarify the actual goal (not just surface question)
- [ ]  List all required data sources
- [ ]  Identify relevant policies or rules
- [ ]  Define success criteria

### During Decomposition

- [ ]  Each step has ONE clear purpose
- [ ]  All deterministic tasks use tools
- [ ]  All probabilistic tasks use LLM
- [ ]  Steps are in logical order
- [ ]  Dependencies are explicit

### After Decomposition

- [ ]  Every step produces verifiable output
- [ ]  Evidence chain is complete
- [ ]  All steps will be logged
- [ ]  Narrative cites evidence
- [ ]  Output meets SOX requirements


## Summary & Key Takeaways

### What You Learned

1. **Decomposition is not optional**
    - Vague instructions → unreliable outputs
    - Structured workflows → auditable results
    - Good decomposition is the foundation of agent success
2. **Two types of decomposition**
    - Human-style: Intuitive but too vague for agents
    - AI-native: Explicit, structured, machine-friendly
3. **The deterministic/probabilistic split**
    - Tools handle precision (data, calculations, rules)
    - LLMs handle narrative (summaries, explanations, synthesis)
    - Never mix the two
4. **Clear workflows enable compliance**
    - Each step is verifiable
    - Evidence trail is complete
    - Auditors can follow your logic

### The Mindset Shift

**Before:** "I'll just ask the agent to check compliance."

**After:** "I need to:

1. Break the question into atomic steps
2. Use tools for facts, LLM for narrative
3. Log everything for the audit trail
4. Ensure each step is verifiable"


<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

💡 Good decomposition = Good agents** Every successful agent workflow starts with clear task decomposition. Get this right, and everything else becomes easier.

</aside>


## Discussion Questions

Think about these (or discuss with your team):

1. **Your Work Context:**
    - What's a complex compliance task you currently do manually?
    - How would you decompose it into deterministic and probabilistic steps?
    - What tools would you need to build?
2. **Risk Identification:**
    - Imagine an agent that checks expense policy violations.
    - What could go wrong if you DON'T properly decompose the task?
    - How would poor decomposition affect the audit trail?
3. **Design Challenge:**
    - Task: "Prepare an executive dashboard showing Q3 compliance across all 12 internal controls."
    - How would you decompose this?
    - Which parts are deterministic? Probabilistic?
    - How many tools would you need?
4. **Scaling Considerations:**
    - You've decomposed one control (PAY-002).
    - How would you design a system that works for ALL controls?
    - What patterns or templates would help?


## Additional Resources

- **Recommended Reading:** "Prompt Engineering Guide" ([promptingguide.ai](http://promptingguide.ai/)) - Section on task decomposition
- **Example Repository:** [Coming in Day 2] Sample agent implementations
- **Discussion Forum:** Share your decomposition patterns with cohort
<!-- **Quick Reference Card:** Print/save the Decomposition Checklist for your desk! -->
