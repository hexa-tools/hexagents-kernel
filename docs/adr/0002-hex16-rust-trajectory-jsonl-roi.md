# ADR 0002 — HEX-16 Rust replacement (trajectory JSONL serialization): measured ROI and the zero-call-site caveat

**Status:** Accepted
**Date:** 2026-09-01
**Related:** `rust/crates/hexagents-trajectory/`, `rust/crates/hexagents-core/src/native.rs`,
`hexagents/infrastructure/adapters/secondary/trajectory/{rust.py,jsonl.py,factory.py}`,
`docs/adr/0001-hex11-rust-arg-coercion-roi.md`

## Context

`docs/adr/0001` flagged Trajectories as a legitimate next candidate (favorable
call frequency vs. arg coercion — once per completed turn, not per tool
call), but set an explicit prerequisite: **measure real payload sizes on a
long-running session before implementing**, to avoid repeating HEX-11's
implement-then-measure-then-fix cycle.

That prerequisite was not met. Research at the start of this ticket found
`JsonlTrajectoryStore.append()` has **zero production call sites**:
`infrastructure/bootstrap/factory.py::build_agent_loop()` never passes
`save_trajectory=` when constructing `AgentLoop`, so `AgentLoop._record()`
always short-circuits (`if self._save_trajectory is None: return`) in the
real running app. No real `.jsonl` trajectory file exists anywhere in this
repo. This is structurally the same situation ADR 0001 already documented
for Routing (*"Nothing to optimize while nothing calls it"*).

**The user was offered the choice to wire `save_trajectory=` into production
and measure a real session first (the ADR-0001-compliant path), and
explicitly chose to skip it and do the straightforward Python→Rust port
now regardless.** This ADR follows that instruction, but — per the same
user's standing rule that measurement and honesty come before a flattering
ratio — reports the consequence of skipping it plainly, in the assessment
below, rather than silently dropping the caveat.

## Design note: this ticket did not repeat HEX-11's naive-attempt cycle

Unlike HEX-11 (which discovered the `pythonize` FFI-overhead problem after
shipping a naive attempt), this ticket applied ADR 0001's criterion *before*
writing code: a trajectory's write-direction payload is always a flat list
of typed `(from, value)` string pairs — not an arbitrary schema tree — so
the pyo3 binding was written as a **thin, typed delegation**
(`Vec<(String, String)>` extraction, no dict-walking) from the start. The
read direction (Rust → Python dict) reused the `native.rs` hand-built
`PyDict` pattern immediately, for the same reason `coerce_args` needed it.
There was no "naive attempt" row to measure and discard this time — the
process ADR 0001 asked for worked.

One genuine, non-obvious implementation finding: Python's `json.dumps`
default separators (`", "` / `": "`) differ from `serde_json`'s default
compact output (no spaces). Semantically identical JSON, but not
byte-for-byte identical — and this ticket requires byte-for-byte
compatibility with existing/future JSONL files. Fixed with a ~15-line custom
`serde_json::ser::Formatter` (`PyCompatFormatter`), verified against a
literal string captured from real `python3 -c "import json; print(json.dumps(...))"`
output in both the Rust unit tests and the Python parity tests.

## Measured ROI

Corpus: **synthetic**, not measured production traffic — no real trajectory
data exists to measure. Modeled on `TrajectoryFormatter`/
`test_trajectory_formatter.py`'s fixtures: a system entry (prompt + tool
defs), a human turn, two assistant turns each with a `<think>`/`<toolcall>`/
`<toolresult>` block, and a final plain-text answer. One formatted record is
**1,073 bytes** — noticeably larger than HEX-11's arg-coercion payload
(tens of bytes), as ADR 0001 predicted for this candidate.

Measured on this dev machine (`scripts/bench_trajectory.py` for end-to-end
Python/Rust-via-FFI numbers, `cargo bench -p hexagents-trajectory` via
criterion for the pure-Rust-no-FFI reference):

| Implementation | ops/sec | Ratio vs. Python |
|---|---|---|
| Pure Python (`_format_trajectory_python`, `json.dumps`) | ~102,000 | 1× (reference) |
| Rust via pyo3, typed FFI (adopted, `format_trajectory_rust`) | ~335,000 | **~3.27×** |
| *(reference only)* pure Rust `format_trajectory_line`, no FFI (`cargo bench`) | ~618,000 (1.62µs/call) | — |
| *(reference only)* pure Rust `parse_trajectory_line`, no FFI (`cargo bench`) | ~515,000 (1.94µs/call) | — |

The FFI crossing still costs real throughput on the write direction
(~618,000 pure-Rust vs. ~335,000 through the Python boundary — roughly 46%
of the pure-Rust throughput lost to marshaling/GIL crossing), but the
larger, more computation-adjacent payload (text/JSON assembly of a
multi-entry structure, not a handful of scalar coercions) amortizes that
cost far better than HEX-11's tiny schema payload did: 3.27× here vs. 1.7×
there.

## Decision

Ship the Rust replacement as the default
(`build_trajectory_store(prefer_rust=True)`), with the explicit/logged
fallback and byte-for-byte-verified parity/compat tests already in place.
Keep it in the codebase — the code is correct, tested, and measurably
faster in isolation. Do **not** count this as evidence that the roadmap's
process worked end-to-end, per the assessment below.

## Honest ROI assessment — do not soften this

The ratio (3.27×) is real, reproducible, and better than HEX-11's. It is
also, today, multiplied by zero.

**Le ratio mesuré (3.27×, meilleur que le 1.7× de HEX-11) ne change rien à
l'utilité réelle de ce remplacement tant que `JsonlTrajectoryStore.append()`
n'a aucun site d'appel en production : 3.27× d'un flux qui vaut zéro appel
par session, c'est zéro gain réel — exactement le même verdict que Routing
dans l'ADR 0001, à la différence près que cette fois la mesure a été sautée
délibérément plutôt que découverte en cours de route.**

This is not a claim that the work was wasted — the crate is correct, the
byte-for-byte compatibility guarantee is real and tested, and if/when
`save_trajectory=` is ever wired into `build_agent_loop()`, this
replacement will already be measured and ready rather than needing another
implement-then-measure cycle. But it is not, today, delivering the
perceptible latency or throughput improvement the ratio alone suggests —
the same trap ADR 0001 warned readers not to round up.

## Re-evaluation

The payload×frequency×computation criterion from ADR 0001, applied to this
candidate with real numbers now available:

| Factor | Value | Note |
|---|---|---|
| Payload | 1,073 bytes/record (synthetic) | Larger than arg coercion; still just text assembly, not numeric computation |
| Call frequency (production, today) | **0** | Confirmed by direct code trace, not assumption — `build_agent_loop()` never passes `save_trajectory=` |
| Real computation? | No — JSON string assembly | Same category as arg coercion, just a bigger payload |
| Measured ratio | 3.27× (FFI), up to ~6.05× (no-FFI reference) | Real, reproducible on this machine |
| **Net effect in production today** | **0** | Ratio × zero calls = zero |

If `save_trajectory=` is wired into `build_agent_loop()` in a future
ticket, this replacement is already in place and already measured — but
that wiring, and a real-session payload/frequency measurement, is a
**separate, still-open prerequisite**, not something this ticket completed
by proxy.
