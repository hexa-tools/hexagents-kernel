<p>

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Docs](https://img.shields.io/badge/docs-getting--started-blue.svg)](docs/)
[![Tests](https://img.shields.io/badge/tests-1769_passed-brightgreen.svg)]()
[![codecov](https://codecov.io/gh/hexa-tools/hexagents/branch/main/graph/badge.svg?token=N9SC3C8NYU)](https://codecov.io/gh/hexa-tools/hexagents)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

</p>

<p>
  <img
    src="assets/hexagents.svg"
    alt="HexAgents"
    width="800"
  />
</p>

---

## Quick Install

> **Linux, macOS (Python 3.12+).** The installer uses [`pipx`](https://pipx.pypa.io)
> (isolated install, no compiled binary); it installs Python itself only if you
> haven't — it never does. WSL2 support is untested and not claimed.

The fastest way to get the CLI (`hexa`):

```bash
curl -fsSL https://install.hexagents.dev/install.sh | bash
```

Then verify:

```bash
hexa --version
```

> **Prefer not to pipe straight into `bash`?** Fetch the script, read it, then
> run it — `curl | bash` executes arbitrary code sight-unseen:

```bash
curl -fsSL https://install.hexagents.dev/install.sh -o hexagents-install.sh
less hexagents-install.sh   # read it first
bash hexagents-install.sh
```

**Verify the script integrity** (a `.sha256` is published next to the script at
every release):

```bash
curl -fsSL https://install.hexagents.dev/install.sh.sha256 | sha256sum -c -
```

### Alternative installation methods

**Directly with `pipx`:**

```bash
pipx install hexagents-cli
hexa --version
```

**With `pip`:**

```bash
pip install hexagents-cli
```

**Homebrew:** a formula isn't available yet — it's a documented future option, not
on the roadmap for now.


