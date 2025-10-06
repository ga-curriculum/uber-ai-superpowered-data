<h1>
  <span>

  ![alt text](./assets/ga-logo.png)

  </span>
  <span class="subhead">History of AI Evaluation and Importance</span>
</h1>

**Learning objective:** Explain how automated checks and human rubrics work together to judge AI output quality.  

## Overview

In compliance-critical environments like finance, the question isn't "Can LLMs produce useful outputs?" but rather **"Can we trust those outputs in an audit workpaper?"**

Traditional AI evaluation metrics (accuracy, BLEU scores, F1) were designed for deterministic systems with clear right/wrong answers. But LLMs are different:

- Multiple valid phrasings exist for the same answer
- Outputs are probabilistic, not deterministic
- "Plausible but wrong" is the most dangerous failure mode
- Compliance requires auditability, reproducibility, and professional clarity
 

## The Quick History

AI evaluation has evolved through distinct eras, each with metrics suited to their time—but inadequate for LLMs in high-stakes workflows:

**Era 1: Classic ML (1990s-2000s)**

- **Metrics:** Accuracy, Precision/Recall
- **Use case:** Fraud detection, classification tasks
- **Why it worked:** Clear ground truth labels (fraud = yes/no)
- **Limitation:** Requires binary correctness—doesn't handle nuance

**Era 2: NLP/Text Generation (2000s-2010s)**

- **Metrics:** BLEU, ROUGE (n-gram overlap)
- **Use case:** Machine translation, summarization
- **Why it worked:** Fast, automated, consistent
- **Limitation:** Penalizes valid rephrasings, rewards word-matching over meaning

**Example:**

```
Reference: "The company settled its invoices."
LLM Output: "The firm paid its bills."
BLEU Score: Low (few matching words)
Actual Quality: Perfect (same meaning)
```

**Era 3: Benchmarks & Leaderboards (2010s-2020)**

- **Metrics:** Task-specific benchmarks (SQuAD, GLUE, ImageNet)
- **Use case:** Model comparison, academic research
- **Why it worked:** Standardized, competitive
- **Limitation:** Models optimize for benchmarks, not real-world tasks

**Era 4: LLMs & Open-Ended Generation (2020-present)**

- **Challenge:** No single "correct" answer
- **What matters now:** Usefulness, clarity, compliance with instructions, factual accuracy
- **Emerging approaches:**
    - Human evaluation rubrics
    - LLM-as-judge (AI evaluating AI)
    - Hybrid programmatic + human validation

## Why This Matters for Compliance

In SOX and financial reporting:

| Traditional Metric | Compliance Reality |
| --- | --- |
| Accuracy = 95% | Not enough—need 100% factual grounding for audit evidence |
| BLEU/ROUGE score | Auditors don't care about word overlap—they care about completeness and clarity |
| Benchmark performance | Irrelevant—need task-specific validation for narratives, exception reports, control summaries |

**The mindset shift:** You're not debugging code anymore. You're auditing probabilistic outputs.

> Key Takeaway: Traditional metrics measure similarity to references. Compliance validation measures fitness for audit use. These are fundamentally different goals.
> 

---

## Why Validation is Non-Negotiable

### The Compliance Bar

In deterministic systems, validation is binary: code either works or doesn't. With LLMs, validation is **layered**:

1. **Structural checks** (deterministic): Does it meet schema requirements?
2. **Grounding checks** (deterministic): Do facts reconcile with source data?
3. **Quality checks** (probabilistic): Is it clear, professional, audit-ready?

### Failure Modes Without Validation

Real examples of what goes wrong:

### 1. Hallucination

```
Source Data: 2 violations found in entries [1002, 1003]
LLM Output: "3 violations were identified..."
Result: Failed control, audit findings
```

### 2. Omission

```
Source Data: Violations in entries 1002, 1003, 1005
LLM Narrative: "Entries 1002 and 1003 violated PAY-002."
Result: Incomplete evidence, missing exception
```

### 3. Ambiguity

```
LLM Output: "Some violations were found in the period."
Result: Too vague for workpapers—auditor cannot verify
```

### 4. Format Drift

```json
// Expected schema
{
  "control_id": "PAY-002",
  "violations_found": 2,
  "narrative": "..."
}

// LLM actually returns
{
  "control": "PAY-002",
  "issues": 2,
  "summary": "..."
}
```

Result: Downstream systems break, pipeline fails

### The Risk Cascade

```
Unchecked LLM Output
    ↓
Goes into audit workpaper
    ↓
Auditor relies on it
    ↓
Turns out to be wrong
    ↓
Control failure / audit exception / regulatory finding
```

### What "Validation" Means in This Context

| Validation Type | Purpose | Examples |
| --- | --- | --- |
| **Programmatic** | Catch structural/factual errors automatically | Schema validation, ID count matching, numeric reconciliation |
| **Human Rubric** | Judge usefulness, clarity, professionalism | Narrative tone, completeness, compliance alignment |
| **Hybrid** | Combine strengths of both | Schema passes + rubric approval = safe for workpapers |

## The Two-Gate Model

```
LLM Output
    ↓
Gate 1: Programmatic Validation
    ├─ Schema check
    ├─ Grounding check
    └─ Guardrails
    ↓
Gate 2: Human Rubric
    ├─ Faithfulness to data
    ├─ Clarity & conciseness
    ├─ Professional tone
    └─ Compliance alignment
    ↓
Audit Workpaper
```

**Both gates must pass. No exceptions.**

## Key Takeaway

<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

💡 In compliance, "plausible" ≠ acceptable. Every output must be structurally sound AND contextually appropriate before it's audit-ready.

</aside>
