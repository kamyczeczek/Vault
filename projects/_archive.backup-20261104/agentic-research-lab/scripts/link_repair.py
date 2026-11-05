#!/usr/bin/env python3
"""Record a verified correction edge: link a quarantined ledger entry to the
remediation that actually resolved it.

This is the honest half of the EXG `fixed_by` pattern. The synthesizer that
generates repair-shaped text to reach a metric was rejected for this
workspace: a generated SHACL snippet or envelope patch is cargo-cult
completion (a comment asserting a safety property is not the property), it
Goodharts the linkage metric, and it violates the recorded rule that
warnings stay pointers, never instructions (ACL'26 safety caveat).

The rule here is inverted: the human verifies, the machine records. This
script refuses to link unless:

- the referenced id exists in the ledger with state `quarantined`;
- the caller states the remediation and how it was verified (both stored).

Appends a `RepairProposal` with state `accepted` and a `resolves` field via
`repair_ledger.append`, so `repair_ledger.py --validate` still passes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from repair_ledger import append, read  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--resolves", required=True, help="quarantined ledger id (or stale:<gen>)")
    ap.add_argument("--remediation", required=True, help="what actually fixed it")
    ap.add_argument("--verified-by", required=True, help="how the fix was checked")
    ap.add_argument("--layer", default="harness",
                    choices=["prompt", "context", "loop", "harness", "graph", "attention", "ontology"])
    ap.add_argument("--boundary", default="correction-edge verification: referenced entry exists quarantined; remediation stated and checked by a human before recording")
    args = ap.parse_args()

    if not args.resolves.startswith("stale:"):
        targets = [e for e in read() if e.get("id") == args.resolves]
        if not targets:
            print(f"REFUSE: {args.resolves} is not a ledger id", file=sys.stderr)
            return 1
        if targets[0].get("state") != "quarantined":
            print(f"REFUSE: {args.resolves} is not quarantined "
                  f"(state={targets[0].get('state')})", file=sys.stderr)
            return 1

    event = append("RepairProposal", {
        "resolves": args.resolves,
        "remediation": args.remediation,
        "verified_by": args.verified_by,
        "layer": args.layer,
        "validation_boundary": args.boundary,
    }, state="accepted")
    print(f"linked {event['id']} --fixed_by--> {args.resolves}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
