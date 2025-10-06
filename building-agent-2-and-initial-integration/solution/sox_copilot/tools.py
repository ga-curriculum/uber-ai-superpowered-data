# sox_copilot/tools.py
import json
from typing import Dict, Any, List
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .checks import (
    load_logs,
    filter_payables_over_threshold,
    find_dual_approval_violations,
    summarize_violations,
    count_pay002_violations_from_csv # New: Reviewer tools
)
from .config import AMOUNT_THRESHOLD, MODEL_NAME, MODEL_TEMP

@tool("run_deterministic_check", return_direct=False)
def run_deterministic_check(control_id: str, period: str, csv_path: str) -> Dict[str, Any]:
    """
    Run a single control check and return ONLY the facts we need in 1A.

        control_id: e.g., "PAY-002" (passed through for future parts)
        period:     e.g., "2024-07"  (passed through for future parts)
        csv_path:   path to journal entries CSV

    Returns:
        {
            "violations_found": int,
            "violation_entries": list[str],
            "population": {"tested_count": int, "criteria": str}
        }
    """

    rows = load_logs(csv_path)

    ap_over = filter_payables_over_threshold(rows, AMOUNT_THRESHOLD)
    violations = find_dual_approval_violations(ap_over)
    summary = summarize_violations(violations)


    return {
        "violations_found": summary["count"],           # How many violations found
        "violation_entries": summary["entry_ids"],     # Which specific entries failed
        "population": {                                # Context about what was tested
            "tested_count": len(ap_over),
            "criteria": f"Accounts Payable entries with amount > {AMOUNT_THRESHOLD:.2f}",
        },
    }

POLICY_TEXT: Dict[str, str] = {
    "PAY-002": "All payables over $1000 require dual approval.",
    "REV-001": "All revenue recognition entries must be approved by a manager.",
}

@tool("get_policy_summary", return_direct=False)
def get_policy_summary(control_id: str) -> str:
    """
    Return a short policy summary string for a SOX control ID.
    
    This gives the agent business context about what the control is testing.
    Essential for generating meaningful audit narratives that explain violations
    in business terms that stakeholders can understand.
    
    Args:
        control_id: SOX control identifier (e.g., "PAY-002", "REV-001")
        
    Returns:
        Human-readable policy description or "Unknown control" for invalid IDs
    """

    return POLICY_TEXT.get(control_id, "Unknown control.")

NARRATIVE_SYSTEM_PROMPT = (
    "You write concise audit narratives (<150 words). "
    "Never invent facts. Only use the provided policy summary and facts JSON. "
    "If violations exist, mention the entry IDs and briefly state the issue. "
    "If none, state the control operated effectively. "
    "Tone: neutral, professional, suitable for workpapers."
)
NARRATIVE_USER_PROMPT = (
    "Compose the narrative for control {control_id} in {period}.\n"
    "Policy summary: {policy_summary}\n"
    "Facts JSON: {facts_json}"
)

@tool("generate_narrative", return_direct=False)
def generate_narrative(control_id: str, period: str, policy_summary: str, facts_json: str) -> str:
    """
    Generate a concise audit narrative from provided policy + facts JSON.
    
    This tool demonstrates the "LLM chain" pattern - using a specialized LLM
    for professional writing while the main agent focuses on orchestration.
    
    Args:
        control_id: SOX control being tested (e.g., "PAY-002")
        period: Audit period (e.g., "2024-07")
        policy_summary: Business rule description
        facts_json: Technical violation data as JSON string
        
    Returns:
        Professional audit narrative suitable for workpapers
    """
    llm = ChatOpenAI(model=MODEL_NAME, temperature=MODEL_TEMP, max_tokens=220)

    prompt = ChatPromptTemplate.from_messages([
        ("system", NARRATIVE_SYSTEM_PROMPT),  # Sets AI behavior/personality
        ("user", NARRATIVE_USER_PROMPT),      # The actual task/request
    ])

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({
        "control_id": control_id,
        "period": period,
        "policy_summary": policy_summary,
        "facts_json": facts_json,
    }).strip()


# ------------------- NEW: reviewer tools -------------------
# sox_copilot/tools.py (inside recount_and_compare)
@tool("recount_and_compare", return_direct=False)
def recount_and_compare(csv_path: str, evidence_json: str) -> Dict[str, Any]:
    """
    Recount violations independently and compare against the provided evidence payload.

    Args:
        csv_path: Path to the source CSV used to generate evidence
        evidence_json: Evidence payload as a JSON string (dict with control_id, period,
                       violations_found, violation_entries, population, narrative, ...)

    Returns:
        {
          "reviewed_control_id": str,
          "period": str,
          "evidence_valid": bool,
          "issues": list[str]
        }
    """
    issues: List[str] = []

    # Parse the incoming JSON string
    try:
        ev = json.loads(evidence_json)
    except Exception:
        return {
            "reviewed_control_id": "UNKNOWN",
            "period": "UNKNOWN",
            "evidence_valid": False,
            "issues": ["invalid_evidence_json"],
        }

    control_id = ev.get("control_id")
    period = ev.get("period", "UNKNOWN")

    # Basic presence checks
    if control_id is None:
        issues.append("missing_control_id")
    if "violations_found" not in ev:
        issues.append("missing_violations_found")
    if "violation_entries" not in ev:
        issues.append("missing_violation_entries")

    # Parity check: count must match list length
    try:
        if ev.get("violations_found") != len(ev.get("violation_entries", [])):
            issues.append("violations_found != len(violation_entries)")
    except Exception:
        issues.append("failed_parity_check")

    # Independent recount (lab supports PAY-002 only)
    if control_id == "PAY-002":
        recount = count_pay002_violations_from_csv(csv_path, AMOUNT_THRESHOLD)
        if recount != ev.get("violations_found"):
            issues.append(
                f"independent_recount={recount} != evidence_count={ev.get('violations_found')}"
            )
    else:
        issues.append(f"unsupported_control_id={control_id}")

    return {
        "reviewed_control_id": control_id or "UNKNOWN",
        "period": period,
        "evidence_valid": len(issues) == 0,
        "issues": issues,
    }


REVIEW_NOTES_SYSTEM_PROMPT = (
    "You are a SOX reviewer. Be concise, neutral, and actionable. "
    "Never invent facts. Write <= 100 words suitable for workpapers."
)

REVIEW_NOTES_USER_PROMPT = (
    "Write reviewer notes for the evidence outcome below.\n"
    "Control ID: {control_id}\n"
    "Period: {period}\n"
    "Evidence valid: {evidence_valid}\n"
    "Issues: {issues}\n"
    "Guidance: If 'Issues' is 'None', say the evidence appears consistent. "
    "Avoid extra commentary."
)

@tool("generate_review_notes", return_direct=False)
def generate_review_notes(control_id: str, period: str, evidence_valid: bool, issues: List[str]) -> str:
    """Generate concise reviewer notes from the comparison result."""
    llm = ChatOpenAI(model=MODEL_NAME, temperature=MODEL_TEMP, max_tokens=140)
    prompt = ChatPromptTemplate.from_messages([
        ("system", REVIEW_NOTES_SYSTEM_PROMPT),
        ("user", REVIEW_NOTES_USER_PROMPT),
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({
        "control_id": control_id,
        "period": period,
        "evidence_valid": str(evidence_valid),              # keep it explicit for the prompt
        "issues": ", ".join(issues) if issues else "None",  # compact list -> string
    }).strip()