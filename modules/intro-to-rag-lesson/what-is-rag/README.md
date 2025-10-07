<h1>
  <span>

  ![](/assets/ga-logo.png)

  </span>
  <span class="subhead">What is RAG?</span>
</h1>

**Learning objective:** Explain the purpose of Retrieval-Augmented Generation (RAG) and outline its core components.

### The Core Idea

**Retrieval-Augmented Generation (RAG)** means injecting relevant external knowledge into an LLM at the moment it generates an answer.

Here's the difference:

| Without RAG                                               | With RAG                                                                       |
| --------------------------------------------------------- | ------------------------------------------------------------------------------ |
| LLM generates from training data only                     | LLM retrieves relevant docs first, *then* generates                            |
| "I think the approval threshold is $5,000" (hallucinated) | "According to Policy PAY-002, section 3.2, the threshold is $1,000" (grounded) |
| No sources                                                | Citable sources                                                                |

### Why Not Just Fine-Tune?

You might be wondering: *Why not fine-tune the model on our data?*

**Fine-tuning:**

- Good for: teaching style, tone, or domain-specific reasoning
- Bad for: frequently changing information, large knowledge bases, or when you need citations

**RAG:**

- Good for: dynamic data, traceability, cost-effectiveness
- Bad for: when you need deep reasoning or the model needs to "internalize" patterns

Most production systems use **both**: fine-tuning for behavior, RAG for knowledge.

### The Mental Model

Think of RAG like this:

> You're taking an open-book exam.
> 
> 
> Instead of memorizing everything (fine-tuning), you're allowed to bring reference materials (RAG). When asked a question, you flip through your notes, find relevant sections, and answer based on what you found.

## RAG Primitives Overview

A RAG pipeline is made of six building blocks. Let's walk through each one.

## 1. Documents

These are your raw sources of knowledge:

- PDFs (policies, reports)
- Markdown files (READMEs, wikis)
- Database records (Jira tickets, logs)
- Web pages (scraped documentation)

**Example:** A folder containing 10 policy documents in `.txt` format.

## 2. Chunking

**Problem:** LLMs have limited context windows. A 50-page PDF won't fit into a prompt.

**Solution:** Split documents into smaller, overlapping pieces called *chunks*.

**How it works:**

```
Original doc: "Policy PAY-002 states that all transactions above $1,000 require dual approval.
This rule was updated in Q3 2024. Exceptions must be logged in the audit trail..."

Chunk 1 (500 chars): "Policy PAY-002 states that all transactions above $1,000 require dual approval.
This rule was updated in Q3 2024..."

Chunk 2 (500 chars, 100-char overlap): "...was updated in Q3 2024. Exceptions must be logged
in the audit trail. The approval workflow..."

```

**Why overlap?** Without it, a sentence split across two chunks loses context.

**Key decision:** Chunk size

- Too small (100 chars): Fragments lose meaning
- Too large (2,000 chars): Less precise retrieval
- Sweet spot: 400-800 characters for most text

## 3. Embeddings

**Problem:** Computers can't understand "similarity" between text the way humans do.

**Solution:** Convert each chunk into a numeric vector (list of numbers) that represents its *meaning*.

**How it works:**

- "What is the approval threshold?" → `[0.23, -0.41, 0.89, ...]`
- "Approval limits for transactions" → `[0.21, -0.39, 0.87, ...]`
- "The weather today is sunny" → `[-0.63, 0.12, -0.34, ...]`

Chunks with similar meanings have vectors that are close together in high-dimensional space.

**Common models:**

- `text-embedding-ada-002` (OpenAI)
- `embed-english-v3.0` (Cohere)
- Open-source options (e.g., `all-MiniLM-L6-v2`)

## 4. Vector Store

**Problem:** You can't search for "similarity" in a normal database.

**Solution:** Use a specialized database designed for vector search.

**How it works:**

- Store all chunk embeddings
- When a query comes in, convert it to a vector
- Find the k-nearest neighbors (most similar chunks)

**Popular options:**

- FAISS (by Meta): Lightweight, in-memory, great for prototyping
- Chroma: Developer-friendly, easy to set up
- Pinecone / Weaviate: Managed, scalable, production-grade

For this lesson, we'll use **FAISS** because it requires zero setup.


## 5. Retriever

The retriever is the component that:

1. Takes your question
2. Converts it to an embedding
3. Queries the vector store
4. Returns the top-k most relevant chunks

**Key decision:** Top-k

- k=1: Very precise, but might miss context
- k=10: More comprehensive, but adds noise
- Sweet spot: k=3-5 for most use cases

**Example:**

```
Query: "What is the approval threshold for PAY-002?"

Retrieved chunks:
1. [Score: 0.89] "Policy PAY-002 states that all transactions above $1,000..."
2. [Score: 0.76] "Dual approval is required for amounts exceeding the threshold..."
3. [Score: 0.68] "The approval workflow must be documented in..."

```


## 6. Generator (LLM)

The final step: take the question *and* the retrieved chunks, and ask the LLM to generate an answer.

**How it works:**

```
System prompt: "Answer the question using only the provided context.
Cite your sources. If the context doesn't support an answer, say 'Insufficient context.'"

User prompt:
Q: What is the approval threshold for PAY-002?

Context:
[Chunk 1] Policy PAY-002 states that all transactions above $1,000 require dual approval...
[Chunk 2] Dual approval is required for amounts exceeding the threshold...
[Chunk 3] The approval workflow must be documented in...

LLM output: "The approval threshold for PAY-002 is $1,000. [Source: PAY-002, Chunk 1]"

```

**Why this works:**

- The LLM has explicit evidence in the prompt
- It's forced to cite sources
- If there's no supporting evidence, it can say so



## Design Decisions & Failure Modes

RAG isn't a "set it and forget it" solution. Here are the key levers you'll tune in practice.

### Chunking Strategy

**Fixed-size chunks:**

- Simple: split every 500 characters
- Problem: can split mid-sentence

**Recursive chunking:**

- Try splitting on paragraphs first, then sentences, then characters
- Better context preservation
- LangChain's `RecursiveCharacterTextSplitter` does this

**Overlap:**

- Always use 10-20% overlap (e.g., 100 chars for a 500-char chunk)
- Prevents context loss at boundaries

---

### Top-k: Precision vs. Recall

Think of top-k like a trade-off:

| k=1                            | k=10                              |
| ------------------------------ | --------------------------------- |
| High precision (very relevant) | High recall (don't miss anything) |
| Fast                           | Slower                            |
| Might miss nuance              | Adds noise                        |

**Rule of thumb:** Start with k=3. Increase if answers feel incomplete. Decrease if the LLM gets confused by irrelevant chunks.

---

### Prompt Engineering for RAG

Your prompt structure matters. Here's a template that works well:

```python
system_prompt = """
You are a helpful assistant. Answer questions using ONLY the provided context.

Rules:
1. If the context supports the answer, provide it with citations
2. If the context is insufficient, respond: "Insufficient context to answer this question"
3. Do not use outside knowledge
4. Always cite which document or chunk you used
"""

user_prompt = """
Question: {question}

Context:
{context}

Answer:
"""

```

**Key phrases:**

- "using ONLY the provided context" prevents hallucination
- "cite which document" adds traceability
- "Insufficient context" ensures fail-closed behavior


## Key Takeaways:

<aside style="background-color:#2a2a2a; padding: .66rem 2rem; border-radius: .5rem">

### 💡 Common Failure Modes

| Problem                                 | Cause                            | Fix                                |
| --------------------------------------- | -------------------------------- | ---------------------------------- |
| Answer is fragmented                    | Chunks too small                 | Increase chunk size or overlap     |
| Wrong answer                            | Retrieved irrelevant chunks      | Improve embeddings, tune top-k     |
| "Insufficient context" (false negative) | Top-k too low                    | Increase k                         |
| Contradictory answer                    | Multiple conflicting docs        | Add re-ranking or metadata filters |
| Hallucination                           | Prompt doesn't enforce grounding | Strengthen system prompt           |

</aside>