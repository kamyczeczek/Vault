#!/usr/bin/env python3
"""Regression tests for last_session_merged.py's builder.

The builder is the part that turns a session list into an auditable artifact:
header counts, index links, anchors, per-session SHA256, empty-session
skipping and harness filtering. These tests pin that shape so a change to the
render layer cannot silently break the delivery contract.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import agent_sessions
import last_session_merged


def _session(agent, sid, title, md, count=2):
    return agent_sessions.SessionItem(
        agent=agent, id=sid, title=title, directory="C:/ws",
        created_at="2026-10-19 10:00:00", updated_at="2026-10-19 10:00:00",
        message_count=count, model="acme/model", raw_path="store.db",
        text_markdown=md,
    )


def _native(agent, title, body):
    return (
        f"# [{agent}] {title}\n\n"
        f"- **Agent**: `{agent}`\n"
        f"- **ID**: `sid`\n\n"
        f"{body}"
    )


def test_losses_str_detailed():
    losses = last_session_merged._losses_str({
        "trunc": 2,
        "trunc_blocks": [2, 3],
        "artifact": 6,
        "artifact_tools": [1],
        "ext768": 5,
        "ext768_tools": [],
        "superseded": 1,
    })
    assert losses == "trunc msg 2,3 | artifact tool 1 | artifact 6 | 768B 5 | superseded 1"


def test_empty_assistant_ignores_tool_result():
    body = ("## [assistant]\n\n## [toolResult]\nok\n\n"
            "## [assistant]\n\n## [user]\nnext\n")
    marked, count = last_session_merged._mark_empty_assistant(body)
    assert count == 1
    assert marked.count("[empty model output]") == 1


def test_count_turns():
    body = "## [user]\na\n\n## [assistant]\nb\n\n## [tool]\nc\n"
    assert last_session_merged._count_turns(body) == 2


def test_build_merged_markdown_contract():
    last_session_merged._AGENT_SESSIONS = agent_sessions

    s1 = _session("opencode", "s1", "First", _native(
        "opencode", "First",
        "## [user]\nhello\n\n"
        "## [idle]\n\n"
        "## [system]\nThe tools changed.\n\n"
        "## [assistant]\n"
        "<details><summary>reasoning</summary>\n\nsecret\n\n</details>\n"
        "world\n"), count=4)
    s2 = _session("droid", "s2", "Empty", _native("droid", "Empty", ""), count=0)
    s3 = _session("omp", "s3", "Third", _native(
        "omp", "Third", "## [user]\nq\n\n## [assistant]\na\n"), count=2)
    sessions = [s1, s2, s3]

    text = last_session_merged.build_merged_markdown(
        sessions, "all", Path("out.md"), available=10)

    failures = []
    if "- **Wyrenderowano**: 2/3" not in text:
        failures.append("rendered/total counter missing or wrong")
    if "puste sesje pominiete: 1" not in text:
        failures.append("empty-session counter missing")
    if "- **Wczytano z magazynow**: 10" not in text:
        failures.append("loaded-from-stores counter missing")
    if text.count("# Sesja ") != 2:
        failures.append("rendered body count is not 2")
    if text.count('<a id="session-') != 2:
        failures.append("anchor count is not 2")
    if text.count("](#session-") != 2:
        failures.append("index link count is not 2")
    if text.count("- **SHA256**") != 2:
        failures.append("per-session SHA256 missing")
    if "## [idle]" in text:
        failures.append("idle event rendered as a turn")
    if "secret" in text:
        failures.append("reasoning kept without --include-reasoning")
    if "The tools changed." not in text:
        failures.append("system event text was lost instead of collapsed")
    if "(0 wiad. — pominieto)" not in text:
        failures.append("empty session not marked in index")
    if "1. **[opencode]** [First](#session-1)" not in text:
        failures.append("first index entry is not linked")

    full = last_session_merged.build_merged_markdown(
        sessions, "all", Path("out.md"), available=10, include_reasoning=True)
    if "secret" not in full:
        failures.append("--include-reasoning did not keep reasoning")

    if failures:
        raise AssertionError("; ".join(failures))


def test_harness_only_sessions():
    """Pin the empty-session policy: textless harness rows are skipped, text is not.

    Decision (documented in `build_merged_markdown`): a session whose body is
    empty after harness collapse is skipped and marked in the index. A session
    that only carries `system` text is NOT empty — the audit text is kept.
    """
    import agent_sessions

    last_session_merged._AGENT_SESSIONS = agent_sessions

    textless = _session(
        "opencode", "e1", "Idle only",
        _native("opencode", "Idle only", "## [idle]\n\n## [model-switched]\n"),
        count=2)
    with_text = _session(
        "opencode", "e2", "System only",
        _native("opencode", "System only", "## [system]\nMaintenance notice.\n"),
        count=1)

    text = last_session_merged.build_merged_markdown(
        [textless, with_text], "all", Path("out.md"))

    failures = []
    if "- **Wyrenderowano**: 1/2" not in text:
        failures.append("textless harness-only session was not skipped")
    if "1. **[opencode]** Idle only" not in text or "(0 wiad. — pominieto)" not in text:
        failures.append("skipped session not marked in the index")
    if "Maintenance notice." not in text:
        failures.append("system text from a harness-only session was lost")
    if text.count("# Sesja ") != 1:
        failures.append("harness-only session rendered as a full body")

    if failures:
        raise AssertionError("; ".join(failures))


def test_truncate_mid():
    """Head+tail keeps both ends and states the omitted size."""
    text = "A" * 500 + "MIDDLE" * 100 + "Z" * 500
    out = agent_sessions._truncate_mid(text, 800)
    failures = []
    if not out.startswith("A" * 400):
        failures.append("head not preserved")
    if not out.endswith("Z" * 400):
        failures.append("tail not preserved")
    if "…[+" not in out or " zn.]…" not in out:
        failures.append("gap marker missing")
    if agent_sessions._truncate_mid("short", 800) != "short":
        failures.append("short text changed")
    if not agent_sessions.TRUNC_MARKER_RE.search(out):
        failures.append("marker regex does not match output")
    if failures:
        raise AssertionError("; ".join(failures))


def test_dedup_tool_outputs():
    """Repeats collapse only within a session; the reference carries a line."""
    payload = "z" * 240
    body = (
        f"## [assistant]\n> out: `{payload}`\n\n"
        f"## [assistant]\n> out: `{payload}`\n")
    s1 = _session("opencode", "d1", "One", _native("opencode", "One", body))
    s2 = _session("opencode", "d2", "Two", _native("opencode", "Two", body))

    text = last_session_merged.build_merged_markdown(
        [s1, s2], "all", Path("out.md"))

    failures = []
    # One kept occurrence per session: session 2 must not reference session 1.
    if text.count(payload) != 2:
        failures.append("kept occurrence count is not 1 per session")
    if "[dup sha256:" not in text or "-> L" not in text:
        failures.append("intra-session reference missing a line offset")
    if "-> sesja" in text:
        failures.append("cross-session dedup still present")
    if ("- **Tool outputs**: 4  (unikalne: 2, dup w sesji: 2"
            not in text):
        failures.append("tool-output accounting line missing or wrong")
    if "krotkie <80 B: 0" not in text or "uciete: 0" not in text:
        failures.append("loss balance categories missing")
    if "- **Superseded (starszy read usuniety)**:" not in text:
        failures.append("superseded category missing")
    if "- **Zdarzenia harnessu (zwinięte)**:" not in text:
        failures.append("harness-event count missing")
    if "- **Rozmiar**: 000000 KB" in text:
        failures.append("size placeholder was not replaced")

    if failures:
        raise AssertionError("; ".join(failures))


def test_truncation_flag_and_fields():
    """A marker-bearing output is flagged (never deduped); extra fields emit."""
    capped = agent_sessions._truncate_mid("y" * 1600, 800)
    truncated_session = _session(
        "omp", "t1", "Cap",
        _native("omp", "Cap", f"## [assistant]\n> **tool result**: `{capped}`\n"))
    truncated_session.parent = "ses_parent123"
    clean = _session(
        "opencode", "t2", "Fine",
        _native("opencode", "Fine", "## [user]\nhi\n\n## [assistant]\nok\n"))

    text = last_session_merged.build_merged_markdown(
        [truncated_session, clean], "all", Path("out.md"))

    failures = []
    if "- **Uciete (marker" not in text or "1 sesji" not in text:
        failures.append("truncated-session counter missing")
    if "- **Uciete**: tak" not in text or "- **Uciete**: nie" not in text:
        failures.append("per-session truncated flag missing")
    if "- **Parent**: `ses_parent123`" not in text:
        failures.append("parent not rendered")
    if "- **Bloki**:" not in text or "- **Tury**:" not in text:
        failures.append("blocks/turns fields missing")
    if "parent ses_parent1" not in text:
        failures.append("parent not surfaced in the index")
    # Every session declares its losses; the capped one shows a trunc count.
    if "- **Straty**: trunc×1" not in text or "- **Straty**: brak" not in text:
        failures.append("per-session loss declaration missing")
    # Loss mechanisms and the verification recipe are declared in the header.
    for needle in ("- **Externalizacja (artifact://)**:",
                   "- **Truncacja 768B/linia**:",
                   "- **Straty razem**:",
                   "- **Miks agentow**:",
                   "- **Miks modeli**:",
                   "- **Charakter**:",
                   "- **Weryfikacja SHA256**:"):
        if needle not in text:
            failures.append(f"header declaration missing: {needle}")

    if failures:
        raise AssertionError("; ".join(failures))


def test_no_tools_externalizes_and_writes_index():
    """`--no-tools` must move payloads to artifacts/ and keep a verifiable index."""
    import hashlib
    import tempfile

    payload = "p" * 400
    capped = agent_sessions._truncate_mid("c" * 1600, 800)
    s1 = _session(
        "omp", "n1", "Tools",
        _native("omp", "Tools",
                f"## [user]\nrun\n\n"
                f"## [assistant]\n> out: `{payload}`\n\n"
                f"## [assistant]\n> out: `{capped}`\n"))
    s2 = _session(
        "opencode", "n2", "Short",
        _native("opencode", "Short", "## [user]\nhi\n\n"
                "## [assistant]\n> out: `tiny`\n"))

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "merged.md"
        text = last_session_merged.build_merged_markdown(
            [s1, s2], "all", out, no_tools=True)
        out.write_text(text, encoding="utf-8")

        assert payload not in text, "long output stayed inline"
        assert capped not in text, "truncated output stayed inline"
        assert text.count("> tool out: [artifact `artifacts/") == 3

        artifacts = sorted((Path(td) / "artifacts").iterdir())
        assert len(artifacts) == 3, artifacts
        assert payload in artifacts[0].read_text(encoding="utf-8")
        assert "[+800 zn.]" in artifacts[1].read_text(encoding="utf-8")

        index = (Path(td) / "index.tsv").read_text(encoding="utf-8").splitlines()
        assert index[0].startswith("session\tagent\tmodel\tsource\t")
        assert len(index) == 3
        assert "artifacts/ses-001-tool-001.txt" in index[1]
        assert "artifacts/ses-001-tool-002.txt" in index[1]
        # render_sha256 is the second-to-last-but-one field and must verify.
        for row in index[1:]:
            cols = row.split("\t")
            assert len(cols[4]) == 64
        assert "- **Externalizacja (artifact://)**:" in text
        assert "- **Tool outputs**: 3  (externalizowane: 3)" in text


def test_signatures_compact_and_index_claims():
    """`--signatures` keeps evidence verbatim and emits verifiable sidecars."""
    import json
    import tempfile

    payload = "noise " * 120
    fail_payload = "traceback line\nExited with code 2"
    body = (
        "## [user]\nrun\n\n"
        "## [assistant]\n"
        "> **tool** `shell` · completed\n"
        "> in: `{\"command\": \"Get-ChildItem\"}`\n"
        f"> out: `{payload}`\n\n"
        "commit 8da09f6 zawiera scripts/eval_queries.json:12\n\n"
        "## [assistant]\n"
        "> **tool** `shell` · completed\n"
        "> in: `{\"command\": \"git status --short\"}`\n"
        "> out: ` M file.py`\n\n"
        "## [assistant]\n"
        "> **tool** `shell` · completed\n"
        "> in: `{\"command\": \"pytest\"}`\n"
        f"> out: `{fail_payload}`\n")
    s1 = _session("omp", "g1", "Sig", _native("omp", "Sig", body))

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "merged.md"
        text = last_session_merged.build_merged_markdown(
            [s1], "all", out, signatures=True)
        out.write_text(text, encoding="utf-8", newline="\n")

        assert "> tool: shell · completed" in text
        assert "out_sha: " in text and "args_sha: " in text
        assert "artifact: artifacts/ses-001-tool-001.txt" in text
        assert payload not in text, "non-whitelisted output stayed inline"
        assert fail_payload in text, "non-zero exit was not kept verbatim"
        assert " M file.py" in text, "whitelisted evidence was not kept verbatim"
        assert "- **Tryb**: sygnatury" in text
        assert "- **Claims**: " in text
        assert "exit: explicit 1 (2:1); missing 2 (unknown, not zero)" in text
        assert "brak `exit:` ≠ exit 0" in text
        assert "brak tresci przy `## [assistant]`" in text

        records = [json.loads(x) for x in
                   (Path(td) / "tool_calls.jsonl").read_text(
                       encoding="utf-8").splitlines()]
        assert len(records) == 3
        assert records[0]["tool"] == "shell"
        assert records[0]["exit"] is None
        assert records[0]["truncated"] is False
        assert records[0]["whitelisted"] is False
        assert records[0]["verbatim"] == "none"
        # ICM: the record holds the payload file NAME (the payload store has
        # its own home, so the folder prefix is not baked into the record);
        # `*_path` carries the link as written in the body.
        assert records[0]["args_artifact"] == (
            "ses-001-tool-001.args.json")
        assert records[0]["args_artifact_path"] == (
            "artifacts/ses-001-tool-001.args.json")
        assert records[0]["artifact_path"] == (
            "artifacts/ses-001-tool-001.txt")
        assert (Path(td) / "artifacts/ses-001-tool-001.args.json").read_text(
            encoding="utf-8") == '{"command": "Get-ChildItem"}'
        assert records[1]["whitelisted"] is True
        assert records[1]["args_artifact"] is None
        assert records[1]["exit"] is None
        assert records[2]["exit"] == 2
        assert records[2]["verbatim"] == "full"
        assert records[2]["args_artifact"] is None

        claims = [json.loads(x) for x in
                  (Path(td) / "claims.jsonl").read_text(
                      encoding="utf-8").splitlines()]
        assert any(c["kind"] == "commit" and c["anchor"] == "8da09f6"
                   for c in claims)
        assert all(c["eval"] == "not_evaluated" for c in claims)
        commit = next(c for c in claims if c["kind"] == "commit")
        assert commit["supported_by"] == 1
        assert commit["support_tool"] == "shell"
        assert (Path(td) / "index.tsv").exists()
        assert (Path(td) / "claims.tsv").exists()
        assert (Path(td) / "artifacts/MANIFEST.tsv").exists()
        assert (Path(td) / "artifacts/MANIFEST.sha256").exists()
        assert (Path(td) / "artifacts/ses-001-tool-001.txt").read_text(
            encoding="utf-8") == payload
        manifest = (Path(td) / "artifacts/MANIFEST.tsv").read_text(
            encoding="utf-8").splitlines()
        assert manifest[0].startswith("session\ttool\tkind\t")
        assert len(manifest) == 5  # header + 3 out + 1 args


def test_split_index_and_sessions():
    """The default layout is an index plus per-session files with local links."""
    import tempfile

    payload = "noise " * 50
    body = (
        "## [user]\nrun\n\n"
        "## [assistant]\n"
        "> **tool** `shell` · completed\n"
        "> in: `{\"command\": \"Get-ChildItem\"}`\n"
        f"> out: `{payload}`\n\n"
        "## [assistant]\n\n"
        "## [user]\nend\n")
    s1 = _session("omp", "g2", "Split", _native("omp", "Split", body))

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "merged.md"
        store = Path(td) / "store.db"
        store.write_text("source", encoding="utf-8")
        s1.raw_path = str(store)
        text = last_session_merged.build_merged_markdown(
            [s1], "all", out, signatures=True, split=True)
        out.write_text(text, encoding="utf-8", newline="\n")

        session = Path(td) / "sessions/ses-001.md"
        assert session.exists()
        assert payload not in text, "body leaked into the index"
        assert "[Split](sessions/ses-001.md)" in text
        assert "- **Indeks**: ten plik" in text
        assert "- **Rozmiar calosci**:" in text

        sess_text = session.read_text(encoding="utf-8")
        assert payload not in sess_text, "signature kept the payload inline"
        assert payload in (Path(td) / "artifacts/ses-001-tool-001.txt").read_text(
            encoding="utf-8")
        assert "artifact: ../artifacts/ses-001-tool-001.txt" in sess_text
        assert "[empty model output]" in sess_text
        assert "- **Straty**: brak" in sess_text
        assert "- **Exit**: 0 jawnych, 1 nieznanych" in sess_text
        assert "- **Artefakty**: 2/2 zweryfikowane" in sess_text
        assert "- **Plik zrodlowy**:" in sess_text and "sha256:" in sess_text
        assert (Path(td) / "claims.tsv").exists()
        assert (Path(td) / "artifacts/MANIFEST.tsv").exists()
        manifest = (Path(td) / "artifacts/MANIFEST.tsv").read_text(
            encoding="utf-8").splitlines()
        assert len(manifest) == 3  # header + out + args


def test_cli_reasoning_flags():
    """Default off, `--include-reasoning` restores, `--no-reasoning` is accepted."""
    import contextlib
    import io
    import tempfile
    import types

    import agent_sessions

    sessions = [_session(
        "opencode", "r1", "Reasoning",
        _native("opencode", "Reasoning",
                "## [assistant]\n"
                "<details><summary>reasoning</summary>\n\nsecret trace\n\n"
                "</details>\nvisible answer\n"), count=1)]

    fake = types.SimpleNamespace(
        SUPPORTED_AGENTS=["opencode"],
        get_all_sessions=lambda *a, **k: sessions,
        render_session_body=agent_sessions.render_session_body,
        _session_header=agent_sessions._session_header,
        TRUNC_MARKER_RE=agent_sessions.TRUNC_MARKER_RE,
    )

    old_argv = sys.argv
    old_loader = last_session_merged._load_agent_sessions
    old_mod = last_session_merged._AGENT_SESSIONS
    failures = []
    try:
        last_session_merged._load_agent_sessions = lambda: fake
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.md"
            cases = [
                ([], False, "default"),
                (["--include-reasoning"], True, "--include-reasoning"),
                (["--no-reasoning"], False, "--no-reasoning"),
            ]
            for flags, expect_secret, label in cases:
                sys.argv = ["last_session_merged.py", "1", "-o", str(out),
                            "--monolith"] + flags
                with contextlib.redirect_stdout(io.StringIO()):
                    last_session_merged.main()
                text = out.read_text(encoding="utf-8")
                has_secret = "secret trace" in text
                if has_secret != expect_secret:
                    failures.append(
                        f"{label}: reasoning presence={has_secret}, "
                        f"expected {expect_secret}")
                if "visible answer" not in text:
                    failures.append(f"{label}: normal text missing")
    finally:
        sys.argv = old_argv
        last_session_merged._load_agent_sessions = old_loader
        last_session_merged._AGENT_SESSIONS = old_mod

    if failures:
        raise AssertionError("; ".join(failures))


if __name__ == "__main__":
    test_count_turns()
    test_build_merged_markdown_contract()
    test_harness_only_sessions()
    test_truncate_mid()
    test_dedup_tool_outputs()
    test_truncation_flag_and_fields()
    test_cli_reasoning_flags()
    print("test_last_session_merged.py: builder tests passed.")
