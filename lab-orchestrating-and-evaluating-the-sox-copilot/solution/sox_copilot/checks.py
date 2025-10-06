import csv
from typing import List, Dict

def load_logs(path: str) -> List[Dict]:
    """Load CSV into a list[dict]; coerce numeric fields as needed."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            # normalize a few fields; students can add more later
            r["amount"] = float(r.get("amount") or 0.0)
            rows.append(r)
        return rows

def filter_payables_over_threshold(logs: List[Dict], amount_threshold: float) -> List[Dict]:
    """Return AP entries with amount > threshold."""
    return [
        r for r in logs
        if r.get("account", "").lower().startswith("accounts payable")
        and float(r.get("amount") or 0) > amount_threshold
    ]

def find_dual_approval_violations(ap_entries: List[Dict]) -> List[Dict]:
    """Return entries missing either approver_1 or approver_2."""
    return [r for r in ap_entries if not (r.get("approver_1") and r.get("approver_2"))]

def summarize_violations(violations: List[Dict]) -> Dict:
    """Return a lightweight summary (count + entry_ids as strings)."""
    return {"count": len(violations), "entry_ids": [str(v.get("entry_id")) for v in violations]}


def count_pay002_violations_from_csv(csv_path: str, amount_threshold: float) -> int:
    """Independent recount for PAY-002 given a CSV path."""
    rows = load_logs(csv_path)
    ap_over = filter_payables_over_threshold(rows, amount_threshold)
    violations = find_dual_approval_violations(ap_over)
    return len(violations)