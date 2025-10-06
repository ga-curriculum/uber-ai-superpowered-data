<h1>

  <span class="prefix">

  ![](./assets/ga-logo.png)

  </span> 

  <span class="headline">RAG for AI Agents</span>
</h1>

# Lab: Policy and Procedure Q&A with RAG

## Overview

In this lab, you'll build a RAG system that answers questions about company policies. Unlike a chatbot that might hallucinate information, your system will retrieve relevant passages from actual documents and generate answers that are grounded in those sources.

This architecture is critical for high-stakes domains like HR, compliance, legal, and customer support where accuracy and auditability matter more than creativity.

## What you'll build

A grounded Q&A agent that answers questions from company policies using RAG (Retrieval-Augmented Generation). The agent must:

- Retrieve relevant passages from a document collection
- Generate a concise answer with citations to source documents
- Fail closed when the context does not support an answer (no hallucinations!)
- Log all decisions for auditability

## Why RAG?

Large Language Models (LLMs) are trained on vast amounts of data, but they don't know about:

- Your company's specific policies
- Recent updates to procedures
- Internal documents not in their training data

RAG solves this by:

- Retrieving relevant documents at query time
- Augmenting the LLM's prompt with that context
- Generating an answer based only on what was retrieved

This keeps answers grounded in truth and auditable.

## Learning Objectives

By the end of this lab, you will be able to:

- Implement a complete RAG pipeline in LangChain
- Wrap the workflow in LangGraph with explicit state and conditional logic
- Add a simple groundedness check and fail-closed guardrail
- Log system outputs in an auditable format

## Prerequisites

**Required Setup:**

**Step 1: Install Python packages**

Using pip:
```bash
pip install langchain langchain-community langchain-openai langgraph faiss-cpu pydantic python-dotenv
```

Or using pipenv (recommended):
```bash
pipenv install
```

**Step 2: Set up your OpenAI API key**

Create a `.env` file in the `solution/` directory:
```bash
OPENAI_API_KEY=your-api-key-here
```

**Step 3: Add this to the top of your `lab.py` file**
```python
from dotenv import load_dotenv
load_dotenv()  # This loads your .env file
```

## Project Structure
```
rag-lab/
├── data/
│   └── policies/
│       ├── PAY-002-expense-approval.txt
│       ├── SEC-001-data-classification.txt
│       └── HR-101-remote-work.txt
├── runs/
│   └── rag_runs.jsonl (will be created)
├── .env (create this with your API key)
└── lab.py (your code goes here)
```

**How to Use This Lab:**

This lab is divided into 4 parts that build on each other. You'll write all your code in a single `lab.py` file, adding to it as you progress through each part. By the end, you'll have a complete RAG system!

1. **Part 1**: Load documents and build a vector store
2. **Part 2**: Add answer generation with an LLM
3. **Part 3**: Wrap everything in LangGraph with guardrails
4. **Part 4**: Test, log, and reflect
