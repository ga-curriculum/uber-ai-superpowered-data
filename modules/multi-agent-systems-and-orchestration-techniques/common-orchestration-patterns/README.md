<h1>
  <span>
  
  ![alt text](./assets/ga-logo.png)

  </span>
  <span class="subhead">Orchestration Patterns in Context</span>
</h1>

**Learning objective:** Describe sequential, hierarchical, and collaborative orchestration patterns, applying each to an Evidence + Reviewer agent example. Evaluate which patterns best fit compliance and auditability requirements.

---

## Overview  

There are three common orchestration patterns, each with different trade-offs. We'll examine:
- How they work (conceptually)
- What they look like in code (examples)
- When to use them in SOX/compliance contexts

**The Three Patterns:**
1. **Sequential:** Agent A → Agent B → Agent C (pipeline)
2. **Hierarchical:** Supervisor delegates to worker agents (coordinator)
3. **Collaborative/Peer:** Agents negotiate or share state (team)

**Spoiler:** For SOX compliance, **Sequential wins** 90% of the time. But you need to understand *why* the other patterns fall short.

---

## **Pattern 1: Sequential Orchestration**

**Flow:** Agent A → Agent B → Agent C

**Conceptual Model:** Think of a factory assembly line. Each station does one job, passes work to the next station.

**Code Structure (pseudocode):**
```python
def sequential_orchestration(control_id, month):
    # Step 1: Generate evidence
    evidence = evidence_agent.run(control_id, month)
    if not evidence.is_valid:
        return {"status": "FAIL", "reason": "Evidence generation failed"}
    
    # Step 2: Independent review
    review = reviewer_agent.run(evidence)
    if not review.is_valid:
        return {"status": "FAIL", "reason": "Review failed"}
    
    # Step 3: Make decision
    decision = decision_agent.run(evidence, review)
    return decision
```

**Strengths:**
- **Predictable:** You always know what runs when
- **Easy to debug:** If output is wrong, check each step in order
- **Auditable:** Clear "who did what, when" for compliance logs
- **Fail-fast:** If Step 1 fails, you don't waste time on Steps 2–3

**Weaknesses:**
- **Brittle:** If Step 1 fails, entire workflow stops
- **Sequential only:** Can't parallelize (e.g., can't run Evidence and Reviewer at same time)
- **No dynamic routing:** You can't skip steps based on conditions

**When to Use:**
- ✅ Compliance workflows (SOX, audit, regulatory reporting)
- ✅ When you need deterministic, repeatable results
- ✅ When audit trail clarity is more important than efficiency

### **SOX Example (Detailed):**

**Control:** PAY-002 (Payroll SoD)
**Sequential Flow:**

1. **Evidence Agent:**
   - Input: `control_id="PAY-002"`, `month="July"`
   - Action: Query payroll database, run SoD logic
   - Output: `EvidenceResult(violations=2, details=[...], timestamp="2025-07-01T10:23:45Z")`

2. **Reviewer Agent:**
   - Input: `EvidenceResult` from Step 1
   - Action: Re-run SoD check using independent method (e.g., different SQL query)
   - Output: `ReviewResult(confirmed=True, confidence="HIGH", discrepancies=[])`

3. **Decision Agent:**
   - Input: `EvidenceResult` + `ReviewResult`
   - Action: Compare findings, apply business rules
   - Output: `{"status": "FAIL", "violations": 2, "evidence_id": "...", "reviewer_id": "..."}`

**Why This Works for SOX:**
- Each step is logged separately (audit trail)
- Reviewer is truly independent (doesn't see Evidence logic)
- If Evidence fails, system stops and marks FAIL (fail-closed)

---

## **Pattern 2: Hierarchical Orchestration**

**Flow:** Supervisor Agent delegates tasks to worker agents

**Conceptual Model:** Think of a project manager assigning tickets to engineers. The PM decides what to do, workers execute.

**Code Structure (pseudocode):**
```python
def hierarchical_orchestration(control_id, month):
    supervisor = SupervisorAgent()
    
    # Supervisor decides what to do
    plan = supervisor.create_plan(control_id, month)
    # Example plan: ["check_evidence", "verify_independently", "compile_report"]
    
    results = {}
    for task in plan:
        # Supervisor picks the right worker for each task
        worker = supervisor.assign_worker(task)
        results[task] = worker.execute(task)
    
    # Supervisor compiles final output
    return supervisor.finalize(results)
```

**Strengths:**
- **Flexible:** Supervisor can adapt to different controls dynamically
- **Centralized logic:** One place (supervisor) handles all routing decisions
- **Parallel execution:** Supervisor can dispatch multiple workers at once
- **Good for complex workflows:** When you have many possible paths (e.g., 50 different control types)

**Weaknesses:**
- **Supervisor is a bottleneck:** If it makes a bad decision, entire workflow suffers
- **Less transparent:** Hard to audit "why did supervisor choose this worker?"
- **Adds latency:** Extra LLM call (supervisor) before real work starts
- **Supervisor can fail:** If supervisor's reasoning is flawed, workers execute wrong tasks

**When to Use:**
- ⚠️ Complex multi-control scenarios (e.g., "Audit all 50 controls for Q2")
- ⚠️ When you need dynamic routing (different controls need different checks)
- ❌ **Not recommended for SOX single-control testing** (too much hidden complexity)

### **SOX Example:**

**Scenario:** Supervisor needs to audit multiple controls (PAY-002, PAY-005, INV-003)

1. **Supervisor Agent:**
   - Input: `["PAY-002", "PAY-005", "INV-003"]`
   - Decision: "For PAY-002, use Evidence + Reviewer. For PAY-005, use Evidence only. For INV-003, use specialized InventoryAgent."
   - Delegates tasks to workers

2. **Worker Agents:**
   - Each worker runs its assigned task
   - Reports results back to Supervisor

3. **Supervisor Agent (again):**
   - Compiles all results into final report

**Why This is Risky for SOX:**
- Auditors will ask: "How did the Supervisor decide to skip Reviewer for PAY-005?"
- Answer: "The LLM reasoned it wasn't necessary."
- Auditor: 🚩 "That's not a documented control procedure."

**The Problem:** Supervisor adds a layer of *AI reasoning* into the workflow design itself—which is hard to audit and validate.

---

## **Pattern 3: Collaborative / Peer-to-Peer**

**Flow:** Agents interact directly, negotiate, or share state

**Conceptual Model:** Think of a Slack channel where team members debate solutions before finalizing.

**Code Structure (pseudocode):**
```python
def collaborative_orchestration(control_id, month):
    evidence = evidence_agent.run(control_id, month)
    review = reviewer_agent.run(evidence)
    
    # If they disagree, they "debate"
    if evidence.violations != review.violations:
        conversation = []
        for round in range(3):  # Max 3 rounds of debate
            evidence_response = evidence_agent.respond_to(review.critique)
            review_response = reviewer_agent.respond_to(evidence_response)
            conversation.append({"evidence": evidence_response, "review": review_response})
            
            # Check if they've reached consensus
            if consensus_reached(conversation):
                break
        
        final_decision = decision_agent.synthesize(conversation)
    else:
        final_decision = {"status": "FAIL", "violations": evidence.violations}
    
    return final_decision
```

**Strengths:**
- **Handles ambiguity:** When rules are unclear, agents can "discuss" to clarify
- **More human-like:** Mimics how teams actually work (debate, refine, agree)
- **Flexible:** Agents can bring different perspectives to the same problem
- **Good for brainstorming:** Useful in exploratory analysis (e.g., "Why did revenue drop?")

**Weaknesses:**
- **Unpredictable:** You don't know how many rounds of debate will happen
- **Non-deterministic:** Same inputs might produce different outputs
- **Hard to audit:** "Who decided?" → "They debated and reached consensus" (not satisfying for auditors)
- **Can diverge:** Agents might never agree, leaving you with no decision
- **Slow:** Multiple LLM calls per "round" of debate

**When to Use:**
- ❌ **Never for SOX compliance** (too unpredictable, not auditable)
- ⚠️ Internal exploratory analysis (e.g., "Analyze this anomaly and suggest causes")
- ⚠️ Creative tasks (e.g., "Draft 3 different marketing emails, have agents vote on best")

### **SOX Example (Why It Fails):**

**Scenario:** Evidence Agent finds 2 violations, Reviewer finds 3

**Collaborative Flow:**
1. Evidence: "I found 2 violations in July."
2. Reviewer: "I found 3. You missed TXN-4901."
3. Evidence: "TXN-4901 was approved in August, not July. I'm correct."
4. Reviewer: "But the transaction *initiated* in July. That's the violation."
5. Evidence: "The control says 'approved in same month,' not 'initiated.'"
6. Reviewer: "Let me check the control definition again... You're right, it's 2 violations."

**Final Output:** 2 violations (after debate)

**The Audit Problem:**
- Auditor: "Show me your evidence for 2 violations."
- You: "Here's a 6-round conversation between two LLMs."
- Auditor: "That's not evidence. I need the deterministic check results."
- You: "Well, the Evidence Agent eventually agreed it was 2..."
- Auditor: 🚩 "This is not a reliable control."

**Why It's Risky:**
- Decision is based on *AI debate*, not deterministic logic
- Reproducibility is questionable (re-run might yield different debate)
- Audit trail is conversational, not procedural

---

## **Comparing the Patterns**

| Pattern | Strengths | Weaknesses | SOX Fit | Use Case |
| --- | --- | --- | --- | --- |
| **Sequential** | Simple, predictable, auditable, fail-fast | Brittle if one step fails, no parallelization | ✅ **Best fit** | Single-control testing, compliance workflows, audit-ready systems |
| **Hierarchical** | Flexible, handles complexity, parallelizable | Supervisor bottleneck, less transparent, adds latency | ⚠️ Possible for multi-control batching | Large-scale audits (50+ controls), dynamic routing |
| **Collaborative** | Handles ambiguity, human-like, flexible | Unpredictable, hard to audit, non-deterministic | ❌ **Avoid for SOX** | Exploratory analysis, brainstorming, low-stakes creative tasks |

## **The "But What If..." Counterarguments**

**Q:** "What if Sequential is too brittle? We have 50 controls—if one fails, we don't want the whole audit to stop."

**A:** Sequential *within* each control, Hierarchical *across* controls. Example:
- Supervisor dispatches 50 control checks in parallel
- Each control uses Sequential orchestration (Evidence → Reviewer → Decision)
- If PAY-002 fails, the other 49 continue

---

**Q:** "What if Evidence and Reviewer disagree? Don't we need them to 'talk it out'?"

**A:** No. Disagreement is **valuable signal**, not a problem to fix. In SOX:
- If Evidence says 2 violations, Reviewer says 3 → **escalate to human**
- Don't let LLMs negotiate the "right answer"—that's the auditor's job

---

**Q:** "Collaborative sounds more intelligent. Why restrict it?"

**A:** Intelligence ≠ Auditability. For compliance, you want:
- Predictable, reproducible results
- Clear audit trail ("Agent A did X, Agent B did Y")
- Fail-closed (if uncertain, mark FAIL)

Collaborative orchestration optimizes for *flexibility*, but SOX optimizes for *reliability*.

---

## **Decision Tree: Which Pattern to Use?**

```
Is this a compliance/audit workflow?
├─ YES → Is it a single control test?
│   ├─ YES → Use Sequential ✅
│   └─ NO (batch audit) → Use Hierarchical for dispatch, Sequential within each control ⚠️
└─ NO → Is the output high-stakes or public-facing?
    ├─ YES → Use Sequential (predictability)
    └─ NO → Consider Collaborative (flexibility OK)
```

---

## **What You'll Build Today**

In the hands-on session, you'll implement **Sequential Orchestration** for PAY-002:
1. Define Pydantic schemas for each handoff
2. Build Evidence Agent → Reviewer Agent → Decision logic
3. Add error handling (fail-closed at each step)
4. Log every step for audit trail

You'll also *intentionally break* the pipeline (schema mismatch, state loss) and learn how to debug it using the Guiding Principles from the next section.

<br>

<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

💡 **Key Message:** In compliance contexts, **Sequential Orchestration** is usually the safest—it maximizes transparency and minimizes hidden complexity. Save Hierarchical for large-scale batching, and avoid Collaborative entirely for SOX.

</aside>
