<h1>
  <span>
  
  ![](/assets/ga-logo.png)

  </span>
  <span class="subhead">When to Use RAG</span>
</h1>

**Learning objective:** Evaluate whether RAG is the right solution for a given use case, and identify appropriate alternatives when it is not.

### Why This Matters

You have learned how RAG works, but knowing when to use it is just as important. RAG is not a universal solution. It adds complexity: you need storage for embeddings, retrieval logic, vector databases, and more context tokens in every LLM call.

The wrong choice costs you:

* **Time:** Building RAG infrastructure when a simple prompt would work
* **Money:** Embedding models, vector databases, and increased LLM context usage
* **Performance:** Added latency from retrieval

This section helps you make the right architectural decision before you write a single line of code.

---
```
### The RAG Decision Framework

Use this mental model:

START: Do I need external knowledge that is not in the LLM’s training data?
↓
NO → Do not use RAG. Use direct prompting or fine-tuning.
↓
YES → Continue
↓
Is the knowledge large in scale or updated frequently enough that it cannot fit in a static prompt?
↓
NO → Use cached context or periodic refresh (preload stable content into the system prompt or rebuild embeddings occasionally).
↓
YES → Continue
↓
Do I need citations, audit trails, or verifiable sources for compliance or traceability?
↓
NO → Evaluate whether tool or function calling (SQL, API, deterministic queries) is sufficient.
↓
YES → RAG is the right choice.
```

Let’s break down each decision point.

---
### Use RAG When...

RAG shines when your knowledge base is large, dynamic, and external to the model. It is ideal for compliance and audit systems where traceability matters.

**Scenario Matrix**

| Situation                                            | Why RAG Helps                               | Real-World Example                                            |
| ---------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------- |
| Policies, Jira tickets, or logs change frequently    | Keeps answers current without retraining    | Support chatbot that needs yesterday's bug fixes              |
| You need citations or verifiable evidence            | Can show exactly which source was used      | Legal research tool citing case law                           |
| Information lives in many places (wikis, docs, PDFs) | Unifies these into a single queryable layer | Enterprise knowledge base across many systems                 |
| Answers depend on factual recall more than reasoning | Supplies facts, model formats them          | "What is the current API rate limit for our production tier?" |
| Compliance requires showing your work                | Every answer can be traced to source chunks | Financial services chatbot with audit requirements            |

**Example: When RAG Is the Right Choice**

Scenario: You are building a chatbot for a SaaS company's internal support team. They need to answer questions about:

* 200+ product documentation pages (updated weekly)
* 500+ resolved Jira tickets (new ones daily)
* Internal runbooks and SOPs (updated monthly)

**Why RAG?**

```python
# INCORRECT: Without RAG, this does not scale
prompt = """
You are a support agent. Answer questions about our product.

[Manually paste entire documentation here - 50,000+ words]
[Manually paste Jira tickets - another 100,000+ words]

Question: {user_question}
"""
# Problems:
# - Exceeds context limits
# - No way to keep documentation current
# - Cannot cite which document was used
```

```python
# CORRECT: With RAG, scalable and maintainable
def answer_support_question(question):
    # 1. Retrieve relevant chunks from vector store
    relevant_chunks = retriever.get_relevant_documents(
        query=question,
        k=5
    )

    # 2. Format with citations
    context = "\n\n".join([
        f"[Source: {chunk.metadata['source']}]\n{chunk.page_content}"
        for chunk in relevant_chunks
    ])

    # 3. Generate answer
    prompt = f"""
    Answer the question using ONLY the provided context. Cite sources.

    Question: {question}

    Context:
    {context}

    Answer:
    """

    return llm.generate(prompt)

# Benefits:
# - Only retrieves relevant documents (5 chunks, not 200 pages)
# - Automatically updates when new documents are added to the vector store
# - Every answer includes source citations
```

Think: "I want the model to be correct for today's data, not last month's fine-tune."

---

### Avoid or Minimize RAG When...

RAG adds complexity, so it is not always worth it.

**Scenario Matrix**

| Situation                                            | Why RAG Might Hurt                           | What to Use Instead                        |
| ---------------------------------------------------- | -------------------------------------------- | ------------------------------------------ |
| Your data set is small and stable                    | Direct prompting or fine-tuning is simpler   | Include data directly in the system prompt |
| You already have the relevant facts in the prompt    | Retrieval adds latency without benefit       | Just use the LLM                           |
| The task is mostly reasoning or judgment, not recall | The model does not need extra context        | Direct prompting with examples             |
| Latency and cost are critical                        | Each retrieval step adds overhead            | Cache frequently used contexts             |
| Information must remain on-prem or air-gapped        | Hosted vector databases may be non-compliant | Use local FAISS or skip RAG entirely       |

**Example: When RAG Is Overkill**

Scenario: Classify customer support emails into five categories: Billing, Technical, Sales, Cancellation, Other.

```python
# INCORRECT: Over-engineered with RAG
# 1. Embed category descriptions
# 2. Store in vector DB
# 3. Retrieve category per email
# 4. Pass to LLM for classification
# Problems:
# - Five categories fit in a prompt (no retrieval needed)
# - Adds latency (embedding + vector search + LLM call)
# - Adds cost (embedding API + vector DB hosting)
```

```python
# CORRECT: Direct prompting
def classify_email(email_text):
    prompt = f"""
    Classify this customer email into ONE category:
    - Billing: payment issues, invoices, refunds
    - Technical: bugs, errors, how-to questions
    - Sales: pricing, demos, enterprise inquiries
    - Cancellation: requests to cancel service
    - Other: anything else

    Email: {email_text}

    Category:
    """
    return llm.generate(prompt)

# Benefits:
# - Single LLM call (fast, inexpensive)
# - No infrastructure to maintain
# - Category definitions are stable (no need for dynamic retrieval)
```

Think: "If I can pass the data in directly, I do not need a retrieval layer."

---

### Key Takeaways

<aside style="background-color:#2a2a2a; padding: .66rem 2rem; border-radius: .5rem">

**When RAG Makes Sense**

* Knowledge base is large
* Information changes frequently
* You need citations for compliance or trust
* Facts are scattered across multiple systems
* Cost of retraining exceeds cost of retrieval infrastructure

**When to Skip RAG**

* Data fits comfortably in a prompt
* Information is stable
* Task is reasoning or judgment, not recall
* Latency is critical
* You need air-gapped or on-prem deployment

**Remember**
RAG is a tool, not a doctrine. The best systems combine RAG, fine-tuning, function calling, and direct prompting based on the specific use case.

</aside>

---

### Practice: RAG Decision-Making

For each scenario below, decide: Use RAG, Skip RAG, or Hybrid. Justify your answer.

**Scenario 1: Email Auto-Responder**
You are building an auto-responder for a customer service team. It needs to classify emails into categories, respond with pre-approved templates, and handle ten email types.

<details>
<summary><strong>Click for answer</strong></summary>
Skip RAG. Use direct prompting with in-context examples.

Why:

* Only ten templates, which fit in the prompt
* Templates are stable
* No need for citations
* Speed matters for auto-responders

Implementation:

```python
system_prompt = """
You are an email auto-responder. Classify emails and respond using these templates:

1. Billing Issue → "Thank you for contacting billing. A specialist will respond within 24 hours..."
2. Technical Support → "We have received your technical issue. Our team is investigating..."
[...more templates...]

Classify the email and respond with the appropriate template.
"""
```

</details>

**Scenario 2: Medical Research Assistant**
You are building a tool for doctors to query medical literature. It needs to search many research papers, provide evidence-based answers, cite specific papers and sections, and update as new research is published.

<details>
<summary><strong>Click for answer</strong></summary>
Use RAG.

Why:

* Large corpus that will not fit in context
* Dynamic and updated frequently
* Citations are critical
* Factual recall dominates

Architecture:

```python
# 1. Embed papers → vector store
# 2. For each query:
#    - Retrieve top 5 relevant sections
#    - Generate answer with citations
# 3. Update vector store on a schedule
```

</details>

**Scenario 3: SQL Query Generator**
You are building a tool that converts natural language to SQL queries for your company's database. It needs to understand your schema, generate valid SQL, and return query results.

<details>
<summary><strong>Click for answer</strong></summary>
Hybrid: Function Calling with optional RAG.

Why:

* Schema can often fit in the prompt
* You need real-time data from the database
* RAG is optional for retrieving similar past queries

Implementation:

```python
# Option 1: Direct prompting
def generate_sql(question, schema):
    prompt = f"""
    Schema: {schema}

    Convert to SQL: {question}
    """
    sql = llm.generate(prompt)
    return execute_sql(sql)

# Option 2: RAG for example retrieval
def generate_sql_with_examples(question, schema):
    examples = retriever.get_relevant_documents(question, k=3)
    prompt = f"""
    Schema: {schema}

    Similar past queries:
    {examples}

    Convert to SQL: {question}
    """
    sql = llm.generate(prompt)
    return execute_sql(sql)
```

</details>

**Scenario 4: Code Review Bot**
You are building a bot that reviews pull requests and suggests improvements. It needs to understand your team's coding standards, reference internal style guides, and adapt as standards evolve.

<details>
<summary><strong>Click for answer</strong></summary>
Skip RAG initially. Use direct prompting with cached context.

Why:

* Style guides are small enough to fit in context
* They change monthly, not daily
* Reasoning over code matters more than recall

Upgrade to RAG when the guides grow significantly, when you add large sets of historical PR examples, or when you need to cite specific guideline sections.

Implementation:

```python
# Month 1-6: Cached context
system_prompt = f"""
{load_style_guides()}  # Cached monthly

Review this PR and suggest improvements based on our standards.
"""
```

</details>

---

