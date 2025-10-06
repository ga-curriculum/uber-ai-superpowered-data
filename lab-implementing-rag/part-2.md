<h1>
  <span>

  ![alt text](./assets/ga-logo.png)

  </span>
  <span class="subhead">Part 2 - Generate Answers with RAG</span>
</h1>

## Goal

Add an LLM to generate grounded answers using retrieved context.

## The RAG Pattern

**Without RAG:**  
`User Question → LLM → Answer (might hallucinate!)`

**With RAG:**  
`User Question → Retrieve Context → LLM(Question + Context) → Grounded Answer`

The key is **prompt engineering** to ensure the LLM:

1. Only uses the provided context
2. Cites its sources
3. Admits when it doesn't know

This is what transforms a chatbot into a reliable Q&A system!

## Steps

### 1. Create an answer chain

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Use GPT-4o-mini for cost-effectiveness
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Craft a prompt that enforces grounding
answer_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a helpful assistant that answers questions about company policies. "
     "Answer ONLY from the provided context. "
     "If the context does not contain enough information to answer confidently, "
     "you MUST say 'Insufficient evidence to answer confidently.' "
     "Always include brief citations like [doc1], [doc2] to reference which context chunks you used."),
    ("human", "Question: {question}\n\nContext:\n{context}")
])

# Chain: prompt → LLM → parse string output
answer_chain = answer_prompt | llm | StrOutputParser()
```

**Why temperature=0?**  
We want deterministic, factual answers, not creative variation.

**Note the prompt engineering:**  
The system message explicitly tells the LLM to:

- ONLY use provided context
- Say "Insufficient evidence" when it can't answer
- Include citations like [doc1], [doc2]

This is critical for preventing hallucinations!

### 2. Test with a supported query

Now let's test it with a question the documents CAN answer:

```python
question = "What is the dual approval threshold for PAY-002?"
ctx_docs = retriever.invoke(question)

# Join all retrieved chunks into a single context string
ctx_text = "\n\n---\n\n".join([
    f"[doc{i+1}]: {doc.page_content}" 
    for i, doc in enumerate(ctx_docs)
])

answer = answer_chain.invoke({
    "question": question,
    "context": ctx_text
})

print(f"Question: {question}")
print(f"Answer: {answer}\n")
```

**Run it!** You should see something like:

```
Question: What is the dual approval threshold for PAY-002?
Answer: The dual approval threshold for PAY-002 is $10,000. Expenses of $10,000 
or more require approval from BOTH the department head and the finance officer [doc1].
```

Notice the citation [doc1] - this tells us which context chunk was used!

### 3. Test an unsupported query

Now let's test with a question the documents CANNOT answer:

```python
unsupported_question = "What is our PTO policy?"
ctx_docs = retriever.invoke(unsupported_question)

# Join all retrieved chunks into a single context string
ctx_text = "\n\n---\n\n".join([
    f"[doc{i+1}]: {doc.page_content}" 
    for i, doc in enumerate(ctx_docs)
])

answer = answer_chain.invoke({
    "question": unsupported_question,
    "context": ctx_text  # Same context (about expense policies)
})

print(f"Question: {unsupported_question}")
print(f"Answer: {answer}\n")
```

**Expected output:**
```
Question: What is our PTO policy?
Answer: Insufficient evidence to answer confidently.
```

**Why does this work?**  
The context is still about expense policies (from the previous query). Since there's nothing about PTO, the LLM follows our instructions and admits it can't answer!

**Discussion Point:**

- Try removing the "Insufficient evidence" instruction from the system prompt. What happens? 
- This demonstrates why explicit guardrails are critical in production systems!
- Can you think of scenarios where the LLM might still hallucinate despite the prompt?

## The Problem

We have a working RAG system. But there's a subtle issue: **we're trusting the LLM to follow our instructions**. What if it doesn't? What if it makes up an answer anyway?

In Part 3, we'll add an automatic **groundedness check** to verify that the LLM actually stayed grounded in the context.

**Checkpoint:** Your system generates answers with citations for supported queries, and says "Insufficient evidence" for unsupported ones.
