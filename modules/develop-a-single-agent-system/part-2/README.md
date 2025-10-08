
<h1>
  <span style="display:flex; gap:20px; text-align:middler; font-size:">

  ![](/assets/ga-logo.png)

  </span> 
  <span class="headline">Observe and Evaluate Your Single-Agent System</span>
</h1>

## About

In this part you will add observability and lightweight evaluation to the Evidence Agent you built in Part 1. You will instrument traces, verify that deterministic facts flow into the final output, and run a small batch eval to compare prompt or model changes.

## Module Objectives

* Capture full execution traces with LangSmith, including prompts, tool inputs and outputs, latency, and token usage.
* Debug issues by inspecting traces and confirming that narrative text matches deterministic facts.
* Create a small evaluation dataset and compute simple quality signals such as faithfulness and pass rate.


---

## Introducing LangSmith

### About

As AI systems grow more complex, debugging and improving them requires more than print statements or manual inspection.
**LangSmith** is LangChain’s built-in **observability and evaluation platform** — a system that helps developers trace, debug, and measure every LLM-powered workflow from end to end.

With LangSmith enabled, every agent run becomes a fully transparent record of:

* which tools were called,
* what data and prompts were passed in,
* what the model responded with,
* and how long and costly each step was.

---

### Why This Matters

Large Language Models behave *probabilistically* — the same input can yield different outputs.
For that reason, testing alone isn’t enough. You need **visibility** into what the model actually did and **metrics** for how well it performed.

LangSmith provides both:

* **Traces** for transparency
* **Evals** for performance measurement
* **Comparisons** for continuous improvement

This combination turns AI workflows from “black boxes” into **auditable systems** that can be tuned, monitored, and trusted — which is especially critical in **SOX-compliant workflows** where traceability is mandatory.

---

### What You Can See in LangSmith

When you run your Evidence Agent with LangSmith enabled, you’ll see a structured tree of steps like this:

```
Evidence Agent (LLM Orchestrator)
├── get_policy_summary
├── run_deterministic_check
└── generate_narrative
```

Each node includes:

* Input parameters and outputs
* Prompt text sent to the LLM
* Model version and latency
* Token usage and cost
* Errors or exceptions, if any

You can replay, compare, and share runs directly from the LangSmith UI.

---
Absolutely — here’s a **ready-to-drop section** for your README, written in the same tone and structure as your other lessons.
It bridges the conceptual gap between *evaluation* and *observability* and explains why LangSmith combines both.

---

## Understanding Evaluation vs. Observability

When building traditional software systems, **evaluation** and **observability** serve different purposes and live in different parts of the development lifecycle.
In AI systems, these two concepts begin to overlap — and LangSmith sits right at that intersection.

---

### Classical Software: Two Separate Layers

In deterministic systems, the rules are clear:

| Concept           | Purpose                                | Typical Tools                                        | When It Happens   |
| ----------------- | -------------------------------------- | ---------------------------------------------------- | ----------------- |
| **Evaluation**    | Verify that code behaves as intended   | Unit tests, integration tests, CI/CD checks          | Before deployment |
| **Observability** | Understand what the system did and why | Logging, tracing, metrics (e.g., Datadog, New Relic) | After deployment  |

Because the code executes deterministically, **a passing test today will pass tomorrow**.
Once validated, observability is primarily about performance and uptime — not correctness.

---

### AI Systems: The Boundary Blurs

In LLM-based systems, outputs are **probabilistic**, and correctness is **contextual**.
Even if your system “passes” once, it might behave differently tomorrow.

That changes everything:

| Characteristic         | Implication                                                   |
| ---------------------- | ------------------------------------------------------------- |
| **Stochastic outputs** | You can’t rely on a single pass/fail test.                    |
| **Subjective quality** | You need human or rubric-based scoring.                       |
| **Opaque reasoning**   | Debugging requires inspecting the model’s intermediate steps. |

This is why **evaluation and observability converge**:
you can’t measure quality without seeing *how* a model reached its answer, and you can’t debug a bad output without knowing *how well* it met the intended criteria.

---

### LangSmith: Evaluation-Aware Observability

LangSmith bridges these layers by combining both functions in one workflow:

| Feature        | Purpose                                                                                     |
| -------------- | ------------------------------------------------------------------------------------------- |
| **Tracing**    | Captures every step of your run — prompts, inputs, outputs, tool calls, latency, and cost.  |
| **Evaluation** | Lets you define metrics (faithfulness, accuracy, tone) and compare across runs or versions. |
| **Linking**    | Each eval result links directly to its trace, so you can inspect *why* it passed or failed. |

In practice:

* **Developers** use traces to debug model behavior.
* **Auditors and analysts** use eval metrics to verify system quality and control compliance.
* **Teams** get a single source of truth for both *what happened* and *how good it was.*

---

### Why This Matters for the SOX Audit Copilot

In compliance contexts like SOX:

* **Observability** provides *traceability* — every step is visible and reproducible.
* **Evaluation** provides *accountability* — each result can be judged against control requirements.

Together, they form an **audit-ready feedback loop**:

> *“We can see exactly what the AI did, and we can prove it met the standard.”*

---

**Key Takeaway:**
In classical systems, evaluation and observability are separate.
In AI systems, they must be unified — because understanding *why* an agent behaved a certain way is inseparable from measuring *how well* it performed.

LangSmith operationalizes that principle by making **evaluation-aware observability** a core part of the agent development workflow.



## Part 2: Observability and Evaluation Lab

Deterministic code is easy to debug with logs. Probabilistic systems are not. When an agent can vary from run to run, you need execution traces that show which tools were called, with what inputs, and what each component produced. LangSmith provides this trace and a workflow for iterating with confidence. In this lab you will:

1. Turn on tracing and run your agent end to end.
2. Use the trace to verify the data path from checks to narrative.
3. Build a tiny eval set and track pass rate and faithfulness across runs.

---

## Prerequisites

**Required Knowledge:**

* Completion of Part 1A, 1B, and 1C with a working Evidence Agent
* Basic understanding of LangChain tools and the agent executor

**Environment Setup:**

```bash
# From the module directory you used in Part 1
cd modules/develop-a-single-agent-system/solution

# Activate the same environment
pipenv shell

# Ensure your .env has your OpenAI key
grep OPENAI_API_KEY .env || echo "OPENAI_API_KEY=your-key-here" >> .env

# Add LangSmith environment variables to your shell or .env
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_API_KEY="ls_api_abc123..."
export LANGCHAIN_PROJECT="uber-audit-copilot"
```

**Dependencies Used (from Pipfile):**

* `langchain` (~=0.3.0)
* `langchain-openai` (~=0.2.0)
* `langchain-core` (~=0.3.0)
* `pandas` (~=2.2.0)
* `python-dotenv` (~=1.0.0)
* `openai` (~=1.55.0)
* `jupyter`
* Python 3.11 required

**Verify your setup:**

```python
import os
from dotenv import load_dotenv
load_dotenv()
assert os.getenv("OPENAI_API_KEY"), "Missing OPENAI_API_KEY"
assert os.getenv("LANGCHAIN_TRACING_V2") == "true", "LangSmith tracing not enabled"
assert os.getenv("LANGCHAIN_API_KEY"), "Missing LANGCHAIN_API_KEY"
```

---

## What You Will Instrument

You will reuse the Evidence Agent from Part 1C. With tracing enabled via environment variables, LangChain will automatically send run metadata to LangSmith. Optionally you can attach a local callback for additional debugging.


## Architecture Overview

You will observe the same three tool calls from Part 1, now with a trace:

```
User Request
   ↓
Evidence Agent (LLM orchestrator)
   ├─ get_policy_summary(control_id) → policy string
   ├─ run_deterministic_check(control_id, period, csv_path) → facts JSON
   └─ generate_narrative(control_id, period, policy_summary, facts_json) → narrative
   ↓
Single JSON result for workpapers
```

Your trace should preserve the facts from `run_deterministic_check` through to the final JSON and the narrative text.

---

## Lab Structure: Progressive Build (2A → 2B → 2C)

### 📁 Part 2A: Instrument Tracing

**Focus:** Produce and inspect a LangSmith trace for one end-to-end run.
**What you build:** No code changes required beyond environment variables.
**Learning goal:** Read traces to confirm tool sequencing, inputs, and outputs.

### 📁 Part 2B: Debug With Traces

**Focus:** Introduce a controlled change, then locate the root cause in the trace.
**What you build:** A small modification in config or data to force a different outcome.
**Learning goal:** Connect changes in facts to changes in narrative via the trace.

### 📁 Part 2C: Batch Eval and Comparison

**Focus:** Create 5 to 10 cases, compute pass rate and a simple faithfulness score, then compare prompts or models.
**What you build:** A CSV of cases and a notebook cell that runs the batch, collects results, and prints summary metrics.
**Learning goal:** Make prompt and model decisions with evidence.

---

## Notebook Structure

The lab uses the notebook `sox_copilot_lab.ipynb` in the solution directory.

**Cell 0: Environment Check**

```python
import os
from dotenv import load_dotenv
load_dotenv()

assert os.getenv("OPENAI_API_KEY"), "Missing OPENAI_API_KEY"
assert os.getenv("LANGCHAIN_TRACING_V2") == "true", "LangSmith tracing not enabled"
assert os.getenv("LANGCHAIN_API_KEY"), "Missing LANGCHAIN_API_KEY"

print("✅ Environment variables loaded successfully!")
```

**Cell 1: Load and Inspect Data**

```python
import pandas as pd

df = pd.read_csv("data/journal_entries.csv")

print(f"📊 Loaded {len(df)} journal entries")
print(f"📋 Columns: {list(df.columns)}")
print("\n🔍 First few rows:")
df.head()
```

**Cell 2: Build Agent**

```python
from sox_copilot.evidence_agent import build_evidence_agent

agent = build_evidence_agent()

print("🤖 Agent built successfully!")
```

**Cell 3: One End-to-End Run**

```python
import json 

control_id = "PAY-002"
period = "2024-07"
csv_path = "data/journal_entries.csv"
params = {
    "control_id": "PAY-002",
    "period": "2024-07",
    "csv_path": "data/journal_entries.csv",
}

print("🚀 Running end-to-end evidence agent...")
res = agent.invoke(params)

raw = res["output"]
report = json.loads(raw)
report
```

**Expectation:** After this run, open LangSmith and confirm a run exists under your `LANGCHAIN_PROJECT`. Inspect the tree to see agent and tool steps with inputs and outputs.

**Cell 4: Local Faithfulness Check**

```python
from sox_copilot.tools import run_deterministic_check
facts = run_deterministic_check.invoke(params)
faithful = int(
    report["violations_found"]==facts["violations_found"] and
    set(report["violation_entries"])==set(facts["violation_entries"])
)
print({"faithfulness":faithful})
```

---

## LangSmith Evaluation on Real Data

### About

Use LangSmith's eval suite to run your agent across multiple real-world audit cases, score outputs, and visualize results.

### Step 1 – Create Dataset

`data/eval_cases.csv`

```csv
control_id,period,csv_path,expected_count
PAY-002,2024-07,data/je_case_01.csv,0
PAY-002,2024-07,data/je_case_02.csv,1
PAY-002,2024-07,data/je_case_03.csv,1
PAY-002,2024-07,data/je_case_04.csv,3
PAY-002,2024-07,data/je_case_edge.csv,1
```

### Step 2 – Upload Dataset to LangSmith

**Cell 5: Create LangSmith Dataset**

```python
from langsmith import Client
import pandas as pd, json
from sox_copilot.evidence_agent import build_evidence_agent
from sox_copilot.tools import run_deterministic_check

client = Client()
dataset = client.create_dataset("sox_eval_cases_2", description="PAY-002 audit controls")
df = pd.read_csv("data/eval_cases.csv")

for _, row in df.iterrows():
    client.create_example(inputs=row.to_dict(), dataset_id=dataset.id)
```

### Step 3 – Run Eval with Faithfulness Scorer

**Cell 6: Define Evaluator and Run Evaluation**

```python
def score_case(run, example):
    # Extract inputs from the example and outputs from the run
    inputs = example.inputs
    output = run.outputs
    
    # Run the deterministic check with the inputs
    facts = run_deterministic_check.invoke(inputs)
    
    # Compare the agent output with the facts
    faithful = int(
        output["violations_found"]==facts["violations_found"] and
        set(output["violation_entries"])==set(facts["violation_entries"])
    )
    return {"key": "faithfulness", "score": faithful}

# Create a wrapper function that accepts inputs
def run_agent(inputs):
    agent = build_evidence_agent()
    result = agent.invoke(inputs)
    return json.loads(result["output"])

client.evaluate(
    run_agent,
    data="sox_eval_cases_2",
    experiment_prefix="LangSmith Eval - PAY-002",
    max_concurrency=3,
    evaluators=[score_case],
)
```

### Step 4 – Inspect Results

In LangSmith → **Evaluations → "LangSmith Eval – PAY-002"**

* Faithfulness scores per case
* Latency and cost per run
* Click any row → full trace for debugging

### Step 5 – Compare Prompt or Model Versions

Re-run the eval with a new prompt or model name and compare pass rate / cost side-by-side in the UI.

---

## Step 6 - Add an LLM-Based Evaluator

Numerical checks capture correctness, but some metrics—like clarity or tone—require human-like judgment.
LangSmith supports **LLM evaluators** that use a secondary model to grade outputs semantically.

### Example LLM Evaluator for Narrative Quality

**Cell 7: Define LLM-Based Evaluator**

```python
from langchain_openai import ChatOpenAI
from langchain.evaluation import EvaluatorType, load_evaluator

# load a prebuilt "criteria" evaluator (faithfulness / conciseness / helpfulness)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
evaluator = load_evaluator(EvaluatorType.CRITERIA, llm=llm, criteria="helpfulness")

def llm_grade(run, example):
    # Extract the narrative from the run outputs
    output = run.outputs
    text = output.get("narrative", "")
    
    # Extract the csv_path from the example inputs
    inputs = example.inputs
    
    grade = evaluator.evaluate_strings(
        input=inputs["csv_path"],  # or a short summary context
        prediction=text
    )
    # returns a dict like {"score":0.9,"explanation":"Narrative clearly explains violations."}
    return {"key": "narrative_quality", "score": grade["score"]}
```

**Cell 8: Run Evaluation with Both Evaluators**

```python
# Create a wrapper function that accepts inputs
def run_agent(inputs):
    agent = build_evidence_agent()
    result = agent.invoke(inputs)
    return json.loads(result["output"])

client.evaluate(
    run_agent,
    data="sox_eval_cases",
    experiment_prefix="LangSmith Eval - PAY-002 (with LLM Grader)",
    evaluators=[score_case, llm_grade],
)
```

LangSmith will store both numeric and semantic scores in the Eval dashboard.

---

## Summary of Eval Flow

| Step                    | Action                          | Outcome                       |
| ----------------------- | ------------------------------- | ----------------------------- |
| **Define dataset**      | Real audit cases                | Input examples                |
| **Run agent**           | Execute on dataset              | Predictions + traces          |
| **Apply evaluators**    | Numeric + LLM grading           | Faithfulness + quality scores |
| **Review in LangSmith** | Inspect runs + compare versions | Continuous improvement        |

---

## Key Takeaway

LangSmith combines **traceability + measurement** into a single workflow.
You can now prove *what* the Evidence Agent did and *how well* it did it—turning probabilistic AI behavior into an auditable, testable, and continuously improvable system.
