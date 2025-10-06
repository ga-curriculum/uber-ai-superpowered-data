<h1>
  <span>

  ![alt text](../assets/ga-logo.png)

  </span>
  <span class="subhead">Cursor Overview</span>
</h1>

**Learning objective:** Review Cursor's core features and setup for AI-assisted, compliance-first coding.

## Overview

In this module, we discuss how to use Cursor as a safe, auditable AI pair-programmer to speed up Python and agent development (LangChain/LangGraph) without sacrificing clarity, traceability, or compliance.

## Origin

Cursor emerged as an AI-powered code editor built on top of VS Code, designed to integrate large language models directly into the developer workflow.

Founding & Vision: Founded by former OpenAI engineers around 2023, Cursor’s mission was to make AI a true pair programmer rather than an autopilot - keeping developers in control while using AI to accelerate code generation, refactoring, and debugging.

Key Milestones:

* 2023: Public beta launch; gained early traction among AI-native developers for its seamless in-editor prompting and context awareness.
* 2024: Introduced codebase-aware chat, @file references, and .cursor/rules for customizable AI behavior.
* 2025: Widely adopted across AI engineering teams as a productivity and compliance tool emphasizing clarity, traceability, and auditability.

In short: Cursor started as a small experiment in embedding AI into code editing and has evolved into one of the core tools for AI-assisted development, teaching engineers how to "steer" AI safely rather than surrender control to it.

## Why Cursor for AI Development

* AI inside your editor: generate code, refactor, and query your codebase in context (no tab-hopping).
* Fast iteration loop for:

  * Python utilities, data pipelines, reconciliation scripts
  * ETL transformations and data quality checks
  * Debugging complex financial calculations
  * Writing docstrings/tests on demand
* Built-in privacy modes and enterprise-friendly posture reduce compliance friction.

**Key idea:** Treat Cursor as a second pair of eyes. You stay in charge of design and approvals.

## Compliance-First Setup

### Must-do settings

* **Privacy Mode:** On. Keep code local; avoid sending sensitive snippets in prompts.
* **Workspace Trust:** Require manual approval for executing code suggestions; disable "auto-run."
* **Model choice:**

  * Use stronger models (e.g., GPT-4 or Claude class) for nontrivial logic/refactors.
  * Use faster models for autocompletion/boilerplate.
* **AI Rules (`.cursor/rules`)**

  * Examples:

    * "Always include Python type hints and docstrings."
    * "Follow PEP8; avoid deprecated internal APIs."
    * "For secrets: use env vars, never literals."
    * "Include SOX-relevant logging for financial calculations (INFO for success, WARN for exceptions)."
    * "When handling GL data: validate account IDs, flag out-of-balance entries."
* **Docs in context (`@Docs`)**

  * Add LangChain/LangGraph APIs, internal library docs, coding standards.
  * Add Pandas, requests, and other common library documentation.
* **Extensions**

  * Python, Jupyter, Git integration, GitLens (blame/history).

**Setup checklist**

* Privacy Mode on
* Workspace Trust hardened
* Preferred models bookmarked
* `.cursor/rules` committed
* @Docs added (LC/LG + internal libs)
* Git + tests ready




