<h1>
  <span>

  ![alt text](./assets/ga-logo.png)

  </span>
  <span class="subhead">Clarity, Traceability, Auditability</span>
</h1>

**Learning objectives:** 
- Identify and explain the core guardrails in Cursor-assisted coding.
- Apply Cursor compliance-oriented workflows (safe prototyping, refactoring, or debugging with verification steps) to improve code.

## Common Gotchas (and How to Fix Them)

| Problem                                       | Why It Happens                               | Solution                                                               | Finance Example                                      |
| --------------------------------------------- | -------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------- |
| Cursor suggests deprecated Pandas `.ix`       | Training data includes old code              | Use `@Docs` to reference latest Pandas documentation                   | Old GL merge logic fails in Pandas 2.0               |
| Generated code has hardcoded `/tmp/` paths    | Model doesn't know your environment          | Prompt: "Use pathlib and make paths configurable via env vars"         | Batch job fails when `/tmp` fills up                 |
| Tests pass but code fails in prod             | AI doesn't know your data quirks             | Add edge cases to prompts: "Handle null cost_center, empty GL strings" | Month-end close breaks on nulls                      |
| Cursor suggests `eval()` for dynamic formulas | AI prioritizes conciseness over safety       | Reject immediately; use safer alternatives (sympy, dict dispatch)      | Risk of code injection in user-defined formulas      |
| API rate limits not handled                   | AI focuses on happy path                     | Explicitly prompt: "Add exponential backoff for API calls"             | Treasury data fetch fails during high-volume periods |
| Logs expose sensitive data                    | Model doesn't understand data classification | Review all logging statements; prompt: "Mask account IDs in logs"      | Audit finding: customer account IDs in app logs      |

**Golden Rule:** If Cursor's suggestion feels "too clever", it probably is. Ask for the simple, readable version.

## When to be Mindful of Using Cursor

**Don't use AI for:**

### 1. Critical SOX logic

* Tax calculations, regulatory formulas, SOX controls, materiality thresholds
* **Why:** One hallucinated formula = audit finding, potential restatement
* **Instead:** Write manually, peer review, have AI generate exhaustive tests

**Example:** Intercompany elimination calculations must match GAAP requirements exactly.

### 2. Production secrets management

* Credential rotation, IAM policies, access control logic
* **Why:** Even with Privacy Mode, risk of leakage in prompts or suggestions
* **Instead:** Use vaults, manual review by security team

### 3. Performance-critical code

* Real-time pricing engines, high-frequency batch jobs, month-end close ETL (millions of rows)
* **Why:** AI optimizes for readability, not performance; may suggest inefficient patterns
* **Instead:** Profile first with actual data volumes, optimize manually, use AI for test generation

**Safer Uses of AI:**

* Boilerplate (arg parsing, logging setup, config loading)
* Test generation (especially edge cases)
* Refactoring for readability (add type hints, split long functions)
* Exploring unfamiliar codebases (chat: "How does this reconciliation work?")
* Documentation (generate docstrings, README sections)

## Quality Rubric (for accepting AI changes)

Before accepting any AI-generated code, verify:

| Criterion       | What to Check                                                   | Example Failure                                |
| --------------- | --------------------------------------------------------------- | ---------------------------------------------- |
| Correctness     | Tests pass; edge cases covered                                  | Missing null handling breaks on real data      |
| Clarity         | Type hints present; docstrings explain business logic           | Function purpose unclear without reading code  |
| Compliance      | No secrets in code/prompts; appropriate logging                 | API key hardcoded; no audit trail for failures |
| Traceability    | Commit message explains what/why; diff is reviewable            | Massive uncommented change; no context         |
| Maintainability | Follows team standards; no deprecated APIs; functions <50 lines | Uses pandas.ix (deprecated); 200-line function |

**Accept only when all five are green.**

## Productivity Tips & Shortcuts

### Essential Commands

| Action            | Shortcut             | Notes                                        | When to Use                              |
| ----------------- | -------------------- | -------------------------------------------- | ---------------------------------------- |
| Inline prompt     | Ctrl/Command+K       | Generate/refactor in place (selection-aware) | "Add type hints to this function"        |
| Chat panel        | Ctrl/Command+L       | Long-form Q&A; use `@file` and `@Docs`       | "Explain how this reconciliation works"  |
| Accept completion | Tab                  | Multi-line context-aware scaffolds           | Let it write boilerplate while you think |
| Switch model      | Ctrl/Command+M       | Try a stronger model for thorny tasks        | Complex refactors                        |
| Quick open        | Ctrl/Command+P       | Jump files fast                              | Navigate codebase during investigation   |
| Project search    | Ctrl/Command+Shift+F | Combine with AI answers                      | "Where else is this API called?"         |
| Go to def         | F12                  | Pair with chat for understanding             | Trace function calls in unfamiliar code  |

### Advanced Tips

* Use `@Docs` to reference official API docs (Pandas, LangChain, internal libs) for accurate suggestions.
* Chain prompts: Generate code -> Add type hints -> Generate tests (three separate prompts).
* Compare models: If two models differ, ask each to explain trade-offs.
* Save good prompts: Keep a `prompts.md` file with your best templates.

## Clarity, Traceability, Auditability: Non-Negotiables

* Review and test AI contributions; treat as untrusted until verified.
* Version control discipline

  * Frequent commits, descriptive messages ("Refactor with AI assist: add type hints + SOX logging").
  * Link PR descriptions to prompts when helpful ("Generated with Cursor prompt: [...]").
* Documentation

  * Ask Cursor: "Generate docstring explaining business assumptions and data flow."
  * Document business logic, calculation formulas, and control points.
* Dual control

  * Peer review for non-trivial AI-generated code (especially financial calculations).
* Sensitive data hygiene

  * No real account IDs, customer data, or live financial data in prompts; use placeholders.
  * Before sharing code with Cursor: redact sensitive values.
* Compliance scans

  * Run SAST/dependency checks; ensure logging is appropriate (not over-exposing PII/account data).

**Mindset:** Programmer-in-the-loop. Cursor accelerates; you remain accountable.

## .cursor/rules Ideas for Finance Teams

Here's what your `.cursor/rules` file could look like:

```markdown
# Finance - Cursor AI Rules

## Code Standards
- Always include Python type hints for function signatures
- Require docstrings for all functions explaining business purpose
- Follow PEP8; use black formatter
- Keep functions under 50 lines; extract helpers for complex logic

## Security & Compliance
- NEVER hardcode credentials, API keys, or account IDs
- Use environment variables for all secrets (prefix with UBER_)
- Add logging.warning() in except blocks for audit trail
- Include transaction IDs in all financial operation logs

## Data Handling
- Validate all GL data: check for null account_id, cost_center
- Flag out-of-balance entries (debits != credits) immediately
- When handling currency: always specify precision (Decimal, not float)
- For date comparisons: use timezone-aware datetime (UTC)

## Testing
- Generate pytest tests for happy path + 2 edge cases minimum
- Mock external APIs (Reuters, Bloomberg, internal services)
- Include data validation tests for finance-specific rules

## When Uncertain
- If unsure about library usage: ask before generating
- For SOX-relevant logic: flag for manual review
- For performance concerns: note "needs profiling with production data"
```

## Integrating LangChain & LangGraph

### Quick Demo: Scaffolding an Agent

**Setup**

* Docs in context: `@LangChainDocs`, `@LangGraphDocs` for accurate API usage
* Model choice: use a strong reasoning model for agent logic

**Pattern: Start Simple, Iterate**

**Step 1: Generate a basic chain (2 min)**
Prompt in Cursor chat (Ctrl/Command+L):

```
@LangChainDocs Create a simple LangChain agent that:
- Uses OpenAI GPT
- Has one tool: query_gl_balance(account_id: str) -> dict
- Returns balance for requested account
- Include type hints and error handling
```

**Review:**

* Check imports
* Verify tool definition structure
* Look for prompt template

**Step 2: Add LangGraph orchestration (2 min)**
Follow-up prompt:

```
@LangGraphDocs Convert this to a LangGraph workflow with nodes:
- "classify_request": Determine if user wants balance, transaction history, or variance
- "fetch_data": Call appropriate tool
- "format_response": Structure output for audit log
Include state management and conditional edges
```

**Review:**

* Check StateGraph setup
* Verify edge conditions
* Ensure state typing is correct

**Step 3: Generate tests (1 min)**

```
Generate pytest tests for this agent:
- Mock the OpenAI API calls
- Test all three routing paths (balance, history, variance)
- Verify audit log format includes request_id and timestamp
```
<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

## Key Takeaways

1. Cursor accelerates coding, refactoring, and understanding. You own the design and the evidence.
2. Bake in compliance: Privacy Mode, .cursor/rules, quality rubric, peer review, and audit trails.
3. Never trust first drafts: Generate -> Review -> Test -> Commit is the non-negotiable loop.
4. Know when not to use AI: Critical SOX logic, secrets management, and performance-critical code require manual implementation.
5. Cursor works for agents too: Same workflows apply to LangChain/LangGraph (preview today, deeper on Day 2).

</aside>

