<h1>
  <span> 

  ![alt text](/assets/ga-logo.png)

  </span>
  <span class="subhead">Why Structure Matters</span>
</h1>

**Learning objective:** Explain why structured agent workflows are required for SOX compliance and contrast them with unstructured LLM use.

## Why can't we use ChatGPT?


### The SOX Requirements

Sarbanes-Oxley Act requires:

1. **Evidence:** You must have proof controls were tested
2. **Independence:** Testing must be objective and repeatable
3. **Auditability:** Auditors must be able to verify your work
4. **Documentation:** Every test must be documented

### How Agents Meet These Requirements

| SOX Requirement   | How Agents Deliver                                            |
| ----------------- | ------------------------------------------------------------- |
| **Evidence**      | Tools provide precise, verifiable data from systems of record |
| **Independence**  | Deterministic tools eliminate subjectivity                    |
| **Auditability**  | Logging creates complete trail from query to conclusion       |
| **Documentation** | Structured outputs can be directly included in workpapers     |

### The Risk of Unstructured LLM Use

**Scenario:** An analyst asks ChatGPT, *"Did we comply with PAY-002 in July?"*

**What could go wrong:**

- ❌ LLM has no access to actual transaction data
- ❌ LLM might "hallucinate" facts
- ❌ No evidence to show auditors
- ❌ No way to reproduce the result
- ❌ Violates independence (analyst's prompt influences result)

**The Agent Alternative:**

**Query:** *"Did we comply with PAY-002 in July?"*

**Agent process:**

1. ✅ Pulls actual transaction data (evidence)
2. ✅ Applies deterministic rule check (objective)
3. ✅ Logs every step (auditable)
4. ✅ Generates structured summary (documentation)


💡 **Key Insight:** Structure isn't just about better answers — it's about compliant, defensible, trustworthy answers.


## Quick Comparison: LLM vs Agent

Let's crystallize the differences:

| Dimension           | Raw LLM                 | Structured Agent                              |
| ------------------- | ----------------------- | --------------------------------------------- |
| **Data access**     | Only training data      | Live system access via tools                  |
| **Accuracy**        | Probabilistic           | Deterministic tools + probabilistic narrative |
| **Verifiability**   | "Trust me"              | "Here's the evidence"                         |
| **Reproducibility** | Varies                  | Consistent                                    |
| **Auditability**    | None                    | Full logging                                  |
| **Compliance**      | Risky                   | Designed for SOX                              |
| **Use case**        | Brainstorming, drafting | Production workflows, compliance testing      |

---

## Knowledge Check: Test Your Understanding

**Question 1:** Which component of an agent decides what tools to call and in what order?

<details>
<summary>Click to reveal answer</summary>

**Answer:** The Orchestrator (the "brain" of the agent)
</details>

**Question 2:** True or False: Memory in an agent is only useful for multi-turn conversations.

<details>
<summary>Click to reveal answer</summary>

**Answer:** False. Memory also stores facts collected during a single session (short-term) and user preferences across sessions (long-term).
</details>

**Question 3:** Which agent pattern would be BEST for the query: "Explain our revenue recognition policy"?

- A) Tool-Using Agent
- B) RAG Agent
- C) Hybrid Agent

<details>
<summary>Click to reveal answer</summary>

**Answer:** B) RAG Agent — This requires retrieving policy documents, not executing tools. A RAG agent can search the knowledge base and cite relevant sections.
</details>

**Question 4:** Why is logging critical for SOX compliance?

<details>
<summary>Click to reveal answer</summary>

**Answer:** Logging creates an audit trail showing how conclusions were reached. Auditors need to verify that controls were tested properly, and logs provide that evidence.
</details>

---



## Summary & Key Takeaways
<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

1. **Agents are systems, not just prompts**
    - They combine LLMs with tools, memory, orchestration, and logging
    - This structure transforms probabilistic models into reliable assistants
2. **Four core components work together**
    - Orchestrator: Decides actions
    - Tools: Execute deterministic tasks
    - Memory: Maintains context
    - Logging: Creates audit trail
3. **Different patterns serve different needs**
    - Tool-using: Best for structured compliance checks
    - RAG: Best for knowledge-intensive queries
    - Hybrid: Most flexible for complex workflows
4. **Structure enables compliance**
    - Agents provide evidence, reproducibility, and auditability
    - Raw LLMs can't meet SOX requirements
    - Proper architecture is non-negotiable for production use

</aside>

### 
**Before:** "I can just ask the LLM and get an answer."

**After:** "I need to design a system where:

- Tools provide evidence
- LLM provides narrative
- Logs provide audit trail
- Structure ensures trust"
  

## Discussion Questions

Reflect on these questions (or discuss with your team):

1. **Application to Your Work:**
    - What's one compliance task you currently do manually that could be automated with an agent?
    - Which components (orchestrator, tools, memory, logging) would be most critical?
2. **Pattern Selection:**
    - Imagine you need to answer: "How do we compare to industry benchmarks for Days Sales Outstanding?"
    - Which agent pattern would you choose and why?
3. **Risk Assessment:**
    - What could go wrong if you deployed an agent without proper logging?
    - How would you explain the risk to a non-technical auditor?
4. **Design Challenge:**
    - Your manager wants to check ALL internal controls automatically every month.
    - Sketch out what components and tools this agent would need.
    - What would the logging structure look like?
