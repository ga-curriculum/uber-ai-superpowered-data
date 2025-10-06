<h1>
  <span>

  ![alt text](../assets/ga-logo.png)

  </span>
  <span class="subhead">Introduction to Agentic Architecture</span>
</h1>

**Lesson objective:** Define what an AI agent is and explain how it differs from a simple LLM call.

## Introduction: Beyond the Chatbot

Working with the web version of ChatGPT, Claude, or other LLMs is highly simplified. You type a question, you get an answer.

But here's the problem: **That interaction is not enough for enterprise use cases.**

Why? Let's use a finance scenario:

**Scenario:** Your manager asks, *"Did we comply with PAY-002 in July?"*

- **Simple LLM approach:** You paste the question into ChatGPT. It gives you a confident-sounding answer... but can you trust it? Where did the data come from? Can an auditor verify it?
- **Agent approach:** A system automatically:
    1. Pulls July payables from your database
    2. Checks each transaction against PAY-002 criteria
    3. Identifies violations with specific transaction IDs
    4. Generates a summary you can include in workpapers
    5. Logs every step for the audit trail

**That's the difference between an LLM call and an agent.**

<aside>

💡 **An agent is not just an LLM.** An agent is an LLM embedded in a structured system with tools, memory, and rules. Think of it like the difference between asking a person a question vs. giving them a workflow to follow.

</aside>

## What is an AI Agent?

### Definition

An **AI agent** is a system that:

- Takes in **goals** or **queries** from users
- **Reasons** about what actions to take
- **Uses tools** to gather information or perform actions
- **Produces outputs** that are verifiable and useful

### Why "Agent" vs "LLM"?

| LLM Call | Agent System |
| --- | --- |
| One-shot interaction | Multi-step workflow |
| No access to real data | Can query databases, APIs, files |
| No memory of context | Can track state across interactions |
| Opaque reasoning | Logs every step for auditability |
| Probabilistic output | Combines deterministic tools + probabilistic reasoning |

### The Finance Context

In finance and compliance work, you need:

- **Evidence:** Actual data from systems of record
- **Accuracy:** Calculations that are 100% correct, not "mostly right"
- **Auditability:** A paper trail showing how conclusions were reached
- **Consistency:** The same query should produce the same results

> 💡 **Agents provide this. Raw LLMs don't.**
