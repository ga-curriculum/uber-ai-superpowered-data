<h1>
  <span>

  ![alt text](../assets/ga-logo.png)

  </span>
  <span class="subhead">Agentic Architectural Patterns</span>
</h1>

**Learning objective:** Describe common architectural patterns for agents, including agents with tools and those using Retrieval-Augmented Generation (RAG).

## Common Agent Patterns

Different use cases require different agent designs. Here are three patterns you'll encounter:

### Pattern 1: Tool-Using Agent

**How it works:**

- Agent has access to specific tools (functions)
- For each query, selects appropriate tools
- Combines tool outputs with LLM narrative

**Strengths:**

- High precision and accuracy
- Strong auditability (tool outputs are evidence)
- Works well for structured compliance checks

**Weaknesses:**

- Limited to available tools
- Can't answer questions outside tool scope
- No access to unstructured knowledge

> **Best for:** Compliance testing, control validation, exception reporting

**Example use case:**

``` 
> Query: "Show me all revenue transactions in Q3 missing required approvals."
```

> **Agent behavior:**
> 
> 1. Calls `get_revenue_transactions(quarter='Q3')`
> 2. Calls `check_approval_status(transactions)`
> 3. Filters violations
> 4. Generates summary citing REV-001 policy

### Pattern 2: RAG Agent (Retrieval-Augmented Generation)

**How it works:**

- Agent has access to a knowledge base (documents, policies, past reports)
- Retrieves relevant context before generating response
- Combines retrieved knowledge with LLM reasoning

**Strengths:**

- Can answer questions requiring company-specific knowledge
- References source documents (citations)
- Adapts to new policies without code changes

**Weaknesses:**

- More complex to build and tune
- Retrieval quality affects answer quality
- Requires well-organized knowledge base

> **Best for:** Policy interpretation, procedure guidance, historical analysis

**Example use case:**

```
Query: "What are the approval requirements for international wire transfers?"
```

> **Agent behavior:**
> 
> 1. Searches knowledge base for "wire transfer policy"
> 2. Retrieves relevant sections from FIN-205
> 3. Generates answer citing specific policy sections
> 4. Provides link to full policy document

### Pattern 3: Hybrid Agent

**How it works:**

- Combines tools AND retrieval
- Can both execute functions and reference documents
- Most flexible but most complex

**Strengths:**

- Handles broad range of queries
- Provides both evidence (tools) and context (retrieval)
- Most enterprise-ready pattern

**Weaknesses:**

- More moving parts to debug
- Requires careful orchestration
- Higher latency

> **Best for:** End-to-end workflows, comprehensive audits, executive dashboards

**Example use case:**

```
Query: "Prepare a Q3 revenue recognition compliance summary."
``` 
 
> **Agent behavior:**
> 
> 1. Retrieves REV-001 policy from knowledge base
> 2. Calls `get_revenue_transactions(quarter='Q3')`
> 3. Calls `check_approval_compliance(transactions)`
> 4. Pulls previous quarter results for comparison
> 5. Generates executive summary with citations and evidence
