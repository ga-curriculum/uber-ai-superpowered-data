<h1>
  <span>

  ![alt text](./assets/ga-logo.png)

  </span>
  <span class="subhead">Part 4 - Run, Log, and Reflect</span>
</h1>

## Goal

Run your complete RAG system, log results for auditability, and test edge cases.

## Why Logging Matters

In production systems, especially for compliance-heavy domains like HR and legal, you need **audit trails**:

- What was asked?
- What context was retrieved?
- What answer was given?
- Was it validated?
- Why did validation pass or fail?

This part adds production-grade logging.

## Steps

### 1. Create a logging function

First, let's create a helper to log results. Add this to your `lab.py`:

```python
import json
import os
from datetime import datetime

def log_result(state_dict):
    """Log the result to a JSONL file for auditability."""
    # Ensure logs directory exists
    os.makedirs("runs", exist_ok=True)
    
    # Create log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": state_dict["question"],
        "answer": state_dict["draft_answer"],
        "passed_grounding": state_dict["passed"],
        "num_contexts": len(state_dict["contexts"]),
        "grading_reason": state_dict["reason"]
    }
    
    # Append to JSONL file (one JSON object per line)
    with open("runs/rag_runs.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    print("Logged to runs/rag_runs.jsonl")
```

**Why JSONL?**  
Each line is a valid JSON object, making it easy to:

- Stream large log files
- Process line-by-line without loading everything into memory
- Append new logs without parsing the whole file

### 2. Run and log a supported question

Now let's test with a question the system CAN answer:

```python
# Test with a question the system can answer
state = QAState(question="What is the dual approval threshold for PAY-002?")
result_dict = app.invoke(state)  # LangGraph returns a dict

print("\n" + "="*60)
print("FINAL STATE")
print("="*60)
print(f"Question: {result_dict['question']}")
print(f"Answer: {result_dict['draft_answer']}")
print(f"Passed Grounding: {result_dict['passed']}")
print(f"Citations: {', '.join(result_dict['citations'])}")
print("="*60 + "\n")

# Log it
log_result(result_dict)
```

**Note:** LangGraph's `.invoke()` returns a dict, not a Pydantic object. That's normal!

### 3. Test fail-closed behavior
Now test with a question outside the policy documents:

```python
# Test with a question outside the policy documents
unsupported_state = QAState(question="What is our PTO policy?")
result_fail = app.invoke(unsupported_state)

print("\n" + "="*60)
print("FAIL-CLOSED TEST")
print("="*60)
print(f"Question: {result_fail['question']}")
print(f"Answer: {result_fail['draft_answer']}")
print(f"Passed Grounding: {result_fail['passed']}")
print("="*60 + "\n")

# Log it
log_result(result_fail)
```

**Expected behavior:** The system should return "Insufficient evidence to answer confidently." even though the LLM initially tried to answer.

### 4. Run a comprehensive test suite
Let's test with diverse questions to validate the system's robustness:

```python
test_cases = [
    "What is the dual approval threshold for PAY-002?",      # Should answer
    "Who needs to approve expenses over $10,000?",           # Should answer
    "What is our PTO policy?",                               # Not in docs - fail closed
    "How do I classify confidential data?",                  # Should answer
    "What's the capital of France?"                          # Completely unrelated - fail closed
]

print("\n" + "="*60)
print("RUNNING TEST SUITE")
print("="*60 + "\n")

for i, question in enumerate(test_cases, 1):
    print(f"\n{'='*60}")
    print(f"Test {i}/{len(test_cases)}: {question}")
    print('='*60 + "\n")
    
    result_dict = app.invoke(QAState(question=question))
    
    print(f"Answer: {result_dict['draft_answer']}")
    print(f"Grounded: {result_dict['passed']}")
    print(f"Sources: {', '.join(result_dict['citations'])}")
    
    # Log each result
    log_result(result_dict)

print("\n" + "="*60)
print("All tests complete! Check runs/rag_runs.jsonl for logs")
print("="*60 + "\n")
```

**Run the full test!**

```bash
python lab.py
```

You should see:

- Tests 1, 2, 4: **PASS** with detailed answers and citations
- Tests 3, 5: **FAIL** → "Insufficient evidence" response

### 5. Inspect the logs

View your audit trail:

```bash
cat runs/rag_runs.jsonl | jq .
```

Or if you don't have `jq`:

```bash
cat runs/rag_runs.jsonl
```

Each log entry includes:

- Timestamp
- Question asked
- Answer generated
- Whether it passed grounding
- Number of context chunks used
- Reason for the grading decision

**Deliverables:**

- Logs exist in `runs/rag_runs.jsonl`
- Supported questions return grounded answers with citations
- Unsupported questions return the fail-closed message
- All decisions are auditable

---

## Wrap-up Discussion

### 1. Which part of the workflow felt most critical?

- **Chunking strategy?** Too small/large affects accuracy
- **Retrieval quality?** If you don't fetch the right docs, nothing else matters
- **Prompt engineering?** The instructions that keep the LLM grounded
- **Grading/validation?** The safety net that catches errors

Which would you invest the most time in for a production system?

### 2. Auditability & Trust

If you were auditing this system for compliance, what would you want logged?

- User questions
- Retrieved documents (and their sources)
- Draft answers before and after grading
- Grading verdicts and reasons
- Timestamps

What else would you add for a real enterprise system?

- User IDs and session IDs
- Model versions used
- Latency metrics
- Cost per query
- Confidence scores

### 3. Scaling Considerations

How would you scale this to 1,000+ documents?

- **Better vector stores**: Pinecone, Weaviate, Qdrant (instead of local FAISS)
- **Hybrid search**: Combine keyword + semantic search
- **Metadata filtering**: "Only search in HR policies" or "Only docs from 2024"
- **Caching**: Store answers to common queries
- **Batch indexing**: Update the vector store incrementally
- **Sharding**: Split documents by department/domain

### 4. Failure Modes

What could still go wrong with this system?

- **Poor chunking**: Loses context across chunk boundaries
- **Retrieval misses relevant docs**: Low recall (we only retrieve top-4)
- **LLM misinterprets context**: Comprehension errors
- **Grading is too lenient/strict**: LLM judge makes mistakes
- **Adversarial queries**: Intentionally trying to trick the system
- **Outdated documents**: Index doesn't reflect latest policy changes
- **Ambiguous policies**: What if two policies contradict each other?

---

## Congratulations!

You've built a complete, production-ready RAG system with:

- Document loading and chunking
- Vector embeddings and semantic search
- LLM-powered answer generation
- Automatic groundedness validation
- Fail-closed guardrails
- Comprehensive audit logging
- LangGraph workflow orchestration

This architecture is used in real-world applications across:

- **Legal**: Case law research
- **Healthcare**: Clinical decision support
- **Finance**: Regulatory compliance
- **Customer Support**: Knowledge base Q&A
- **Internal Tools**: Company policy assistants

**Want more?** Check out `stretch.md` for advanced challenges!
