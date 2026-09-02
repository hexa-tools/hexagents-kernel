# ADR 0001 — HEX-11 Rust replacement (arg coercion): measured ROI and its consequences for the roadmap

**Status:** Accepted
**Date:** 2026-09-01
**Related:** `rust/crates/hexagents-coerce/`, `rust/crates/hexagents-core/src/native.rs`,
`hexagents/infrastructure/adapters/secondary/tools/arg_coercer_rust.py`

## Context

HEX-11 was the first "replace an existing Python hot path with Rust behind
the same port" ticket, meant to prove the pattern for four more planned
replacements (trajectories, chat, credentials, routing). The ticket assumed
a ~10× speedup based on generic Rust-vs-Python throughput comparisons for
JSON-schema-style validation.

Reality, measured (representative corpus: 8 properties, string/int/float/
bool/null/array/object coercions; `cargo bench -p hexagents-coerce` +
`scripts/bench_arg_coercion.py`, dev machine):

| Implementation | ops/sec (end to end, FFI included) | Ratio vs. Python |
|---|---|---|
| Pure Python (`coerce_args`) | ~230,000 | 1× (reference) |
| Rust via `pythonize` (generic serde round-trip — 1st attempt) | ~130,000 | **~0.56× (slower)** |
| Rust via direct `PyDict`/`PyAny` access + `intern!` (adopted) | ~390,000 | **~1.7×** |
| *(reference only)* pure Rust algorithm, no FFI (`cargo bench`) | ~372,000 (2.65µs/call) | — |

The first attempt (generic `pythonize` serialize/deserialize round-trip
through an intermediate `serde_json::Value` tree) was measurably **slower**
than pure Python — the FFI/allocation cost dominated the algorithmic
speedup for this hot path's small payloads. Rewriting the binding to walk
`PyDict`/`PyAny` directly (`PyDict::get_item`/`set_item`, `intern!` on the
literal keys re-read every call — `"type"`, `"properties"`, `"required"`)
removed that intermediate allocation and flipped the ratio to ~1.7×,
confirmed stable across multiple runs.

## Decision

Ship the Rust replacement (the 1.7× native-access version), keep it as the
default (`build_arg_coercer(prefer_rust=True)`), and use this ticket's
*process* — not its headline ratio — as the template for the next
replacements: measure both a naive and an optimized FFI approach, report
both, and re-evaluate the roadmap against real code before committing
implementation time to the next candidate.

## Honest ROI assessment — do not soften this

The absolute gain measured is ~1.8µs/call (Python ~4.3µs/call, Rust native
~2.5µs/call). Even across 1000 tool calls in a session, that is ~1.8ms
cumulative — below the noise floor of a single LLM call (hundreds of ms to
several seconds) or a single tool call itself (subprocess/network, on the
order of milliseconds).

**Isolée, la coercion d'arguments n'était pas un vrai goulot de latence —
c'était un goulot de *débit* (ops/sec) mesuré hors contexte, qui ne se
traduit pas en gain perceptible dans une boucle agent mono-session.**

This ticket is justified by what it built and learned (the `rust/`
workspace, guard rules R20/R21, the logged-fallback pattern, the benchmark
methodology, and the FFI lesson above) — not by the 1.7× itself. Argument
coercion was structurally **the worst possible candidate** to prove this
pattern: small payload, maximum call frequency (potentially several times
per turn), i.e. the worst possible ratio of (FFI overhead) / (real work)
among the identified hotspots. Whoever reads this later and is tempted to
round it up to "success" — don't; the number above is the actual result.

## New criterion for future Rust replacements

Before committing implementation time to a candidate hotspot: estimate the
FFI break-even point for **that specific hotspot** — payload size × call
frequency × whether there is real computation or just data assembly /
branching — rather than assuming the ratio measured here generalizes. A
hotspot with a larger payload, or genuine computational cost (not just
serialization or branching), amortizes the FFI crossing better than
argument coercion did. A hotspot with a tiny payload and high frequency
must, like this one, skip the generic serialization round-trip and go
straight to native `PyDict`/`PyAny` access on the first attempt, not as a
second pass discovered the hard way.

## Re-evaluation of the four planned replacements

Applied the new criterion to the actual code (not assumptions) before
touching any of the four:

| Candidate | Real call frequency | Payload | Real computation? | Verdict |
|---|---|---|---|---|
| **Credentials** (`CredentialPool.mark`/`resolve`, `adapters/secondary/llm/retry.py`) | `.mark()` on every LLM call | A handful of `Credential` objects (typically 1–5) | No — filtering + sorting a tiny list | **Worse candidate than arg coercion itself** (smaller payload, zero computation). Removed from the list. |
| **Routing** (`domain/services/task_router.py::TaskRouter.resolve`) | **Zero production call sites** (constructed in bootstrap, never invoked) — confirmed by direct grep, twice, after a failed delegated research attempt hit a rate limit and returned nothing to inherit from | A dict lookup | No — pure branching | Nothing to optimize while nothing calls it. Removed from the list until a real call site exists. |
| **Trajectories** (`application/service/trajectory_formatter.py::TrajectoryFormatter.format`) | Once per **completed turn**, not per tool call — structurally much less frequent than coercion | One entry per turn (not per tool call), `json.dumps` on tool-call args | String assembly + JSON serialization, no numeric computation | Favorable frequency; algorithmic win uncertain (text, not compute). Legitimate candidate — measure before implementing. |
| **Chat** (`infrastructure/adapters/secondary/llm/chat_completions.py`) | Once per LLM API call (per turn) | The full message array sent to the API — **grows with the conversation**, potentially KB to hundreds of KB | JSON serialization/parsing of the request/response payload | **Best structural candidate of the four** (large, growing payload; low frequency) — instrument real payload sizes before investing, don't assume. |

**Roadmap decision:** Credentials and Routing are **removed** from the
Rust-replacement list (not merely deprioritized) — neither has the
payload×frequency×computation profile needed to beat the FFI cost, even
optimized. Chat is next, Trajectories after it — **both require measuring
real payload sizes on a long-running session before any implementation
starts**, per the criterion above. Do not repeat HEX-11's
implement-then-measure-then-fix cycle; measure first this time.
