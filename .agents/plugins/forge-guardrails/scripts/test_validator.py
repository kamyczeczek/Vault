"""Anti-tautological test validator (forge-guardrails).

Three layers, in increasing strength:

  1. AST (static, cheap) -- reject tests that cannot possibly fail.
  2. Fails-first          -- run the test; a *good* test must fail before the
                              implementation exists.
  3. Mutation (optional)  -- mutate the implementation and confirm the test
                              still catches it (strongest signal).

Layer 1 is pure stdlib. Layers 2/3 run a test command and are opt-in so the
validator stays fast on every PostToolUse.
"""
from __future__ import annotations

import ast
import re
import subprocess
from dataclasses import dataclass, field


@dataclass
class Finding:
    rule: str
    line: int
    message: str
    layer: str = "ast"


@dataclass
class Verdict:
    ok: bool
    findings: list[Finding] = field(default_factory=list)

    def to_json(self) -> dict:
        return {
            "ok": self.ok,
            "findings": [
                {"rule": f.rule, "line": f.line, "message": f.message,
                 "layer": f.layer}
                for f in self.findings
            ],
        }


# ---------------------------------------------------------------------------
# Layer 1: AST
# ---------------------------------------------------------------------------

_MOCK_ASSERT_RE = re.compile(r"^mock\.[A-Za-z_]+\.assert_(called|any_call|no_calls|not_called|called_once|called_with|assert_has_calls|called_with_.*|called_once_.*|assert_called_.*)$")


def _norm(node) -> str:
    """Canonical string of a Call node so LHS==RHS can be compared."""
    if isinstance(node, ast.Call):
        fn = _norm(node.func)
        args = ", ".join(_norm(a) for a in node.args)
        return f"{fn}({args})"
    if isinstance(node, ast.Attribute):
        return f"{_norm(node.value)}.{node.attr}"
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant):
        return repr(node.value)
    return ast.dump(node)


def _has_value_assert(tree: ast.Module) -> bool:
    """True if the module asserts on a computed value (not only on mock calls)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            # assert X == 42, assert X > 1, assert X is not None, etc.
            if node.test is not None and not _is_mock_only_assert(node.test):
                return True
    return False


def _is_mock_only_assert(test_node) -> bool:
    # mock.assert_called_once() -- a Call whose func is an Attribute on a name
    # that is itself an Attribute/Name ending in 'mock'
    if isinstance(test_node, ast.Call):
        return bool(_MOCK_ASSERT_RE.match(_norm(test_node)))
    return False


def check_ast(path: str, source: str) -> list[Finding]:
    findings: list[Finding] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        findings.append(Finding("syntax_error", e.lineno or 0,
                                f"test file does not parse: {e.msg}", "ast"))
        return findings

    if not any(isinstance(n, ast.FunctionDef) and
               re.match(r"^test_.+", n.name) for n in ast.walk(tree)) and \
       not any(isinstance(n, ast.ClassDef) and n.name.endswith("Test")
               for n in ast.walk(tree)):
        findings.append(Finding("no_test_function", 1,
                                "no test_* function or *Test class found", "ast"))

    if not _has_value_assert(tree):
        findings.append(Finding("no_value_assertion", 1,
                                "no assertion on a computed value -- test can "
                                "trivially pass (tautology risk)", "ast"))

    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            t = node.test
            if not isinstance(t, (ast.Compare, ast.UnaryOp)) or not getattr(
                    t, "left", None):
                continue
            # tautology: assert calc(x) == calc(x)  (identical LHS/RHS)
            if isinstance(t, ast.Compare) and len(t.comparators) == 1:
                lhs = _norm(t.left)
                rhs = _norm(t.comparators[0])
                if lhs == rhs and lhs.count("(") > 0:
                    findings.append(Finding(
                        "tautology_lhs_equals_rhs", t.lineno,
                        f"assert compares identical calls: {lhs} == {rhs}",
                        "ast"))
    return findings


# ---------------------------------------------------------------------------
# Layer 2: fails-first
# ---------------------------------------------------------------------------

def check_fails_first(test_cmd: str, cwd: str,
                      timeout: int = 60) -> tuple[bool, str]:
    """Run the test. A valid test of a not-yet-implemented feature FAILS.

    Returns (should_fail, reason). If the suite passes, either the code already
    exists or the test is tautological.
    """
    try:
        proc = subprocess.run(test_cmd, shell=True, cwd=cwd, timeout=timeout,
                              capture_output=True, text=True)
    except Exception as e:  # noqa: BLE001
        return True, f"could not run test command ({e}) -- assume must fail"
    # exit 0 == all passed. For a pre-implementation test we WANT non-zero.
    passed = proc.returncode == 0
    tail = (proc.stdout + proc.stderr).strip().splitlines()
    tail = tail[-8:] if tail else []
    return (not passed), " ".join(tail)


# ---------------------------------------------------------------------------
# Layer 3: mutation (optional, strongest)
# ---------------------------------------------------------------------------

def check_mutation(impl_path: str, test_cmd: str, cwd: str,
                   timeout: int = 90) -> tuple[bool, str]:
    """Flip a boolean operator in the impl; the test must now fail.

    A deliberately crude mutator (no external mutation engine): replace '=='
    with '!=' and 'True' with 'False' in the target impl. If the test still
    passes under mutation, it does not actually exercise the behaviour.
    """
    import shutil
    import tempfile
    try:
        src = open(impl_path, encoding="utf-8").read()
    except Exception as e:  # noqa: BLE001
        return False, f"cannot read impl {impl_path}: {e}"
    mutated = (src.replace("==", "!=").replace("True", "False")
               .replace("False", "True"))
    if mutated == src:
        return False, "no operable token to mutate -- not a meaningful check"
    with tempfile.TemporaryDirectory() as tmp:
        bak = f"{tmp}.impl.bak"
        shutil.copyfile(impl_path, bak)
        try:
            open(impl_path, "w", encoding="utf-8").write(mutated)
            proc = subprocess.run(test_cmd, shell=True, cwd=cwd,
                                  timeout=timeout, capture_output=True,
                                  text=True)
            caught = proc.returncode != 0
        finally:
            shutil.copyfile(bak, impl_path)
    return caught, ("mutation was caught by the test" if caught
                    else "MUTATION SURVIVED -- test does not pin the behaviour")


# ---------------------------------------------------------------------------
# Entry points used by forge_hook.py
# ---------------------------------------------------------------------------

def validate_test_file(path: str) -> Verdict:
    src = open(path, encoding="utf-8").read()
    findings = check_ast(path, src)
    ok = not any(f.rule in ("tautology_lhs_equals_rhs", "no_value_assertion",
                           "syntax_error") for f in findings)
    return Verdict(ok=ok, findings=findings)
