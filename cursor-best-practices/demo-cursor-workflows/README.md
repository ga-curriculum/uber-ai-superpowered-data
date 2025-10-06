<h1>
  <span>

  ![alt text](../assets/ga-logo.png)

  </span>
  <span class="subhead">Demo: Cursor Workflows</span>
</h1>


**Learning objective:** Generate code with Cursor and evaluate workflow efficiency tradeoffs. 

## Overview

In this live session, we’ll build and refine a real finance utility together using Cursor. The goal is to understand *how to steer Cursor* for reliable, auditable outcomes.

We’ll go step by step, showing Cursor’s different workflows: inline generation, chat-based explanation, refactoring, test generation, and commit best practices.
Participants will follow along in their own environments.

---

## Part 1: Setting Up

Before starting, ensure that:

* Privacy Mode is turned **on** in Cursor.
* The `.cursor/rules` file is present in your workspace.
* You have an empty folder or repository ready to work in.

Confirm that you can use:

* **Inline generation:** `Ctrl/Command + K`
* **Chat panel:** `Ctrl/Command + L`

---

## Part 2: Generate the Utility

**Scenario:** Treasury needs a utility to fetch daily FX rates, cache them for 4 hours, and validate them against Bloomberg data for month-end close.

### Step 1: Create the function

1. Create a new file named `fx_reconciliation.py`.

2. In Cursor, open an inline prompt (`Ctrl/Command + K`) and enter:

   ```
   Create fetch_fx_rates() function:
   - Uses requests library to call Reuters FX API
   - Reads API key from FX_API_KEY environment variable
   - Caches results for 4 hours using a dict with timestamp
   - Returns dict of {currency_code: rate}
   - Includes error handling for API failures
   ```

3. Review the generated code carefully:

   * Verify all imports (`requests`, `os`, `datetime`).
   * Confirm that the API key is pulled from an environment variable.
   * Review caching and error handling logic for completeness.

**What to look for:** The function should meet most of the prompt requirements, but ensure that they have clarity ie type hints, and detailed logging.

---

## Part 3: Add Compliance and Clarity
If they do not have clarity, type hints, etc:

1. Highlight the entire function and use an inline prompt (`Ctrl/Command + K`):

   ```
   Add Python type hints and a detailed docstring explaining:
   - Purpose (month-end close process)
   - Parameters and return types
   - Cache behavior and SLA
   - Error scenarios
   ```

2. Review the suggested changes and apply them if correct.

3. Add audit logging for compliance:

   * Highlight the `except` block and prompt:

     ```
     Add logging.warning() with request details for audit trail. Do not log API key.
     ```

4. Add a validation function below the main one:

   ```
   Create validate_rates() function:
   - Checks rates against expected ranges (EUR 0.8–1.2, GBP 1.1–1.4, JPY 100–150)
   - Returns list of out-of-range currencies
   - Includes type hints and docstring
   ```

**Key point:** Review every suggestion for safety. Reject any code that logs sensitive data or modifies business logic incorrectly.

---

## Part 4: Generate and Run Tests

1. Open the chat panel (`Ctrl/Command + L`).

2. Prompt:

   ```
   @fx_reconciliation.py Generate pytest tests for:
   - Successful API call with mocked response
   - Cache hit (within 4 hours)
   - Cache miss (after 4 hours)
   - API failure handling
   - Validation function with out-of-range rates
   Use pytest-mock for mocking requests and datetime.
   ```

3. Create a file named `test_fx_reconciliation.py` and copy the generated tests into it.

4. Run the tests:

   ```
   pytest -v
   ```

5. Review results and fix any issues that appear, such as incorrect imports or missing fixtures.

**What to notice:** The AI generates useful scaffolding for tests but may not handle all edge cases correctly. Validate that all test conditions align with the business logic.

---

## Part 5: Document and Commit

1. In the chat panel, ask Cursor to explain the file:

   ```
   Explain what @fx_reconciliation.py does and summarize the key logic.
   ```

   Review the explanation and copy key details into your project documentation.

2. Commit your work:

   ```bash
   git add fx_reconciliation.py test_fx_reconciliation.py
   git commit -m "Add FX rate reconciliation utility with AI assist: env vars, caching, and audit logging"
   ```

**Key point:** Commit messages should describe the intent of the change and note when AI assistance was used.

---


## Key Takeaways

1. **Cursor is a coding partner, not an autopilot.** Every generation requires review, testing, and verification.
2. **Follow the workflow:** Generate → Review → Refactor → Test → Commit.
3. **Compliance and clarity are non-negotiable.** Keep Privacy Mode on, redact sensitive data, and document all logic.
4. **Cursor accelerates iteration, not decision-making.** Human oversight ensures correctness, readability, and auditability.
5. **Good practice builds trust.** The more explicit your prompts and rules, the more reliable Cursor’s output will be.

