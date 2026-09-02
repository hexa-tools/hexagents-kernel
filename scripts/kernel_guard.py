#!/usr/bin/env python3
"""
kernel_guard.py — deterministic architecture guard for HexAgents Kernel.

This guard is intentionally kernel-specific.

It protects the boundaries between:
    kernel domain
    kernel application/services
    architecture-specific code
    device adapters
    user space

The kernel must never depend on:
    LLMs, MCP, agents, GUI frameworks, application code, or cloud SDKs.

The guard is designed to run as a Claude Code PostToolUse hook after
Write/Edit/MultiEdit operations.

Rules:
    K1  — Rust territory: no Python source under rust/
    K2  — Kernel purity: no LLM/MCP/GUI/application dependencies
    K3  — Architecture boundary: arch-specific code stays under arch/
    K4  — DDD: bounded contexts communicate through public contracts
    K5  — Domain purity: domain modules do not depend on adapters/arch
    K6  — Unsafe: every unsafe block requires a SAFETY explanation
    K7  — No panic in domain/application code for expected failures
    K8  — Typed errors: expected failures use Result/Option
    K9  — No secrets
    K10 — No TODO/XXX debt in production Rust
    K11 — File size guard
    K12 — No generated/build artefacts in source
    K13 — Python reference model never becomes a Rust dependency
    K14 — User-space concepts never enter the kernel
    K15 — Formatting / Cargo validation is delegated to CI, not this hook

Important:
    This script must never run git commands.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Claude Code event
# ---------------------------------------------------------------------------

data = json.load(sys.stdin)
tool_name = data.get("tool_name", "")
tool_input = data.get("tool_input", {})

if tool_name not in ("Write", "Edit", "MultiEdit"):
    sys.exit(0)

file_path = tool_input.get("file_path", "")
if not file_path:
    sys.exit(0)

path = Path(file_path)
content = tool_input.get("content", tool_input.get("new_content", ""))
str_path = str(path).replace("\\", "/")

if not content:
    # Some editor events do not contain the complete file content.
    # Do not invent content; let cargo/rustfmt/CI validate it later.
    sys.exit(0)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def block(rule: str, reason: str) -> None:
    print(
        json.dumps(
            {
                "decision": "block",
                "reason": f"[kernel_guard] ❌ {rule}\n{reason}",
            }
        )
    )
    sys.exit(2)


def warn(rule: str, reason: str) -> None:
    print(
        json.dumps(
            {
                "decision": "warn",
                "reason": f"[kernel_guard] ⚠️ {rule}\n{reason}",
            }
        )
    )


def contains_any(text: str, patterns: tuple[str, ...]) -> str | None:
    lowered = text.lower()
    for pattern in patterns:
        if pattern.lower() in lowered:
            return pattern
    return None


def is_test_path(value: str) -> bool:
    return (
        "/tests/" in f"/{value}/"
        or value.startswith("tests/")
        or "/test_" in value
        or value.endswith("_test.rs")
    )


def is_production_rust(value: str) -> bool:
    return value.endswith(".rs") and not is_test_path(value)


def has_safety_explanation(text: str, unsafe_line: int) -> bool:
    """Require a nearby // SAFETY: explanation for each unsafe block."""
    lines = text.splitlines()
    start = max(0, unsafe_line - 5)
    end = min(len(lines), unsafe_line + 1)
    window = "\n".join(lines[start:end])
    return bool(re.search(r"//\s*SAFETY\s*:", window, re.IGNORECASE))


# ---------------------------------------------------------------------------
# Scope
# ---------------------------------------------------------------------------

is_rust = str_path.startswith("rust/") or "/rust/" in str_path
is_python = path.suffix == ".py"
is_rust_source = is_rust and path.suffix == ".rs"
is_cargo_manifest = is_rust and path.name == "Cargo.toml"


# ---------------------------------------------------------------------------
# K1 — Rust territory: no Python source under rust/
# ---------------------------------------------------------------------------

if is_rust and is_python:
    block(
        "K1 — RUST TERRITORY",
        f"'{path}' is a Python file inside rust/.\n"
        "The kernel implementation is Rust-only.\n"
        "Python reference code belongs under python/reference/ and must never "
        "be a runtime dependency of the kernel.",
    )


# ---------------------------------------------------------------------------
# K2/K14 — Kernel purity: user-space dependencies forbidden
# ---------------------------------------------------------------------------

USER_SPACE_FORBIDDEN = (
    "mcp",
    "anthropic",
    "openai",
    "ollama",
    "langchain",
    "langgraph",
    "claude",
    "qwen",
    "llm",
    "prompt",
    "agent_runtime",
    "agent-runtime",
    "hexagents_agent",
    "hexagents-agent",
    "flutter",
    "react",
    "tauri",
    "electron",
    "fastapi",
    "axum",
    "actix_web",
    "actix-web",
    "poem",
    "rocket",
    "reqwest",
    "tokio",
    "sqlx",
    "diesel",
    "stripe",
    "sendgrid",
)

# Terms such as "agent" and "prompt" are intentionally forbidden in kernel
# implementation source. They belong to user space.
if is_rust_source and not is_test_path(str_path):
    match = contains_any(content, USER_SPACE_FORBIDDEN)
    if match:
        block(
            "K2/K14 — USER-SPACE DEPENDENCY IN KERNEL",
            f"'{match}' detected in '{path}'.\n"
            "The kernel must not know about LLMs, MCP, agents, GUI, "
            "application frameworks, cloud SDKs, or user-space protocols.\n"
            "Move this concern to user space and cross the boundary through "
            "syscalls, IPC, VFS, devices, or another explicit kernel contract.",
        )


# ---------------------------------------------------------------------------
# K3 — Architecture boundary
# ---------------------------------------------------------------------------

ARCH_COMPONENTS = (
    "x86_64",
    "aarch64",
    "riscv64",
)

if is_rust_source:
    path_has_arch = any(f"/arch/{arch}/" in f"/{str_path}/" for arch in ARCH_COMPONENTS)

    if not path_has_arch:
        # Architecture-specific imports and cfgs must not leak into the domain.
        arch_patterns = (
            "target_arch = \"x86_64\"",
            "target_arch = \"aarch64\"",
            "target_arch = \"riscv64\"",
            "asm!(",
            "global_asm!(",
            "core::arch::x86_64",
            "core::arch::aarch64",
        )
        match = contains_any(content, arch_patterns)
        if match:
            block(
                "K3 — ARCHITECTURE BOUNDARY",
                f"'{match}' detected in '{path}'.\n"
                "Architecture-specific code must live under rust/arch/<arch>/.\n"
                "Keep the kernel domain architecture-independent.",
            )


# ---------------------------------------------------------------------------
# K4/K5 — DDD context boundaries
# ---------------------------------------------------------------------------

BOUNDED_CONTEXTS = (
    "kernel",
    "process",
    "scheduler",
    "memory",
    "capabilities",
    "syscall",
    "ipc",
    "vfs",
    "tty",
    "devices",
    "loader",
    "init",
)

PRIVATE_MODULE_IMPORTS = (
    "::domain::",
    "::application::",
    "::ports::",
    "::adapters::",
)

# Cross-context imports should use the crate's public API rather than reach
# into another bounded context's private implementation layers.
if is_rust_source:
    context_match = None
    current_context = None

    for context in BOUNDED_CONTEXTS:
        if f"/crates/{context}/" in f"/{str_path}/":
            current_context = context
            break

    if current_context:
        for context in BOUNDED_CONTEXTS:
            if context == current_context:
                continue
            import_patterns = (
                f"hexagents_{context}::domain::",
                f"hexagents_{context}::application::",
                f"hexagents_{context}::ports::",
                f"hexagents_{context}::adapters::",
            )
            context_match = contains_any(content, import_patterns)
            if context_match:
                break

        if context_match:
            block(
                "K4 — BOUNDED CONTEXT VIOLATION",
                f"'{context_match}' detected in '{path}'.\n"
                "A bounded context must not reach into another context's "
                "domain/application/ports/adapters internals.\n"
                "Expose an explicit public contract and depend on that contract.",
            )


# ---------------------------------------------------------------------------
# K5 — Domain purity
# ---------------------------------------------------------------------------

DOMAIN_MARKERS = ("/domain/", "/domain.rs")

if is_rust_source and any(marker in f"/{str_path}" for marker in DOMAIN_MARKERS):
    forbidden_domain_patterns = (
        "crate::adapters",
        "crate::arch",
        "crate::devices::drivers",
        "::adapters::",
        "hexagents_",
        "std::net",
        "std::fs",
    )
    match = contains_any(content, forbidden_domain_patterns)
    if match:
        block(
            "K5 — DOMAIN PURITY",
            f"'{match}' detected in '{path}'.\n"
            "Domain code must express kernel invariants, not hardware or "
            "infrastructure details.\n"
            "Move the dependency to a port/application boundary or adapter.",
        )


# ---------------------------------------------------------------------------
# K6 — Unsafe requires a SAFETY explanation
# ---------------------------------------------------------------------------

if is_rust_source and "unsafe" in content:
    lines = content.splitlines()
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if (
            "unsafe {" in stripped
            or stripped.startswith("unsafe fn ")
            or stripped.startswith("unsafe trait ")
            or stripped.startswith("unsafe impl ")
        ):
            if not has_safety_explanation(content, index):
                block(
                    "K6 — UNSAFE WITHOUT SAFETY CONTRACT",
                    f"Line {index} in '{path}' introduces unsafe code without "
                    "a nearby '// SAFETY:' explanation.\n"
                    "Document why the operation is safe, which invariant "
                    "establishes safety, and what prevents callers from "
                    "violating it.",
                )


# ---------------------------------------------------------------------------
# K7 — No panic in domain/application code
# ---------------------------------------------------------------------------

if is_rust_source and (
    "/domain/" in f"/{str_path}" or "/application/" in f"/{str_path}"
):
    panic_patterns = (
        "panic!(",
        "unreachable!(",
        "todo!(",
        "unimplemented!(",
    )
    match = contains_any(content, panic_patterns)
    if match:
        block(
            "K7 — PANIC IN DOMAIN/APPLICATION",
            f"'{match}' detected in '{path}'.\n"
            "Expected failures must be represented explicitly with Result "
            "or Option.\n"
            "Reserve panic/unreachable for genuinely impossible kernel "
            "invariants and keep those assertions at the appropriate boundary.",
        )


# ---------------------------------------------------------------------------
# K8 — Typed error discipline
# ---------------------------------------------------------------------------

if is_rust_source and "/domain/" in f"/{str_path}":
    weak_error_patterns = (
        "Result<T, String>",
        "Result<(), String>",
        "Result<T, Box<dyn Error",
        "Box<dyn std::error::Error",
    )
    match = contains_any(content, weak_error_patterns)
    if match:
        block(
            "K8 — UNTYPED DOMAIN ERROR",
            f"'{match}' detected in '{path}'.\n"
            "Domain errors must be explicit types owned by their bounded "
            "context. Prefer Result<T, ProcessError>, MemoryError, "
            "CapabilityError, etc.",
        )


# ---------------------------------------------------------------------------
# K9 — Secrets
# ---------------------------------------------------------------------------

SECRET_PATTERNS = (
    "sk-ant-",
    "AKIA",
    "ghp_",
    "github_pat_",
    "xoxb-",
    "xoxp-",
    "AIza",
    "-----BEGIN RSA PRIVATE KEY-----",
    "-----BEGIN EC PRIVATE KEY-----",
    "-----BEGIN OPENSSH PRIVATE KEY-----",
    "password = \"",
    "password=\"",
    "api_key = \"",
    "api_key=\"",
    "secret_key = \"",
    "secret_key=\"",
    "token = \"",
    "token=\"",
)

if is_rust_source and not is_test_path(str_path):
    match = contains_any(content, SECRET_PATTERNS)
    if match:
        block(
            "K9 — POTENTIAL SECRET",
            f"Pattern '{match}' detected in '{path}'.\n"
            "Secrets must never be committed to source code.",
        )


# ---------------------------------------------------------------------------
# K10 — No TODO/XXX debt in production kernel code
# ---------------------------------------------------------------------------

if is_rust_source and not is_test_path(str_path):
    match = contains_any(content, ("TODO", "FIXME", "XXX"))
    if match:
        block(
            "K10 — UNTRACKED TECHNICAL DEBT",
            f"'{match}' detected in '{path}'.\n"
            "Architecture work should be tracked as a ticket/ADR instead "
            "of leaving TODO/FIXME/XXX markers in production kernel code.",
        )


# ---------------------------------------------------------------------------
# K11 — File size
# ---------------------------------------------------------------------------

MAX_RUST_LINES = 500
HARD_CAP_LINES = 800

if is_rust_source:
    line_count = len(content.splitlines())

    if line_count > HARD_CAP_LINES:
        block(
            "K11 — GOD FILE",
            f"'{path}' has {line_count} lines (hard cap {HARD_CAP_LINES}).\n"
            "Split the module along a domain, contract, or adapter boundary.",
        )

    if line_count > MAX_RUST_LINES:
        block(
            "K11 — FILE TOO LARGE",
            f"'{path}' has {line_count} lines (limit {MAX_RUST_LINES}).\n"
            "Prefer smaller modules with explicit responsibilities.",
        )


# ---------------------------------------------------------------------------
# K12 — Build/generated artefacts must never be source-controlled here
# ---------------------------------------------------------------------------

FORBIDDEN_PATH_PARTS = (
    "/target/",
    "/node_modules/",
    "/build/",
    "/dist/",
    "/coverage/",
    "/__pycache__/",
)

if any(part in f"/{str_path}" for part in FORBIDDEN_PATH_PARTS):
    block(
        "K12 — GENERATED ARTEFACT IN KERNEL REPOSITORY",
        f"'{path}' is inside a generated/build directory.\n"
        "Do not modify generated artefacts as source.",
    )


# ---------------------------------------------------------------------------
# K13 — Python reference model cannot leak into Rust
# ---------------------------------------------------------------------------

if is_rust_source:
    reference_patterns = (
        "python/reference",
        "pyo3",
        "PyO3",
        "python3_sys",
        "cpython",
    )
    match = contains_any(content, reference_patterns)
    if match:
        block(
            "K13 — PYTHON REFERENCE LEAK",
            f"'{match}' detected in '{path}'.\n"
            "The Python reference model is a test oracle only. "
            "The kernel must remain independently buildable and runnable "
            "without Python.",
        )


# ---------------------------------------------------------------------------
# Cargo manifests — lightweight dependency policy
# ---------------------------------------------------------------------------

if is_cargo_manifest:
    forbidden_crates = (
        "anthropic",
        "openai",
        "ollama",
        "langchain",
        "langgraph",
        "reqwest",
        "axum",
        "actix-web",
        "rocket",
        "poem",
        "sqlx",
        "diesel",
        "pyo3",
        "flutter",
        "tauri",
        "electron",
    )

    match = contains_any(content, forbidden_crates)
    if match:
        block(
            "K2/K13 — FORBIDDEN CARGO DEPENDENCY",
            f"Dependency '{match}' detected in '{path}'.\n"
            "The kernel workspace must not depend on user-space, cloud, "
            "GUI, LLM, web-framework, database, or Python-runtime crates.",
        )


# ---------------------------------------------------------------------------
# Informational warnings
# ---------------------------------------------------------------------------

if is_rust_source and "unsafe" in content and "/arch/" not in f"/{str_path}":
    warn(
        "K6 — LOW-LEVEL CODE REVIEW",
        f"'{path}' contains unsafe code outside rust/arch/.\n"
        "This may be legitimate, but it should have an explicit safety "
        "contract and receive focused review.",
    )


# ---------------------------------------------------------------------------
# All checks passed
# ---------------------------------------------------------------------------

print(json.dumps({"decision": "approve"}))
sys.exit(0)
