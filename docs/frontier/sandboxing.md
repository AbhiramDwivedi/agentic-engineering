# 9.4 Sandboxing

*The moment an agent runs code it wrote, that code can reach whatever your process can reach. A sandbox is the boundary your code builds around it: which files, which hosts, which secrets. It holds only if you name the threat, cover every path that executes something, and never hand the same code both private data and a way out.*

*Also called: code execution sandbox, execution boundary, sandbox mode (Codex), `/sandbox` (Claude Code).*

## Why you'd reach for it

In June 2023, a security researcher got Auto-GPT, an early open-source autonomous agent, to escape the Docker container it ran in. The attack targeted the self-built Docker setup, and every step went through the agent's own tools.[^1] The agent browsed a web page carrying instructions in zero-size text. It followed them, downloaded a script, and ran it. The container held one thing worth attacking: the project's own `docker-compose.yml`, mounted inside it. The script rewrote that file to mount the host's root filesystem with full privileges, then stopped the container, and the next restart ran the attacker's configuration on the host. No container bug was needed: the file that defined the container was mounted inside it, writable.

Give a model a code interpreter or a shell and it writes programs you never read, which run with your process's reach: your files, your network, your environment variables, your cloud credentials. A model can do damage on its own, deleting the wrong directory because it misread the task, or be steered by instructions hidden in anything it reads, which is indirect prompt injection. Either way, what the code touches is decided by the boundary around it, and the easiest boundary to build is a subprocess with a timeout. That bounds how long the code runs and nothing else.

You need a real boundary when:

- **The model writes code or shell commands and something executes them.** A coding agent, a data-analysis tool, a code interpreter.
- **The model reads content you do not control** while it can execute: web pages, uploaded files, issues in a public repo.
- **More than one tenant shares the machine** the code runs on.
- **You want fewer approval prompts.** A boundary that holds lets people stop approving each command, because the worst a command can do is bounded.

The counter-trigger: if the agent acts only through typed tools you wrote, it runs no code of its own, and the boundary is argument validation and least privilege inside each tool ([2.1 Tool Use](../the-unit/tool-use.md), [4.4 Guardrails & Safety](../craft/guardrails-and-safety.md)). Do not put a container around a function call.

## What it actually is

A sandbox is an enforced boundary, built by your code and held by the operating system or a hypervisor, that limits what model-written code can read, write, reach over the network, and inherit from its environment, whatever the model intends. It has three walls (the filesystem, the network, and the inherited environment with its secrets), and it has to wrap every path through which something executes.

![A diagram of the model proposing code, which passes into a boundary drawn by your code with three walls labelled filesystem, network, and environment and secrets; inside, the code reaches only an allowed workspace folder and allowed hosts, and a bounded result with exit code, truncated output and a timeout flag flows back to the model.](sandboxing-boundary.svg)

Your code decides here. The model chooses what to run, and that choice belongs to the agent loop ([2.5 The Agent Loop](../the-unit/the-agent-loop.md)); what the choice can reach is fixed before the model speaks and does not move when the model asks. This is old engineering. Serverless platforms were running many strangers' code side by side on one host long before agents existed;[^6] what changed is that the untrusted author is now your own agent. The boundary is part of the harness, the code that wraps the model ([2.6 The Harness](../the-unit/the-harness.md)).

The maturity is **Established**. Anthropic states the core principle plainly: effective sandboxing needs both filesystem and network isolation, because without the network wall a compromised agent can send your SSH keys out, and without the filesystem wall it can escape the sandbox and reach the network anyway.[^2] That pairing, default-deny egress (outbound network traffic blocked unless its destination is on an allowlist), and keeping approvals separate from isolation are settled practice. The hosted agent-sandbox platforms and the benchmarks that try to measure escape are newer and still settling.

### Every path that executes

The boundary covers only the paths you put inside it. Claude Code's sandbox is a public example you can read. It wraps shell commands and the processes they start, using Seatbelt, the sandbox profile system built into macOS, and bubblewrap, a small Linux tool that starts a process with a restricted view of the filesystem and network.[^2] Its file tools follow permission rules instead, and command hooks and local MCP servers run with your full access.[^3] Inside the writable directories it still refuses writes to the files Claude Code loads configuration and code from, such as `.claude` settings, `.mcp.json` and shell startup files like `.bashrc`, because a command that could edit those "could grant itself permissions, or add a hook or MCP server that Claude Code runs outside the sandbox."[^3] By analogy, the same rule would have blocked the Auto-GPT pattern: there the file was `docker-compose.yml`, here it is the agent's own configuration, and in both cases sandboxed code must not write the file that decides what runs next.

You can check this on your own screen. In Claude Code on macOS, Linux or WSL2 with the sandbox on, ask it to run `touch ~/sandbox-probe` and expect "Operation not permitted" or "Read-only file system"; ask for `curl --noproxy '*' https://example.com` and expect "Could not resolve host". Decline any offer to retry outside the sandbox. A command you type yourself after Claude Code's `!` prefix, which sends a line straight to your shell, usually runs unsandboxed, so it proves nothing.[^3] The probe tests those two walls, not every path that executes: hooks and local MCP servers sit outside it.

### Mechanisms, chosen by threat

The isolation mechanisms differ in how much they share with the host, and they compose:

- **OS sandbox** (Seatbelt on macOS; bubblewrap and Landlock on Linux, where Landlock is a kernel feature that lets a process give up its own file access rights). Restricts a process on your own kernel. Cheap, starts instantly, fits a local agent on a laptop.
- **Container.** Namespaces (each container gets its own view of processes, files and network) and cgroups (kernel limits on CPU, memory and process count) on the host's shared kernel. A kernel bug or a careless mount is an escape route.
- **gVisor.** An application kernel that intercepts the sandboxed program's system calls, so few of them reach the host. Its own docs warn that "one should not assume that the mere use of virtualization hardware makes a system more or less secure."[^5]
- **MicroVM** (Firecracker). Each workload gets its own guest kernel behind a minimal hypervisor, the layer that runs virtual machines directly on the hardware, built to run many tenants' functions on one host.[^6]

Pick by what the code might do and what sits next to it. Your own agent editing your own repo on your laptop, where the threat is a confused model or an injected instruction, is well served by an OS sandbox with a tight network allowlist. Strangers' code on shared servers, where the threat is a deliberate attacker, wants a kernel boundary: gVisor or a microVM.

There are two deployment shapes. A **local agent sandbox** wraps a coding agent on a developer's machine: Claude Code's `/sandbox`, or Codex's `sandbox_mode` of `read-only`, `workspace-write` or `danger-full-access`.[^4] **Hosted execution** runs the code on a provider's infrastructure: Anthropic's code execution tool. Their defaults differ with the threat: Claude Code's local sandbox, once switched on, allows writes inside the working directory and reaches the network only through an allowlist of hosts.[^3] Anthropic's hosted container has "no internet access" at all, so the code cannot download packages at runtime.[^7]

### What it gets confused with

**Approvals** decide when the agent stops to ask; the sandbox sets what is technically possible whether or not anyone was asked. OpenAI's Codex docs draw the same line: "The sandbox defines technical boundaries," and "the approval policy decides when the agent must stop and ask before crossing them."[^4] A team that tunes approvals while the agent holds full access has done half the job ([4.3 Human-in-the-Loop](../craft/human-in-the-loop.md)).

**The lethal trifecta** is Simon Willison's name for an agent that combines access to private data, exposure to untrusted content, and the ability to communicate externally.[^13] An agent with all three can be steered into sending the data out. A sandbox narrows the third leg and does nothing about the first two. Put a merchant's customer list inside a microVM with an open route to the internet, and the strongest isolation available will faithfully carry out the theft. Decide which leg to remove before you choose the mechanism ([4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md)).

## How to do it

Build the contract first, because it stays put when the backend changes. Every backend takes code and a time limit and returns the same bounded, structured result:

```python
from dataclasses import dataclass
from typing import Protocol

MAX_OUTPUT_CHARS = 2000  # a backend never returns unbounded output to the model


@dataclass(frozen=True)
class ExecResult:
    exit_code: int | None  # None when the run was killed by the timeout
    stdout: str
    stderr: str
    timed_out: bool = False
    truncated: bool = False


def bound(text: str, limit: int = MAX_OUTPUT_CHARS) -> tuple[str, bool]:
    """Cut text to the limit; report whether anything was dropped."""
    if len(text) <= limit:
        return text, False
    return text[:limit], True


class ExecutionBackend(Protocol):
    def run(self, code: str, timeout_s: float) -> ExecResult: ...
```

After every run the model gets an `ExecResult`: an exit code or `None`, output capped at 2,000 characters with a flag saying it was cut, and a timeout flag. A denied file read comes back as exit code 1 with `denied: path /etc/passwd` in `stderr`, which the model can read and work around. Anthropic's hosted tool makes a similar split: a normal result carries the program's output, and a separate error type carries codes such as `unavailable` and `execution_time_exceeded`.[^7] The model recovers from either inside its loop, and scheduled retries are your code's job ([3.7 The Outer Loop](../composition/the-outer-loop.md)). Neither recovery path ever widens the policy.

The bound also protects the context window: Anthropic's case for code execution with MCP is that the agent filters large data inside the sandbox and returns only what the model needs.[^8]

The policy is the second piece, and the one place the dangerous combination is refused:

```python
import re
from dataclasses import dataclass

from .contract import ExecResult, bound


class PolicyError(ValueError):
    """The configuration itself is unsafe; refused before any code runs."""


@dataclass(frozen=True)
class Policy:
    allowed_paths: tuple[str, ...] = ("/workspace/",)
    allow_egress: bool = False
    mounts_private_data: bool = False

    def __post_init__(self) -> None:
        if self.mounts_private_data and self.allow_egress:
            raise PolicyError("private data and an outbound channel in one sandbox")

    def path_ok(self, path: str) -> bool:
        return any(path.startswith(p) for p in self.allowed_paths) and ".." not in path
```

Egress is off by default. A policy that mounts private data and allows egress cannot be constructed, so the mistake fails when someone writes the config, before any model output exists to blame.

The companion repo puts two backends behind that contract: a fake that enforces the policy by scanning the program text, and the unsafe runner for comparison. The fake's two regular expressions match `open('...')` calls and `fetch('...')` or `connect('...')` calls written with literal strings.

<details markdown>
<summary>The two backends: the policy fake and the unsafe subprocess</summary>

```python
# Matches open('...') and fetch('...') / connect('...') calls written as literals.
_OPEN = re.compile(r"open\(['\"]([^'\"]+)['\"]")
_NET = re.compile(r"(?:fetch|connect)\(['\"]([^'\"]+)['\"]")


class PolicyBackend:
    """Regex-scans code for file and network intents; not OS-enforced."""

    def __init__(self, policy: Policy) -> None:
        self.policy = policy

    def run(self, code: str, timeout_s: float) -> ExecResult:
        for path in _OPEN.findall(code):
            if not self.policy.path_ok(path):
                return ExecResult(1, "", f"denied: path {path}")
        if _NET.search(code) and not self.policy.allow_egress:
            return ExecResult(1, "", "denied: network egress")
        out, cut = bound(f"ran {len(code)} chars")
        return ExecResult(0, out, "", truncated=cut)
```

```python
import subprocess
import sys

from .contract import ExecResult, bound


class UnsafeSubprocessBackend:
    """Same contract, no containment: the child inherits files, network and env."""

    def run(self, code: str, timeout_s: float) -> ExecResult:
        try:
            p = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True, text=True, timeout=timeout_s,
            )
        except subprocess.TimeoutExpired:
            return ExecResult(None, "", "timed out", timed_out=True)
        out, c1 = bound(p.stdout)
        err, c2 = bound(p.stderr)
        return ExecResult(p.returncode, out, err, truncated=c1 or c2)
```

</details>

What the tests run, in order:

1. `open('/etc/passwd')` against the default policy: exit code 1, `denied: path /etc/passwd`. A path containing `..` is refused the same way.
2. A `fetch(...)` with egress off: exit code 1, `denied: network egress`. With egress allowed, the same program runs.
3. `Policy(mounts_private_data=True, allow_egress=True)` raises `PolicyError` before any code runs. Either flag alone is accepted.
4. The unsafe runner prints 5,000 characters; the model gets 2,000 and `truncated=True`. A 30-second sleep under a 1-second timeout comes back `timed_out=True` with `exit_code=None`.
5. A temporary file the policy backend refuses (exit code 1) is read back in full by the unsafe runner.

Step 5 is why the unsafe runner exists: a subprocess with a timeout satisfies the contract and contains nothing.

These tests prove the contract (bounded output, a timeout flag, a structured denial) and the policy (paths outside the allowlist refused, egress off by default, private data plus egress rejected at configuration). They do not prove kernel isolation. The fake backend only sees paths and hosts written as string literals, and a program that builds its path from a variable walks straight past it. Nothing in the companion repo depends on a kernel feature, so the same tests run offline on Windows and Linux. The wall comes from a backend that enforces the same policy at the OS or hypervisor level, such as bubblewrap, gVisor or a microVM, slotted in behind `ExecutionBackend`.

### From one sandbox to many

Production adds users. Bind each environment to one tenant and one session, never reuse it for another, and destroy it explicitly, because a sandbox that keeps files between runs carries one session's data into the next. Give each environment its own CPU, memory, process-count, disk and wall-clock limits: a Docker container has no resource constraints by default,[^12] and gVisor relies on the host's cgroups to defend against resource exhaustion.[^5] When time runs out, kill the whole process tree, because `subprocess.run` kills the child it started on timeout and leaves anything that child spawned running. Who the sandbox acts as belongs to [8.5 Locks, PII & Identity](../production/locks-pii-identity.md); what a pool of warm environments costs belongs to [8.4 Controlling Cost](../production/controlling-cost.md).

> **On Stockwell.** The Repricer, the agent on Stockwell (the fictional commerce platform this book uses as its running example) that adjusts prices within rules, acts only through typed tools, so it runs no code of its own and its boundary is validation inside each tool. The day it is allowed to write a script over a merchant's price history, that script needs a real backend behind `ExecutionBackend` and a `Policy` with egress off, because the merchant's data is private and the competitor pages it reads are untrusted.

## Gotchas

1. **The sandbox that isn't.** A "restricted" Python interpreter or a regex over the program text gets sold as a sandbox, and so does the unsafe runner above. Insist on an OS or hypervisor boundary, and test it with a negative case that has to fail.

2. **Default containers leak.** Running a container privileged or mounting writable host paths into it gives code inside a way out; the Auto-GPT escape rewrote a writable mount.[^1] Runtimes have bugs too: CVE-2024-21626 let a process in a runc container reach the host filesystem through a leaked file descriptor until runc 1.1.12.[^10] SandboxEscapeBench found that frontier models can find and exploit such holes when they are planted in a test environment.[^9] That shows the risk of misconfiguration; it does not show that a patched, hardened container is escapable.

3. **Configuration undoes the boundary.** In Claude Code, a command that fails in the sandbox may be retried with `dangerouslyDisableSandbox` and run unsandboxed; `excludedCommands` run "with your full access"; opening all Unix sockets hands sandboxed code every local daemon; on native Windows, commands run unsandboxed; and if the sandbox cannot start, commands run without it unless `failIfUnavailable` is set.[^3] Read your settings as an attacker would, and fail closed in anything unattended.

4. **A string allowlist is a filter, and filters get bypassed.** CVE-2025-54794 was a path-prefix check in Claude Code that a sibling directory sharing the prefix slipped past, fixed in 0.2.111; CVE-2025-54795 let a crafted command skip the approval prompt, fixed in 1.0.20.[^11] Both needed untrusted content in the agent's context. Both were string checks inside the application, and neither was an OS boundary.

5. **An allowed host carries anything.** Claude Code's proxy checks each host against an allowlist and by default does not inspect TLS traffic (it sees which host a connection goes to, not what the encrypted stream carries), so anything the code can say to an allowed host, it can send.[^3] Allow the narrowest set of hosts, and count every general-purpose host (code hosting, a paste site, a storage bucket) as an outbound channel. OWASP's agentic top ten lists unexpected code execution as a risk of its own (ASI05) and advises running code "in sandboxed containers with strict limits, including network access."[^14]

6. **Secrets ride along.** An API key in an environment variable or a token passed in as a tool argument goes wherever the code is allowed to send it. Scrub the environment before execution and mount only what the task needs.

7. **Vendor numbers lack a method.** Anthropic reports that sandboxing cut permission prompts by 84% in its internal usage, with no stated baseline or workload.[^2] Treat it as a direction, and measure your own prompt rate before and after.

## In short

If your agent runs code it wrote, build the result contract and the policy first, put a real OS or hypervisor backend behind them, and keep egress off by default. Use an OS sandbox for your own agent on your own machine, gVisor or a microVM for anyone else's code on shared hardware. Cover every path that executes, protect the files that decide what runs next, fail closed, and never let one sandbox hold both private data and a way out. Then prove it with a probe that has to fail.

<small class="chapter-meta">**Maturity: Established** (filesystem plus network isolation and default-deny egress are settled practice; hosted agent-sandbox platforms and escape benchmarks are still emerging) · *Who decides:* your code · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^1]: Euler, L., Positive Security, "Hacking Auto-GPT and escaping its docker container" (2023-06-29). A security disclosure, fixed in Auto-GPT v0.4.3; not a production postmortem. <https://positive.security/blog/auto-gpt-rce>
[^2]: Anthropic, "Beyond permission prompts: making Claude Code more secure and autonomous" (2025-10-20). The 84% figure is from internal usage; no method is stated. <https://www.anthropic.com/engineering/claude-code-sandboxing>
[^3]: Anthropic, Claude Code documentation, "Sandboxing." Behaviour as documented at the time of review; setting names change between releases. <https://code.claude.com/docs/en/sandboxing>
[^4]: OpenAI, Codex documentation, "Sandbox." <https://learn.chatgpt.com/docs/sandboxing>
[^5]: gVisor documentation, "Security Model." <https://gvisor.dev/docs/architecture_guide/security/>
[^6]: Agache, A., et al., "Firecracker: Lightweight Virtualization for Serverless Applications," NSDI '20, pp. 419-434. <https://www.usenix.org/conference/nsdi20/presentation/agache>
[^7]: Anthropic, "Code execution tool." <https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool>
[^8]: Anthropic, "Code execution with MCP: building more efficient agents" (2025-11). <https://www.anthropic.com/engineering/code-execution-with-mcp>
[^9]: Marchand, R., et al., "Quantifying Frontier LLM Capabilities for Container Sandbox Escape," arXiv:2603.02277 (v1 2026-03-01). Vulnerabilities are deliberately added to the test environments. <https://arxiv.org/abs/2603.02277>
[^10]: NIST NVD, CVE-2024-21626 (runc). <https://nvd.nist.gov/vuln/detail/CVE-2024-21626>
[^11]: NIST NVD, CVE-2025-54794 and CVE-2025-54795 (Claude Code). <https://nvd.nist.gov/vuln/detail/CVE-2025-54794>, <https://nvd.nist.gov/vuln/detail/CVE-2025-54795>; GitHub advisories GHSA-pmw4-pwvc-3hx2 (fixed in 0.2.111) and GHSA-x56v-x2h6-7j34 (fixed in 1.0.20). <https://github.com/advisories/GHSA-pmw4-pwvc-3hx2>, <https://github.com/advisories/GHSA-x56v-x2h6-7j34>
[^12]: Docker documentation, "Resource constraints." <https://docs.docker.com/engine/containers/resource_constraints/>
[^13]: Willison, S., "The lethal trifecta for AI agents: private data, untrusted content, and external communication" (2025-06-16). <https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/>
[^14]: OWASP GenAI Security Project, "OWASP Top 10 for Agentic Applications for 2026" (2025-12-09), ASI05 Unexpected Code Execution (RCE). <https://genai.owasp.org/agentic-applications-2026/asi05-unexpected-code-execution-rce/>

## See also

- [2.1 Tool Use](../the-unit/tool-use.md), for the typed-tool path that needs validation instead of a sandbox.
- [2.5 The Agent Loop](../the-unit/the-agent-loop.md), where the model decides what to run and reads the result this chapter bounds.
- [2.6 The Harness](../the-unit/the-harness.md), the code that owns this boundary along with permissions and stop conditions.
- [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md), for approvals, the control most often mistaken for isolation.
- [4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md), on removing a leg of the trifecta before choosing a mechanism.
- [9.6 Coding Agents](coding-agents.md), the agents most of these sandboxes were built for.
- [The Anti-Patterns Catalog](../catalogs/anti-patterns.md), for the sandbox that isn't.

## Further reading

- Anthropic, ["Beyond permission prompts"](https://www.anthropic.com/engineering/claude-code-sandboxing) (2025-10-20): why filesystem and network isolation come as a pair, from a team shipping both.
- Anthropic, [Claude Code sandboxing docs](https://code.claude.com/docs/en/sandboxing): a detailed public account of what one local sandbox covers and what it leaves outside.
- gVisor, ["Security Model"](https://gvisor.dev/docs/architecture_guide/security/): a threat-model-first argument about shared kernel surface.
- Agache et al., ["Firecracker"](https://www.usenix.org/conference/nsdi20/presentation/agache) (NSDI '20): how a microVM isolates many tenants' code on one host.
- Euler, ["Hacking Auto-GPT and escaping its docker container"](https://positive.security/blog/auto-gpt-rce) (2023): an agent escape, end to end.
