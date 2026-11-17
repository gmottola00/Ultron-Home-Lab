<div align="center">

<img src="docs/assets/banner.svg" alt="Ultron: the AI operator for your Kubernetes home lab. It opens pull requests, never touches the cluster." width="100%">

[![Backend CI](https://github.com/gmottola00/Ultron-Home-Lab/actions/workflows/backend.yml/badge.svg)](https://github.com/gmottola00/Ultron-Home-Lab/actions/workflows/backend.yml)
[![Web CI](https://github.com/gmottola00/Ultron-Home-Lab/actions/workflows/web.yml/badge.svg)](https://github.com/gmottola00/Ultron-Home-Lab/actions/workflows/web.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python 3.12](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)
![Node 22](https://img.shields.io/badge/node-22-339933?logo=nodedotjs&logoColor=white)
![Kubernetes](https://img.shields.io/badge/kubernetes-read--only-326CE5?logo=kubernetes&logoColor=white)
![ArgoCD](https://img.shields.io/badge/GitOps-ArgoCD-EF7B4D?logo=argo&logoColor=white)

**Ask it why a pod is crashing. Tell it to scale an app. Approve the merge from your phone.**

[Try it in 30 seconds](#-quick-start) · [How it works](#-how-it-works) · [Add a capability](#-adding-a-capability) · [In my home lab](#-in-my-home-lab) · [Contributing](CONTRIBUTING.md)

<br>

<img src="docs/assets/demo.gif" alt="Ultron checks tickup, opens a pull request to scale it, and stops for approval before merging" width="100%">

<sub>Real UI, offline demo: fixtures instead of a cluster, a scripted model instead of an API key. <a href="docs/assets/demo.mp4">MP4</a></sub>

</div>

---

## 🤖 An AI agent with no `kubectl apply`

Most AI agents for Kubernetes get a kubeconfig and your trust. **Ultron gets neither.**

It *reads* everything (Kubernetes, Prometheus, Loki, Alertmanager, ArgoCD, GHCR) and
*writes* only to Git, as commits and pull requests against your infra repo.
ArgoCD stays the only thing that changes the cluster, so every action Ultron takes
is **diffable, reviewable and revertible**.

That is not a guideline, it is the architecture: there is no apply, patch, delete
or scale tool anywhere in this codebase, and a test asserts there never is.

<table>
<tr>
<td width="33%" valign="top">

### 🔒 Safe by construction
Reads run freely. Writes are PRs. Anything hard to reverse, like **merging**, suspends
the run and waits for a human. No prompt can talk it past that gate.

</td>
<td width="33%" valign="top">

### 📱 Approve from your phone
Installable PWA with push notifications. The run is checkpointed in Postgres, so
it waits for you even across a restart. Tap *Approve* and ArgoCD ships it.

</td>
<td width="33%" valign="top">

### 🧪 Runs with no cluster
`JARVIS_FAKE_TOOLS=true` serves every tool from fixtures: no cluster, no token,
no API key. The whole agent graph is tested against a scripted model.

</td>
</tr>
</table>

### How it compares

| | kubectl by hand | Agent with a kubeconfig | **Ultron** |
|---|:---:|:---:|:---:|
| Diagnoses from metrics, logs and events in one question | ❌ | ✅ | ✅ |
| Every change is a reviewable PR | ⚠️ discipline | ❌ | ✅ |
| Cannot change the cluster directly, even if prompted to | ❌ | ❌ | ✅ |
| Undo = `git revert` | ❌ | ❌ | ✅ |
| Human approval from your phone | ❌ | ⚠️ sometimes | ✅ |
| Local models via LiteLLM, Claude as fallback | — | ⚠️ varies | ✅ |

---

## 📸 A look around

<table>
<tr>
<td width="50%"><img src="docs/assets/status.png" alt="Status: every problem in the lab, worst first, each one a click away from an investigation"><br><sub><b>Status</b>: every problem across Kubernetes, ArgoCD and Alertmanager, worst first. <i>Investigate</i> hands one to Ultron.</sub></td>
<td width="50%"><img src="docs/assets/approval.png" alt="The approval dialog for a destructive tool call"><br><sub><b>The gate</b>: the one moment the agent stops and a person decides.</sub></td>
</tr>
<tr>
<td width="50%"><img src="docs/assets/delivery.png" alt="Delivery: from a CI build to a running pod, per image"><br><sub><b>Delivery</b>: built, green, pinned, running, per image, without asking the agent.</sub></td>
<td width="50%"><img src="docs/assets/tools.png" alt="Capabilities: every tool, its risk level and how often it is called"><br><sub><b>Capabilities</b>: every tool the model gets, what the gate does with it, how often it runs.</sub></td>
</tr>
</table>

<p align="center">
<img src="docs/assets/phone-status.png" alt="Status on iPhone" width="24%">&nbsp;
<img src="docs/assets/phone-chat.png" alt="Chat on iPhone" width="24%">&nbsp;
<img src="docs/assets/phone-cluster.png" alt="Cluster on iPhone" width="24%">
<br><sub>Add it to your Home Screen: full screen, its own icon, push for pending approvals.</sub>
</p>

### Architecture

```mermaid
flowchart LR
    you["📱 You<br/>web console / PWA"] -- "chat (SSE)" --> ultron

    subgraph lab["Home lab (k3s)"]
        ultron["🤖 Ultron"]
        k8s["Kubernetes API<br/>read-only ClusterRole"]
        prom["Prometheus"]
        loki["Loki"]
        am["Alertmanager"]
        argo["ArgoCD"]
    end

    gh[("GitHub<br/>infra + app repos")]
    ghcr[("GHCR")]

    ultron -- read --> k8s & prom & loki & am & argo & ghcr
    ultron -- "commit · open PR" --> gh
    you -- "approve merge" --> ultron
    gh -- "GitOps sync" --> argo
    argo == "the only writer" ==> k8s
    ultron -. "✗ no apply / patch / delete" .-x k8s
```

> [!WARNING]
> The console has **no built-in authentication**. Run it behind a private network
> (e.g. Tailscale) and never expose it to the public internet. See [SECURITY.md](SECURITY.md).

---

## 📦 Prerequisites

- **Python 3.12** and [uv](https://docs.astral.sh/uv/) — the backend.
- **Node 22** — only to build the dashboard. Install it with
  [nvm](https://github.com/nvm-sh/nvm) or your package manager.
- **Docker** — only for `make up`. The backend runs fine without it.

`web/dist/` is already built, so `make run-api` serves the dashboard on :8100
before Node is installed. Node is needed to change the dashboard.

## 🚀 Quick start

Nothing below needs a cluster, a token, or even an API key to run.

```bash
make setup        # venv + dependencies + dashboard + .env
make run          # builds the dashboard, serves everything on :8100
```

Open <http://localhost:8100>. With `JARVIS_FAKE_TOOLS=true` (the default in
`.env.example`) every capability is served from fixtures that mirror the real lab,
so the dashboard populates and the deploy flow can be rehearsed offline.

Add `ANTHROPIC_API_KEY` to `.env` to enable chat.

**The demo from the GIF**, with no key at all: a scripted model replays the
"scale tickup" conversation against the fixtures, approval gate included.

```bash
uv run python scripts/readme-assets/demo_server.py   # http://localhost:8100
```

`uv run scripts/readme-assets/capture.py` re-shoots every image in `docs/assets/`
from it (needs Chrome).

**While developing**, two processes are nicer than one:

```bash
make run-api      # :8100, reloading
make run-web      # :5173, hot module reload, proxies /api to :8100
```

**The full stack**, with Postgres and Redis so suspended approvals survive a
restart:

```bash
make up           # dashboard on :8080
```

---

## 🧠 How it works

The agent loop is [`quaerium.agents`](https://github.com/gmottola00/quaerium)
(Quaerium ≥ 0.4), a reusable agent kernel. Ultron brings the
capabilities, the prompts, the router's vocabulary, the policy texts, the model
catalog and the gateway. To work on both at once: `make quaerium-dev`, then
`UV_NO_SYNC=1 make check`.

```mermaid
flowchart LR
    msg(["user message"]) --> router
    router{"router"} -- "small talk:<br/>no tools, low effort" --> model
    router -- "everything else:<br/>full tool surface" --> model
    model["model<br/>streamed"] -- "tool calls" --> gate{"gate"}
    model -- "no tool calls" --> answer(["answer"])
    gate -- "read / write" --> act["act<br/>concurrent calls"]
    gate -- destructive --> wait["⏸ interrupt<br/>checkpointed"]
    wait -- "approved" --> act
    wait -- "rejected" --> model
    act -- "all results,<br/>one message" --> model
```

- **router** — small talk gets no tools and low effort; everything else gets the
  full surface.
- **model** — Claude Opus 5 with adaptive thinking, streamed. The Anthropic SDK
  is confined to the kernel's `AnthropicLLM`; everything else talks to a
  protocol, which is how the whole graph is tested without an API key.
- **gate** — the one place a human is asked. Reads and writes pass; destructive
  calls suspend the run via LangGraph's `interrupt`, checkpointed to Postgres.
- **act** — cleared calls run concurrently and every result comes back in a
  single message.

The policy:

| risk | meaning | what happens |
|---|---|---|
| `read` | no side effects | runs immediately |
| `write` | commit or pull request — never the cluster | runs immediately |
| `destructive` | hard to reverse | suspends and asks |

`github__merge_pr` is destructive on purpose. Merging is what ships; that gate is never automated.

What "scale tickup to 2" looks like end to end:

```mermaid
sequenceDiagram
    autonumber
    actor U as You
    participant J as Ultron
    participant G as GitHub
    participant H as notify-hub
    participant A as ArgoCD

    U->>J: "scale tickup to 2"
    J->>G: github__set_replicas (write)
    G-->>J: PR 42 opened
    J->>G: github__check_runs (read)
    J->>J: github__merge_pr → gate: destructive
    Note over J: run suspended (interrupt),<br/>checkpoint in Postgres
    J-)H: "Approval needed"
    H-)U: push to the phone
    U->>J: approve (even after a restart)
    J->>G: merge PR 42
    A->>G: sync main
    A->>A: rollout tickup, replicas: 2
    J-->>U: done, with the PR link
```

---

## 🧩 Adding a capability

**This is where Ultron grows.** Three steps, and nothing else changes — not the
graph, not the gate, not the API, not the dashboard.

```
src/jarvis/tools/<name>/
├── client.py    # typed async client; reads its token from Settings
├── fake.py      # same surface, static fixtures
├── tools.py     # the @tool functions + a ClientProvider
└── __init__.py  # exports TOOLS and provider
```

```python
@tool(namespace="home", risk=RiskLevel.WRITE)
async def wake(host: str) -> str:
    """Send a Wake-on-LAN packet.

    Args:
        host: The machine to wake, e.g. "desktop-5080".
    """
    return await provider.get().wol(host)
```

The JSON Schema is derived from the signature and the docstring, so that
`Args:` block becomes the parameter description the model reads. Then add the
module to `CAPABILITIES` in `src/jarvis/tools/__init__.py`. Done.

A capability may import from `jarvis.core`, `jarvis.settings` and `jarvis.tools` —
never from `jarvis.agent` or `jarvis.api`. That is what keeps lifting one out into
a standalone MCP server an adapter rather than a rewrite.

```mermaid
flowchart TD
    api["jarvis.api<br/>FastAPI, SSE"] --> agent["jarvis.agent<br/>prompts, policy, models"]
    api --> tools
    agent --> tools
    agent --> kernel["quaerium.agents<br/>graph, gate, runner"]
    subgraph tools["jarvis.tools.#lt;name#gt;"]
        t["tools.py"] --> c["client.py"] & f["fake.py"]
    end
    tools --> core["jarvis.core<br/>no I/O"] & settings["jarvis.settings"]
    tools -. "✗ never" .-x agent
    tools -. "✗ never" .-x api
```

### What ships today

| namespace | tools | risk |
|---|---|---|
| `k8s` | `list_nodes` `list_pods` `get_logs` `list_events` `rollout_status` | read |
| `argocd` | `list_apps` `app_health` `app_diff` | read |
| `argocd` | `hard_refresh` | destructive |
| `ghcr` | `list_tags` `newest_green_tag` | read |
| `github` | `read_file` `list_prs` `check_runs` | read |
| `github` | `create_branch` `commit_file` `open_pr` | write |
| `github` | `set_replicas` (PR that sets `replicas` in the kustomization; apps in `JARVIS_REPLICAS_APPS` only) | write |
| `github` | `merge_pr` | destructive |
| `prometheus` | `query` `query_range` `pod_resources` `targets_down` | read |
| `loki` | `search` `query` | read |
| `alertmanager` | `list_alerts` | read |

---

## 🗂️ Layout

```
src/jarvis/
├── settings.py        pydantic-settings; every credential lives here
├── exceptions.py      JarvisError, below the kernel's AgentError
├── core/              dashboard value types, the console's log logic, kustomize edits — no I/O
├── tools/             one folder per capability
├── gateway/           LiteLLM spend, failures and latency for the gateway view
├── notify/            notify-hub client: notify() never raises, and the approval push
├── agent/             prompts, router vocabulary, policy texts, model catalog, playbooks
└── api/               FastAPI: lifespan, SSE chat, lab overview push (approvals and runs from quaerium)

web/src/
├── lib/               types mirroring quaerium.agents.types and core/types.py, the SSE parser, REST calls
├── components/        chat, approval dialog, lab panel, run timeline
└── pages/Dashboard.tsx
```

---

## ⚙️ Configuration

Everything is `JARVIS_`-prefixed except `ANTHROPIC_API_KEY`. See `.env.example`.

Ultron starts degraded rather than refusing to boot:

| missing | consequence |
|---|---|
| `ANTHROPIC_API_KEY` | chat says why; the dashboard still works |
| `JARVIS_DATABASE_URL` | in-memory checkpointer — a restart forgets pending approvals |
| `JARVIS_REDIS_URL` | in-process session history |
| capability tokens | that capability's tools return an error naming the variable to set |
| `JARVIS_LLM_GATEWAY_URL` | Claude only, straight to Anthropic; the model picker is hidden |
| `JARVIS_OLLAMA_URL` | local models always shown as available; the gateway's fallback still covers a dead GPU |
| `JARVIS_PROMETHEUS_URL` | `prometheus__*` tools return an error naming the variable; the rest of the agent is unaffected |
| `JARVIS_LOKI_URL` | `loki__*` tools likewise; `k8s__get_logs` still reads live containers |
| `JARVIS_ALERTMANAGER_URL` | the alerts page shows an error card; the dashboard's alert count is simply left out |
| `JARVIS_NOTIFY_URL`, `NOTIFY_TOKEN` | push notifications off; the bell says why |
| `JARVIS_LITELLM_DB_URL` | Settings shows only Ultron's own budget; no per-app spend, failures or latency, no gateway problems in Status |

### Models and the LLM gateway

With `JARVIS_LLM_GATEWAY_URL` pointing at a LiteLLM proxy, every model call goes
through it and `ANTHROPIC_API_KEY` holds the proxy's virtual key, not the real
one. The chat gets a model picker fed by `GET /api/models`, which is whatever
that key may call:

- `claude-*` go through the proxy's Anthropic pass-through, so adaptive
  thinking, effort and the refusal fallback arrive untouched;
- `local/*` (Ollama on the GPU desktop) go through the proxy's `/v1/messages`,
  with a trimmed request. Their thinking is streamed but not kept in history,
  since a later Claude turn would reject an unsigned thinking block.

While the desktop is off, `local/*` show as offline. A message sent to one
never silently lands on Claude: the chat answers `model_unavailable`, asks
whether to use `JARVIS_LOCAL_FALLBACK_MODEL` (default `claude-haiku-4-5`)
instead, and only then resends with `allow_fallback`. No timeout is waited on —
Ultron probes Ollama itself. The answering model is shown under each reply. In
the cluster the proxy is `apps/litellm` in Home-Lab-Infra; locally,
`docker compose --profile gateway up`.

```mermaid
flowchart LR
    pick["model picker<br/>GET /api/models"] --> kind{"model?"}
    kind -- "claude-*" --> pass["LiteLLM /anthropic<br/>pass-through"] --> anth["Anthropic"]
    kind -- "local/*" --> gpu{"Ollama answers?<br/>/api/ps probe"}
    gpu -- yes --> msgs["LiteLLM /v1/messages<br/>trimmed request"] --> ollama["Ollama<br/>GPU desktop"]
    gpu -- no --> ask["model_unavailable<br/>ask the user"]
    ask -- "allow_fallback" --> fb["JARVIS_LOCAL_FALLBACK_MODEL"] --> pass
    ask -- "no" --> stop(["nothing sent"])
```

### On the phone and notifications

Added to the iPhone Home Screen (Share → Add to Home Screen) Ultron opens as
**Ultron**, full screen, with its own icon and launch screen. `web/public/sw.js`
keeps the shell so it never opens blank, and never touches `/api`. Icons and
launch screens are rendered by `npm run pwa-assets` (needs `google-chrome`).

Push goes through notify-hub, a small lab service that holds the
VAPID key and the subscribed phones; the phone subscribes via Ultron
(`/api/push/*`), never to the hub, which is cluster-internal.

```mermaid
sequenceDiagram
    participant P as iPhone (Ultron PWA)
    participant J as Ultron
    participant H as notify-hub<br/>(cluster-internal)
    participant S as Apple push service

    P->>J: GET /api/push/key
    J->>H: GET /v1/vapid-public-key
    P->>P: pushManager.subscribe(key)
    P->>J: PUT /api/push/subscription
    J->>H: PUT /v1/subscriptions
    Note over J: a run suspends for approval
    J-)H: POST /v1/notify "Approval needed"
    Note over J: the SSE stream never waits on the hub
    H->>S: encrypted, VAPID-signed
    S-->>P: notification → tap opens approvals
```

- **Bell** in the phone top bar (or "notifications" in the sidebar): turn on, off,
  send a test. On iPhone it works only from the Home Screen app.
- **A run waiting for approval** pushes "Approval needed"; the tap opens
  Ultron → approvals. In the background: the stream never waits on the hub.
- **From code:** `await svc.notifier.notify("Title", "Body", url="/#status", tag="...")`.
  It never raises: a hub that does not answer logs `notify.failed` and returns `None`.

---

## 🧪 Testing

```bash
make check        # black, isort, ruff, mypy --strict, pytest
make smoke-web    # the browser's SSE client, against a live backend
```

The graph tests drive a `ScriptedLLM` — a list of turns replayed in order — so
every assertion is about what the loop does, not about what a language model
happened to say. The API tests run the real ASGI app: routers, SSE encoding,
runner, graph, gate and checkpointer, all together.

`make smoke-web` covers the one seam Python cannot reach: the wire format as the
browser parses it. It earned its place — it caught a CRLF framing bug that every
Python test missed, because httpx normalises line endings and `fetch` does not.

---

## 🛣️ Roadmap

Planned phases:

- **P1 — voice.** Push-to-talk → Pipecat + whisper + Piper.
- **P2 — GPU on demand.** The desktop joins as a k3s agent, woken by WoL.
- **P3 — vision and gesture.**
- **P4 — autonomy.** `mcp-coder`, preview namespaces per PR.

## 🚢 In my home lab

Ultron runs on the same single-node k3s cluster it operates, managed from
[**Home-Lab-Infra**](https://github.com/gmottola00/Home-Lab-Infra) (manifests in
`apps/jarvis`). It is reachable only over the tailnet (`jarvis.<tailnet>.ts.net`),
reads the cluster through a `jarvis` ServiceAccount bound to the read-only
ClusterRole `jarvis-reader` (no access to Secrets), and calls models through the
lab's LiteLLM gateway with its own budgeted virtual key.

```mermaid
flowchart LR
    push["git push main"] --> ci["CI: make check<br/>(backend / web)"]
    ci --> build["image<br/>ghcr.io/gmottola00/jarvis-backend:sha"]
    build --> bump["bump newTag in<br/>Home-Lab-Infra/apps/jarvis"]
    bump --> argo["ArgoCD sync"] --> pod["new pod"]
```

Nothing is applied by hand — the same rule Ultron itself follows.

---

## 🤝 Contributing

Issues and pull requests are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) first,
and report vulnerabilities privately as described in [SECURITY.md](SECURITY.md).

## 📄 License

[MIT](LICENSE) © Gianmarco Mottola
