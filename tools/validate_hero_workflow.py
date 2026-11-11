#!/usr/bin/env python3
"""Enforce monotonic, evidence-backed review gates for the first hero craft.

This validates the gate record and blocks claims of out-of-order approval.
It cannot independently prove that the user saw or approved the evidence.
"""
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "art/hero_01/progress.json"
EXPECTED = [
    "Engineering and proportion plan",
    "Clay silhouette blockout",
    "Main fuselage surfacing",
    "Structural layers and aero",
    "Propulsion and lift hardware",
    "Canopy and cockpit",
    "Secondary geometry",
    "UV and PBR finish",
    "High-detail hero audit",
    "Godot export and inspection",
    "Mobile optimization and validation",
    "Game integration",
]


def validate_status(data: dict[str, Any]) -> list[str]:
    errors = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(data.get("schema_version") == 1, "schema_version must remain 1")
    check(data.get("asset_id") == "NF-H01", "unexpected craft ID")
    check(data.get("sequence_locked") is True, "hero craft sequence must remain locked")
    gates = data.get("gates", [])
    if not isinstance(gates, list) or len(gates) != len(EXPECTED):
        return errors + ["the full canonical 12-gate sequence must be present"]

    approved = data.get("last_approved_stage")
    active = data.get("current_stage")
    if type(approved) is not int or type(active) is not int:
        return errors + ["last_approved_stage and current_stage must be integers"]

    check(0 <= approved <= len(EXPECTED), "last_approved_stage out of range")
    check(active == approved + 1, "current stage must immediately follow last approved gate")
    check(1 <= active <= len(EXPECTED) + 1, "current stage out of range")

    for i, item in enumerate(gates, start=1):
        if not isinstance(item, dict):
            errors.append(f"gate {i}: invalid record")
            continue

        check(item.get("id") == i, f"gate {i}: cannot renumber or reorder gate ID")
        check(item.get("title") == EXPECTED[i-1], f"gate {i}: canonical title changed")
        state = item.get("state")
        evidence = item.get("evidence")
        review = item.get("user_review")

        check(isinstance(evidence, list), f"gate {i}: evidence must be an array")
        if i <= approved:
            check(state == "approved", f"gate {i}: previous stage must be approved")
            check(isinstance(evidence, list) and bool(evidence),
                  f"gate {i}: missing evidence of actual work")
            check(isinstance(review, dict) and review.get("decision") == "approved"
                  and bool(review.get("reference")) and bool(review.get("note")),
                  f"gate {i}: approval needs explicit user review reference and note")
        elif i == active:
            check(state == "in_progress", f"gate {i}: exactly current gate must be active")
            check(review is None, f"gate {i}: open gate cannot claim approval")
        else:
            check(state == "pending", f"gate {i}: future stage must stay pending")
            check(evidence == [], f"gate {i}: future stage must not claim completed evidence")
            check(review is None, f"gate {i}: future stage has premature approval")

        # Unknown state values are never legal, even when the stage is inactive.
        check(state in ("approved", "in_progress", "pending"),
              f"gate {i}: invalid state value")

    return errors


def main() -> int:
    data = json.loads(STATUS.read_text(encoding="utf-8"))
    errors = validate_status(data)
    if errors:
        for error in errors:
            print("HERO_WORKFLOW_ERROR:", error)
        return 1
    print(f"NF_HERO_BUILD_ORDER_OK current={data['current_stage']} approved_through={data['last_approved_stage']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
