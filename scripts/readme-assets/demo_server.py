"""Serve the console with fake tools and a scripted model, for README captures.

No API key, no cluster, no network: every capability answers from fixtures and
the model replays the turns below, streamed word by word so a recording looks
like a real conversation. The story is the one the README tells: look at
tickup, open a PR to scale it, stop at the merge for the human's approval.

    uv run python scripts/readme-assets/demo_server.py   # http://localhost:8100
"""

from __future__ import annotations

import asyncio
import os
import re
from typing import Any

os.environ["JARVIS_FAKE_TOOLS"] = "true"
os.environ.setdefault("ANTHROPIC_API_KEY", "demo")  # never used: the model is scripted

import uvicorn  # noqa: E402
from quaerium.agents.llm import Emit, ModelTurn  # noqa: E402
from quaerium.agents.testing import ScriptedLLM  # noqa: E402
from quaerium.agents.types import RiskLevel, ToolCall, Usage, new_id  # noqa: E402

from jarvis.settings import Settings  # noqa: E402

# Ignore .env: a capture must never reach the real lab (gateway, ArgoCD, GitHub)
# nor show its hostnames. Everything comes from the fixtures.
Settings.model_config["env_file"] = None

from jarvis.api.app import create_app  # noqa: E402
from jarvis.tools import CAPABILITIES  # noqa: E402

# Fixtures answer in 0 ms, which reads as fake on screen. Give each tool the
# latency of a real API call.
LATENCY = {"read": 0.45, "write": 1.3, "destructive": 0.9}


def _slowed(spec: Any) -> None:
    fn, delay = spec.fn, LATENCY.get(str(getattr(spec.risk, "value", spec.risk)), 0.5)

    async def slow(*args: Any, **kwargs: Any) -> str:
        await asyncio.sleep(delay)
        return await fn(*args, **kwargs)

    object.__setattr__(spec, "fn", slow)


for _module in CAPABILITIES:
    for _spec in _module.TOOLS:
        _slowed(_spec)

PROMPT = "tickup feels slow, check it and scale the backend to 2 if it needs it"


def _usage(text: str) -> Usage:
    return Usage(input_tokens=6200 + 40 * len(text), output_tokens=60 + len(text) // 3, cache_read_tokens=5800)


def _turn(text: str, calls: list[tuple[str, dict[str, Any], Any]]) -> ModelTurn:
    # Each turn's text ends a paragraph: the console concatenates the turns of a run.
    text += "\n\n"
    content: list[dict[str, Any]] = [{"type": "text", "text": text}]
    tool_calls = []
    for name, args, risk in calls:
        call_id = new_id("toolu")
        content.append({"type": "tool_use", "id": call_id, "name": name, "input": args})
        tool_calls.append(ToolCall(id=call_id, name=name, args=args, risk=risk))
    return ModelTurn(content=content, text=text, tool_calls=tool_calls, usage=_usage(text), stop_reason="tool_use")


def _say(text: str) -> ModelTurn:
    return ModelTurn(content=[{"type": "text", "text": text}], text=text, usage=_usage(text))


SCRIPT = [
    _turn(
        "Let me look at tickup's pods and how much they are using.",
        [
            ("k8s__list_pods", {"namespace": "tickup"}, RiskLevel.READ),
            ("prometheus__pod_resources", {"namespace": "tickup"}, RiskLevel.READ),
        ],
    ),
    _turn(
        "`tickup-backend` runs as a **single pod at 97% of its memory limit**, with 2 restarts "
        "in the last 24h. A second replica spreads the load and removes the single point of "
        "failure. I'll open a pull request against the infra repo.",
        [
            (
                "github__set_replicas",
                {
                    "app": "tickup",
                    "component": "backend",
                    "replicas": 2,
                    "reason": "single pod at 97% of its memory limit, 2 restarts in 24h",
                },
                RiskLevel.WRITE,
            )
        ],
    ),
    _turn(
        "PR **#13** is open. Merging it is what ships the change, so I need your approval.",
        [("github__merge_pr", {"number": 13}, RiskLevel.DESTRUCTIVE)],
    ),
    _say(
        "Merged **#13**. ArgoCD will roll out `tickup-backend` with **2 replicas** on its next "
        "sync; nothing touched the cluster directly.\n\n"
        "Separately, `tickup-web` is stuck in `ImagePullBackOff`. Want me to look into it?"
    ),
]


class DemoLLM(ScriptedLLM):
    """A ScriptedLLM that streams its text and pauses like a model thinking."""

    async def complete(
        self,
        *,
        system: list[dict[str, Any]],
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
        effort: str,
        emit: Emit,
        model: str | None = None,
    ) -> ModelTurn:
        if not self._turns:
            self._turns = list(SCRIPT)  # replay for the next recording
        turn = self._turns.pop(0)
        await asyncio.sleep(0.8)
        for word in re.findall(r"\s*\S+\s*", turn.text):
            emit("token", word)
            await asyncio.sleep(0.045)
        return turn


app = create_app(llm=DemoLLM(list(SCRIPT)))

if __name__ == "__main__":
    uvicorn.run(app, port=int(os.environ.get("PORT", "8100")), log_level="warning")
