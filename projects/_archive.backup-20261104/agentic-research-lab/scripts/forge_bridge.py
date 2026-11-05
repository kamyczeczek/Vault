"""
Forge Guardrails adapter for Agentic Research Lab (ARL).

Weaker/cheaper remote models (routed through an OpenAI-compatible endpoint,
e.g. the nara/omniroute gateway) fail at tool-calling far more than frontier
models: malformed JSON, skipped steps, drifted responses. This module wraps
Antoine Zambelli's `forge-guardrails` package (installed in the project-local
`.venv-forge` Python 3.12 environment) to add:

  * rescue parsing     — recover tool calls from malformed / free-text output
  * retry nudging      — targeted nudges when a step fails validation
  * response validation — reject tool calls that don't match the schema
  * context compaction — TieredCompact / SlidingWindowCompact for long loops

It is an OPT-IN seam: nothing in ARL's core inference path changes unless a
call site explicitly routes a weaker-model loop through this module.

Run under the project venv, not the global Hermes interpreter:

    python .venv-forge/Scripts/python scripts/forge_bridge.py --check
    python .venv-forge/Scripts/python scripts/forge_bridge.py --info
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field


@dataclass
class ForgeRunner:
    """A ready-to-run forge `WorkflowRunner` preconfigured for ARL loops.

    `client` and `context_manager` are constructed by the caller (via
    `forge.OpenAICompatClient` / `forge.ContextManager`) so the runner stays
    endpoint-agnostic. Defaults encode ARL's reliability policy: rescue on,
    retry nudge on, bounded iterations.
    """
    client: object
    context_manager: object
    max_iterations: int = 10
    max_retries_per_step: int = 3
    max_tool_errors: int = 2
    rescue_enabled: bool = True
    retry_nudge: str | None = "Your last tool call was malformed or did not match the schema. Retry with a valid JSON tool call."
    stream: bool = False
    _runner: object = field(default=None, repr=False)

    def _build(self) -> object:
        # Lazy import so `--check`/`--info` still work without a live backend.
        from forge import WorkflowRunner
        return WorkflowRunner(
            client=self.client,
            context_manager=self.context_manager,
            max_iterations=self.max_iterations,
            max_retries_per_step=self.max_retries_per_step,
            max_tool_errors=self.max_tool_errors,
            stream=self.stream,
            rescue_enabled=self.rescue_enabled,
            retry_nudge=self.retry_nudge,
        )

    async def run(self, workflow, user_message, prompt_vars=None, initial_messages=None):
        """Run a guarded agentic loop; returns the terminal tool response."""
        runner = self._runner if self._runner is not None else self._build()
        self._runner = runner
        return await runner.run(
            workflow=workflow,
            user_message=user_message,
            prompt_vars=prompt_vars,
            initial_messages=initial_messages,
        )


def build_compat_runner(
    base_url: str,
    model: str,
    api_key: str | None = None,
    context_strategy: str = "tiered",
    budget_tokens: int = 32_768,
) -> ForgeRunner:
    """Factory for ARL's case: a *weaker* model behind an OpenAI-compatible
    endpoint (nara/omniroute or any OpenAI-shaped gateway).

    `api_key` defaults to the `FORGE_API_KEY` env var when omitted.
    """
    import forge

    key = api_key if api_key is not None else os.environ.get("FORGE_API_KEY", "")
    client = forge.OpenAICompatClient(model=model, base_url=base_url, api_key=key)
    if context_strategy == "sliding":
        strategy = forge.SlidingWindowCompact(keep_recent=2)
    else:
        strategy = forge.TieredCompact(keep_recent=2)
    cm = forge.ContextManager(strategy=strategy, budget_tokens=budget_tokens)
    return ForgeRunner(client=client, context_manager=cm)


def check() -> int:
    """Verify the forge package imports and reports the guardrail surface. Exit 0/1."""
    try:
        import forge
    except ImportError as exc:  # pragma: no cover - env dependent
        print(f"ERROR: forge not importable under this interpreter: {exc}")
        print("Run with: python .venv-forge/Scripts/python scripts/forge_bridge.py --check")
        return 1
    required = ("WorkflowRunner", "Guardrails", "ToolSpec", "ToolDef",
                "OpenAICompatClient", "ContextManager", "TieredCompact")
    missing = [n for n in required if not hasattr(forge, n)]
    if missing:
        print(f"ERROR: forge missing expected symbols: {missing}")
        return 1
    print(f"OK: forge {forge.__version__} loaded under {sys.executable}")
    print(f"    symbols present: {', '.join(required)}")
    return 0


def info() -> int:
    """List the forge backends + guardrail surface available in this venv."""
    import forge

    backends = [
        n for n in dir(forge)
        if n.endswith("Client") or n in {"setup_backend", "ServerManager"}
    ]
    guardrails = [
        n for n in dir(forge)
        if n in {"Guardrails", "ResponseValidator", "StepEnforcer",
                 "ErrorTracker", "ContextManager", "TieredCompact",
                 "SlidingWindowCompact", "NoCompact"}
    ]
    print(f"forge {forge.__version__}")
    print(f"  backends   : {backends}")
    print(f"  guardrails : {guardrails}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ARL <-> forge-guardrails bridge")
    parser.add_argument("--check", action="store_true", help="verify import + version")
    parser.add_argument("--info", action="store_true", help="list backends/guardrails")
    args = parser.parse_args(argv)

    if args.info:
        return info()
    # default to --check
    return check()


if __name__ == "__main__":
    sys.exit(main())
