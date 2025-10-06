"""
RAG Lab: Policy and Procedure Q&A with Retrieval-Augmented Generation
====================================================================

This lab demonstrates building a grounded Q&A system using:
- LangChain for RAG components
- LangGraph for workflow orchestration
- OpenAI for embeddings and LLM
- FAISS for vector storage

"""

import json
import os
from datetime import datetime
from typing import List, Optional

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# =============================================================================
# Part 1: Prepare Documents & Build Vector Store (20 min)
# =============================================================================

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import glob

# Load all .txt files from the policies directory
# Using TextLoader directly to avoid dependency on 'unstructured' package
policy_files = glob.glob("data/policies/*.txt")
docs = []
for file_path in policy_files:
    loader = TextLoader(file_path)
    docs.extend(loader.load())

# Split documents into manageable chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,      # ~200 tokens per chunk
    chunk_overlap=120    # 15% overlap to preserve context
)
splits = splitter.split_documents(docs)

print(f"Loaded {len(docs)} documents")
print(f"Split into {len(splits)} chunks")
print("\nSample chunk:")
print(splits[0].page_content)
print(f"\nMetadata: {splits[0].metadata}")

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Create embeddings using OpenAI's embedding model
emb = OpenAIEmbeddings()

# Build a FAISS vector store (local, in-memory)
vs = FAISS.from_documents(splits, emb)

# Create a retriever that returns top 4 most similar chunks
retriever = vs.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)

print("Vector store created and ready for retrieval")

# Test retrieval
query = "What is the dual approval threshold for PAY-002?"
results = retriever.invoke(query)

print(f"\nRetrieved {len(results)} chunks for: '{query}'\n")
for i, doc in enumerate(results, 1):
    print(f"--- Chunk {i} ---")
    print(doc.page_content[:300])  # First 300 chars
    print(f"Source: {doc.metadata.get('source', 'Unknown')}\n")


# =============================================================================
# Part 2: Generate Answers with RAG (25 min)
# =============================================================================

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

# Test with a supported query
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

# Test an unsupported query
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


# =============================================================================
# Part 3: Add State & Guardrails with LangGraph (30 min)
# =============================================================================

from pydantic import BaseModel, Field

class QAState(BaseModel):
    """State object for our RAG workflow."""
    
    # Input
    question: str = Field(description="User's question")
    
    # Retrieval
    contexts: List[str] = Field(default_factory=list, description="Retrieved text chunks")
    citations: List[str] = Field(default_factory=list, description="Source references")
    
    # Generation
    draft_answer: Optional[str] = Field(default=None, description="LLM-generated answer")
    
    # Validation
    passed: Optional[bool] = Field(default=None, description="Did answer pass grounding check?")
    reason: Optional[str] = Field(default=None, description="Grading explanation")

# Create a groundedness grader
grade_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a strict fact-checker. Check if the answer is FULLY supported by the provided context. "
     "Reply with 'PASS' or 'FAIL' on the first line, then a short reason explaining your decision. "
     "Be strict: if the answer makes any claims not in the context, even minor ones, mark it as FAIL."),
    ("human", "Answer:\n{answer}\n\nContext:\n{context}")
])

grade_chain = grade_prompt | llm | StrOutputParser()

# Define graph nodes
from langgraph.graph import StateGraph, START, END

def retrieve_node(state: QAState) -> QAState:
    """Retrieve relevant documents."""
    docs = retriever.invoke(state.question)
    state.contexts = [doc.page_content for doc in docs]
    state.citations = [f"doc{i+1}" for i in range(len(docs))]
    print(f"Retrieved {len(docs)} chunks")
    return state

def generate_node(state: QAState) -> QAState:
    """Generate answer from context."""
    # Format context with citations
    joined = "\n\n---\n\n".join([
        f"[{state.citations[i]}]: {ctx}"
        for i, ctx in enumerate(state.contexts)
    ])
    
    state.draft_answer = answer_chain.invoke({
        "question": state.question,
        "context": joined
    })
    print(f"Generated draft answer ({len(state.draft_answer)} chars)")
    return state

def grade_node(state: QAState) -> QAState:
    """Check if answer is grounded in context."""
    joined = "\n\n---\n\n".join(state.contexts)
    verdict = grade_chain.invoke({
        "answer": state.draft_answer,
        "context": joined
    })
    
    state.passed = verdict.strip().upper().startswith("PASS")
    state.reason = verdict
    print(f"Grading: {'PASS' if state.passed else 'FAIL'}")
    return state

def fail_closed_node(state: QAState) -> QAState:
    """Fallback when grounding check fails."""
    state.draft_answer = "Insufficient evidence to answer confidently."
    print("Fail-closed response triggered")
    return state

# Initialize graph with our state schema
wf = StateGraph(QAState)

# Add nodes
wf.add_node("retrieve", retrieve_node)
wf.add_node("generate", generate_node)
wf.add_node("grade", grade_node)
wf.add_node("fail_closed", fail_closed_node)

# Define edges (flow)
wf.set_entry_point("retrieve")
wf.add_edge("retrieve", "generate")
wf.add_edge("generate", "grade")

# Conditional routing based on grading result
wf.add_conditional_edges(
    "grade",
    lambda state: "pass" if state.passed else "fail",
    {
        "pass": END,              # Success path
        "fail": "fail_closed"     # Failure path
    }
)

wf.add_edge("fail_closed", END)

# Compile into runnable
app = wf.compile()

# Quick test of the graph
test_state = QAState(question="What is the dual approval threshold for PAY-002?")
result = app.invoke(test_state)

print("\n" + "="*60)
print("GRAPH TEST RESULT")
print("="*60)
print(f"Answer: {result['draft_answer']}")
print(f"Passed: {result['passed']}")
print("="*60 + "\n")


# =============================================================================
# Part 4: Run, Log, and Reflect (15 min)
# =============================================================================

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

# Run comprehensive test suite
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
