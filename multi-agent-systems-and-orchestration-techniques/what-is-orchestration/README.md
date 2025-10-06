<h1>
  <span>

  ![alt text](../assets/ga-logo.png)

  </span>
  <span class="subhead">What is Multi-Agent Orchestration?</span>
</h1>

**Learning objectives:** 
- Define orchestration as the coordination of multiple autonomous agents to achieve a goal. 
- Differentiate from single-agent systems: not just “adding another LLM,” but designing structured collaboration.  

## Overview  

Orchestration is the **coordination of multiple autonomous agents** to achieve a shared goal.

- An **agent** = an AI-powered system that can use tools, retrieve data, and generate outputs.
- **Orchestration** = deciding how agents interact, in what order, and how they exchange information.

## **Why It Matters**

- A single agent can only go so far, it often mixes too many responsibilities.
- Multi-agent systems allow for **specialization** (e.g., one agent generates evidence, another reviews it).
- But… without orchestration, these agents talk past each other or fail silently.
>*What could that look like?*

## **The "More LLMs" Trap**

**Multiple agent** can sometimes mean making our system slower and more expensive since we're calling more LLMs.

But that's not what this is about.

**Bad multi-agent design:**
- Calls multiple LLMs for the same task "just in case"
- Adds agents because it sounds impressive
- Creates redundant work without clear value

**Good multi-agent design:**
- Separates concerns that *must* be independent (e.g., generator vs. validator)
- Allows specialization where one generalist agent would fail
- Creates auditability through separation of duties

> *Think about your agentic systems. Where do you already use "multiple agents" (different services/scripts) instead of one monolithic script? What made you split them?*

## **Single Agent vs Multi-Agent**

### **Single Agent**
- Example: Evidence Agent that runs checks *and* writes the narrative.
- **Risk**: “Judge and jury” problem → no independence.
### **Multi-Agent**
- **Example**: Evidence Agent + Reviewer Agent.
- **Strength**: Independence, cross-validation, accountability.
- **But**: Needs orchestration to ensure smooth handoff.


## **When Multi-Agent is Overkill**
Not every problem needs orchestration. Use single agents when:

The task is simple and low-stakes (e.g., "Summarize this email")
You need speed over auditability
There's no compliance requirement for independence
Use multi-agent orchestration when:

Independence is required (SOX, regulatory compliance)
Specialization improves outcomes (one agent for retrieval, another for reasoning)
You need an audit trail showing separation of duties
Failure of one component must be caught by another


## **Orchestration in Context**
### SOX Example:
- **Evidence Agent:** Runs deterministic check → “Found 2 violations in July.”
- **Reviewer Agent:** Independently re-performs check → “Confirming 2 violations.”
- **Orchestration:** Defines the flow → Evidence runs first, Reviewer validates second, then system produces **PASS/FAIL**.

### Detailed SOX Example:
**Control**: PAY-002 (Segregation of Duties in Payroll)

**Data**: 847 payroll transactions in July

**The Flow**:

1. Evidence Agent:
- Runs deterministic check: "Find any transactions where `created_by == approved_by`"
- Outputs: `{"violations_found": 2, "transaction_ids": ["TXN-4721", "TXN-4838"], "evidence": "2 transactions violated SoD policy"}`

2. Reviewer Agent:

- Does NOT see Evidence Agent's code or reasoning
- Independently re-runs the check with different methodology (e.g., SQL query vs. pandas, or samples 10% of transactions)
- Outputs: `{"independent_verification": "Confirmed 2 violations", "sample_check": "10% sample clean", "confidence": "HIGH"}`

3. Decision Agent:

- Compares both outputs
- If they agree → "PASS" or "FAIL" with high confidence
- If they disagree → "NEEDS_MANUAL_REVIEW" (escalates to human)


**The Orchestration Layer decides**:

- Evidence runs first
- Reviewer runs only if Evidence succeeds
- Decision runs only if both Evidence and Reviewer complete
- If any step fails → system outputs FAIL with diagnostic


## Key Takeaway

<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

💡 Orchestration is __not__ “more LLM calls.” It’s the discipline of designing structured collaboration between agents.

</aside>
