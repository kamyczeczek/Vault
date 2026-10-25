"""Run the OKF-RAG Smart Connections benchmark with local cosine ranking.

Vectors and source records are read from ``.smart-env``. Obsidian CLI is used
only to export block locators and same-model query embeddings; all source and
passage scoring and ranking happens in this Python process.
"""

from __future__ import annotations

import argparse
from array import array
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
NOTES_ROOT = ROOT / "Notes" / "OKF-rag"
QUESTIONS_PATH = NOTES_ROOT / "benchmark-questions.json"
SOURCE_INDEX_PATH = ROOT / ".smart-env" / "smart_sources" / "smart_sources.ajson"
SOURCE_VECTORS_PATH = ROOT / ".smart-env" / "smart_sources" / "mf_ccarbz"
BLOCK_VECTORS_PATH = ROOT / ".smart-env" / "smart_blocks" / "mf_ccarbz"
OBSIDIAN_CLI = Path(r"C:\Program Files\Obsidian\Obsidian.com")
MODEL_KEY = "TaylorAI/bge-micro-v2"
VECTOR_DIMS = 384
VECTOR_BYTES = VECTOR_DIMS * 4
DEFAULT_RESULTS_PATH = NOTES_ROOT / "benchmark-results-20.json"
CURATED_PREFIXES = ("SYNTHESIS", "DECISION-", "EXPERIMENT-")


def load_json(path: Path) -> Any:
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Smart Connections stores collection maps as top-level property fragments.
        fragment = raw.strip()
        if fragment.endswith(","):
            fragment = fragment[:-1]
        return json.loads("{" + fragment + "}")


def corpus_fingerprint() -> tuple[str, int]:
    digest = hashlib.sha256()
    paths = sorted(NOTES_ROOT.rglob("*.md"), key=lambda path: path.relative_to(ROOT).as_posix())
    for path in paths:
        relative = path.relative_to(ROOT).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest(), len(paths)


def normalize_path(value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(ROOT.resolve()).as_posix()
        except ValueError:
            return path.as_posix()
    return PurePosixPath(value.replace("\\", "/")).as_posix().removeprefix("./")


def in_corpus(path: str) -> bool:
    return path.startswith("Notes/OKF-rag/") and path.lower().endswith(".md")


def raw_only(path: str) -> bool:
    name = PurePosixPath(path).name.upper()
    return name != "INDEX.MD" and not name.startswith(CURATED_PREFIXES)


def load_float_vectors(path: Path) -> tuple[array, int]:
    raw = path.read_bytes()
    if len(raw) % VECTOR_BYTES:
        raise ValueError(f"{path} size {len(raw)} is not a multiple of {VECTOR_BYTES}")
    values = array("f")
    values.frombytes(raw)
    if sys.byteorder != "little":
        values.byteswap()
    return values, len(raw) // VECTOR_BYTES


def vector_at(values: array, count: int, file_i: Any, label: str) -> tuple[float, ...]:
    if not isinstance(file_i, int) or file_i < 0 or file_i >= count:
        raise ValueError(f"{label} references invalid file_i={file_i!r} (capacity={count})")
    start = file_i * VECTOR_DIMS
    return tuple(values[start : start + VECTOR_DIMS])


def cosine(left: Iterable[float], right: Iterable[float]) -> float:
    left_values = tuple(left)
    right_values = tuple(right)
    if len(left_values) != VECTOR_DIMS or len(right_values) != VECTOR_DIMS:
        raise ValueError("Embedding dimension mismatch")
    dot = math.fsum(a * b for a, b in zip(left_values, right_values))
    left_norm = math.sqrt(math.fsum(value * value for value in left_values))
    right_norm = math.sqrt(math.fsum(value * value for value in right_values))
    if left_norm == 0.0 or right_norm == 0.0:
        return -1.0
    return dot / (left_norm * right_norm)


def source_records(index: dict[str, Any]) -> tuple[list[dict[str, Any]], Counter[str]]:
    records: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    for key, record in index.items():
        if not key.startswith("smart_sources:") or not isinstance(record, dict):
            continue
        raw_path = record.get("path") or key.partition(":")[2]
        path = normalize_path(str(raw_path))
        if not in_corpus(path):
            continue
        counts["in_scope"] += 1
        if not (ROOT / Path(path)).is_file():
            counts["missing_files"] += 1
            continue
        embedding = record.get("embedding")
        default_embedding = embedding.get("default") if isinstance(embedding, dict) else None
        reference = default_embedding.get("mf_ccarbz", {}) if isinstance(default_embedding, dict) else {}
        file_i = reference.get("file_i") if isinstance(reference, dict) else None
        if not isinstance(file_i, int):
            counts["without_vector"] += 1
            continue
        last_read = record.get("last_read")
        read_hash = last_read.get("hash") if isinstance(last_read, dict) else None
        vector_hash = reference.get("read_hash")
        if read_hash and vector_hash and read_hash != vector_hash:
            counts["stale_vector"] += 1
            continue
        records.append({"key": key, "path": path, "file_i": file_i})
    counts["rankable"] = len(records)
    return records, counts


def eval_cli_json(javascript: str, timeout: int) -> Any:
    if not OBSIDIAN_CLI.is_file():
        raise FileNotFoundError(f"Obsidian CLI not found: {OBSIDIAN_CLI}")
    completed = subprocess.run(
        [str(OBSIDIAN_CLI), "eval", f"code={javascript}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    output = completed.stdout.strip()
    marker = output.find("=>")
    if completed.returncode != 0 or marker < 0:
        raise RuntimeError(
            "Obsidian eval failed: "
            f"exit={completed.returncode}, stdout={output[:700]!r}, stderr={completed.stderr[-700:]!r}"
        )
    payload = output[marker + 2 :].strip()
    try:
        parsed = json.loads(payload)
        if isinstance(parsed, str):
            return json.loads(parsed)
        return parsed
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Obsidian eval did not return JSON: {payload[:700]!r}") from error


def export_block_metadata(timeout: int) -> list[dict[str, Any]]:
    javascript = (
        "(()=>{const p=app.plugins.plugins[\"smart-connections\"];"
        "if(!p?.env)throw new Error(\"Smart Connections is not loaded\");"
        "const items=p.env.smart_blocks.items||{},out=[];"
        "for(const [key,b] of Object.entries(items)){"
        "if(!key.startsWith(\"Notes/OKF-rag/\"))continue;"
        "const d=b.data||{},r=d.embedding?.default?.mf_ccarbz;"
        "if(!r||!Number.isInteger(r.file_i))continue;"
        "out.push({key,source_key:b.source_key||key.split(\"#\")[0],"
        "lines:Array.isArray(d.lines)?d.lines:null,file_i:r.file_i,read_hash:r.read_hash});"
        "}return JSON.stringify(out)})()"
    )
    result = eval_cli_json(javascript, timeout)
    if not isinstance(result, list):
        raise TypeError("Block metadata export must be a JSON array")
    return result


def embed_query_batch(questions: list[dict[str, str]], timeout: int) -> dict[str, tuple[float, ...]]:
    encoded_questions = json.dumps(questions, ensure_ascii=False)
    javascript = (
        "(async()=>{const p=app.plugins.plugins[\"smart-connections\"];"
        "if(!p?.env)throw new Error(\"Smart Connections is not loaded\");"
        "const model=p.env.smart_sources.embed_model;if(!model)throw new Error(\"No query embedding model\");"
        f"const questions={encoded_questions},out=[];"
        "for(const q of questions){const r=await model.embed({embed_input:q.query,purpose:\"query\"});"
        "out.push({id:q.id,vec:Array.from(r.vec||[])});}return JSON.stringify(out)})()"
    )
    result = eval_cli_json(javascript, timeout)
    if not isinstance(result, list):
        raise TypeError("Query embedding export must be a JSON array")
    vectors: dict[str, tuple[float, ...]] = {}
    for row in result:
        vector = row.get("vec") if isinstance(row, dict) else None
        if not isinstance(vector, list) or len(vector) != VECTOR_DIMS:
            raise ValueError(f"Invalid query vector for {row.get('id') if isinstance(row, dict) else row!r}")
        if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in vector):
            raise ValueError(f"Non-finite query vector for {row.get('id')}")
        vectors[str(row["id"])] = tuple(float(value) for value in vector)
    return vectors


def load_slice_map() -> dict[str, dict[str, Any]]:
    mappings: dict[str, dict[str, Any]] = {}
    for manifest_path in NOTES_ROOT.glob("_slices/**/manifest.json"):
        manifest = load_json(manifest_path)
        origin_path = normalize_path(str(manifest.get("origin", {}).get("path", "")))
        origin_hash = manifest.get("origin", {}).get("hash")
        origin_file = ROOT / Path(origin_path)
        actual_origin_hash = hashlib.sha256(origin_file.read_bytes()).hexdigest() if origin_file.is_file() else None
        origin_hash_matches = bool(origin_hash and actual_origin_hash == origin_hash)
        for item in manifest.get("slices", []):
            slice_path = (manifest_path.parent / str(item.get("path", ""))).resolve()
            try:
                relative_slice_path = slice_path.relative_to(ROOT).as_posix()
            except ValueError:
                continue
            lines = slice_path.read_text(encoding="utf-8").splitlines() if slice_path.is_file() else []
            marker = next((i for i, line in enumerate(lines) if line.strip() == "## Source excerpt"), None)
            source_lines = item.get("source_lines")
            if marker is None or not isinstance(source_lines, list) or len(source_lines) != 2:
                continue
            mappings[relative_slice_path] = {
                "origin_path": origin_path,
                "origin_hash_matches": origin_hash_matches,
                "source_start": int(source_lines[0]),
                "source_end": int(source_lines[1]),
                "excerpt_local_start": marker + 3,
                "slice_hash": item.get("slice_hash"),
            }
    return mappings


def resolve_source(path: str, slice_map: dict[str, dict[str, Any]]) -> str:
    return str(slice_map.get(path, {}).get("origin_path", path))


def map_block_lines(
    path: str,
    lines: Any,
    slice_map: dict[str, dict[str, Any]],
) -> list[int] | None:
    if not isinstance(lines, list) or len(lines) != 2 or not all(isinstance(n, int) for n in lines):
        return None
    start, end = lines
    mapping = slice_map.get(path)
    if not mapping:
        return [start, end]
    excerpt_local_start = mapping["excerpt_local_start"]
    excerpt_local_end = excerpt_local_start + mapping["source_end"] - mapping["source_start"]
    clipped_start = max(start, excerpt_local_start)
    clipped_end = min(end, excerpt_local_end)
    if clipped_start > clipped_end:
        return None
    origin_start = mapping["source_start"] + clipped_start - excerpt_local_start
    origin_end = mapping["source_start"] + clipped_end - excerpt_local_start
    return [origin_start, origin_end]


def enclosing_section(path: str, gold_lines: list[int]) -> list[int]:
    file_path = ROOT / Path(path)
    lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    headings: list[tuple[int, int]] = []
    for number, line in enumerate(lines, start=1):
        match = re.match(r"^(#{1,6})\s+", line)
        if match:
            headings.append((number, len(match.group(1))))
    preceding = [heading for heading in headings if heading[0] <= gold_lines[0]]
    if not preceding:
        return gold_lines[:]
    start, level = preceding[-1]
    next_heading = next((number for number, next_level in headings if number > start and next_level <= level), len(lines) + 1)
    return [start, max(gold_lines[1], next_heading - 1)]


def make_source_candidates(
    records: list[dict[str, Any]], values: array, capacity: int, slice_map: dict[str, dict[str, Any]], mode: str
) -> tuple[list[dict[str, Any]], Counter[str]]:
    candidates: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    for record in records:
        path = record["path"]
        if mode == "raw_only" and not raw_only(path):
            counts["curated_filtered"] += 1
            continue
        vector = vector_at(values, capacity, record["file_i"], record["key"])
        if not any(vector):
            counts["zero_vectors"] += 1
            continue
        candidates.append({
            "path": path,
            "resolved_source_path": resolve_source(path, slice_map),
            "file_i": record["file_i"],
            "vector": vector,
        })
    counts["rankable"] = len(candidates)
    return candidates, counts


def make_block_candidates(
    metadata: list[dict[str, Any]], values: array, capacity: int, slice_map: dict[str, dict[str, Any]], mode: str
) -> tuple[list[dict[str, Any]], Counter[str]]:
    candidates: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    seen_file_indices: set[int] = set()
    for row in metadata:
        path = normalize_path(str(row.get("source_key", "")))
        if not in_corpus(path):
            continue
        if not (ROOT / Path(path)).is_file():
            counts["missing_files"] += 1
            continue
        if mode == "raw_only" and not raw_only(path):
            counts["curated_filtered"] += 1
            continue
        file_i = row.get("file_i")
        if isinstance(file_i, int) and file_i in seen_file_indices:
            counts["duplicate_file_indices"] += 1
        if isinstance(file_i, int):
            seen_file_indices.add(file_i)
        vector = vector_at(values, capacity, file_i, str(row.get("key")))
        if not any(vector):
            counts["zero_vectors"] += 1
            continue
        candidates.append({
            "key": row.get("key"),
            "path": path,
            "resolved_source_path": resolve_source(path, slice_map),
            "lines": map_block_lines(path, row.get("lines"), slice_map),
            "source_lines": row.get("lines"),
            "slice_origin_hash_matches": slice_map.get(path, {}).get("origin_hash_matches", True),
            "file_i": file_i,
            "vector": vector,
        })
    counts["rankable"] = len(candidates)
    return candidates, counts


def rank_candidates(
    candidates: list[dict[str, Any]], query_vector: tuple[float, ...], min_score: float, top_k: int
) -> tuple[list[dict[str, Any]], float | None]:
    scored = [(cosine(candidate["vector"], query_vector), candidate) for candidate in candidates]
    scored.sort(key=lambda item: (-item[0], str(item[1].get("key", item[1]["path"]))))
    max_score = scored[0][0] if scored else None
    return [dict(candidate, score=score) for score, candidate in scored if score >= min_score][:top_k], max_score


def score_range_is_exact(lines: list[int] | None, gold_lines: list[int]) -> bool:
    return bool(lines and lines[0] >= gold_lines[0] and lines[1] <= gold_lines[1])


def overlaps(left: list[int] | None, right: list[int]) -> bool:
    return bool(left and left[0] <= right[1] and right[0] <= left[1])


def summarize_hits(
    ranked_sources: list[dict[str, Any]],
    ranked_blocks: list[dict[str, Any]],
    question: dict[str, Any],
    section_lines: list[int],
    top_k: int,
) -> dict[str, Any]:
    gold_path = question["gold_file"]
    gold_lines = question["gold_lines"]
    related_ranges = question.get("related_lines", [])
    source_rank = next(
        (i for i, row in enumerate(ranked_sources, 1) if row["resolved_source_path"] == gold_path), None
    )
    exact_passage_rank = None
    related_passage_rank = None
    for rank, row in enumerate(ranked_blocks, 1):
        if row["resolved_source_path"] != gold_path:
            continue
        lines = row.get("lines")
        exact = score_range_is_exact(lines, gold_lines)
        if exact and exact_passage_rank is None:
            exact_passage_rank = rank
        related = not exact and (
            overlaps(lines, section_lines) or any(overlaps(lines, item) for item in related_ranges)
        )
        if related and related_passage_rank is None:
            related_passage_rank = rank

    first_block = ranked_blocks[0] if ranked_blocks else None
    citation_lines = first_block.get("lines") if first_block else None
    citation_file = ROOT / Path(first_block["resolved_source_path"]) if first_block else None
    citation_line_count = (
        len(citation_file.read_text(encoding="utf-8", errors="replace").splitlines())
        if citation_file and citation_file.is_file() else 0
    )
    first_valid_citation = bool(
        citation_lines
        and citation_file
        and citation_file.is_file()
        and 1 <= citation_lines[0] <= citation_lines[1] <= citation_line_count
        and first_block.get("slice_origin_hash_matches", True)
    )
    top1_citation_correct = bool(
        first_valid_citation
        and first_block["resolved_source_path"] == gold_path
        and overlaps(first_block.get("lines"), gold_lines)
    )
    top1_citation_exact = bool(
        first_valid_citation
        and first_block["resolved_source_path"] == gold_path
        and score_range_is_exact(first_block.get("lines"), gold_lines)
    )

    return {
        "source_rank": source_rank,
        "source_recall_at_1": source_rank is not None and source_rank <= 1,
        "source_recall_at_5": source_rank is not None and source_rank <= 5,
        "source_recall_at_10": source_rank is not None and source_rank <= 10,
        "passage_exact_rank": exact_passage_rank,
        "passage_exact_at_1": exact_passage_rank is not None and exact_passage_rank <= 1,
        "passage_exact_at_10": exact_passage_rank is not None and exact_passage_rank <= top_k,
        "passage_related_rank": related_passage_rank,
        "passage_related_at_10": related_passage_rank is not None and related_passage_rank <= top_k,
        "passage_any_exact_or_related_at_10": (
            (exact_passage_rank is not None and exact_passage_rank <= top_k)
            or (related_passage_rank is not None and related_passage_rank <= top_k)
        ),
        "citation_target_valid_at_1": first_valid_citation,
        "citation_target_correct_at_1": top1_citation_correct,
        "citation_target_exact_at_1": top1_citation_exact,
    }


def question_result(
    question: dict[str, Any],
    query_vector: tuple[float, ...],
    sources: list[dict[str, Any]],
    blocks: list[dict[str, Any]],
    min_score: float,
    top_k: int,
    slice_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    ranked_sources, max_source_score = rank_candidates(sources, query_vector, min_score, top_k)
    ranked_blocks, max_block_score = rank_candidates(blocks, query_vector, min_score, top_k)
    has_gold = bool(question.get("gold_file") and question.get("gold_lines"))
    section_lines = enclosing_section(question["gold_file"], question["gold_lines"]) if has_gold else None
    metrics = (
        summarize_hits(ranked_sources, ranked_blocks, question, section_lines, top_k)
        if has_gold else {}
    )

    def public_candidate(row: dict[str, Any], kind: str) -> dict[str, Any]:
        result = {
            "rank": None,
            "score": round(float(row["score"]), 6),
            "retrieval_path": row["path"],
            "citation_path": row["resolved_source_path"],
            "file_i": row["file_i"],
        }
        if kind == "passage":
            result["citation_lines"] = row.get("lines")
            result["retrieval_lines"] = row.get("source_lines")
            result["key"] = row.get("key")
            result["source_hash_matches"] = row.get("slice_origin_hash_matches", True)
        return result

    source_results = []
    for rank, row in enumerate(ranked_sources, 1):
        item = public_candidate(row, "source")
        item["rank"] = rank
        source_results.append(item)
    passage_results = []
    for rank, row in enumerate(ranked_blocks, 1):
        item = public_candidate(row, "passage")
        item["rank"] = rank
        passage_results.append(item)

    output = {
        "id": question["id"],
        "query": question["query"],
        "gold_file": question.get("gold_file"),
        "gold_lines": question.get("gold_lines"),
        "expected_section": question.get("expected_section"),
        "section_bounds_used_for_related": section_lines,
        "max_source_score": round(max_source_score, 6) if max_source_score is not None else None,
        "max_passage_score": round(max_block_score, 6) if max_block_score is not None else None,
        "metrics": metrics,
        "source_results": source_results,
        "passage_results": passage_results,
    }
    return output


def aggregate_metrics(results: list[dict[str, Any]], top_k: int, min_score: float) -> dict[str, Any]:
    metric_names = (
        "source_recall_at_1",
        "source_recall_at_5",
        "source_recall_at_10",
        "passage_exact_at_1",
        "passage_exact_at_10",
        "passage_related_at_10",
        "passage_any_exact_or_related_at_10",
        "citation_target_valid_at_1",
        "citation_target_correct_at_1",
        "citation_target_exact_at_1",
    )
    counts = {
        name: sum(bool(row["metrics"][name]) for row in results)
        for name in metric_names
    }
    return {
        "question_count": len(results),
        "top_k": top_k,
        "min_score": min_score,
        "counts": counts,
        "rates": {
            name: (count / len(results) if results else None)
            for name, count in counts.items()
        },
        "source_rank_mrr_at_10": (
            math.fsum(1 / row["metrics"]["source_rank"] for row in results if row["metrics"]["source_rank"])
            / len(results) if results else None
        ),
        "passage_exact_mrr_at_10": (
            math.fsum(1 / row["metrics"]["passage_exact_rank"] for row in results if row["metrics"]["passage_exact_rank"])
            / len(results) if results else None
        ),
    }


def run(args: argparse.Namespace) -> int:
    dataset = load_json(QUESTIONS_PATH)
    fingerprint, corpus_file_count = corpus_fingerprint()
    expected_fingerprint = dataset.get("corpus_sha256")
    if not expected_fingerprint:
        raise ValueError("benchmark-questions.json needs corpus_sha256; run --print-corpus-hash and freeze it before benchmarking")
    if fingerprint != expected_fingerprint and not args.allow_corpus_drift:
        raise ValueError(
            f"Corpus fingerprint changed: questions={expected_fingerprint}, current={fingerprint}. "
            "Review the corpus, update its pinned hash, or pass --allow-corpus-drift for an explicit drift run."
        )
    questions = dataset.get("questions", [])
    if len(questions) != 20:
        raise ValueError(f"Expected exactly 20 in-corpus questions, got {len(questions)}")
    model_key = dataset.get("settings", {}).get("model")
    if model_key != MODEL_KEY:
        raise ValueError(f"Question set model {model_key!r} does not match vector sidecar {MODEL_KEY!r}")
    top_k = int(dataset.get("settings", {}).get("top_k", 10))
    min_score = float(dataset.get("settings", {}).get("min_score", 0.55))

    source_index = load_json(SOURCE_INDEX_PATH)
    source_records_list, source_index_counts = source_records(source_index)
    source_values, source_capacity = load_float_vectors(SOURCE_VECTORS_PATH)
    block_values, block_capacity = load_float_vectors(BLOCK_VECTORS_PATH)
    slice_map = load_slice_map()
    block_metadata = export_block_metadata(args.timeout)
    query_vectors: dict[str, tuple[float, ...]] = {}
    query_inputs = [{"id": row["id"], "query": row["query"]} for row in questions + dataset.get("out_of_corpus", [])]
    for start in range(0, len(query_inputs), args.batch_size):
        batch = query_inputs[start : start + args.batch_size]
        query_vectors.update(embed_query_batch(batch, args.timeout))

    modes = ["all", "raw_only"] if args.mode == "both" else [args.mode]
    mode_results: dict[str, Any] = {}
    for mode in modes:
        sources, source_counts = make_source_candidates(
            source_records_list, source_values, source_capacity, slice_map, mode
        )
        blocks, block_counts = make_block_candidates(
            block_metadata, block_values, block_capacity, slice_map, mode
        )
        per_question = [
            question_result(
                question,
                query_vectors[question["id"]],
                sources,
                blocks,
                min_score,
                top_k,
                slice_map,
            )
            for question in questions
        ]
        ooc_results = []
        for question in dataset.get("out_of_corpus", []):
            result = question_result(
                question,
                query_vectors[question["id"]],
                sources,
                blocks,
                min_score,
                top_k,
                slice_map,
            )
            result["expected_refusal"] = bool(question.get("expected_refusal", False))
            result["retrieval_abstained"] = not result["source_results"] and not result["passage_results"]
            result["highest_score_over_min_score"] = max(
                (score for score in (result["max_source_score"], result["max_passage_score"]) if score is not None),
                default=None,
            )
            ooc_results.append(result)
        mode_results[mode] = {
            "candidate_counts": {"sources": dict(source_counts), "passages": dict(block_counts)},
            "metrics": aggregate_metrics(per_question, top_k, min_score),
            "questions": per_question,
            "out_of_corpus": ooc_results,
            "ooc_retrieval_abstained": all(row["retrieval_abstained"] for row in ooc_results),
        }

    results = {
        "schema_version": 1,
        "benchmark": dataset.get("dataset"),
        "query_origin": dataset.get("query_origin"),
        "baseline_report": dataset.get("baseline_report"),
        "corpus": {
            "scope": dataset.get("corpus_scope"),
            "sha256": fingerprint,
            "markdown_file_count": corpus_file_count,
            "hash_matches_pinned_questions": fingerprint == expected_fingerprint,
        },
        "settings": {
            "model": MODEL_KEY,
            "dimensions": VECTOR_DIMS,
            "top_k": top_k,
            "min_score": min_score,
            "modes": modes,
            "query_batch_size": args.batch_size,
            "source_index": str(SOURCE_INDEX_PATH.relative_to(ROOT)).replace("\\", "/"),
            "source_vectors": str(SOURCE_VECTORS_PATH.relative_to(ROOT)).replace("\\", "/"),
            "passage_vectors": str(BLOCK_VECTORS_PATH.relative_to(ROOT)).replace("\\", "/"),
            "ranking_implementation": "Python local cosine; Obsidian CLI exports only query vectors and block locators",
            "raw_only_filter": "exclude index.md and filenames prefixed SYNTHESIS, DECISION-, EXPERIMENT-; generated source slices remain eligible and resolve through manifests",
        },
        "index_inventory": {
            "source_records": dict(source_index_counts),
            "source_vector_capacity": source_capacity,
            "passage_vector_capacity": block_capacity,
            "live_block_metadata_count": len(block_metadata),
            "slice_mappings": len(slice_map),
        },
        "metrics_definition": {
            "source_rank": "rank of first source-vector result whose path (or source-slice manifest origin) is the gold file",
            "passage_rank": "rank of first block-vector result resolving to the gold file and the gold line interval",
            "passage_exact": "block citation lines are fully contained in the recorded gold_lines interval",
            "passage_related": "block resolves within the containing Markdown heading section or a recorded related_lines interval, but is not exact",
            "citation_target_correct_at_1": "top passage resolves to the gold file and its mapped lines overlap gold_lines; citation_target_exact_at_1 separately requires full containment. Neither checks generated answer text or quotation wording",
            "ooc_refusal": "retrieval abstention only: no source or passage result clears min_score; no answer-generation/refusal model is tested",
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "comparison_caveats": [
            "The earlier 20-question report did not preserve its exact prompts; this set labels reconstructed queries and is not a strict prompt-for-prompt replication.",
            "This run includes the current corpus and targeted source slices; compare all and raw_only within this result, not as an exact before/after score against reports with different corpus snapshots.",
        ],
        "modes": mode_results,
    }
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"results={output_path}")
    print(f"corpus_sha256={fingerprint} markdown_files={corpus_file_count}")
    for mode, result in mode_results.items():
        print(f"[{mode}] metrics={json.dumps(result['metrics']['counts'], ensure_ascii=False)} ooc_abstained={result['ooc_retrieval_abstained']}")
        for name, counts in result["candidate_counts"].items():
            print(f"[{mode}] {name}_candidates={counts.get('rankable', 0)} filtered={counts.get('curated_filtered', 0)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("all", "raw_only", "both"), default="both")
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=90, help="Timeout in seconds per Obsidian CLI eval")
    parser.add_argument("--output", default=str(DEFAULT_RESULTS_PATH.relative_to(ROOT)))
    parser.add_argument("--allow-corpus-drift", action="store_true")
    parser.add_argument("--print-corpus-hash", action="store_true")
    parser.add_argument("--inspect", action="store_true", help="Inspect local source-index/vector coverage and live block locators")
    args = parser.parse_args()
    if args.batch_size < 1 or args.batch_size > 5:
        parser.error("--batch-size must be between 1 and 5")
    if args.print_corpus_hash:
        fingerprint, count = corpus_fingerprint()
        print(f"corpus_sha256={fingerprint}")
        print(f"markdown_files={count}")
        return 0
    if args.inspect:
        index = load_json(SOURCE_INDEX_PATH)
        records, counts = source_records(index)
        _, source_capacity = load_float_vectors(SOURCE_VECTORS_PATH)
        _, block_capacity = load_float_vectors(BLOCK_VECTORS_PATH)
        metadata = export_block_metadata(args.timeout)
        refs = [row.get("file_i") for row in metadata if isinstance(row.get("file_i"), int)]
        print(f"source_index_scope={dict(counts)} source_vectors_capacity={source_capacity}")
        print(f"live_block_locators={len(metadata)} unique_file_i={len(set(refs))} block_vectors_capacity={block_capacity}")
        print(f"slice_mappings={len(load_slice_map())}")
        return 0
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
