# sox_copilot/evidence_agent.py
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.agents import create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .config import MODEL_NAME, AGENT_TEMP, MAX_ITER
from .tools import run_deterministic_check, get_policy_summary, generate_narrative

SYSTEM_GUIDANCE = f"""
You are a precise audit assistant for SOX controls.
- You MUST call tools to get policy, facts, and the narrative. Do not guess.
- Use counts and entry IDs EXACTLY as returned by tools.
- If a tool returns an error, include the error and do not fabricate results.
- Return ONLY one JSON object (no prose, no backticks).
""".strip()


PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_GUIDANCE),
    ("user",
     """Produce the audit result for control {control_id} in {period} using data at {csv_path}.
Required steps:
1) get_policy_summary(control_id) -> policy_summary
2) run_deterministic_check(control_id, perimod, csv_path) -> facts_json
3) generate_narrative(control_id, period, policy_summary, facts_json=<exact JSON from step 2>) -> narrative

Return ONLY this JSON:
{{
  "control_id": "{control_id}",
  "period": "{period}",
  "violations_found": <int from facts>,
  "violation_entries": <list[str] from facts>,
  "policy_summary": "<string from policy>",
  "population": {{
    "tested_count": <int from facts>,
    "criteria": "<string from facts>"
  }},
  "narrative": "<string from narrative>"
}}
"""),
    MessagesPlaceholder("agent_scratchpad"),
])

def build_evidence_agent() -> AgentExecutor:
    llm = ChatOpenAI(model=MODEL_NAME, temperature=AGENT_TEMP)
    # Adding more tools
    tools = [run_deterministic_check, get_policy_summary, generate_narrative]

    agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=PROMPT)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=MAX_ITER,           # Safety: prevent runaway agents
        handle_parsing_errors=True,       # Graceful error handling
        verbose=True,                    # More verbose output for testing
    )
