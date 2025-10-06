# sox_copilot/reviewer_agent.py
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .config import MODEL_NAME, AGENT_TEMP, MAX_ITER
from .tools import recount_and_compare, generate_review_notes

SYSTEM_GUIDANCE = f"""
You are a SOX Reviewer Agent.
- NEVER invent facts; you must call tools to re-check evidence deterministically.
- Use tool outputs EXACTLY as returned for counts/IDs/flags.
- When calling recount_and_compare, pass the EXACT evidence JSON string you received.
- Write concise, professional review notes (<100 words); no extra commentary.
- Final answer must be a single JSON object only (no extra text, no backticks).
""".strip()

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_GUIDANCE),
    ("user",
     """Review this submitted evidence against the source CSV.

Evidence (JSON string):
{evidence}

CSV path:
{csv_path}

Use tools to:
1) recount_and_compare(csv_path, evidence_json=<the EXACT string above>) -> comparison
2) generate_review_notes(control_id=<from comparison>, period=<from comparison>,
   evidence_valid=<from comparison>, issues=<from comparison>) -> review_notes

Return ONLY this JSON:
{{
  "reviewed_control_id": "<from comparison>",
  "period": "<from comparison>",
  "evidence_valid": true|false,
  "issues": <list of strings from comparison>,
  "review_notes": "<short narrative from tool>"
}}
"""),
    MessagesPlaceholder("agent_scratchpad"),
])

def build_reviewer_agent() -> AgentExecutor:
    llm = ChatOpenAI(model=MODEL_NAME, temperature=AGENT_TEMP)
    tools = [recount_and_compare, generate_review_notes]
    agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=PROMPT)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=MAX_ITER,
        verbose=True,
        handle_parsing_errors=True,
    )
