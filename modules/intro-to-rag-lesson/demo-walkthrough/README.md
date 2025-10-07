<h1>
  <span>
  
  ![](/assets/ga-logo.png)

  </span>
  <span class="subhead">Demo: RAG Walkthrough</span>
</h1>

**Learning objectives:** 
- Build and evaluate a simple RAG pipeline by combining document retrieval with LLM generation
- Apply validation and monitoring techniques to ensure accuracy and reliability.

## Overview

Now let's see RAG in action. We'll build a simple system that answers questions about internal policies.

## Workflow
### Setup
Assume we have:

- A folder `/data/policies/` with 5 text files
- LangChain installed (`pip install langchain langchain-openai langchain-community faiss-cpu`)
- An OpenAI API key

---

### Step 1: Load Documents

```python
from langchain_community.document_loaders import DirectoryLoader

# Load all .txt files from the policies folder
loader = DirectoryLoader("data/policies", glob="*.txt")
docs = loader.load()

print(f"Loaded {len(docs)} documents")
print(docs[0].page_content[:300])  # Preview first 300 chars
```

**Output:**

```
Loaded 5 documents
Policy PAY-002: Dual Approval Requirements

All financial transactions exceeding $1,000 must receive dual approval before processing.
This policy applies to all payment types including wire transfers, ACH payments, and
credit card transactions...
```

---

### Step 2: Chunk Documents

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Split into 500-char chunks with 100-char overlap
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = splitter.split_documents(docs)
print(f"{len(chunks)} chunks created from {len(docs)} documents")
```

**Output:**

```
23 chunks created from 5 documents
```

---

### Step 3: Create Embeddings & Vector Store

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Create embeddings for all chunks
embeddings = OpenAIEmbeddings()

# Store in FAISS (in-memory vector database)
vectorstore = FAISS.from_documents(chunks, embeddings)

# Create a retriever that returns top-3 chunks
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
```

---

### Step 4: Query Without RAG (Baseline)

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

question = "What is the dual approval threshold for PAY-002?"
response = llm.invoke(question)

print(response.content)
```

**Output:**

```
I don't have access to specific company policies like PAY-002.
Typically, dual approval thresholds vary by organization, but they're
often set around $5,000 to $10,000 for financial transactions.
```

---

### Step 5: Query With RAG

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Define the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the question using only the provided context. "
               "Cite your sources. If the context doesn't support an answer, "
               "say 'Insufficient context.'"),
    ("human", "Question: {question}\n\nContext:\n{context}\n\nAnswer:")
])

# Create a simple chain
chain = prompt | llm | StrOutputParser()

# Retrieve relevant chunks
retrieved_docs = retriever.invoke(question)

# Combine chunks into a single context string
context = "\n\n".join([doc.page_content for doc in retrieved_docs])

# Generate answer
answer = chain.invoke({"question": question, "context": context})
print(answer)
```

**Output:**

```
The dual approval threshold for PAY-002 is $1,000. All financial transactions
exceeding this amount must receive dual approval before processing.
[Source: Policy PAY-002, Section 1]
```

---

### What Just Happened?

```
1. User asks: "What is the dual approval threshold for PAY-002?"
   ↓
2. Question is embedded
   ↓
3. Vector store finds 3 most similar chunks
   ↓
4. These chunks are inserted into the prompt as "context"
   ↓
5. LLM reads context and generates: "The threshold is $1,000 [Source: PAY-002]"

```


## Evaluation & Monitoring

Building a RAG pipeline is the easy part. The harder part is knowing if it’s actually **working** in production. Evaluation and monitoring are how you move from “it seems right” to “we can trust this system.”


### Why RAG Evaluation Matters
- A single hallucinated answer can undermine trust with business users.
- Retrieval drift happens as your knowledge base changes over time.
- Auditability requires evidence that answers were correct *at the time they were given.*

---

### 1. Evaluating Retrieval

You need to know if your retriever is actually finding the right chunks.

**Common metrics:**

- **Recall@k**: Did the correct chunk show up in the top-k results?
- **MRR (Mean Reciprocal Rank):** How high in the list was the right chunk?
- **Diversity:** Are you retrieving different perspectives, not just duplicates?

**How to test:**

- Create a “golden set” of Q&A pairs with known answers.
- Run them through your retriever and score performance.

---

### 2. Evaluating Generation

Even if retrieval is correct, the LLM might mis-summarize.

**Checks to apply:**

- **Faithfulness**: Does the answer stick to the retrieved context?
- **Completeness**: Did it include all the relevant parts?
- **Formatting**: Is it structured (JSON, citations) as expected?

**Techniques:**

- Use programmatic validators (regex, schema checks with Pydantic).
- Run a second model (or rule-based system) as a “fact checker.”
- Layer in human spot-checks for high-stakes use cases.

---

### 3. Monitoring in Production

Once deployed, you need continuous visibility.

**Best practices:**

- **Log every query, retrieved docs, and final answer** (for debugging and audits).
- **Track drift**: Measure how often new documents enter the index and whether embeddings need to be refreshed.
- **Feedback loops**: Let users flag wrong answers, then feed that back into evaluation sets.
- **Alerting**: Set thresholds (e.g., retrieval confidence < 0.7) that trigger alerts or fallback behaviors.

---

### 4. Putting It All Together

A practical evaluation setup might look like this:

```
1. Golden dataset (50–100 Q&A pairs)
2. Automated retriever tests (recall@k, MRR)
3. Automated generator tests (schema validation, citation checks)
4. Human review of flagged edge cases
5. Monitoring dashboard (latency, cost, accuracy trends)

```

> 💡**Rule of thumb:** Treat your RAG pipeline like a machine learning model. If you can’t measure its accuracy and reliability, you can’t trust it in production.

## Key Takeaways

### Core Concepts

1. **RAG = Runtime knowledge injection**, not retraining
    - LLMs retrieve first, then generate
    - Answers are grounded in provided evidence
2. **Six primitives:**
    - Documents → Chunking → Embeddings → Vector Store → Retriever → Generator
3. **Key design levers:**
    - Chunk size: 400-800 chars (sweet spot for most use cases)
    - Overlap: 10-20% to preserve context
    - Top-k: 3-5 for balanced precision/recall
    - Prompt engineering: Enforce citations and fail-closed behavior
4. **Failure modes to watch for:**
    - Fragmented context (chunks too small)
    - Irrelevant retrieval (wrong top-k or embeddings)
    - Hallucination (weak prompt constraints)

<br>
<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

💡 **RAG doesn't make the LLM "know" your data.** It gives the LLM a research assistant. The LLM still generates the answer, but now it has evidence in front of it, just like you'd do better on an exam with your notes.

</aside>

---