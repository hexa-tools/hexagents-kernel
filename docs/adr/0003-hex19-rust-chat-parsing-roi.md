# ADR 0003 — HEX-19 Rust replacement (chat response parsing): measured ROI and the small-payload trap resurfacing

**Status:** Accepted
**Date:** 2026-09-01
**Related:** `rust/crates/hexagents-chat/`, `rust/crates/hexagents-core/src/native.rs`,
`hexagents/infrastructure/adapters/secondary/llm/{chat_rust.py,chat_completions.py,chat_completions_factory.py}`,
`docs/adr/0001-hex11-rust-arg-coercion-roi.md`

## Context

`docs/adr/0001` called Chat *"the best structural candidate of the four (large, growing payload; low frequency) — instrument real payload sizes before investing, don't assume."* Before implementing, this ticket traced the actual code and found that framing wrong on two counts, plus two ticket items with nothing real behind them:

- **Payload does not grow across turns.** The server discards any client-sent conversation history and rebuilds `[system(227B), user]` from scratch on every `/api/chat` call — there is no cross-turn server-side state. Only *within* a single request does the message array grow, bounded by `IterationBudget` (default 50 iterations), with small tool-observation messages.
- **Call frequency is real and confirmed** (unlike Trajectories, ADR 0002's zero-call-site finding) — traced end to end: `POST /api/chat` → `ChatUseCase` → `AgentLoop` → `ChatCompletionsTransport`, live in production on every turn.
- **"Dedup" of messages** — no such logic exists anywhere in the codebase. Excluded from scope.
- **"Thinking" field extraction** — `LLMResponse` has no `thinking` field; only two aspirational docstring references in `think_scrubber.py` claim otherwise. Excluded from scope — building it would be new feature work, not a port.
- **Request-body assembly (`_build_body`)** was evaluated and excluded too: it's a trivial list comprehension plus a couple of conditionals, not meaningfully CPU-bound, and entangled with domain validation (`ConfigError`/`clamp_effort`). Only `_parse`/`_parse_usage` — the one function with real multi-field structured extraction — was ported, per the user's explicit "reduce to what's real" instruction.

## Edge-case pass: one real bug found and fixed, one real robustness gain documented

A follow-up edge-case pass (probing the live compiled module directly, not just the happy-path corpus) found a genuine parity bug before it shipped: Python's `int(raw.get("prompt_tokens", 0))` truncates a float usage value (`int(10.5) == 10`), but the first Rust implementation used `serde_json::Value::as_i64()` alone, which returns `None` for *any* float-backed JSON number — even a whole one like `16.0` — silently defaulting to `0`. Fixed in both the pure crate and the duplicated `native.rs` PyDict-walking implementation (`as_i64()` first, falling back to `as_f64() as i64` to truncate toward zero, matching Python exactly), verified live against the rebuilt module, and locked in with a parity test.

The same pass also surfaced a genuine, permanent behavioral difference — not a bug: on a wrong-shaped response (`choices` as a string, `message` as a string, etc.), the pure-Python `_parse_response_python` **crashes** with a raw `AttributeError`/`KeyError` (it was never written defensively), while the Rust port — because every field access is an explicit `Option`/type check — degrades gracefully everywhere, either returning empty/default fields or raising the controlled `ValueError`→`LLMError` for a wrong-typed `choices`. This is documented in `test_chat_rust.py` as an intentional robustness improvement, explicitly excluded from the parity corpus (parity is about well-formed responses, per the ticket's own acceptance criterion — matching a Python crash exactly would mean making Rust *less* safe, not more).

## Design note: applied the FFI lesson from the start

The input side (an already-decoded response dict) needed walking — same as `coerce_args`'s input side, so `native::parse_chat_response` hand-walks `PyDict`/`PyList` with `intern!`, no `pythonize`. The output side returns plain tuples (`String`, `Vec<(String,String,String)>`, `Option<(i64,i64,i64)>`, `Option<String>`), never a constructed `PyDict` — cheaper than even HEX-16's `parse_trajectory` output. There was no naive-attempt-then-fix cycle this time; the lesson from HEX-11 was applied on the first attempt.

## Measured ROI

Corpus: **synthetic**, 424 bytes — a short text field, two tool calls with realistic argument JSON, and a usage block. Notably *smaller* than HEX-16's trajectory payload (1,073 bytes) and closer in order of magnitude to HEX-11's arg-coercion payload.

Measured on this dev machine (`scripts/bench_chat_parse.py` for end-to-end Python/Rust-via-FFI numbers, `cargo bench -p hexagents-chat` via criterion for the pure-Rust-no-FFI reference):

| Implementation | ops/sec | Ratio vs. Python |
|---|---|---|
| Pure Python (`_parse_response_python`) | ~223,000 | 1× (reference) |
| Rust via pyo3, native `PyDict` access (adopted, first attempt) | ~251,000 | **~1.13×** |
| *(reference only)* pure Rust `parse_chat_response`, no FFI (`cargo bench`, 710ns/call) | ~1,408,000 | — |

The pure-Rust algorithm is ~6.3× faster than pure Python in isolation — but the FFI crossing (walking a `PyDict`, building a Python tuple/list of tuples to return) eats nearly all of that advantage. End to end, Rust is barely faster than Python at all.

## Decision

Ship it — the code is correct, tested, byte-for-byte behaviorally identical to the Python fallback (parity-tested against `test_chat_completions.py`'s corpus), and the call site is real, unlike Trajectories. Keep it as the default (`build_chat_completions_transport(prefer_rust=True)`). But do not present 1.13× as a win.

## Honest ROI assessment — do not soften this

**Avec 1.13×, le gain mesuré est dans le bruit de mesure — plus proche de zéro que d'un vrai gain perceptible, malgré une fréquence d'appel réelle et confirmée en production (contrairement aux Trajectories de l'ADR 0002). Le payload (424 octets, du même ordre de grandeur que celui de la coercion d'arguments) reste trop petit pour amortir la traversée FFI, même avec l'accès `PyDict` natif appliqué dès la première tentative plutôt que découvert après coup — la fréquence d'appel réelle ne compense pas une taille de payload structurellement défavorable.**

This is the weakest measured ratio of the three Rust replacements shipped so far (HEX-11: 1.7×, HEX-16: 3.27×, HEX-19: 1.13×) — and it's the one candidate ADR 0001 predicted would be the *best*. The prediction was built on an assumption about payload size that was never checked against the actual code before this ticket. That is the concrete cost of skipping the "measure before implementing" step at the ADR-writing stage, not just the coding stage.

## Re-evaluation

| Factor | Value | Note |
|---|---|---|
| Payload | 424 bytes/response (synthetic) | Smaller than HEX-16's trajectory record; comparable to HEX-11's arg-coercion payload |
| Call frequency (production, today) | **Real, confirmed** — every `/api/chat` → `AgentLoop` → LLM completion turn | Traced end to end, not assumed — the one confirmed-live candidate among the three shipped |
| Real computation? | No — dict field extraction with fallback defaults | Same category as arg coercion and trajectory formatting: branching/assembly, not numeric computation |
| Measured ratio | 1.13× (FFI), ~6.3× (no-FFI reference) | Real call frequency did not rescue a small-payload candidate |

**Standing criterion reaffirmed, sharpened**: payload size dominates the FFI break-even calculation more than call frequency does. A frequently-called, small-payload hotspot (arg coercion, chat parsing) consistently underperforms a less-frequent, larger-payload one (trajectory formatting) — frequency alone is not a reliable predictor of ROI; it must always be paired with a real payload-size measurement, checked against the actual code, before any implementation time is committed.
