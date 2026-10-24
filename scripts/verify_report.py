#!/usr/bin/env python3
"""Verify agent report against session transcript.

Detects helpfulness bias: claims in the report that have no
corresponding action in the transcript.

Based on "Harness as a Judge" pattern (Arize AI, Fuad Ali).
"""

import argparse
import json
import re
import sys
from pathlib import Path

CLAIM_KEYWORDS = [
    "wykonano", "zrobiono", "utworzono", "zmodyfikowano", "dodano", "dopisano",
    "wdrożono", "zaktualizowano", "zastosowano", "test", "passed", "ok", "✓",
    "commit", "hash", "git log", "read", "edit", "write", "guard",
    "stworzono", "poprawiono", "naprawiono", "zamknięto",
    "created", "modified", "added", "updated", "implemented", "committed", "fixed"
]

def parse_report(path: Path) -> list[dict]:
    """Extract claims from report. Returns list of {line_num, text, keywords, files}."""
    claims = []
    if not path.exists():
        return claims
    text = path.read_text(encoding="utf-8", errors="replace")
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("- ") or stripped.startswith("* "):
            # check if bullet or heading contains claim keywords
            pass
        # Check if line contains any claim keyword
        lower_line = stripped.lower()
        matched_kw = [kw for kw in CLAIM_KEYWORDS if kw in lower_line]
        if matched_kw:
            # Extract potential file paths mentioned in the line
            file_matches = re.findall(r'`?([a-zA-Z0-9_\-\./]+\.(?:md|py|json|yaml|yml|txt|sh))`,?', stripped)
            claims.append({
                "line_num": i,
                "text": stripped,
                "keywords": matched_kw,
                "files": file_matches
            })
    return claims

def parse_transcript(path: Path) -> list[dict]:
    """Extract actions from transcript (.jsonl or .json). Returns list of {tool, args, text}."""
    actions = []
    if not path.exists():
        return actions

    content = path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    # Try parsing as JSONL or single JSON
    try:
        data = json.loads(content)
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = [data]
        else:
            items = []
    except json.JSONDecodeError:
        items = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                # Fallback: treat line as raw text action
                actions.append({"tool": "text", "args": {}, "text": line})

    def extract_from_obj(obj):
        if isinstance(obj, dict):
            tool = obj.get("tool") or obj.get("tool_name") or obj.get("name") or obj.get("type")
            args = obj.get("arguments") or obj.get("args") or obj.get("parameters") or {}
            command = obj.get("command") or obj.get("cmd") or ""

            # Also check if it's a message with tool_calls
            if "tool_calls" in obj and isinstance(obj["tool_calls"], list):
                for tc in obj["tool_calls"]:
                    extract_from_obj(tc)

            if tool or command or args:
                actions.append({
                    "tool": str(tool or "unknown"),
                    "args": args if isinstance(args, dict) else {"raw": args},
                    "command": str(command),
                    "text": json.dumps(obj, ensure_ascii=False)
                })

            for v in obj.values():
                if isinstance(v, (dict, list)):
                    extract_from_obj(v)
        elif isinstance(obj, list):
            for item in obj:
                extract_from_obj(item)

    for item in items:
        extract_from_obj(item)

    return actions

def match_claims_to_actions(claims: list[dict], actions: list[dict]) -> list[dict]:
    """For each claim, find matching action. Returns list of {claim, match, evidence}."""
    results = []

    # Flatten action descriptions for searching
    action_texts = []
    for a in actions:
        t_str = f"{a.get('tool', '')} {a.get('command', '')} {json.dumps(a.get('args', {}))} {a.get('text', '')}".lower()
        action_texts.append(t_str)

    for claim in claims:
        matched = False
        evidence = "Found matching action in transcript"

        c_text = claim["text"].lower()
        c_files = claim["files"]

        # Check file references
        if c_files:
            file_matched = False
            for f in c_files:
                f_name = Path(f).name.lower()
                for a_text in action_texts:
                    if f_name in a_text or f.lower() in a_text:
                        file_matched = True
                        break
                if file_matched:
                    break
            if file_matched:
                matched = True
            else:
                evidence = f"No transcript action found referencing files: {c_files}"

        # Check commit reference
        elif "commit" in c_text or "git" in c_text:
            commit_matched = any("commit" in a or "git" in a for a in action_texts)
            if commit_matched:
                matched = True
            else:
                evidence = "No git commit action found in transcript"

        # Check test reference
        elif "test" in c_text or "passed" in c_text:
            test_matched = any("test" in a or "pytest" in a or "python" in a for a in action_texts)
            if test_matched:
                matched = True
            else:
                evidence = "No test run action found in transcript"

        else:
            # General keyword match against actions
            keyword_matched = any(kw in a for a in action_texts for kw in claim["keywords"] if len(kw) > 3)
            if keyword_matched or not actions:
                matched = True
            else:
                evidence = "No action corresponding to claim found in transcript"

        results.append({
            "claim": claim,
            "match": evidence if matched else None,
            "evidence": evidence
        })

    return results

def main():
    parser = argparse.ArgumentParser(description="Verify agent report against session transcript.")
    parser.add_argument("--report", required=True, help="Path to report markdown file")
    parser.add_argument("--transcript", required=True, help="Path to transcript file (.jsonl or .json)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args()

    report_path = Path(args.report)
    transcript_path = Path(args.transcript)

    if not report_path.exists():
        print(f"Error: report file not found: {report_path}", file=sys.stderr)
        sys.exit(2)
    if not transcript_path.exists():
        print(f"Error: transcript file not found: {transcript_path}", file=sys.stderr)
        sys.exit(2)

    claims = parse_report(report_path)
    actions = parse_transcript(transcript_path)
    results = match_claims_to_actions(claims, actions)

    discrepancies = [r for r in results if r["match"] is None]

    if args.json:
        print(json.dumps({
            "total_claims": len(claims),
            "total_actions": len(actions),
            "discrepancies": [d["claim"] for d in discrepancies]
        }, indent=2, ensure_ascii=False))
    else:
        print(f"=== Report Verification Results ===")
        print(f"Report: {report_path}")
        print(f"Transcript: {transcript_path}")
        print(f"Claims extracted: {len(claims)}")
        print(f"Actions extracted: {len(actions)}")
        print(f"Discrepancies found: {len(discrepancies)}")
        print()
        for d in discrepancies:
            c = d["claim"]
            print(f"ROZBIEŻNOŚĆ [Line {c['line_num']}]: {c['text']}")
            print(f"  Powód: {d['evidence']}")
            print()

    sys.exit(1 if discrepancies else 0)

if __name__ == "__main__":
    main()
