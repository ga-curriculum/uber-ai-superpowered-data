<h1>
<span>

![alt text](./assets/ga-logo.png)

</span>
  <span class="subhead">Scoring and Valiation Wrap-Up</span>
</h1>

**Learning objective:** Summarize key validation principles and discuss strategies to design audit-ready review workflows.

## Summary & Key Takeaways

### The Big Ideas

1. **Traditional metrics don't work for LLMs in compliance**
    - BLEU/ROUGE measure word overlap, not audit readiness
    - Accuracy doesn't capture clarity or professionalism
2. **Validation is two-layered: programmatic + human**
    - Programmatic catches structural/factual errors (schema, grounding, guardrails)
    - Human rubrics catch quality issues (clarity, tone, completeness)
3. **Both gates must pass—no exceptions**
    - Gate 1 (automated) weeds out broken outputs
    - Gate 2 (human) ensures audit readiness
    - Only approved outputs go into workpapers
4. **Fail-closed is the principle**
    - When in doubt, reject
    - Better to flag a false positive than miss a hallucination
5. **Validation is part of the pipeline, not an afterthought**
    - Build validation into your ETL/orchestration
    - Log results for audit trails
    - Iterate based on failure patterns


## Further Practice & Discussion Questions

### For Self-Study

1. **Extend the Pydantic validator** to check that narrative length correlates with violation count (more violations = longer narrative expected)
2. **Design a rubric** for a different use case (e.g., expense report summarization, vendor risk assessment)
3. **Write an LLM-as-judge prompt** that evaluates outputs against your rubric

### For Team Discussion

1. **Where in your current workflows would you add validation layers?**
    - Identify 2-3 high-stakes outputs that need validation
2. **Who should be the "human reviewers" on your team?**
    - What expertise do they need?
    - How much time can they dedicate?
3. **How would you handle the volume problem?**
    - If you generate 1000 outputs/day, how do you scale human review?
    - When would you use LLM-as-judge vs. sampling for human review?
4. **What's your organization's risk tolerance?**
    - How many false positives (rejected good outputs) are acceptable to avoid one false negative (approved bad output)?


## Additional Resources

### Tools & Libraries

- **Pydantic** (Python): Schema validation with type hints
- **Guardrails AI**: Framework for LLM output validation
- **LangSmith**: LLM evaluation and monitoring platform
- **Weights & Biases**: Experiment tracking with eval suites

