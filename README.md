# Uber x GA: AI Superpowered Data Professionals

## About

This three-day course equips data scientists and data engineers to extend their AI/ML practice into principled, production-ready agentic systems.

*   **Day 1:** You’ll build a foundation in compliant AI engineering—connecting financial controls, auditability, and probabilistic thinking with hands-on validation of LLM outputs and modern coding tools.
*   **Day 2:** Focuses on single-agent design: you’ll architect an agent, break down tasks, and implement Retrieval-Augmented Generation (RAG) to ground outputs in private data.
*   **Day 3:** Brings it all together in a capstone project where you design, build, and orchestrate a compliant two-agent system to solve a real-world business challenge.

## Prerequisites

*   Professional experience as a Data Scientist or Data Engineer.
*   Proficiency in Python and daily experience with AI/ML engineering tasks.

## Getting Started

To get started with this course, you'll need to have Python (version 3.11 or higher recommended) and Node.js installed on your machine.

1.  **Clone the repository:**
    ```bash
    git clone https://git.generalassemb.ly/modular-curriculum-all-courses/uber-ai-superpowered-data.git
    ```
2.  **Set up Python environment:**
    It's highly recommended to use a virtual environment to manage your Python dependencies.
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```
3.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```
4.  **Configure API Keys (if applicable):**
    Some modules may require API keys for services like OpenAI. Please refer to individual module instructions for details on how to set these up (e.g., via environment variables in a `.env` file).

## Course Schedule

### Day 1 - Principled & Compliant AI Engineering

| Module                                                              | Type               | Est. Delivery Time | About                                                                                      |
| ------------------------------------------------------------------- | ------------------ | ------------------ | ------------------------------------------------------------------------------------------ |
| Ice-breakers & Warm up Activities                                   | -                  | 30 min             | Orientation & module framing content                                                       |
| [AI Compliance & Risk Management (SOX)](./modules/ai-compliance-and-risk-management-sox) | Lecture            | 60 min             | Learn how SOX controls, data integrity, and auditability apply to AI systems.              |
| [Mindset Shift: Deterministic vs. Probabilistic Systems](./modules/mindset-shift-deterministic-vs-probabilistic-systems) | Lecture/Discussion | 60 min             | Contrast deterministic code with probabilistic AI, emphasizing a reliability mindset when “steering” models. |
| [Cursor Best Practices](./modules/cursor-best-practices)                      | Lecture/Workshop   | 60 min             | Leverage Cursor for AI-assisted coding, refactoring, debugging, and workflow best practices. |
| [Agent Architecture: Understanding Agents & Their Capabilities](./modules/agent-architecture-understanding-agents-and-their-capabilities) | Lecture            | 30 min             | Explore agent design patterns through scenarios, matching architecture to business needs.      |
| [Task Decomposition](./modules/task-decomposition-for-ai-agents)              | Lecture/Lab        | 30 min             | Break down complex problems into agent-ready tasks, comparing good vs poor approaches.     |
| [Scoring and Validation w/ LLMs](./modules/scoring-and-validation-w-llms)     | Lecture/Workshop   | 120 min            | Combine automated checks and human rubrics to evaluate LLM outputs.                        |
| Lesson Wrap up                                                      | -                  | 30 min             | Module summary activities.                                                                 |
| **Total content**                                                   |                    | **7 total course hours** |                                                                                            |

### Day 2 - AI Agent Architecture and RAG

| Module                               | Type               | Est. Delivery Time | About                                                                          |
| ------------------------------------ | ------------------ | ------------------ | ------------------------------------------------------------------------------ |
| Warm up Activities                   | -                  | 30 min             | Overview of day's lessons and content review                                   |
| [Intro to LangChain and LangGraph](./modules/modules/lab-orchestrating-and-evaluating-the-sox-copilot) | Lecture/Workshop   | 90 min             | Apply LangGraph primitives to build auditable workflows with branching and classifiers. |
| [Develop a Single-Agent System](./modules/develop-a-single-agent-system) | Lecture/Walkthrough| 120 min            | Design, assemble, and test a complete agent that meets requirements and design choices. |
| [Introduction to RAG](./modules/modules/lab-implementing-rag) | Lecture/Walkthrough| 60 min             | Identify core components of a Retrieval-Augmented Generation system.           |
| [Lab - Implementing RAG](./modules/lab-implementing-rag) | Lab                | 90 min             | Implement and evaluate RAG pipelines.                                          |
| Lesson Wrap up                       | -                  | 30 min             | Module summary activities.                                                     |
| **Total content**                    |                    | **7 total course hours** |                                                                                |

### Day 3 - Orchestrating Multi-Agent Systems

| Module                                       | Type               | Est. Delivery Time | About                                                                          |
| -------------------------------------------- | ------------------ | ------------------ | ------------------------------------------------------------------------------ |
| Warm up Activities                           | -                  | 30 min             | Overview of day's lessons and content review                                   |
| [Multi-Agent Systems & Orchestration](./modules/multi-agent-systems-and-orchestration-techniques) | Lecture            | 60 min             | Explore orchestration patterns, state management, context sharing, and error handling. |
| [Lab - Build the Compliance Reviewer Agent](./modules/building-agent-2-and-initial-integration) | Walkthrough/Lab    | 120 min            | Build and integrate a second agent to create a complete, functioning system.   |
| [Lab - Upgrading to LangGraph](./modules/lab-orchestrating-and-evaluating-the-sox-copilot) | Walkthrough/Lab    | 120 min            | Create evaluation plans, define success metrics, and trace system errors.      |
| [Lab — Refining the SOX Audit Copilot](./modules/lab-refining-the-SOX-audit-copilot) | Lab                | 120 min            | Test, debug, and refine the complete two-agent system.                         |
| Lab & Course Wrap up                         | -                  | 30 min             | Module summary activities.                                                     |
| **Total content**                            |                    | **7 total course hours** |                                                                                |


## Module Structure

Each module in this repository follows a consistent structure to help you navigate the content:

*   `README.md`: Provides an overview of the module, learning objectives, and key concepts.
*   `assets/`: Contains images and other static assets used in the module.
*   `solution/`: Contains the completed code and solutions for the labs and exercises.
*   `starter/`: Contains starter code for the labs and exercises, where applicable.
*   Other directories: May contain additional lecture materials, notebooks, or specific lab components.

## Labs Overview

Here is a consolidated list of all the labs in this course:

*   **Day 1:**
    *   [Task Decomposition](./modules/task-decomposition-for-ai-agents)
    *   [Scoring and Validation w/ LLMs](./modules/scoring-and-validation-w-llms)
*   **Day 2:**
    *   [Lab - Implementing RAG](./modules/lab-implementing-rag)
*   **Day 3:**
    *   [Lab - Build the Compliance Reviewer Agent](./modules/building-agent-2-and-initial-integration)
    *   [Lab - Upgrading to LangGraph](./modules/lab-orchestrating-and-evaluating-the-sox-copilot)
    *   [Lab — Refining the SOX Audit Copilot](./modules/lab-refining-the-sox-audit-copilot)
'''
