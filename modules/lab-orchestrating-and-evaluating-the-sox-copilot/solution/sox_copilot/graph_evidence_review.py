# sox_copilot/graph_evidence_review.py

# [TEACHING POINT] LangGraph mindset:
# - Dev controls the flow (nodes + edges), not the LLM.
# - Explicit, typed state + replayable runs => auditability.

from typing import TypedDict, Optional
import json

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from .config import AMOUNT_THRESHOLD, MODEL_NAME, MODEL_TEMP
from .models import EvidencePayload, ReviewPayload
from .tools import (
    get_policy_summary,
    run_deterministic_check,
    generate_narrative,
    recount_and_compare,
    generate_review_notes,
)

# ------------------------
# Graph State (typed)
# ------------------------
class GraphState(TypedDict, total=False):
    # Inputs
    control_id: str
    period: str
    csv_path: str

    # Evidence phase intermediates
    policy_summary: str
    facts: dict            # {"violations_found": int, "violation_entries": [...], "population": {...}}
    facts_json: str
    narrative: str

    # Validated outputs
    evidence: EvidencePayload
    evidence_errors: str   # serialized pydantic errors if any

    # Review phase intermediates
    comparison: dict       # {"reviewed_control_id":..., "period":..., "evidence_valid":..., "issues":[...]}
    review_notes: str

    # Final
    review: ReviewPayload


# ------------------------
# Nodes (pure functions)
# ------------------------

def node_get_policy(state: GraphState) -> GraphState:
    # [TEACHING POINT] In LangGraph, nodes are just Python functions.
    # We can reuse our LangChain tools as plain callables via .invoke().
    summary = get_policy_summary.invoke({"control_id": state["control_id"]})
    return {"policy_summary": summary}

def node_run_check(state: GraphState) -> GraphState:
    facts = run_deterministic_check.invoke({
        "control_id": state["control_id"],
        "period": state["period"],
        "csv_path": state["csv_path"],
    })
    return {"facts": facts, "facts_json": json.dumps(facts)}

def node_generate_narrative(state: GraphState) -> GraphState:
    nar = generate_narrative.invoke({
        "control_id": state["control_id"],
        "period": state["period"],
        "policy_summary": state["policy_summary"],
        "facts_json": state["facts_json"],
    })
    return {"narrative": nar}

def node_assemble_and_validate_evidence(state: GraphState) -> GraphState:
    # [TEACHING POINT] Pydantic at the graph boundary:
    # If this fails, we route to a failure path (typed, auditable).
    try:
        payload = EvidencePayload.model_validate({
            "control_id": state["control_id"],
            "period": state["period"],
            "violations_found": state["facts"]["violations_found"],
            "violation_entries": state["facts"]["violation_entries"],
            "policy_summary": state["policy_summary"],
            "population": state["facts"]["population"],
            "narrative": state["narrative"],
        })
        return {"evidence": payload, "evidence_errors": None}
    except Exception as e:
        return {"evidence_errors": str(e)}

def route_evidence_valid(state: GraphState) -> str:
    # [TEACHING POINT] Conditional edges: explicit routing logic.
    return "ok" if not state.get("evidence_errors") else "invalid"

def node_recount_and_compare(state: GraphState) -> GraphState:
    # [TEACHING POINT] Deterministic re-check (independent recount).
    comparison = recount_and_compare.invoke({
        "csv_path": state["csv_path"],
        "evidence_json": state["evidence"].model_dump_json(),
    })
    return {"comparison": comparison}

def node_generate_review_notes(state: GraphState) -> GraphState:
    notes = generate_review_notes.invoke({
        "control_id": state["comparison"]["reviewed_control_id"],
        "period": state["comparison"]["period"],
        "evidence_valid": state["comparison"]["evidence_valid"],
        "issues": state["comparison"]["issues"],
    })
    return {"review_notes": notes}

def node_assemble_and_validate_review(state: GraphState) -> GraphState:
    try:
        review = ReviewPayload.model_validate({
            "reviewed_control_id": state["comparison"]["reviewed_control_id"],
            "period": state["comparison"]["period"],
            "evidence_valid": state["comparison"]["evidence_valid"],
            "issues": state["comparison"]["issues"],
            "review_notes": state["review_notes"],
        })
        return {"review": review}
    except Exception as e:
        # [TEACHING POINT] Even review has a contract; fail closed.
        return {"review": None}

# ------------------------
# Graph builder
# ------------------------
def build_evidence_review_graph():
    # [TEACHING POINT] StateGraph wires nodes + routing into a compiled app.
    g = StateGraph(GraphState)

    # Evidence path
    g.add_node("get_policy", node_get_policy)
    g.add_node("run_check", node_run_check)
    g.add_node("write_narrative", node_generate_narrative)
    g.add_node("evidence_validate", node_assemble_and_validate_evidence)

    # Review path
    g.add_node("recount_compare", node_recount_and_compare)
    g.add_node("write_review_notes", node_generate_review_notes)
    g.add_node("review_validate", node_assemble_and_validate_review)

    # Edges: Evidence sequence
    g.add_edge(START, "get_policy")
    g.add_edge("get_policy", "run_check")
    g.add_edge("run_check", "write_narrative")
    g.add_edge("write_narrative", "evidence_validate")

    # Conditional: evidence validation gate
    g.add_conditional_edges(
        "evidence_validate",
        route_evidence_valid,
        {
            "ok": "recount_compare",      # proceed to reviewer flow
            "invalid": END,               # stop early; evidence schema failed
        },
    )

    # Review sequence
    g.add_edge("recount_compare", "write_review_notes")
    g.add_edge("write_review_notes", "review_validate")
    g.add_edge("review_validate", END)

    return g.compile()
