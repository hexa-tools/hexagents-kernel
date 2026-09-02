# Phase 14 — Noyau Agentique (OS)

> **Rôle de ce fichier** : Ce fichier est le premier de la **Phase 14 — Noyau Agentique**. Il définit la sous-phase **Scheduler**, qui est le cœur de la couche OS. Le scheduler est responsable de la planification de l'exécution des agents, comme un noyau Unix planifie des processus.
>
> **Structure** : Chaque ticket est décrit avec un rôle détaillé. Les tickets sont ordonnés logiquement (Python d'abord, Rust ensuite, puis les extensions). Le fallback pur-Python est obligatoire pour chaque brique Rust.
>
> **Prochaine étape** : Une fois cette sous-phase terminée, on passera à la **Sous-phase 14.2 — Policy Engine**.
>
> **Dépendances** : Cette sous-phase ne dépend d'aucune autre sous-phase de la Phase 14. Elle est la fondation.


# OS-002 — Domain Error Architecture

## Goal

Mettre en place le système de gestion des erreurs transversal de HexOS afin que les bounded contexts puissent représenter leurs failures de manière :

- typée
- explicite
- déterministe
- testable
- composable
- indépendante de l'infrastructure
- compatible avec les frontières Domain / Application / Ports / Adapters

Cette task définit le **contrat d'erreur du système** avant l'implémentation des premiers bounded contexts.

---

# 1. Architectural Principles

Les erreurs sont des éléments du contrat architectural.

```text
Domain invariant
      ↓
Domain Error
      ↓
Application Error
      ↓
Port / Adapter Error
      ↓
System / Syscall Error
      ↓
User-space representation



# OS-001 — Kernel Architecture Bootstrap

## Goal

Créer le squelette architectural initial de HexOS afin que tous les futurs composants du kernel puissent être développés avec une séparation claire entre :

* Domain
* Application
* Ports
* Adapters
* Infrastructure
* Architecture matérielle
* Tests
* Reference model Python

L'objectif n'est **pas** encore de rendre le kernel fonctionnel.

L'objectif est de poser les frontières qui permettront d'éviter un kernel monolithique au fur et à mesure des 700+ tickets.

---

# 1. Architectural Principles

HexOS suit les principes suivants :

```text
Domain
   ↓
Application
   ↓
Ports
   ↓
Adapters
   ↓
Infrastructure / Hardware
```

Les dépendances doivent pointer vers l'intérieur.

```text
┌──────────────────────────────────────────────┐
│              Infrastructure                  │
│                                              │
│   Hardware / Drivers / QEMU / Architecture  │
│                    ↓                         │
├──────────────────────────────────────────────┤
│                 Adapters                     │
│                    ↓                         │
├──────────────────────────────────────────────┤
│                   Ports                      │
│                    ↓                         │
├──────────────────────────────────────────────┤
│                Application                   │
│                    ↓                         │
├──────────────────────────────────────────────┤
│                  Domain                      │
│                                              │
│              System Invariants               │
└──────────────────────────────────────────────┘
```

**Important :**

L'architecture hexagonale est un **principe de dépendance**, pas une obligation de créer artificiellement `domain/application/ports/adapters` dans chaque petit module.

---

# 2. Top-Level Repository Structure

Créer :

```text
hexagents/
│
├── AGENTS.md
├── ARCHITECTURE.md
├── README.md
├── TICKETS.md
├── TICKETS-OS.md
│
├── rust/
│   ├── Cargo.toml
│   │
│   ├── crates/
│   │   │
│   │   ├── kernel/
│   │   ├── process/
│   │   ├── scheduler/
│   │   ├── memory/
│   │   ├── capabilities/
│   │   ├── syscall/
│   │   ├── ipc/
│   │   ├── vfs/
│   │   ├── tty/
│   │   ├── devices/
│   │   ├── loader/
│   │   ├── init/
│   │   └── agent-runtime/
│   │
│   ├── arch/
│   │   └── x86_64/
│   │
│   ├── tests/
│   │
│   └── linker/
│
├── python/
│   ├── reference/
│   │   ├── process/
│   │   ├── scheduler/
│   │   ├── memory/
│   │   ├── capabilities/
│   │   ├── syscall/
│   │   ├── ipc/
│   │   ├── vfs/
│   │   ├── tty/
│   │   ├── devices/
│   │   └── runtime/
│   │
│   └── tests/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── cross_reference/
│   ├── security/
│   ├── stress/
│   ├── fuzz/
│   └── qemu/
│
├── images/
│   ├── debug/
│   └── release/
│
├── scripts/
│   ├── build/
│   ├── test/
│   ├── qemu/
│   └── benchmark/
│
└── docs/
    ├── architecture/
    ├── kernel/
    ├── hardware/
    ├── security/
    ├── testing/
    └── reference-model/
```

---

# 3. Rust Kernel Structure

Chaque bounded context principal possède son propre crate.

```text
rust/crates/
│
├── kernel/
│
├── process/
├── scheduler/
├── memory/
├── capabilities/
├── syscall/
├── ipc/
├── vfs/
├── tty/
├── devices/
├── loader/
├── init/
└── agent-runtime/
```

Ces crates ne sont pas toutes forcément identiques architecturalement.

---

# 4. Domain-Driven Kernel

Les bounded contexts principaux sont :

```text
Process
Scheduler
Memory
Capabilities
Syscall
IPC
VFS
TTY
Devices
Loader
Init
Agent Runtime
```

Chaque contexte possède ses propres invariants.

---

## Process Context

```text
process/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   └── process.rs
│   │   │
│   │   ├── value_objects/
│   │   │   ├── pid.rs
│   │   │   ├── process_state.rs
│   │   │   └── process_priority.rs
│   │   │
│   │   ├── services/
│   │   │   └── lifecycle.rs
│   │   │
│   │   └── errors.rs
│   │
│   ├── application/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── services/
│   │
│   ├── ports/
│   │   ├── process_repository.rs
│   │   ├── process_spawner.rs
│   │   └── process_clock.rs
│   │
│   ├── adapters/
│   │   └── kernel/
│   │
│   └── lib.rs
│
└── tests/
    ├── domain/
    ├── application/
    └── integration/
```

---

# 5. Scheduler Context

```text
scheduler/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── scheduling_entity.rs
│   │   │   └── run_queue.rs
│   │   │
│   │   ├── value_objects/
│   │   │   ├── priority.rs
│   │   │   ├── time_slice.rs
│   │   │   └── scheduling_state.rs
│   │   │
│   │   ├── services/
│   │   │   ├── scheduling_policy.rs
│   │   │   └── fairness.rs
│   │   │
│   │   └── errors.rs
│   │
│   ├── application/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── services/
│   │
│   ├── ports/
│   │   ├── clock.rs
│   │   ├── cpu.rs
│   │   └── context_switch.rs
│   │
│   ├── adapters/
│   │   └── kernel/
│   │
│   └── lib.rs
│
└── tests/
```

Le scheduler ne doit pas connaître directement :

```text
x86_64
APIC
PIT
HPET
QEMU
```

Ces détails arrivent via des ports/adapters.

---

# 6. Memory Context

```text
memory/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── address_space.rs
│   │   │   ├── page.rs
│   │   │   └── frame.rs
│   │   │
│   │   ├── value_objects/
│   │   │   ├── virtual_address.rs
│   │   │   ├── physical_address.rs
│   │   │   ├── page_permissions.rs
│   │   │   └── memory_region.rs
│   │   │
│   │   ├── services/
│   │   │   ├── page_mapper.rs
│   │   │   └── allocation.rs
│   │   │
│   │   └── errors.rs
│   │
│   ├── application/
│   │
│   ├── ports/
│   │   ├── frame_allocator.rs
│   │   ├── page_table.rs
│   │   └── memory_backend.rs
│   │
│   ├── adapters/
│   │   └── kernel/
│   │
│   └── lib.rs
│
└── tests/
```

---

# 7. Capability Context

```text
capabilities/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── capability.rs
│   │   │   └── capability_set.rs
│   │   │
│   │   ├── value_objects/
│   │   │   ├── capability_id.rs
│   │   │   ├── capability_type.rs
│   │   │   ├── capability_scope.rs
│   │   │   └── expiration.rs
│   │   │
│   │   ├── services/
│   │   │   ├── evaluator.rs
│   │   │   ├── delegation.rs
│   │   │   └── revocation.rs
│   │   │
│   │   └── errors.rs
│   │
│   ├── application/
│   │
│   ├── ports/
│   │   ├── capability_store.rs
│   │   └── policy_engine.rs
│   │
│   ├── adapters/
│   │
│   └── lib.rs
│
└── tests/
```

---

# 8. IPC Context

```text
ipc/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── channel.rs
│   │   │   ├── message_queue.rs
│   │   │   └── shared_memory_region.rs
│   │   │
│   │   ├── value_objects/
│   │   │   ├── channel_id.rs
│   │   │   └── message_id.rs
│   │   │
│   │   ├── services/
│   │   │   ├── routing.rs
│   │   │   └── authorization.rs
│   │   │
│   │   └── errors.rs
│   │
│   ├── application/
│   │
│   ├── ports/
│   │   ├── scheduler.rs
│   │   └── memory.rs
│   │
│   ├── adapters/
│   │
│   └── lib.rs
│
└── tests/
```

---

# 9. VFS Context

```text
vfs/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── inode.rs
│   │   │   ├── directory.rs
│   │   │   ├── file.rs
│   │   │   └── mount.rs
│   │   │
│   │   ├── value_objects/
│   │   │   ├── path.rs
│   │   │   ├── file_mode.rs
│   │   │   ├── inode_id.rs
│   │   │   └── file_offset.rs
│   │   │
│   │   ├── services/
│   │   │   ├── path_resolution.rs
│   │   │   └── permission.rs
│   │   │
│   │   └── errors.rs
│   │
│   ├── application/
│   │
│   ├── ports/
│   │   ├── filesystem.rs
│   │   ├── block_device.rs
│   │   └── mount.rs
│   │
│   ├── adapters/
│   │   ├── simplefs/
│   │   └── ramfs/
│   │
│   └── lib.rs
│
└── tests/
```

---

# 10. TTY Context

```text
tty/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── tty.rs
│   │   │   ├── session.rs
│   │   │   └── process_group.rs
│   │   │
│   │   ├── value_objects/
│   │   │   ├── tty_id.rs
│   │   │   └── terminal_mode.rs
│   │   │
│   │   ├── services/
│   │   │   ├── line_discipline.rs
│   │   │   └── terminal_control.rs
│   │   │
│   │   └── errors.rs
│   │
│   ├── application/
│   │
│   ├── ports/
│   │   ├── console.rs
│   │   └── input.rs
│   │
│   ├── adapters/
│   │
│   └── lib.rs
│
└── tests/
```

---

# 11. Device Context

Le contexte Device est particulier.

Il doit être fortement orienté ports/adapters car son rôle est précisément de faire le pont entre le kernel et le hardware.

```text
devices/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── device.rs
│   │   │   └── device_driver.rs
│   │   │
│   │   ├── value_objects/
│   │   │   ├── device_id.rs
│   │   │   ├── device_type.rs
│   │   │   └── device_state.rs
│   │   │
│   │   └── errors.rs
│   │
│   ├── application/
│   │
│   ├── ports/
│   │   ├── device.rs
│   │   ├── interrupt.rs
│   │   ├── timer.rs
│   │   ├── block_device.rs
│   │   ├── network_device.rs
│   │   └── console.rs
│   │
│   ├── adapters/
│   │   ├── qemu/
│   │   └── hardware/
│   │
│   └── lib.rs
│
└── tests/
```

---

# 12. Syscall Context

Le syscall layer est principalement une **application/interface boundary**.

```text
syscall/
├── src/
│   ├── domain/
│   │   ├── syscall.rs
│   │   ├── syscall_number.rs
│   │   └── syscall_error.rs
│   │
│   ├── application/
│   │   ├── dispatcher.rs
│   │   └── handlers/
│   │
│   ├── ports/
│   │   ├── process.rs
│   │   ├── memory.rs
│   │   ├── filesystem.rs
│   │   └── ipc.rs
│   │
│   ├── adapters/
│   │   └── kernel/
│   │
│   └── lib.rs
│
└── tests/
```

---

# 13. Loader Context

```text
loader/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── executable.rs
│   │   │   └── segment.rs
│   │   │
│   │   ├── value_objects/
│   │   │   ├── entry_point.rs
│   │   │   └── segment_permissions.rs
│   │   │
│   │   └── errors.rs
│   │
│   ├── application/
│   │   ├── load_program.rs
│   │   └── exec.rs
│   │
│   ├── ports/
│   │   ├── executable_reader.rs
│   │   └── address_space.rs
│   │
│   ├── adapters/
│   │   └── elf/
│   │
│   └── lib.rs
│
└── tests/
```

---

# 14. Init Context

```text
init/
├── src/
│   ├── domain/
│   │   ├── service.rs
│   │   ├── service_state.rs
│   │   ├── dependency.rs
│   │   └── restart_policy.rs
│   │
│   ├── application/
│   │   ├── bootstrap.rs
│   │   ├── start_service.rs
│   │   └── shutdown.rs
│   │
│   ├── ports/
│   │   ├── process.rs
│   │   └── filesystem.rs
│   │
│   └── main.rs
│
└── tests/
```

---

# 15. Agent Runtime Context

Le runtime agent est entièrement user-space.

Il ne doit jamais devenir une dépendance du kernel.

```text
agent-runtime/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── agent.rs
│   │   │   ├── task.rs
│   │   │   └── execution.rs
│   │   │
│   │   ├── value_objects/
│   │   │   ├── agent_id.rs
│   │   │   ├── task_id.rs
│   │   │   └── agent_state.rs
│   │   │
│   │   ├── services/
│   │   │   ├── lifecycle.rs
│   │   │   ├── supervision.rs
│   │   │   └── scheduling.rs
│   │   │
│   │   └── errors.rs
│   │
│   ├── application/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── services/
│   │
│   ├── ports/
│   │   ├── process.rs
│   │   ├── filesystem.rs
│   │   ├── ipc.rs
│   │   ├── model.rs
│   │   └── tool.rs
│   │
│   ├── adapters/
│   │   ├── model/
│   │   ├── mcp/
│   │   └── tools/
│   │
│   └── main.rs
│
└── tests/
```

**Note :**

`agent-runtime` est dans le workspace Rust, mais ce n'est **pas du kernel Rust**.

Il s'agit d'un programme user-space compilé avec Rust.

---

# 16. Kernel Composition Root

Le crate `kernel` assemble les bounded contexts.

```text
kernel/
├── src/
│   ├── bootstrap/
│   │   ├── boot.rs
│   │   ├── initialization.rs
│   │   └── shutdown.rs
│   │
│   ├── composition/
│   │   ├── process.rs
│   │   ├── memory.rs
│   │   ├── scheduler.rs
│   │   ├── devices.rs
│   │   └── filesystem.rs
│   │
│   ├── kernel.rs
│   ├── entry.rs
│   ├── panic.rs
│   └── lib.rs
│
└── tests/
```

Le kernel devient donc le **composition root** du système.

Il assemble les implementations concrètes des ports.

---

# 17. Architecture-Specific Code

Tout ce qui dépend du CPU doit être isolé.

```text
rust/arch/
└── x86_64/
    ├── boot/
    │   ├── entry.rs
    │   └── multiboot.rs
    │
    ├── cpu/
    │   ├── registers.rs
    │   ├── control.rs
    │   └── instructions.rs
    │
    ├── interrupts/
    │   ├── idt.rs
    │   ├── handlers.rs
    │   └── context.rs
    │
    ├── memory/
    │   ├── page_tables.rs
    │   └── address.rs
    │
    ├── scheduler/
    │   └── context_switch.rs
    │
    ├── devices/
    │
    └── mod.rs
```

---

# 18. Architecture Boundary

Le reste du kernel ne doit pas dépendre directement de :

```text
x86_64 instructions
CR3
CR2
APIC
IDT
GDT
I/O ports
MMIO addresses
```

Il doit utiliser des abstractions.

```text
Scheduler
    ↓
ContextSwitch trait
    ↓
x86_64 implementation
```

ou :

```text
Memory
    ↓
PageTable trait
    ↓
x86_64 page table implementation
```

---

# 19. Python Reference Architecture

Le modèle Python reproduit les comportements du système mais pas les détails hardware.

```text
python/reference/
│
├── process/
│   ├── domain/
│   ├── application/
│   └── ports/
│
├── scheduler/
│   ├── domain/
│   ├── application/
│   └── ports/
│
├── memory/
├── capabilities/
├── syscall/
├── ipc/
├── vfs/
├── tty/
├── devices/
└── runtime/
```

Le Python reste :

```text
Reference Model
      ↓
Expected Behavior
```

et jamais :

```text
Python
  ↓
Kernel
```

---

# 20. Testing Architecture

Créer dès maintenant :

```text
tests/
├── unit/
│   ├── process/
│   ├── scheduler/
│   ├── memory/
│   ├── capabilities/
│   ├── ipc/
│   ├── vfs/
│   └── tty/
│
├── integration/
│   ├── process_scheduler/
│   ├── memory_process/
│   ├── ipc_scheduler/
│   ├── vfs_storage/
│   └── tty_devices/
│
├── cross_reference/
│   ├── process/
│   ├── scheduler/
│   ├── memory/
│   ├── capabilities/
│   ├── ipc/
│   └── vfs/
│
├── security/
│   ├── capabilities/
│   ├── isolation/
│   ├── memory/
│   └── ipc/
│
├── stress/
├── fuzz/
└── qemu/
```

---

# 21. Dependency Rules

Les règles suivantes doivent être documentées et respectées.

## Rule 1 — Domain independence

```text
domain
  X
  ├── hardware
  ├── QEMU
  ├── filesystem implementation
  └── architecture-specific code
```

Le domain ne dépend pas de détails externes.

---

## Rule 2 — Application depends inward

```text
application
    ↓
domain
```

mais jamais :

```text
domain
    ↓
application
```

---

## Rule 3 — Ports belong to the consumer

Le contexte qui a besoin d'une abstraction définit son port.

Exemple :

```text
scheduler
    ↓
ContextSwitch trait
```

plutôt que :

```text
generic/
└── ContextSwitch
```

sans propriétaire clair.

---

## Rule 4 — Adapters implement ports

```text
Port
 ↓
Adapter
```

Exemple :

```text
PageTable
   ↑
   │ implements
   │
x86_64::PageTable
```

---

## Rule 5 — Hardware stays at the edge

```text
Domain
   ↓
Application
   ↓
Port
   ↓
Adapter
   ↓
Hardware
```

---

## Rule 6 — Agent Runtime never becomes kernel dependency

```text
Kernel
   X
   ↓
Agent Runtime
```

mais :

```text
Agent Runtime
      ↓
   Syscalls
      ↓
    Kernel
```

---

# 22. Cargo Workspace

Créer un workspace Rust central.

Exemple :

```toml
[workspace]
resolver = "2"

members = [
    "crates/kernel",
    "crates/process",
    "crates/scheduler",
    "crates/memory",
    "crates/capabilities",
    "crates/syscall",
    "crates/ipc",
    "crates/vfs",
    "crates/tty",
    "crates/devices",
    "crates/loader",
    "crates/init",
    "crates/agent-runtime",
]
```

Les dépendances inter-crates doivent être explicites.

---

# 23. Initial Empty Crates

Créer les crates avec une structure compilable.

Chaque crate doit au minimum contenir :

```text
src/
└── lib.rs
```

ou, pour les programmes :

```text
src/
└── main.rs
```

Les modules DDD peuvent initialement être vides.

**Ne pas créer prématurément des abstractions artificielles.**

---

# 24. Architecture Documentation

Créer :

```text
docs/architecture/
├── bounded-contexts.md
├── dependency-rules.md
├── hexagonal-boundaries.md
├── kernel-user-space.md
├── hardware-boundary.md
└── testing-strategy.md
```

---

# 25. Architecture Diagram

Ajouter dans `ARCHITECTURE.md` :

```text
                         USER SPACE
┌──────────────────────────────────────────────────────────┐
│                                                          │
│ Shell   Coreutils   Init   Agent Runtime   Applications  │
│                           │                              │
│                           │ Syscalls / IPC              │
└───────────────────────────┼──────────────────────────────┘
                            │
════════════════════════════╪═══════════════════════════════
                            │
                         KERNEL
                            │
┌───────────────────────────▼──────────────────────────────┐
│                                                          │
│ Process │ Scheduler │ Memory │ Capabilities │ IPC        │
│                                                          │
│ VFS │ TTY │ Syscalls │ Loader │ Devices                 │
│                                                          │
└───────────────────────────┬──────────────────────────────┘
                            │
                         Ports
                            │
┌───────────────────────────▼──────────────────────────────┐
│                     ADAPTERS                             │
│                                                          │
│ x86_64 │ QEMU │ Block Device │ Timer │ Console │ Input  │
└───────────────────────────┬──────────────────────────────┘
                            │
                         HARDWARE
```

---

# 26. Bootstrap Test

Créer un premier test architectural.

### Test

Vérifier que :

```text
domain
```

ne peut pas importer :

```text
arch
hardware
qemu
```

et que les dépendances suivent les règles définies.

---

# 27. Bootstrap Build

Le repository doit permettre :

```bash
cargo check --workspace
```

avec succès.

Puis :

```bash
cargo test --workspace
```

avec succès.

Le kernel réel n'est pas encore bootable à ce stade.

---

# 28. Bootstrap Documentation

Documenter explicitement :

### DDD

```text
Bounded Context
    ↓
Domain Model
    ↓
Invariants
```

### Hexagonal Architecture

```text
Core
 ↓
Ports
 ↓
Adapters
 ↓
Infrastructure
```

### TDD

```text
Test
 ↓
Invariant
 ↓
Implementation
 ↓
Integration
 ↓
QEMU
```

### Reference Model

```text
Python
   ↓
Behavioral Specification
   ↓
Rust
```

---

# Definition of Done — OS-001

La task est terminée lorsque :

* [ ] Rust workspace créé
* [ ] kernel crate créé
* [ ] process crate créé
* [ ] scheduler crate créé
* [ ] memory crate créé
* [ ] capabilities crate créé
* [ ] syscall crate créé
* [ ] IPC crate créé
* [ ] VFS crate créé
* [ ] TTY crate créé
* [ ] devices crate créé
* [ ] loader crate créé
* [ ] init crate créé
* [ ] agent-runtime crate créé
* [ ] architecture x86_64 isolée
* [ ] Python reference structure créée
* [ ] test structure créée
* [ ] QEMU test directory créée
* [ ] architecture documentation créée
* [ ] bounded contexts documentés
* [ ] dependency rules documentées
* [ ] kernel/user-space boundary documentée
* [ ] hardware boundary documentée
* [ ] hexagonal boundaries documentées
* [ ] cargo check passe
* [ ] cargo test passe
* [ ] aucun code hardware dans le domain
* [ ] aucun code agent dans le kernel
* [ ] aucun couplage Python → kernel
* [ ] architecture validée avant implémentation fonctionnelle

---

# Final Architecture

```text
hexagents/
│
├── rust/
│   │
│   ├── crates/
│   │   │
│   │   ├── kernel/
│   │   ├── process/
│   │   ├── scheduler/
│   │   ├── memory/
│   │   ├── capabilities/
│   │   ├── syscall/
│   │   ├── ipc/
│   │   ├── vfs/
│   │   ├── tty/
│   │   ├── devices/
│   │   ├── loader/
│   │   ├── init/
│   │   └── agent-runtime/
│   │
│   └── arch/
│       └── x86_64/
│
├── python/
│   └── reference/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── cross_reference/
│   ├── security/
│   ├── stress/
│   ├── fuzz/
│   └── qemu/
│
├── scripts/
├── images/
└── docs/
    ├── architecture/
    ├── kernel/
    ├── hardware/
    ├── security/
    └── testing/
```

## Architectural invariant

> **Le Domain décrit les invariants du système.**
>
> **L'Application orchestre les cas d'utilisation du contexte.**
>
> **Les Ports définissent les dépendances nécessaires.**
>
> **Les Adapters connectent ces ports au monde extérieur.**
>
> **L'Infrastructure contient les détails techniques.**
>
> **L'architecture CPU reste isolée.**
>
> **Le kernel compose les bounded contexts.**
>
> **Le user-space consomme le kernel via des interfaces publiques.**
>
> **Le Python reference model spécifie le comportement attendu.**
>
> **Les tests verrouillent les invariants avant les implémentations.**





## 14.1 — Kernel Foundation & Process Scheduler

**Objectif :** construire les premières primitives d'un véritable kernel capable de gérer des processus indépendamment de leur nature.

### Kernel Foundation

* [ ] **OS-001 — Define Kernel Architecture** `[📄 Markdown]`

  * Définir les responsabilités du kernel.
  * Définir la séparation kernel-space / user-space.
  * Définir les interfaces internes.
  * Documenter les invariants fondamentaux.

* [ ] **OS-002 — Create Rust Kernel Crate** `[🦀 Rust]`

  * Créer le crate Rust dédié au kernel.
  * Configurer le build `no_std`.
  * Préparer la cible QEMU.
  * Séparer kernel et user-space.

* [ ] **OS-003 — Implement Kernel Entry Point** `[🦀 Rust + 🔧 Assembly]`

  * Implémenter le point d'entrée.
  * Initialiser les structures kernel.
  * Initialiser la stack kernel.
  * Entrer dans la boucle kernel principale.

* [ ] **OS-004 — Implement Kernel Logging** `[🦀 Rust]`

  * Ajouter une console kernel.
  * Implémenter les logs kernel.
  * Définir les niveaux de logs.

* [ ] **OS-005 — Implement Kernel Panic Handler** `[🦀 Rust]`

  * Implémenter le panic handler.
  * Afficher le contexte minimal.
  * Garantir un comportement déterministe en cas d'erreur fatale.

* [ ] **OS-006 — Create Kernel QEMU Boot Harness** `[🦀 Rust + 🐚 Shell]`

  * Ajouter le lancement automatique dans QEMU.
  * Ajouter un smoke test de boot.
  * Vérifier que le kernel démarre sans Python.

---

### Process Model

* [ ] **OS-007 — Define Process Model** `[🦀 Rust]`

  * Définir `Process`.
  * Définir les états :

    * `READY`
    * `RUNNING`
    * `BLOCKED`
    * `TERMINATED`
  * Définir les invariants de transition.

* [ ] **OS-008 — Implement PID Manager** `[🦀 Rust]`

  * Allocation des PID.
  * Réutilisation contrôlée.
  * Détection des collisions.
  * Tests d'allocation.

* [ ] **OS-009 — Implement Process Table** `[🦀 Rust]`

  * Table globale des processus.
  * Lookup par PID.
  * Ajout / suppression.
  * Gestion du lifecycle.

* [ ] **OS-010 — Implement Process Lifecycle** `[🦀 Rust]`

  * `spawn`
  * `exit`
  * `kill`
  * `wait`
  * `block`
  * `unblock`

* [ ] **OS-011 — Implement Parent / Child Relationship** `[🦀 Rust]`

  * Relations parent/enfant.
  * Gestion de la terminaison du parent.
  * Gestion des processus orphelins.

---

### Execution Context

* [ ] **OS-012 — Define CPU Context** `[🦀 Rust]`

  * Définir la structure du contexte CPU.
  * Instruction pointer.
  * Stack pointer.
  * Registers.
  * Process state.

* [ ] **OS-013 — Implement Initial Process Context** `[🦀 Rust + 🔧 Assembly]`

  * Construire le contexte initial.
  * Préparer la stack.
  * Définir le point d'entrée du processus.

* [ ] **OS-014 — Implement Context Save / Restore** `[🔧 Assembly + 🦀 Rust]`

  * Sauvegarder le contexte CPU.
  * Restaurer le contexte.
  * Tester la conservation des registers.

---

### Timer & Interrupts

* [ ] **OS-015 — Implement Kernel Tick** `[🦀 Rust]`

  * Ajouter le compteur de ticks.
  * Définir la fréquence du timer.
  * Exposer le temps kernel.

* [ ] **OS-016 — Implement Timer Interrupt** `[🔧 Assembly + 🦀 Rust]`

  * Configurer l'interruption timer.
  * Entrer dans le kernel.
  * Déclencher le scheduler.

* [ ] **OS-017 — Implement Interrupt Dispatch** `[🦀 Rust + 🔧 Assembly]`

  * Définir la table des interruptions.
  * Implémenter les handlers.
  * Séparer hardware interrupts et exceptions.

---

### Scheduler

* [ ] **OS-018 — Define Scheduler Interface** `[🦀 Rust]`

  * Définir `SchedulerPort`.
  * `schedule`
  * `yield`
  * `block`
  * `unblock`
  * `spawn`
  * `kill`

* [ ] **OS-019 — Implement Ready Queue** `[🦀 Rust]`

  * Queue des processus `READY`.
  * Ajout / retrait.
  * Garantir l'absence de doublons.

* [ ] **OS-020 — Implement Round-Robin Scheduler** `[🦀 Rust]`

  * Implémenter Round-Robin.
  * Sélectionner le prochain processus.
  * Garantir une distribution équitable.

* [ ] **OS-021 — Implement Process Yield** `[🦀 Rust]`

  * Permettre au processus de céder le CPU.
  * Retourner en `READY`.
  * Relancer le scheduler.

* [ ] **OS-022 — Implement Process Blocking** `[🦀 Rust]`

  * Implémenter `block`.
  * Implémenter `unblock`.
  * Retirer les processus bloqués du scheduler.
  * Réinsérer correctement les processus réveillés.

---

### Preemptive Scheduling

* [ ] **OS-023 — Implement Time Quantum** `[🦀 Rust]`

  * Définir le quantum.
  * Comptabiliser le temps CPU.
  * Détecter l'expiration.

* [ ] **OS-024 — Implement Scheduler Preemption** `[🦀 Rust + 🔧 Assembly]`

  * Déclencher le scheduler depuis le timer.
  * Sauvegarder le contexte.
  * Sélectionner le prochain processus.
  * Restaurer son contexte.

* [ ] **OS-025 — Implement Context Switch** `[🔧 Assembly + 🦀 Rust]`

  * Implémenter le context switch réel.
  * Sauvegarder/restaurer les registers.
  * Tester plusieurs processus.

---

### Priority Scheduling

* [ ] **OS-026 — Add Process Priority** `[🦀 Rust]`

  * Ajouter la priorité au processus.
  * Définir les niveaux.
  * Définir les règles de comparaison.

* [ ] **OS-027 — Implement Priority Scheduler** `[🦀 Rust]`

  * Intégrer les priorités.
  * Garantir le respect des priorités.
  * Prévenir la starvation.

* [ ] **OS-028 — Test Scheduler Fairness** `[🦀 Rust]`

  * Tester Round-Robin.
  * Tester les priorités.
  * Tester starvation.
  * Tester les changements dynamiques.

---

### Resource Accounting

* [ ] **OS-029 — Implement CPU Accounting** `[🦀 Rust]`

  * Comptabiliser le temps CPU.
  * Exposer les statistiques.
  * Tester le accounting.

* [ ] **OS-030 — Define Process Resource Limits** `[🦀 Rust]`

  * Définir `cpu_quota`.
  * Définir `memory_limit`.
  * Définir `process_limit`.
  * Préparer le futur Resource Manager.

---

### Python Reference Model

* [ ] **OS-031 — Implement Python Process Model** `[🐍 Python]`

  * Implémenter une version simulée de `Process`.
  * Reproduire les mêmes états.
  * Reproduire les mêmes invariants.

* [ ] **OS-032 — Implement Python Reference Scheduler** `[🐍 Python]`

  * Round-Robin.
  * Priorités.
  * Blocking.
  * Yield.
  * Quantum.

* [ ] **OS-033 — Cross-Implementation Behavioral Tests** `[🐍 Python + 🦀 Rust]`

  * Comparer les transitions Python / Rust.
  * Vérifier les invariants communs.
  * Utiliser Python comme modèle de référence.

---

### Kernel Test Infrastructure

* [ ] **OS-034 — Kernel Unit Test Framework** `[🦀 Rust]`

  * Tester les primitives kernel.
  * Tester les structures sans boot complet.

* [ ] **OS-035 — Kernel Integration Test Harness** `[🦀 Rust + 🐚 Shell]`

  * Tester le kernel dans QEMU.
  * Vérifier le boot.
  * Vérifier la création de processus.
  * Vérifier le scheduler.

* [ ] **OS-036 — Scheduler Stress Tests** `[🦀 Rust]`

  * Plusieurs processus.
  * Changements fréquents de contexte.
  * Processus bloqués.
  * Processus terminés.
  * Workloads CPU-bound.

---

### First User-Space Process

* [ ] **OS-037 — Implement Minimal User-Space Process** `[🦀 Rust]`

  * Créer un premier processus user-space.
  * Le rendre indépendant du kernel.

* [ ] **OS-038 — Implement Kernel → User-Space Transition** `[🦀 Rust + 🔧 Assembly]`

  * Implémenter la transition kernel → user.
  * Vérifier les privilèges d'exécution.
  * Tester le retour vers le kernel.

* [ ] **OS-039 — Run Multiple User-Space Processes** `[🦀 Rust]`

  * Lancer plusieurs processus.
  * Les scheduler.
  * Vérifier leur isolation.

---

### Agent Process Proof

* [ ] **OS-040 — Define Agent as User-Space Process** `[📄 Markdown]`

  * Documenter qu'un agent est une application user-space.
  * Définir son contrat avec le kernel.
  * Garantir que le kernel ne dépend pas du LLM/MCP.

* [ ] **OS-041 — Implement Minimal Agent Process** `[🦀 Rust]`

  * Créer un processus représentant un agent.
  * Lancer l'agent via les primitives kernel.
  * Vérifier son scheduling.

* [ ] **OS-042 — End-to-End Kernel Process Demo** `[🦀 Rust + 🔧 Assembly + 🐚 Shell]`

  * Boot du kernel.
  * Création de plusieurs processus.
  * Scheduling.
  * Timer interrupt.
  * Preemption.
  * Context switch.
  * Exécution d'un processus agent.
  * Terminaison propre.

---

### Definition of Done

* [ ] Kernel bootable indépendamment de Python.
* [ ] Processus avec PID et lifecycle complet.
* [ ] Scheduler Round-Robin fonctionnel.
* [ ] Preemption par timer.
* [ ] Context switching fonctionnel.
* [ ] Priority scheduling.
* [ ] Resource accounting.
* [ ] User-space process.
* [ ] Agent exécuté comme processus user-space.
* [ ] Tests unitaires et intégration QEMU.
* [ ] Python reference model.
* [ ] Aucun LLM/MCP requis par le kernel.

**Principe fondamental :**

> Le kernel ne gère pas des "agents".
> Il gère des processus, de la mémoire, du CPU, des ressources et des primitives système.
> Les agents utilisent ces primitives depuis le user-space.



## Sous-phase 14.2 — Capability & Security Engine

> **Rôle de ce fichier** : Ce fichier est le deuxième de la **Phase 14 — Noyau Agentique**. Il définit la sous-phase **Capability & Security Engine**, responsable du modèle de capacités et du contrôle des accès aux primitives du kernel.
>
> **Principe fondamental** : le kernel ne doit pas dépendre directement d'un moteur RBAC/ABAC complexe. Les primitives kernel sont protégées par des **capabilities**. Les policies RBAC/ABAC constituent une couche supérieure permettant de déterminer quelles capabilities peuvent être accordées à un processus.
>
> **Architecture** :
>
> ```text
> User / Agent
>      │
>      ▼
> Policy Engine
>   RBAC / ABAC
>      │
>      ▼
> Capability Manager
>      │
>      ▼
> Kernel Security Boundary
>      │
>      ├── Syscalls
>      ├── IPC
>      ├── Memory
>      ├── Filesystem
>      ├── Network
>      └── Resources
> ```
>
> **Structure** : Chaque ticket est décrit avec un rôle détaillé. Les tickets sont ordonnés logiquement : modèle de capabilities, implémentation Python de référence, implémentation Rust kernel, puis policy engine et extensions. Le fallback pur-Python est obligatoire pour chaque brique Rust lorsque cela est pertinent.
>
> **Règle de sécurité** :
>
> > Une policy peut accorder une capability.
> >
> > Une policy ne peut jamais contourner une capability refusée par le kernel.
>
> **Dépendances** :
>
> * **14.1 — Kernel Foundation & Process Scheduler** : le Capability Engine s'attache aux processus kernel.
> * **14.3 — Memory Manager** : intégration future avec l'isolation mémoire.
> * **14.4 — Syscall Layer** : les syscalls deviendront le principal point de contrôle des capabilities.
> * **14.5 — IPC** : les capabilities contrôleront les communications inter-processus.
>
> **Prochaine étape** : **Sous-phase 14.3 — Memory Manager**.

---

### Capability Model

* [ ] **OS-043 — Define Capability Model** `[📄 Markdown]`

  * Définir le concept de capability.
  * Définir les ressources protégées.
  * Définir les opérations autorisées.
  * Définir les invariants de sécurité.
  * Documenter la différence entre capability et policy.

* [ ] **OS-044 — Define Capability Structure** `[🦀 Rust]`

  * Définir `Capability`.
  * Définir l'identité de la capability.
  * Définir la ressource ciblée.
  * Définir les actions autorisées.
  * Définir les contraintes éventuelles.

  Exemple :

  ```text
  Capability
  ├── id
  ├── resource
  ├── actions
  ├── constraints
  └── scope
  ```

* [ ] **OS-045 — Define Capability Types** `[🦀 Rust]`

  * Définir les premières catégories :

    * `PROCESS`
    * `MEMORY`
    * `FILE`
    * `IPC`
    * `NETWORK`
    * `DEVICE`
    * `RESOURCE`
  * Préparer l'extension future du modèle.

* [ ] **OS-046 — Define Capability Scope** `[🦀 Rust]`

  * Définir les scopes.
  * Supporter les ressources ciblées.
  * Empêcher une capability globale lorsqu'une capability scoped suffit.

  Exemple :

  ```text
  FILE_READ:/workspace
  FILE_WRITE:/workspace/output
  NETWORK_CONNECT:api.example.com:443
  IPC_CONNECT:hexasec
  GPU_USE:0
  ```

---

### Capability Lifecycle

* [ ] **OS-047 — Implement Capability Store** `[🦀 Rust]`

  * Stocker les capabilities associées à un processus.
  * Ajouter une capability.
  * Retirer une capability.
  * Rechercher une capability.

* [ ] **OS-048 — Implement Capability Grant** `[🦀 Rust]`

  * Accorder une capability à un processus.
  * Vérifier l'autorité du processus demandeur.
  * Empêcher l'auto-attribution de privilèges.

* [ ] **OS-049 — Implement Capability Revoke** `[🦀 Rust]`

  * Révoquer une capability.
  * Gérer les capabilities révoquées.
  * Garantir que les nouvelles opérations sont refusées immédiatement.

* [ ] **OS-050 — Implement Capability Delegation** `[🦀 Rust]`

  * Permettre la délégation contrôlée d'une capability.
  * Empêcher l'élévation de privilèges par délégation.
  * Limiter la délégation au scope de la capability originale.

* [ ] **OS-051 — Implement Capability Expiration** `[🦀 Rust]`

  * Supporter une durée de vie optionnelle.
  * Expirer automatiquement les capabilities temporaires.
  * Tester les capacités expirées.

---

### Capability Evaluation

* [ ] **OS-052 — Define Capability Evaluator** `[🦀 Rust]`

  * Définir `CapabilityEvaluator`.
  * Vérifier :

    * sujet ;
    * ressource ;
    * action ;
    * scope ;
    * état de la capability.

* [ ] **OS-053 — Implement Capability Check** `[🦀 Rust]`

  * Implémenter :

  ```text
  check(process, resource, action)
  ```

  * Retourner `ALLOW` ou `DENY`.
  * Garantir un comportement déterministe.

* [ ] **OS-054 — Implement Default Deny** `[🦀 Rust]`

  * Refuser toute opération sans capability explicite.
  * Vérifier qu'aucun fallback implicite n'accorde un accès.

* [ ] **OS-055 — Implement Capability Non-Escalation** `[🦀 Rust]`

  * Une capability ne peut pas créer une capability plus puissante.
  * Une capability déléguée ne peut pas dépasser son scope parent.
  * Tester les scénarios d'escalade.

---

### Python Reference Model

* [ ] **OS-056 — Implement Python Capability Model** `[🐍 Python]`

  * Implémenter le modèle de capability.
  * Reproduire les mêmes invariants que Rust.

* [ ] **OS-057 — Implement Python Capability Store** `[🐍 Python]`

  * Ajouter / supprimer / rechercher des capabilities.
  * Tester le lifecycle.

* [ ] **OS-058 — Implement Python Capability Evaluator** `[🐍 Python]`

  * Implémenter `check`.
  * Default deny.
  * Scope checking.
  * Expiration.
  * Delegation.

* [ ] **OS-059 — Cross-Implementation Capability Tests** `[🐍 Python + 🦀 Rust]`

  * Comparer les décisions Python / Rust.
  * Vérifier les mêmes résultats.
  * Tester les mêmes scénarios de sécurité.

---

### Policy Engine

* [ ] **OS-060 — Define Policy Model** `[📄 Markdown + 🐍 Python]`

  * Définir `Policy`.
  * Définir :

    * `subject`
    * `resource`
    * `action`
    * `effect`
    * `conditions`
  * Documenter la sémantique.

* [ ] **OS-061 — Implement RBAC** `[🐍 Python]`

  * Définir les rôles.
  * Associer rôles et capabilities.
  * Implémenter l'évaluation des rôles.

* [ ] **OS-062 — Implement ABAC** `[🐍 Python]`

  * Définir les attributs.
  * Implémenter les conditions.
  * Évaluer les policies contextuelles.

* [ ] **OS-063 — Implement Policy Composition** `[🐍 Python]`

  * Définir les règles de combinaison.
  * Gérer `ALLOW` / `DENY`.
  * Définir la priorité des règles.
  * Garantir le comportement `default deny`.

* [ ] **OS-064 — Implement Policy Engine** `[🐍 Python]`

  * Implémenter `PolicyEngine.evaluate`.
  * Transformer une décision de policy en demande de capability.
  * Ne jamais permettre au Policy Engine de bypasser le kernel.

---

### Rust Policy Layer

* [ ] **OS-065 — Define Rust Policy ABI** `[🦀 Rust]`

  * Définir l'interface entre policy layer et capability manager.
  * Définir les structures sérialisables.
  * Définir les résultats d'évaluation.

* [ ] **OS-066 — Implement Rust Policy Evaluator** `[🦀 Rust]`

  * Implémenter l'évaluation déterministe.
  * Reproduire les règles du modèle Python.
  * Ne pas introduire de dépendance LLM.

* [ ] **OS-067 — Cross-Implementation Policy Tests** `[🐍 Python + 🦀 Rust]`

  * Comparer Python / Rust.
  * Vérifier les décisions identiques.
  * Tester les cas limites.

---

### Process Security Integration

* [ ] **OS-068 — Attach Capabilities to Process** `[🦀 Rust]`

  * Associer un capability set à chaque processus.
  * Initialiser les capabilities lors du `spawn`.
  * Nettoyer les capabilities lors du `exit`.

* [ ] **OS-069 — Implement Process Capability Boundary** `[🦀 Rust]`

  * Empêcher un processus d'accéder aux capabilities d'un autre.
  * Vérifier l'isolation.
  * Tester les accès inter-processus.

* [ ] **OS-070 — Implement Capability-Aware Process Spawn** `[🦀 Rust]`

  * Permettre au parent de fournir un capability set limité.
  * Empêcher l'enfant d'obtenir plus de privilèges que son parent.

---

### Security Invariants

* [ ] **OS-071 — Test Default Deny** `[🦀 Rust + 🐍 Python]`

  * Aucun accès sans capability.
  * Aucun fallback permissif.

* [ ] **OS-072 — Test Privilege Escalation Resistance** `[🦀 Rust + 🐍 Python]`

  * Auto-grant.
  * Capability forgery.
  * Capability duplication.
  * Capability escalation.
  * Delegation abuse.

* [ ] **OS-073 — Test Cross-Process Isolation** `[🦀 Rust]`

  * Process A ne peut pas utiliser les capabilities de Process B.
  * Processus privilégié et non privilégié.
  * Tests d'accès croisés.

* [ ] **OS-074 — Test Capability Revocation** `[🦀 Rust]`

  * Révocation immédiate.
  * Réutilisation d'une capability révoquée.
  * Expiration.

---

### Audit & Observability

* [ ] **OS-075 — Implement Security Decision Events** `[🦀 Rust]`

  * Logger les décisions :

    * `ALLOW`
    * `DENY`
    * `GRANT`
    * `REVOKE`
    * `EXPIRE`

* [ ] **OS-076 — Define Security Audit Model** `[🦀 Rust]`

  * Définir :

    * timestamp ;
    * PID ;
    * capability ;
    * resource ;
    * action ;
    * decision ;
    * reason.

* [ ] **OS-077 — Implement Security Audit Tests** `[🦀 Rust + 🐍 Python]`

  * Vérifier la génération des événements.
  * Vérifier la traçabilité des décisions.
  * Vérifier qu'un `DENY` est observable.

---

### Agent Security Integration

* [ ] **OS-078 — Define Agent Capability Profile** `[📄 Markdown]`

  * Définir les capabilities minimales d'un agent.
  * Séparer les profils :

    * read-only ;
    * worker ;
    * networked ;
    * privileged.

* [ ] **OS-079 — Implement Agent Capability Bootstrap** `[🦀 Rust]`

  * Créer un agent avec un capability set minimal.
  * Ne jamais donner de privilèges implicites.

* [ ] **OS-080 — Implement Capability-Aware Agent Execution** `[🦀 Rust]`

  * Vérifier les capabilities pendant l'exécution.
  * Refuser les opérations hors scope.
  * Générer les événements d'audit.

* [ ] **OS-081 — End-to-End Security Boundary Test** `[🦀 Rust + 🐍 Python]`

  * Créer un agent.
  * Lui attribuer des capabilities.
  * Exécuter des opérations autorisées.
  * Exécuter des opérations interdites.
  * Vérifier les `ALLOW` / `DENY`.
  * Vérifier l'audit.

---

### Definition of Done

* [ ] Capability model défini.
* [ ] Capability store fonctionnel.
* [ ] Grant / revoke fonctionnels.
* [ ] Capability scope fonctionnel.
* [ ] Default deny garanti.
* [ ] Capability non-escalation garantie.
* [ ] Python reference model disponible.
* [ ] Rust implementation fonctionnelle.
* [ ] RBAC implémenté.
* [ ] ABAC implémenté.
* [ ] Policy Engine séparé du kernel capability enforcement.
* [ ] Processus associés à des capability sets.
* [ ] Isolation inter-processus testée.
* [ ] Audit des décisions de sécurité.
* [ ] Tests d'escalade de privilèges.
* [ ] Agent exécuté avec un capability profile minimal.

**Principe fondamental :**

> **La Policy décide ce qui peut être accordé.**
>
> **La Capability représente ce qui est accordé.**
>
> **Le Kernel décide finalement si l'opération peut être exécutée.**

```text
                    POLICY SPACE
                         │
                  RBAC / ABAC
                         │
                         ▼
                 Capability Grant
                         │
                         ▼
              ┌────────────────────┐
              │   KERNEL SECURITY  │
              │      BOUNDARY      │
              └────────────────────┘
                         │
                  Capability Check
                         │
                  ┌──────┴──────┐
                  │             │
                ALLOW          DENY
                  │             │
                  ▼             ▼
              Syscall /       Error
              Operation
```



## Sous-phase 14.3 — Memory Manager

> **Rôle de ce fichier** : Ce fichier est le troisième de la **Phase 14 — Noyau Agentique**. Il définit la sous-phase **Memory Manager**, responsable de la gestion et de l'isolation de la mémoire utilisée par le kernel et les processus.
>
> **Principe fondamental** : chaque processus doit disposer de son propre espace d'adressage. Un processus ne doit jamais pouvoir lire ou modifier arbitrairement la mémoire d'un autre processus ou celle du kernel.
>
> **Architecture** :
>
> ```text
> Hardware Memory
>       │
>       ▼
> Physical Memory Manager
>       │
>       ▼
> Virtual Memory Manager
>       │
>       ├── Kernel Address Space
>       │
>       └── Process Address Spaces
>               │
>               ├── Code
>               ├── Heap
>               ├── Stack
>               └── Mapped Memory
> ```
>
> **Structure** : Les tickets sont ordonnés progressivement : modèle mémoire, allocation physique, mémoire virtuelle, address spaces, isolation, heap, mapping, protection et intégration avec les processus.
>
> **Langages** :
>
> * 🦀 **Rust** : implémentation réelle du kernel.
> * 🐍 **Python** : modèle de référence / simulation.
> * 🔧 **Assembly** : opérations dépendantes du CPU/MMU lorsque nécessaire.
> * 🧪 **Rust + Python** : validation comportementale.
>
> **Règle de sécurité** :
>
> > Un processus ne possède jamais un accès direct à la mémoire physique.
> >
> > Tout accès mémoire d'un processus passe par son espace d'adressage contrôlé par le kernel.
>
> **Dépendances** :
>
> * **14.1 — Kernel Foundation & Process Scheduler** : chaque processus devra posséder un address space.
> * **14.2 — Capability & Security Engine** : les futures opérations mémoire pourront être protégées par capabilities.
>
> **Prochaine étape** : **Sous-phase 14.4 — Syscall Layer**.

---

### Memory Architecture

* [ ] **OS-082 — Define Kernel Memory Architecture** `[📄 Markdown]`

  * Définir la mémoire physique.
  * Définir la mémoire virtuelle.
  * Définir kernel-space / user-space.
  * Définir les différents segments mémoire.
  * Documenter les invariants mémoire.

* [ ] **OS-083 — Define Address Space Model** `[🦀 Rust]`

  * Définir `AddressSpace`.
  * Définir les mappings.
  * Définir les permissions mémoire.
  * Définir l'identité d'un address space.

* [ ] **OS-084 — Define Memory Page Model** `[🦀 Rust]`

  * Définir `Page`.
  * Définir `Frame`.
  * Définir la taille des pages.
  * Définir les états d'une page.

  ```text
  Page
  ├── virtual_address
  ├── physical_frame
  ├── permissions
  └── state
  ```

---

### Physical Memory Manager

* [ ] **OS-085 — Implement Physical Frame Allocator** `[🦀 Rust]`

  * Détecter la mémoire physique disponible.
  * Maintenir les frames libres.
  * Allouer un frame.
  * Libérer un frame.

* [ ] **OS-086 — Implement Frame Allocation Strategy** `[🦀 Rust]`

  * Implémenter une stratégie d'allocation initiale.
  * Garantir qu'un frame ne peut pas être attribué deux fois.
  * Tester allocation/libération.

* [ ] **OS-087 — Implement Physical Memory Accounting** `[🦀 Rust]`

  * Compter les frames utilisés.
  * Compter les frames libres.
  * Exposer les statistiques mémoire.

* [ ] **OS-088 — Implement Physical Memory Tests** `[🦀 Rust]`

  * Allocation simple.
  * Allocation multiple.
  * Libération.
  * Réutilisation.
  * Épuisement de la mémoire.

---

### Virtual Memory

* [ ] **OS-089 — Implement Page Table Abstraction** `[🦀 Rust]`

  * Définir l'abstraction page table.
  * Définir les niveaux de traduction nécessaires à l'architecture cible.
  * Ajouter les opérations de mapping.

* [ ] **OS-090 — Implement Virtual Address Translation** `[🦀 Rust + 🔧 Assembly]`

  * Configurer la traduction virtuelle → physique.
  * Initialiser la MMU.
  * Vérifier les mappings.

* [ ] **OS-091 — Implement Page Mapping** `[🦀 Rust]`

  * Mapper une page virtuelle vers un frame.
  * Démapper une page.
  * Vérifier les collisions.
  * Vérifier les mappings invalides.

* [ ] **OS-092 — Implement Memory Permissions** `[🦀 Rust]`

  * Supporter :

    * `READ`
    * `WRITE`
    * `EXECUTE`
  * Empêcher les combinaisons interdites.
  * Préparer les protections `NX`.

* [ ] **OS-093 — Implement Page Fault Handler** `[🦀 Rust + 🔧 Assembly]`

  * Intercepter les page faults.
  * Identifier l'adresse fautive.
  * Identifier le type de violation.
  * Retourner une erreur kernel appropriée.

---

### Kernel Address Space

* [ ] **OS-094 — Define Kernel Address Space** `[🦀 Rust]`

  * Définir l'espace mémoire du kernel.
  * Définir les mappings kernel.
  * Définir les zones protégées.

* [ ] **OS-095 — Protect Kernel Memory** `[🦀 Rust]`

  * Empêcher l'accès user-space aux pages kernel.
  * Tester les accès lecture.
  * Tester les accès écriture.
  * Tester les accès exécution.

* [ ] **OS-096 — Implement Kernel Heap** `[🦀 Rust]`

  * Ajouter un allocator heap kernel.
  * Configurer l'allocation dynamique.
  * Ajouter allocation/libération.
  * Tester les allocations.

---

### Process Address Spaces

* [ ] **OS-097 — Attach Address Space to Process** `[🦀 Rust]`

  * Ajouter `AddressSpace` au modèle `Process`.
  * Créer un address space lors du `spawn`.
  * Détruire l'address space lors du `exit`.

* [ ] **OS-098 — Implement User Stack** `[🦀 Rust]`

  * Allouer la stack user.
  * Mapper la stack.
  * Définir ses permissions.
  * Ajouter une guard page.

* [ ] **OS-099 — Implement User Heap** `[🦀 Rust]`

  * Définir la zone heap user.
  * Ajouter les mécanismes d'extension.
  * Préparer l'interface future avec `mmap` / allocation dynamique.

* [ ] **OS-100 — Implement Process Memory Isolation** `[🦀 Rust]`

  * Chaque processus possède son propre address space.
  * Process A ne peut pas accéder à Process B.
  * Process user ne peut pas accéder au kernel.

---

### Memory Allocation

* [ ] **OS-101 — Define Kernel Allocator Interface** `[🦀 Rust]`

  * Définir l'interface d'allocation.
  * Séparer allocation physique et allocation virtuelle.
  * Préparer plusieurs stratégies d'allocator.

* [ ] **OS-102 — Implement Kernel Heap Allocator** `[🦀 Rust]`

  * Implémenter l'allocation dynamique.
  * Supporter allocation/libération.
  * Gérer les erreurs d'allocation.

* [ ] **OS-103 — Implement User Memory Allocation Interface** `[🦀 Rust]`

  * Définir les primitives nécessaires aux futurs syscalls mémoire.
  * Préparer :

    * `mmap`
    * `munmap`
    * `brk` ou équivalent.

* [ ] **OS-104 — Memory Fragmentation Tests** `[🦀 Rust]`

  * Tester les allocations de tailles différentes.
  * Tester les libérations partielles.
  * Tester la fragmentation.
  * Tester l'épuisement.

---

### Memory Protection

* [ ] **OS-105 — Implement Read Protection** `[🦀 Rust]`

  * Empêcher les lectures hors mappings.
  * Tester les accès invalides.

* [ ] **OS-106 — Implement Write Protection** `[🦀 Rust]`

  * Empêcher les écritures sur les pages read-only.
  * Tester les violations.

* [ ] **OS-107 — Implement Execute Protection** `[🦀 Rust]`

  * Supporter les pages non exécutables.
  * Empêcher l'exécution de mémoire non-X.

* [ ] **OS-108 — Implement Guard Pages** `[🦀 Rust]`

  * Ajouter une page inaccessible autour des stacks.
  * Détecter les stack overflows.
  * Tester les accès à la guard page.

---

### Memory Quotas

* [ ] **OS-109 — Define Process Memory Quota** `[🦀 Rust]`

  * Définir une limite mémoire par processus.
  * Associer la limite au `Process`.

* [ ] **OS-110 — Implement Memory Quota Enforcement** `[🦀 Rust]`

  * Refuser une allocation dépassant le quota.
  * Comptabiliser la mémoire consommée.
  * Libérer correctement les ressources.

* [ ] **OS-111 — Implement Kernel Memory Quota Tests** `[🦀 Rust]`

  * Allocation sous quota.
  * Allocation exactement au quota.
  * Allocation dépassant le quota.
  * Libération puis réallocation.

---

### Python Reference Model

* [ ] **OS-112 — Implement Python Memory Model** `[🐍 Python]`

  * Simuler la mémoire physique.
  * Simuler les frames.
  * Simuler les pages.
  * Simuler les address spaces.

* [ ] **OS-113 — Implement Python Page Mapper** `[🐍 Python]`

  * Mapping.
  * Unmapping.
  * Permissions.
  * Isolation.

* [ ] **OS-114 — Implement Python Memory Allocator** `[🐍 Python]`

  * Allocation.
  * Libération.
  * Quotas.
  * Épuisement.

* [ ] **OS-115 — Cross-Implementation Memory Tests** `[🐍 Python + 🦀 Rust]`

  * Comparer les comportements Python / Rust.
  * Vérifier les invariants.
  * Tester les mêmes scénarios mémoire.

---

### Process & Scheduler Integration

* [ ] **OS-116 — Integrate Address Space with Process Creation** `[🦀 Rust]`

  * Créer l'address space lors du `spawn`.
  * Initialiser stack et heap.
  * Préparer le contexte mémoire.

* [ ] **OS-117 — Integrate Address Space with Context Switch** `[🦀 Rust + 🔧 Assembly]`

  * Changer l'address space lors du context switch.
  * Garantir que le processus récupère son espace mémoire.

* [ ] **OS-118 — Implement Process Memory Cleanup** `[🦀 Rust]`

  * Libérer les mappings.
  * Libérer les frames.
  * Détruire l'address space à la terminaison.

* [ ] **OS-119 — Process Memory Isolation Integration Test** `[🦀 Rust]`

  * Créer Process A.
  * Créer Process B.
  * Vérifier leurs espaces mémoire indépendants.
  * Vérifier qu'une violation déclenche le mécanisme de protection.

---

### Agent Memory Model

* [ ] **OS-120 — Define Agent Memory Contract** `[📄 Markdown]`

  * Définir ce qu'un agent peut considérer comme mémoire.
  * Séparer :

    * mémoire du processus ;
    * mémoire persistante ;
    * mémoire applicative ;
    * mémoire kernel.
  * Le kernel ne doit pas connaître la sémantique LLM de la mémoire.

* [ ] **OS-121 — Implement Minimal Agent Address Space** `[🦀 Rust]`

  * Créer un address space pour un processus agent.
  * Initialiser stack et heap.
  * Appliquer les permissions mémoire.

* [ ] **OS-122 — Agent Memory Isolation Test** `[🦀 Rust]`

  * Tester l'isolation entre deux agents.
  * Vérifier l'absence d'accès mémoire croisé.
  * Vérifier la protection du kernel.

---

### Memory Stress & Security Tests

* [ ] **OS-123 — Memory Stress Test** `[🦀 Rust]`

  * Allocations massives.
  * Création de nombreux processus.
  * Libérations massives.
  * Épuisement contrôlé.

* [ ] **OS-124 — Address Space Isolation Tests** `[🦀 Rust]`

  * Accès lecture interdit.
  * Accès écriture interdit.
  * Accès exécution interdit.
  * Accès à une adresse non mappée.

* [ ] **OS-125 — Memory Corruption Tests** `[🦀 Rust]`

  * Détection des mappings invalides.
  * Double release.
  * Frame déjà attribué.
  * Page déjà mappée.

* [ ] **OS-126 — Memory Security Regression Suite** `[🦀 Rust + 🐍 Python]`

  * Centraliser les invariants mémoire.
  * Vérifier les régressions.
  * Comparer les résultats avec le modèle Python.

---

### Definition of Done

* [ ] Physical Frame Allocator fonctionnel.
* [ ] Virtual Memory Manager fonctionnel.
* [ ] Page tables fonctionnelles.
* [ ] Address spaces fonctionnels.
* [ ] Kernel memory protégée.
* [ ] User memory isolée.
* [ ] Kernel heap fonctionnel.
* [ ] User stack fonctionnelle.
* [ ] User heap préparé.
* [ ] Page fault handler fonctionnel.
* [ ] Read / Write / Execute permissions.
* [ ] Guard pages.
* [ ] Memory quotas.
* [ ] Python reference model.
* [ ] Rust implementation.
* [ ] Tests d'isolation inter-processus.
* [ ] Tests de stress mémoire.
* [ ] Agent exécuté dans son propre address space.

**Principe fondamental :**

> **Chaque processus possède son propre espace d'adressage.**
>
> **Le kernel contrôle les mappings et les permissions.**
>
> **Aucun processus user-space ne peut accéder arbitrairement à la mémoire du kernel ou d'un autre processus.**

```text
                    KERNEL SPACE
              ┌──────────────────────┐
              │ Kernel Code          │
              │ Kernel Heap          │
              │ Kernel Structures    │
              └──────────────────────┘
                       ▲
                       │ PROTECTED
                       │
              ─────────┼─────────
                       │
                       ▼
                   USER SPACE
              ┌──────────────────────┐
              │ Process A            │
              │ ├── Code             │
              │ ├── Stack            │
              │ └── Heap             │
              └──────────────────────┘

              ┌──────────────────────┐
              │ Process B            │
              │ ├── Code             │
              │ ├── Stack            │
              │ └── Heap             │
              └──────────────────────┘

              Process A ✕ Process B
              Process A ✕ Kernel
              Process B ✕ Kernel
```


## Sous-phase 14.4 — Syscall Layer

> **Rôle de ce fichier** : Ce fichier est le quatrième de la **Phase 14 — Noyau Agentique**. Il définit la sous-phase **Syscall Layer**, responsable de l'interface contrôlée entre le user-space et le kernel.
>
> **Principe fondamental** : un processus user-space ne doit jamais appeler directement les primitives internes du kernel. Toute opération privilégiée passe par une **system call**.
>
> **Architecture** :
>
> ```text
> User Space
>     │
>     │ syscall
>     ▼
> ┌──────────────────────┐
> │   Syscall Boundary   │
> └──────────────────────┘
>     │
>     ▼
> Kernel
>     │
>     ├── Process Manager
>     ├── Memory Manager
>     ├── Capability Manager
>     ├── IPC
>     ├── VFS
>     └── Network
> ```
>
> **Règle fondamentale** :
>
> > Le user-space demande.
> >
> > Le kernel décide.
> >
> > Le kernel exécute ou refuse.
>
> **Langages** :
>
> * 🦀 **Rust** : implémentation du syscall layer.
> * 🔧 **Assembly** : transition user-space → kernel-space et retour lorsque nécessaire.
> * 🐍 **Python** : modèle de référence de l'ABI et des sémantiques.
> * 🧪 **Rust + Python** : tests comportementaux.
>
> **Dépendances** :
>
> * **14.1 — Kernel Foundation & Process Scheduler**
> * **14.2 — Capability & Security Engine**
> * **14.3 — Memory Manager**
>
> **Prochaine étape** : **Sous-phase 14.5 — IPC & Message Passing**.

---

### Syscall Architecture

* [ ] **OS-127 — Define Syscall Architecture** `[📄 Markdown]`

  * Définir la frontière user-space / kernel-space.
  * Définir les responsabilités du syscall layer.
  * Définir les invariants de sécurité.
  * Documenter le cycle de vie d'un syscall.

* [ ] **OS-128 — Define Syscall ABI** `[📄 Markdown]`

  * Définir le numéro de syscall.
  * Définir les arguments.
  * Définir les valeurs de retour.
  * Définir le format des erreurs.
  * Définir les conventions d'appel.

* [ ] **OS-129 — Define Syscall Registry** `[🦀 Rust]`

  * Définir la table des syscalls.
  * Associer numéro → handler.
  * Refuser les numéros inconnus.

---

### User → Kernel Transition

* [ ] **OS-130 — Implement Syscall Entry Point** `[🔧 Assembly + 🦀 Rust]`

  * Implémenter le point d'entrée syscall.
  * Sauvegarder le contexte user.
  * Passer en kernel mode.
  * Transmettre le numéro de syscall.

* [ ] **OS-131 — Implement Syscall Dispatcher** `[🦀 Rust]`

  * Lire le numéro du syscall.
  * Sélectionner le handler.
  * Valider les arguments.
  * Retourner le résultat au processus.

* [ ] **OS-132 — Implement Syscall Return Path** `[🔧 Assembly + 🦀 Rust]`

  * Restaurer le contexte user.
  * Restaurer les registres.
  * Retourner au processus appelant.

* [ ] **OS-133 — Implement Invalid Syscall Handling** `[🦀 Rust]`

  * Détecter un syscall inexistant.
  * Retourner une erreur.
  * Empêcher tout accès arbitraire au kernel.

---

### Process Syscalls

* [ ] **OS-134 — Implement `sys_spawn`** `[🦀 Rust]`

  * Créer un processus depuis le user-space.
  * Valider les paramètres.
  * Initialiser l'address space.
  * Initialiser les capabilities.

* [ ] **OS-135 — Implement `sys_exit`** `[🦀 Rust]`

  * Terminer le processus courant.
  * Libérer ses ressources.
  * Nettoyer son address space.

* [ ] **OS-136 — Implement `sys_wait`** `[🦀 Rust]`

  * Attendre la terminaison d'un processus enfant.
  * Gérer le blocage du processus parent.

* [ ] **OS-137 — Implement `sys_yield`** `[🦀 Rust]`

  * Permettre au processus de céder volontairement le CPU.
  * Retourner dans la ready queue.

* [ ] **OS-138 — Implement `sys_sleep`** `[🦀 Rust]`

  * Bloquer le processus pendant une durée.
  * Réveiller automatiquement le processus.

---

### Memory Syscalls

* [ ] **OS-139 — Implement `sys_mmap`** `[🦀 Rust]`

  * Mapper une région mémoire.
  * Valider les permissions.
  * Vérifier le quota mémoire.
  * Vérifier les capabilities.

* [ ] **OS-140 — Implement `sys_munmap`** `[🦀 Rust]`

  * Supprimer un mapping.
  * Libérer les ressources associées.

* [ ] **OS-141 — Implement `sys_brk` or Heap Expansion** `[🦀 Rust]`

  * Permettre l'extension contrôlée du heap.
  * Respecter les limites mémoire.

* [ ] **OS-142 — Implement Memory Syscall Validation** `[🦀 Rust]`

  * Vérifier les adresses.
  * Vérifier les tailles.
  * Vérifier les permissions.
  * Empêcher les mappings kernel.

---

### Capability Integration

* [ ] **OS-143 — Integrate Capability Checks into Syscalls** `[🦀 Rust]`

  * Chaque syscall privilégié doit vérifier les capabilities nécessaires.
  * Aucun syscall ne doit contourner le Capability Manager.

* [ ] **OS-144 — Define Syscall Capability Requirements** `[🦀 Rust]`

  * Associer chaque syscall à ses capabilities.

  Exemple :

  ```text
  sys_spawn
      → PROCESS_CREATE

  sys_mmap
      → MEMORY_MAP

  sys_open
      → FILE_READ / FILE_WRITE

  sys_socket
      → NETWORK_CONNECT
  ```

* [ ] **OS-145 — Implement Syscall Default Deny** `[🦀 Rust]`

  * Refuser toute opération sans capability.
  * Vérifier que les syscalls ne possèdent aucun fallback permissif.

* [ ] **OS-146 — Syscall Security Audit** `[🦀 Rust]`

  * Journaliser :

    * PID ;
    * syscall ;
    * arguments pertinents ;
    * capability ;
    * résultat ;
    * erreur éventuelle.

---

### User-Space Syscall Library

* [ ] **OS-147 — Create User-Space Syscall Library** `[🦀 Rust]`

  * Créer une API user-space.
  * Masquer les détails de l'ABI.
  * Fournir des wrappers sûrs.

  Exemple :

  ```text
  process::spawn()
  process::exit()
  process::wait()
  process::yield()
  memory::map()
  memory::unmap()
  ```

* [ ] **OS-148 — Implement Raw Syscall Interface** `[🔧 Assembly + 🦀 Rust]`

  * Implémenter l'appel brut.
  * Passer les arguments selon l'ABI.
  * Récupérer les valeurs de retour.

* [ ] **OS-149 — Implement Syscall Error Model** `[🦀 Rust]`

  * Définir les erreurs kernel.
  * Convertir les erreurs en erreurs user-space.
  * Ne pas exposer directement les structures internes du kernel.

---

### File Descriptor Foundation

* [ ] **OS-150 — Define File Descriptor Model** `[🦀 Rust]`

  * Définir `FileDescriptor`.
  * Associer les descriptors au processus.
  * Définir `stdin`, `stdout`, `stderr`.

* [ ] **OS-151 — Implement FD Table** `[🦀 Rust]`

  * Allocation de descriptors.
  * Lookup.
  * Fermeture.
  * Nettoyage lors de `exit`.

* [ ] **OS-152 — Implement `sys_read`** `[🦀 Rust]`

  * Lire depuis un descriptor.
  * Vérifier les permissions.
  * Gérer les erreurs.

* [ ] **OS-153 — Implement `sys_write`** `[🦀 Rust]`

  * Écrire vers un descriptor.
  * Vérifier les permissions.
  * Gérer les erreurs.

* [ ] **OS-154 — Implement `sys_close`** `[🦀 Rust]`

  * Fermer un descriptor.
  * Libérer les ressources associées.

---

### Python Reference ABI

* [ ] **OS-155 — Implement Python Syscall Model** `[🐍 Python]`

  * Simuler la frontière syscall.
  * Représenter les numéros.
  * Représenter les arguments.
  * Représenter les résultats.

* [ ] **OS-156 — Implement Python Syscall Dispatcher** `[🐍 Python]`

  * Reproduire la logique de dispatch.
  * Gérer les erreurs.
  * Tester les syscalls invalides.

* [ ] **OS-157 — Implement Python Capability-Aware Syscalls** `[🐍 Python]`

  * Reproduire les contrôles de capabilities.
  * Default deny.
  * Audit.

* [ ] **OS-158 — Cross-Implementation Syscall Tests** `[🐍 Python + 🦀 Rust]`

  * Comparer Python / Rust.
  * Vérifier les mêmes résultats.
  * Vérifier les mêmes erreurs.
  * Vérifier les mêmes règles de sécurité.

---

### Syscall Security

* [ ] **OS-159 — Validate User Pointers** `[🦀 Rust]`

  * Vérifier qu'une adresse fournie par user-space appartient à son address space.
  * Refuser les pointeurs kernel.
  * Vérifier les tailles de buffers.

* [ ] **OS-160 — Implement Safe User Memory Access** `[🦀 Rust]`

  * Encapsuler les accès kernel → user memory.
  * Empêcher les accès directs non vérifiés.
  * Gérer les page faults.

* [ ] **OS-161 — Test Syscall Argument Validation** `[🦀 Rust]`

  * Pointeurs invalides.
  * Tailles invalides.
  * Descriptors invalides.
  * PID inexistants.
  * Permissions insuffisantes.

* [ ] **OS-162 — Test Syscall Privilege Escalation** `[🦀 Rust + 🐍 Python]`

  * Tentative d'accès kernel.
  * Tentative de modification d'un autre processus.
  * Tentative de création de capabilities.
  * Tentative de syscall sans permission.

---

### Agent Syscall Interface

* [ ] **OS-163 — Define Agent Syscall Contract** `[📄 Markdown]`

  * Définir les primitives accessibles aux agents.
  * Ne pas créer de syscalls spécifiques à un LLM.
  * Définir les capacités nécessaires.

* [ ] **OS-164 — Implement Agent Process API** `[🦀 Rust]`

  * Fournir aux agents une API user-space.
  * Process lifecycle.
  * Memory.
  * IPC preparation.
  * File descriptors.

* [ ] **OS-165 — Implement Minimal Agent User-Space Runtime** `[🦀 Rust]`

  * Runtime minimal utilisant uniquement les syscalls.
  * Aucun accès direct aux structures kernel.

* [ ] **OS-166 — Agent Syscall Integration Test** `[🦀 Rust]`

  * Créer un agent.
  * Utiliser les syscalls.
  * Tester les opérations autorisées.
  * Tester les opérations interdites.

---

### Syscall Stress Tests

* [ ] **OS-167 — Syscall Throughput Benchmark** `[🦀 Rust]`

  * Mesurer le coût des syscalls.
  * Mesurer le dispatch.
  * Mesurer la transition user/kernel.

* [ ] **OS-168 — Syscall Concurrency Tests** `[🦀 Rust]`

  * Plusieurs processus.
  * Syscalls concurrents.
  * Vérifier l'absence de corruption des structures kernel.

* [ ] **OS-169 — Syscall Fuzzing** `[🦀 Rust]`

  * Fuzzer sur les numéros de syscall.
  * Fuzzer sur les arguments.
  * Fuzzer sur les tailles.
  * Vérifier l'absence de crash kernel.

* [ ] **OS-170 — Syscall Regression Suite** `[🦀 Rust + 🐍 Python]`

  * Centraliser les invariants.
  * Vérifier les régressions.
  * Comparer avec le modèle Python.

---

### Definition of Done

* [ ] Syscall ABI définie.
* [ ] Syscall registry fonctionnelle.
* [ ] User → kernel transition fonctionnelle.
* [ ] Kernel → user transition fonctionnelle.
* [ ] Syscall dispatcher fonctionnel.
* [ ] Process syscalls.
* [ ] Memory syscalls.
* [ ] Capability checks intégrés.
* [ ] Default deny.
* [ ] User pointer validation.
* [ ] File descriptor foundation.
* [ ] User-space syscall library.
* [ ] Python reference model.
* [ ] Tests Python / Rust.
* [ ] Syscall security tests.
* [ ] Syscall fuzzing.
* [ ] Agent user-space utilisant les syscalls.

**Principe fondamental :**

> **Le syscall est la frontière officielle entre le processus et le kernel.**
>
> Le processus ne peut pas appeler directement le kernel.
>
> Il formule une demande via un syscall ; le kernel valide l'identité, les arguments, les capabilities et les ressources avant d'exécuter l'opération.

```text
              USER SPACE
┌─────────────────────────────────┐
│                                 │
│        Agent / Process          │
│              │                  │
│              ▼                  │
│       User-Space API            │
│              │                  │
└──────────────┼──────────────────┘
               │
          SYSCALL ABI
               │
───────────────┼────────────────────
               │
┌──────────────▼──────────────────┐
│        KERNEL SPACE             │
│                                 │
│       Syscall Dispatcher        │
│              │                  │
│       ┌──────┴──────┐           │
│       ▼             ▼           │
│ Capability      Validation      │
│   Check          Arguments      │
│       │             │           │
│       └──────┬──────┘           │
│              ▼                  │
│      Kernel Subsystem           │
│                                 │
└─────────────────────────────────┘
```

## Sous-phase 14.5 — IPC & Message Passing

> **Rôle de ce fichier** : Ce fichier est le cinquième de la **Phase 14 — Noyau Agentique**. Il définit la sous-phase **IPC (Inter-Process Communication)**, responsable des primitives permettant aux processus de communiquer entre eux de manière contrôlée, isolée et observable.
>
> **Principe fondamental** : les processus sont isolés par défaut. Toute communication entre deux processus doit passer par une primitive IPC explicitement autorisée par le kernel.
>
> **MCP n'est pas l'IPC du kernel.**
>
> MCP est un protocole applicatif user-space. Le kernel fournit les primitives IPC sous-jacentes permettant ensuite à des runtimes, agents, services et serveurs MCP de communiquer.
>
> **Architecture** :
>
> ```text
>                    USER SPACE
>
>      Agent A                    Agent B
>         │                         │
>         │                         │
>         ▼                         ▼
>   Agent Runtime            Agent Runtime
>         │                         │
>         └──────────┬──────────────┘
>                    │
>                 Syscalls
>                    │
>                    ▼
>              KERNEL SPACE
>        ┌──────────────────────┐
>        │     IPC Manager      │
>        ├──────────────────────┤
>        │ Channels             │
>        │ Message Queues       │
>        │ Pipes                │
>        │ Shared Memory        │
>        │ Signals              │
>        │ Synchronization      │
>        └──────────────────────┘
> ```
>
> **Langages** :
>
> * 🦀 **Rust** : implémentation kernel.
> * 🔧 **Assembly** : uniquement pour les primitives bas niveau nécessaires.
> * 🐍 **Python** : modèle de référence / simulation.
> * 🧪 **Rust + Python** : validation comportementale.
>
> **Dépendances** :
>
> * **14.1 — Kernel Foundation & Process Scheduler**
> * **14.2 — Capability & Security Engine**
> * **14.3 — Memory Manager**
> * **14.4 — Syscall Layer**
>
> **Prochaine étape** : **Sous-phase 14.6 — Resource Manager**.

---

### IPC Architecture

* [ ] **OS-171 — Define IPC Architecture** `[📄 Markdown]`

  * Définir les responsabilités de l'IPC Manager.
  * Définir les primitives IPC supportées.
  * Définir les invariants d'isolation.
  * Définir les relations entre IPC et capabilities.

* [ ] **OS-172 — Define IPC Object Model** `[🦀 Rust]`

  * Définir `IpcEndpoint`.
  * Définir `Channel`.
  * Définir `Message`.
  * Définir `Pipe`.
  * Définir les identifiants IPC.

* [ ] **OS-173 — Define IPC Lifecycle** `[🦀 Rust]`

  * Création.
  * Ouverture.
  * Fermeture.
  * Destruction.
  * Nettoyage automatique lors de la terminaison d'un processus.

---

### Message Passing

* [ ] **OS-174 — Implement Message Model** `[🦀 Rust]`

  * Définir la structure d'un message.
  * Définir la taille maximale.
  * Définir les métadonnées.
  * Garantir l'intégrité du message.

* [ ] **OS-175 — Implement Message Queue** `[🦀 Rust]`

  * Ajouter une queue FIFO.
  * Ajouter `send`.
  * Ajouter `receive`.
  * Gérer une queue vide.
  * Gérer une queue pleine.

* [ ] **OS-176 — Implement Blocking Receive** `[🦀 Rust]`

  * Bloquer le processus lorsqu'aucun message n'est disponible.
  * Réveiller le processus lorsqu'un message arrive.
  * Intégrer le scheduler.

* [ ] **OS-177 — Implement Blocking Send** `[🦀 Rust]`

  * Bloquer l'émetteur lorsque la queue est pleine.
  * Réveiller l'émetteur lorsqu'une place est disponible.

---

### Channels

* [ ] **OS-178 — Implement IPC Channel** `[🦀 Rust]`

  * Créer un canal bidirectionnel.
  * Associer les endpoints.
  * Gérer l'état du canal.

* [ ] **OS-179 — Implement Channel Send** `[🦀 Rust]`

  * Envoyer un message vers un endpoint.
  * Valider les permissions.
  * Vérifier la disponibilité du canal.

* [ ] **OS-180 — Implement Channel Receive** `[🦀 Rust]`

  * Recevoir un message.
  * Valider l'accès au channel.
  * Gérer le blocking.

* [ ] **OS-181 — Implement Channel Close** `[🦀 Rust]`

  * Fermer proprement un endpoint.
  * Réveiller les processus bloqués.
  * Nettoyer les ressources.

---

### Pipes

* [ ] **OS-182 — Define Pipe Model** `[🦀 Rust]`

  * Définir un pipe unidirectionnel.
  * Définir reader / writer.
  * Définir le lifecycle.

* [ ] **OS-183 — Implement Pipe Read** `[🦀 Rust]`

  * Lire les données.
  * Gérer les buffers vides.
  * Bloquer si nécessaire.

* [ ] **OS-184 — Implement Pipe Write** `[🦀 Rust]`

  * Écrire les données.
  * Gérer les buffers pleins.
  * Bloquer si nécessaire.

* [ ] **OS-185 — Implement Pipe Process Integration** `[🦀 Rust]`

  * Connecter un pipe à deux processus.
  * Tester la communication parent/enfant.

---

### Shared Memory

* [ ] **OS-186 — Define Shared Memory Model** `[📄 Markdown + 🦀 Rust]`

  * Définir les règles de mémoire partagée.
  * Définir les permissions.
  * Définir le lifecycle des régions partagées.

* [ ] **OS-187 — Implement Shared Memory Region** `[🦀 Rust]`

  * Créer une région mémoire partagée.
  * Mapper la région dans plusieurs address spaces.
  * Vérifier les permissions.

* [ ] **OS-188 — Implement Shared Memory Capability Control** `[🦀 Rust]`

  * Exiger une capability dédiée.
  * Limiter les processus autorisés.
  * Empêcher les mappings arbitraires.

* [ ] **OS-189 — Implement Shared Memory Cleanup** `[🦀 Rust]`

  * Nettoyer les mappings.
  * Libérer les frames lorsque plus aucun processus ne les utilise.

---

### Synchronization

* [ ] **OS-190 — Define Synchronization Primitives** `[🦀 Rust]`

  * Définir :

    * mutex ;
    * semaphore ;
    * condition variable ;
    * wait queue.

* [ ] **OS-191 — Implement Kernel Mutex** `[🦀 Rust]`

  * Lock.
  * Unlock.
  * Blocking.
  * Wake-up.

* [ ] **OS-192 — Implement Semaphore** `[🦀 Rust]`

  * `wait`.
  * `signal`.
  * Blocking.
  * Wake-up.

* [ ] **OS-193 — Implement Wait Queues** `[🦀 Rust]`

  * Ajouter des queues de processus bloqués.
  * Intégrer avec le scheduler.
  * Garantir le réveil correct.

* [ ] **OS-194 — Synchronization Stress Tests** `[🦀 Rust]`

  * Concurrence.
  * Contention.
  * Deadlock scenarios.
  * Wake-up ordering.

---

### IPC Capability Security

* [ ] **OS-195 — Define IPC Capabilities** `[🦀 Rust]`

  * Définir :

    * `IPC_CREATE`
    * `IPC_SEND`
    * `IPC_RECEIVE`
    * `IPC_CONNECT`
    * `IPC_SHARE_MEMORY`

* [ ] **OS-196 — Implement IPC Capability Checks** `[🦀 Rust]`

  * Vérifier les capabilities lors des opérations IPC.
  * Default deny.
  * Vérifier le scope.

* [ ] **OS-197 — Implement Process IPC Isolation** `[🦀 Rust]`

  * Empêcher l'accès aux endpoints non autorisés.
  * Empêcher la découverte arbitraire des channels.

* [ ] **OS-198 — Test IPC Privilege Escalation** `[🦀 Rust]`

  * Accès sans capability.
  * Endpoint forgé.
  * Channel inexistant.
  * Capability insuffisante.
  * Accès à la mémoire partagée d'un autre processus.

---

### IPC Syscalls

* [ ] **OS-199 — Implement `sys_ipc_create`** `[🦀 Rust]`

  * Créer un endpoint IPC.
  * Retourner un identifiant contrôlé par le kernel.

* [ ] **OS-200 — Implement `sys_ipc_send`** `[🦀 Rust]`

  * Envoyer un message.
  * Valider le buffer user.
  * Vérifier la capability.

* [ ] **OS-201 — Implement `sys_ipc_receive`** `[🦀 Rust]`

  * Recevoir un message.
  * Valider le buffer destination.
  * Gérer le blocking.

* [ ] **OS-202 — Implement `sys_ipc_close`** `[🦀 Rust]`

  * Fermer un endpoint.
  * Nettoyer les ressources.

* [ ] **OS-203 — Implement `sys_shared_memory_map`** `[🦀 Rust]`

  * Mapper une région partagée.
  * Vérifier les capabilities.
  * Vérifier les permissions mémoire.

---

### Python Reference Model

* [ ] **OS-204 — Implement Python IPC Model** `[🐍 Python]`

  * Simuler les endpoints.
  * Simuler les channels.
  * Simuler les messages.

* [ ] **OS-205 — Implement Python Message Queue** `[🐍 Python]`

  * FIFO.
  * Blocking.
  * Send / receive.

* [ ] **OS-206 — Implement Python Shared Memory Model** `[🐍 Python]`

  * Simuler les régions partagées.
  * Permissions.
  * Lifecycle.

* [ ] **OS-207 — Implement Python Synchronization Model** `[🐍 Python]`

  * Mutex.
  * Semaphore.
  * Wait queues.

* [ ] **OS-208 — Cross-Implementation IPC Tests** `[🐍 Python + 🦀 Rust]`

  * Comparer les comportements.
  * Vérifier les invariants.
  * Tester les mêmes scénarios.

---

### Scheduler Integration

* [ ] **OS-209 — Integrate IPC Blocking with Scheduler** `[🦀 Rust]`

  * Bloquer un processus sur `receive`.
  * Réveiller le processus à l'arrivée d'un message.
  * Réintégrer le processus dans `READY`.

* [ ] **OS-210 — Integrate IPC Wake-up with Scheduler** `[🦀 Rust]`

  * Définir les règles de wake-up.
  * Gérer plusieurs processus en attente.

* [ ] **OS-211 — IPC Scheduler Integration Tests** `[🦀 Rust]`

  * Processus bloqué.
  * Message reçu.
  * Wake-up.
  * Rescheduling.
  * Terminaison pendant un blocage.

---

### Agent Communication

* [ ] **OS-212 — Define Agent IPC Contract** `[📄 Markdown]`

  * Définir comment deux agents communiquent.
  * Définir les primitives disponibles.
  * Ne pas introduire de dépendance directe à MCP dans le kernel.

* [ ] **OS-213 — Implement Agent Channel** `[🦀 Rust]`

  * Créer un channel entre deux processus agents.
  * Appliquer les capabilities.

* [ ] **OS-214 — Implement Agent Message API** `[🦀 Rust]`

  * API user-space pour envoyer / recevoir des messages.
  * Encapsuler les syscalls IPC.

* [ ] **OS-215 — Agent-to-Agent Communication Test** `[🦀 Rust]`

  * Agent A envoie un message.
  * Agent B reçoit.
  * Vérifier les permissions.
  * Vérifier l'isolation.

---

### MCP User-Space Integration

* [ ] **OS-216 — Define MCP-over-IPC Architecture** `[📄 Markdown]`

  * Documenter la relation entre IPC kernel et MCP.
  * MCP reste user-space.
  * Le transport peut utiliser les primitives IPC du kernel.

* [ ] **OS-217 — Implement User-Space MCP IPC Adapter** `[🦀 Rust]`

  * Adapter un transport MCP vers les primitives IPC.
  * Aucun code MCP dans le kernel.

* [ ] **OS-218 — MCP IPC Integration Test** `[🦀 Rust]`

  * Agent → IPC → MCP runtime.
  * Vérifier les permissions.
  * Vérifier les messages.
  * Vérifier les erreurs.

---

### IPC Observability

* [ ] **OS-219 — Implement IPC Audit Events** `[🦀 Rust]`

  * Logger :

    * création ;
    * connexion ;
    * send ;
    * receive ;
    * close ;
    * deny.

* [ ] **OS-220 — Define IPC Metrics** `[🦀 Rust]`

  * Messages envoyés.
  * Messages reçus.
  * Taille des messages.
  * Channels actifs.
  * Processus bloqués.

* [ ] **OS-221 — IPC Observability Tests** `[🦀 Rust + 🐍 Python]`

  * Vérifier les événements.
  * Vérifier les compteurs.
  * Vérifier les décisions `ALLOW` / `DENY`.

---

### IPC Stress & Security Tests

* [ ] **OS-222 — IPC Throughput Benchmark** `[🦀 Rust]`

  * Mesurer le débit des messages.
  * Mesurer la latence.
  * Mesurer le coût syscall → IPC.

* [ ] **OS-223 — IPC Concurrency Stress Test** `[🦀 Rust]`

  * Nombreux producteurs.
  * Nombreux consommateurs.
  * Channels concurrents.
  * Blocking / wake-up.

* [ ] **OS-224 — IPC Fuzzing** `[🦀 Rust]`

  * Fuzzer les messages.
  * Fuzzer les tailles.
  * Fuzzer les endpoints.
  * Fuzzer les IDs.
  * Vérifier l'absence de crash kernel.

* [ ] **OS-225 — IPC Security Regression Suite** `[🦀 Rust + 🐍 Python]`

  * Isolation.
  * Capabilities.
  * Invalid endpoints.
  * Invalid buffers.
  * Shared memory violations.
  * Privilege escalation.

---

### Definition of Done

* [ ] IPC architecture définie.
* [ ] Message passing fonctionnel.
* [ ] Channels fonctionnels.
* [ ] Pipes fonctionnels.
* [ ] Shared memory fonctionnelle.
* [ ] Mutex / semaphore / wait queues.
* [ ] IPC intégré au scheduler.
* [ ] IPC protégé par capabilities.
* [ ] Syscalls IPC fonctionnels.
* [ ] Python reference model.
* [ ] Tests Python / Rust.
* [ ] IPC fuzzing.
* [ ] IPC stress tests.
* [ ] Audit et observabilité.
* [ ] Communication agent-to-agent fonctionnelle.
* [ ] MCP utilisable au-dessus de l'IPC sans faire partie du kernel.

**Principe fondamental :**

> **Le kernel fournit les primitives de communication.**
>
> **Les applications choisissent les protocoles qu'elles utilisent au-dessus.**
>
> **MCP est un protocole user-space ; IPC est une primitive kernel.**

```text
                    USER SPACE
┌─────────────────────────────────────────────┐
│                                             │
│   Agent A                Agent B             │
│      │                      ▲               │
│      │                      │               │
│      ▼                      │               │
│  MCP Runtime ───────── MCP Runtime          │
│      │                      ▲               │
│      └──────── IPC Adapter ─┘               │
│                    │                        │
└────────────────────┼────────────────────────┘
                     │
                  SYSCALL
                     │
─────────────────────┼─────────────────────────
                     │
┌────────────────────▼────────────────────────┐
│                  KERNEL                     │
│                                             │
│              IPC Manager                   │
│                  │                          │
│       ┌──────────┼──────────┐               │
│       ▼          ▼          ▼               │
│    Channel     Pipe    Shared Memory        │
│       │          │          │               │
│       └──────────┴──────────┘               │
│                  │                          │
│            Capability Check                │
│                  │                          │
│              Scheduler                     │
│                                             │
└─────────────────────────────────────────────┘
```

## Sous-phase 14.6 — VFS & Filesystem

> **Rôle de ce fichier** : Ce fichier est le sixième de la **Phase 14 — Noyau Agentique**. Il définit la sous-phase **VFS & Filesystem**, responsable de fournir au kernel une abstraction uniforme pour accéder aux fichiers, répertoires et systèmes de fichiers.
>
> **Principe fondamental** : le kernel ne doit pas dépendre d'un filesystem particulier. Le **VFS (Virtual File System)** fournit une interface commune entre les syscalls et les implémentations concrètes des filesystems.
>
> **Architecture** :
>
> ```text
>                    USER SPACE
>                         │
>                    sys_open()
>                    sys_read()
>                    sys_write()
>                    sys_close()
>                         │
>                         ▼
>                    ┌───────┐
>                    │  VFS  │
>                    └───┬───┘
>                        │
>              ┌─────────┼─────────┐
>              ▼         ▼         ▼
>           TmpFS     SimpleFS   Future FS
>              │         │         │
>              └─────────┼─────────┘
>                        ▼
>                 Block Device
>                        │
>                        ▼
>                      Disk
> ```
>
> **Objectif initial** : commencer avec un filesystem simple et maîtrisable avant d'introduire un filesystem plus complexe.
>
> **Langages** :
>
> * 🦀 **Rust** : VFS, filesystem et logique kernel.
> * 🔧 **Assembly** : uniquement pour les opérations hardware/architecture qui le nécessitent.
> * 🐍 **Python** : modèle de référence / simulation.
> * 🧪 **Rust + Python** : validation comportementale.
>
> **Dépendances** :
>
> * **14.1 — Kernel Foundation & Process Scheduler**
> * **14.2 — Capability & Security Engine**
> * **14.3 — Memory Manager**
> * **14.4 — Syscall Layer**
> * **14.5 — IPC & Message Passing**
>
> **Prochaine étape** : **Sous-phase 14.7 — Device Drivers**.

---

### VFS Architecture

* [ ] **OS-226 — Define VFS Architecture** `[📄 Markdown]`

  * Définir les responsabilités du VFS.
  * Définir la frontière VFS / filesystem.
  * Définir la frontière VFS / block device.
  * Documenter les invariants.

* [ ] **OS-227 — Define VFS Object Model** `[🦀 Rust]`

  * Définir :

    * `Vfs`
    * `File`
    * `Directory`
    * `Inode`
    * `Mount`
    * `Superblock`
    * `FileSystem`

* [ ] **OS-228 — Define Filesystem Interface** `[🦀 Rust]`

  * Définir le trait/interface commun aux filesystems.
  * Définir :

    * mount ;
    * unmount ;
    * open ;
    * read ;
    * write ;
    * create ;
    * remove ;
    * stat.

* [ ] **OS-229 — Define VFS Error Model** `[🦀 Rust]`

  * Définir les erreurs :

    * `NotFound`
    * `PermissionDenied`
    * `AlreadyExists`
    * `NotDirectory`
    * `IsDirectory`
    * `InvalidPath`
    * `ReadOnly`
    * `NoSpace`

---

### Inodes & Metadata

* [ ] **OS-230 — Implement Inode Model** `[🦀 Rust]`

  * Définir l'identité d'un fichier.
  * Définir le type :

    * regular file ;
    * directory ;
    * symlink ;
    * device.
  * Définir les métadonnées.

* [ ] **OS-231 — Implement File Metadata** `[🦀 Rust]`

  * Taille.
  * Permissions.
  * Owner.
  * Timestamps.
  * Type de fichier.

* [ ] **OS-232 — Implement Inode Lookup** `[🦀 Rust]`

  * Recherche par inode.
  * Validation de l'existence.
  * Gestion du cache futur.

* [ ] **OS-233 — Implement File Metadata Tests** `[🦀 Rust]`

  * Création.
  * Modification.
  * Suppression.
  * Permissions.
  * Taille.
  * Timestamps.

---

### Paths & Directories

* [ ] **OS-234 — Implement Path Parser** `[🦀 Rust]`

  * Parser :

    * `/`
    * `.`
    * `..`
    * chemins absolus ;
    * chemins relatifs.
  * Normaliser les chemins.

* [ ] **OS-235 — Implement Directory Model** `[🦀 Rust]`

  * Créer un répertoire.
  * Ajouter une entrée.
  * Supprimer une entrée.
  * Rechercher une entrée.

* [ ] **OS-236 — Implement Directory Traversal** `[🦀 Rust]`

  * Résoudre `/a/b/c`.
  * Traverser les inodes.
  * Gérer les chemins invalides.

* [ ] **OS-237 — Implement Current Working Directory** `[🦀 Rust]`

  * Associer un répertoire courant à chaque processus.
  * Supporter les chemins relatifs.

* [ ] **OS-238 — Implement Root Filesystem** `[🦀 Rust]`

  * Définir `/`.
  * Monter le filesystem racine.
  * Garantir qu'un processus dispose d'un root valide.

---

### File Descriptors

* [ ] **OS-239 — Integrate VFS with File Descriptors** `[🦀 Rust]`

  * Associer un `FileDescriptor` à un objet VFS.
  * Gérer le lifecycle.

* [ ] **OS-240 — Implement File Open** `[🦀 Rust]`

  * Ouvrir un fichier.
  * Résoudre le path.
  * Vérifier les permissions.
  * Retourner un FD.

* [ ] **OS-241 — Implement File Close** `[🦀 Rust]`

  * Fermer un FD.
  * Libérer les références.

* [ ] **OS-242 — Implement File Read** `[🦀 Rust]`

  * Lire depuis un fichier.
  * Maintenir la position.
  * Vérifier les permissions.

* [ ] **OS-243 — Implement File Write** `[🦀 Rust]`

  * Écrire dans un fichier.
  * Maintenir la position.
  * Vérifier les permissions.

* [ ] **OS-244 — Implement File Seek** `[🦀 Rust]`

  * Modifier la position de lecture/écriture.
  * Vérifier les limites.

---

### SimpleFS

* [ ] **OS-245 — Define SimpleFS Format** `[📄 Markdown]`

  * Définir le layout disque.
  * Définir le superblock.
  * Définir les inodes.
  * Définir les data blocks.
  * Définir les free blocks.

  Exemple :

  ```text
  Disk
  ├── Superblock
  ├── Inode Table
  ├── Free Block Bitmap
  └── Data Blocks
  ```

* [ ] **OS-246 — Implement SimpleFS Superblock** `[🦀 Rust]`

  * Lire le superblock.
  * Écrire le superblock.
  * Valider la version du filesystem.

* [ ] **OS-247 — Implement SimpleFS Block Allocator** `[🦀 Rust]`

  * Allouer un block.
  * Libérer un block.
  * Maintenir le bitmap.
  * Détecter l'épuisement.

* [ ] **OS-248 — Implement SimpleFS Inode Table** `[🦀 Rust]`

  * Allouer un inode.
  * Libérer un inode.
  * Lire un inode.
  * Écrire un inode.

* [ ] **OS-249 — Implement SimpleFS File Storage** `[🦀 Rust]`

  * Associer les inodes aux data blocks.
  * Lire les blocks.
  * Écrire les blocks.

* [ ] **OS-250 — Implement SimpleFS Directories** `[🦀 Rust]`

  * Créer des directories.
  * Ajouter des entrées.
  * Supprimer des entrées.
  * Rechercher des entrées.

* [ ] **OS-251 — Implement SimpleFS File Operations** `[🦀 Rust]`

  * Create.
  * Open.
  * Read.
  * Write.
  * Delete.

---

### Block Device Abstraction

* [ ] **OS-252 — Define Block Device Interface** `[🦀 Rust]`

  * Définir `BlockDevice`.
  * Lire un block.
  * Écrire un block.
  * Définir la taille des blocks.

* [ ] **OS-253 — Implement RAM Block Device** `[🦀 Rust]`

  * Simuler un disque en mémoire.
  * Permettre les tests du filesystem sans hardware.

* [ ] **OS-254 — Implement QEMU Disk Block Device** `[🦀 Rust]`

  * Connecter le filesystem à un disque virtuel QEMU.
  * Lire/écrire les blocks.

* [ ] **OS-255 — Block Device Integration Tests** `[🦀 Rust]`

  * Read.
  * Write.
  * Invalid block.
  * Out-of-range access.
  * Concurrent access.

---

### Mount System

* [ ] **OS-256 — Define Mount Model** `[🦀 Rust]`

  * Définir `Mount`.
  * Associer un filesystem à un path.
  * Gérer les mounts actifs.

* [ ] **OS-257 — Implement Filesystem Mount** `[🦀 Rust]`

  * Monter un filesystem.
  * Vérifier le superblock.
  * Ajouter le mount au VFS.

* [ ] **OS-258 — Implement Filesystem Unmount** `[🦀 Rust]`

  * Démonter un filesystem.
  * Vérifier les fichiers ouverts.
  * Nettoyer les ressources.

* [ ] **OS-259 — Implement Mount Namespace Foundation** `[🦀 Rust]`

  * Préparer la possibilité d'avoir des namespaces de mounts par processus.
  * Définir les règles d'héritage.

---

### Permissions & Capabilities

* [ ] **OS-260 — Integrate Filesystem Permissions** `[🦀 Rust]`

  * Vérifier les permissions de lecture.
  * Vérifier les permissions d'écriture.
  * Vérifier les permissions d'exécution.

* [ ] **OS-261 — Integrate Filesystem Capabilities** `[🦀 Rust]`

  * Associer les opérations VFS aux capabilities.

  ```text
  open(read)
      → FILE_READ

  open(write)
      → FILE_WRITE

  create()
      → FILE_CREATE

  remove()
      → FILE_DELETE
  ```

* [ ] **OS-262 — Implement Path Scope Enforcement** `[🦀 Rust]`

  * Limiter les accès à un scope.
  * Empêcher `../` de sortir du scope autorisé.
  * Garantir la canonicalisation avant validation.

* [ ] **OS-263 — Filesystem Security Tests** `[🦀 Rust]`

  * Unauthorized read.
  * Unauthorized write.
  * Unauthorized delete.
  * Path traversal.
  * Capability escalation.
  * Cross-process filesystem access.

---

### VFS Syscalls

* [ ] **OS-264 — Implement `sys_open`** `[🦀 Rust]`

  * Résoudre le path.
  * Vérifier les capabilities.
  * Créer un FD.

* [ ] **OS-265 — Implement `sys_read`** `[🦀 Rust]`

  * Lire depuis un FD.
  * Valider le buffer user.
  * Vérifier les permissions.

* [ ] **OS-266 — Implement `sys_write`** `[🦀 Rust]`

  * Écrire depuis un buffer user.
  * Vérifier les permissions.
  * Vérifier l'espace disponible.

* [ ] **OS-267 — Implement `sys_close`** `[🦀 Rust]`

  * Fermer le FD.
  * Nettoyer les références.

* [ ] **OS-268 — Implement `sys_stat`** `[🦀 Rust]`

  * Retourner les metadata d'un fichier.

* [ ] **OS-269 — Implement `sys_mkdir`** `[🦀 Rust]`

  * Créer un répertoire.
  * Vérifier les capabilities.

* [ ] **OS-270 — Implement `sys_unlink`** `[🦀 Rust]`

  * Supprimer un fichier.
  * Vérifier les permissions.
  * Gérer les références restantes.

* [ ] **OS-271 — Implement `sys_readdir`** `[🦀 Rust]`

  * Lire les entrées d'un répertoire.
  * Valider le FD.

---

### Python Reference Filesystem

* [ ] **OS-272 — Implement Python VFS Model** `[🐍 Python]`

  * Simuler :

    * fichiers ;
    * directories ;
    * inodes ;
    * paths ;
    * mounts.

* [ ] **OS-273 — Implement Python SimpleFS** `[🐍 Python]`

  * Simuler le layout disque.
  * Simuler les blocks.
  * Simuler les inodes.
  * Simuler les opérations fichier.

* [ ] **OS-274 — Implement Python Permission Model** `[🐍 Python]`

  * Permissions.
  * Capabilities.
  * Path scopes.

* [ ] **OS-275 — Cross-Implementation Filesystem Tests** `[🐍 Python + 🦀 Rust]`

  * Comparer Python / Rust.
  * Vérifier les mêmes résultats.
  * Vérifier les mêmes erreurs.
  * Vérifier les mêmes invariants.

---

### Agent Workspace

* [ ] **OS-276 — Define Agent Workspace Model** `[📄 Markdown]`

  * Définir le filesystem visible par un agent.
  * Définir son workspace.
  * Définir les limites de son accès.

  Exemple :

  ```text
  /agents/
      agent-42/
          workspace/
          tmp/
          output/
  ```

* [ ] **OS-277 — Implement Agent Workspace Mount** `[🦀 Rust]`

  * Monter un workspace dédié.
  * Associer le workspace au processus agent.

* [ ] **OS-278 — Implement Agent Filesystem Isolation** `[🦀 Rust]`

  * Limiter l'agent à son scope.
  * Empêcher l'accès aux fichiers kernel.
  * Empêcher l'accès aux autres workspaces.

* [ ] **OS-279 — Agent Filesystem Security Tests** `[🦀 Rust]`

  * Read allowed.
  * Write allowed.
  * Read forbidden.
  * Write forbidden.
  * Path traversal.
  * Cross-agent access.

---

### Filesystem Consistency

* [ ] **OS-280 — Implement Filesystem Flush** `[🦀 Rust]`

  * Synchroniser les données vers le block device.
  * Préparer la future gestion du cache.

* [ ] **OS-281 — Implement Filesystem Recovery Checks** `[🦀 Rust]`

  * Détecter un filesystem incohérent.
  * Vérifier les blocks.
  * Vérifier les inodes.

* [ ] **OS-282 — Filesystem Corruption Tests** `[🦀 Rust]`

  * Superblock invalide.
  * Inode invalide.
  * Block invalide.
  * Bitmap incohérent.

---

### VFS Observability

* [ ] **OS-283 — Implement Filesystem Audit Events** `[🦀 Rust]`

  * Logger :

    * open ;
    * read ;
    * write ;
    * mkdir ;
    * unlink ;
    * mount ;
    * unmount ;
    * deny.

* [ ] **OS-284 — Define Filesystem Metrics** `[🦀 Rust]`

  * Filesystem size.
  * Used blocks.
  * Free blocks.
  * Open files.
  * Active mounts.
  * Read/write operations.

* [ ] **OS-285 — Filesystem Observability Tests** `[🦀 Rust + 🐍 Python]`

  * Vérifier les événements.
  * Vérifier les compteurs.
  * Vérifier les décisions de sécurité.

---

### Filesystem Stress Tests

* [ ] **OS-286 — Filesystem Throughput Benchmark** `[🦀 Rust]`

  * Read throughput.
  * Write throughput.
  * Small files.
  * Large files.

* [ ] **OS-287 — Filesystem Stress Test** `[🦀 Rust]`

  * Création massive de fichiers.
  * Création massive de directories.
  * Allocations/libérations répétées.
  * Épuisement des blocks.

* [ ] **OS-288 — Filesystem Fuzzing** `[🦀 Rust]`

  * Fuzzer le parser de paths.
  * Fuzzer les metadata.
  * Fuzzer les structures disque.
  * Fuzzer les opérations VFS.

* [ ] **OS-289 — Filesystem Regression Suite** `[🦀 Rust + 🐍 Python]`

  * Centraliser les invariants.
  * Vérifier les régressions.
  * Comparer avec le modèle Python.

---

### Definition of Done

* [ ] VFS architecture définie.
* [ ] Filesystem interface définie.
* [ ] Inodes fonctionnels.
* [ ] Directories fonctionnels.
* [ ] Path resolution fonctionnelle.
* [ ] File descriptors intégrés.
* [ ] SimpleFS fonctionnel.
* [ ] Block device abstraction.
* [ ] RAM block device.
* [ ] QEMU disk support.
* [ ] Mount / unmount.
* [ ] Permissions filesystem.
* [ ] Capability checks.
* [ ] Path scope enforcement.
* [ ] VFS syscalls.
* [ ] Python reference model.
* [ ] Tests Python / Rust.
* [ ] Agent workspace.
* [ ] Agent filesystem isolation.
* [ ] Filesystem audit.
* [ ] Stress tests.
* [ ] Fuzzing.
* [ ] Recovery / consistency checks.

**Principe fondamental :**

> **Le VFS abstrait le stockage.**
>
> **Le filesystem organise les données.**
>
> **Le block device fournit le stockage brut.**
>
> **Le kernel contrôle l'accès à travers les syscalls et les capabilities.**
>
> **Les agents ne voient qu'un filesystem correspondant à leurs permissions et à leur scope.**

```text
                         USER SPACE
                              │
             ┌────────────────┼────────────────┐
             │                │                │
           Agent A          Agent B          Shell
             │                │                │
             └────────────────┼────────────────┘
                              │
                           Syscalls
                              │
══════════════════════════════╪════════════════════════
                              │
                         KERNEL SPACE
                              │
                         ┌────▼────┐
                         │   VFS   │
                         └────┬────┘
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
              SimpleFS      TmpFS       FutureFS
                 │            │            │
                 └────────────┼────────────┘
                              │
                       Block Device
                              │
                              ▼
                             Disk
```


## Sous-phase 14.7 — Device Drivers

> **Rôle de ce fichier** : Ce fichier est le septième de la **Phase 14 — Noyau Agentique**. Il définit la sous-phase **Device Drivers**, responsable de l'abstraction et de la gestion des périphériques matériels utilisés par le kernel.
>
> **Principe fondamental** : le kernel ne doit pas dépendre directement d'un hardware particulier. Les drivers exposent des interfaces génériques permettant aux autres sous-systèmes du kernel d'utiliser les périphériques sans connaître leur implémentation matérielle.
>
> **Architecture** :
>
> ```text
>                         KERNEL
>                            │
>                     Device Manager
>                            │
>              ┌─────────────┼─────────────┐
>              ▼             ▼             ▼
>          Console        Storage        Network
>           Driver         Driver         Driver
>              │             │             │
>              ▼             ▼             ▼
>          Keyboard         Disk           NIC
> ```
>
> **Principe d'abstraction** :
>
> ```text
> Kernel subsystem
>        │
>        ▼
> Generic Device Interface
>        │
>        ▼
> Hardware-specific Driver
>        │
>        ▼
> Hardware
> ```
>
> **Langages** :
>
> * 🦀 **Rust** : drivers et abstractions kernel.
> * 🔧 **Assembly** : accès CPU/interruptions/port I/O lorsque nécessaire.
> * 🐍 **Python** : modèle de référence et simulation des devices.
> * 🧪 **Rust + Python** : validation comportementale.
>
> **Dépendances** :
>
> * **14.1 — Kernel Foundation & Process Scheduler**
> * **14.2 — Capability & Security Engine**
> * **14.3 — Memory Manager**
> * **14.4 — Syscall Layer**
> * **14.5 — IPC & Message Passing**
> * **14.6 — VFS & Filesystem**
>
> **Prochaine étape** : **Sous-phase 14.8 — TTY & Terminal**.

---

### Device Architecture

* [ ] **OS-290 — Define Device Architecture** `[📄 Markdown]`

  * Définir les responsabilités du Device Manager.
  * Définir les catégories de devices.
  * Définir la frontière kernel / driver.
  * Définir les invariants de sécurité.

* [ ] **OS-291 — Define Device Model** `[🦀 Rust]`

  * Définir `Device`.
  * Définir `DeviceId`.
  * Définir `DeviceType`.
  * Définir le lifecycle d'un device.

* [ ] **OS-292 — Define Device Driver Interface** `[🦀 Rust]`

  * Définir le trait `DeviceDriver`.
  * Définir :

    * `probe`
    * `init`
    * `read`
    * `write`
    * `ioctl`
    * `shutdown`

* [ ] **OS-293 — Implement Device Registry** `[🦀 Rust]`

  * Enregistrer les devices.
  * Lookup par ID.
  * Lookup par type.
  * Gestion des devices actifs/inactifs.

---

### Hardware Discovery

* [ ] **OS-294 — Define Hardware Discovery Layer** `[🦀 Rust]`

  * Définir comment le kernel découvre le hardware.
  * Préparer les mécanismes spécifiques à la plateforme.

* [ ] **OS-295 — Implement Platform Information Discovery** `[🦀 Rust]`

  * CPU.
  * Mémoire.
  * Devices disponibles.
  * Informations de boot.

* [ ] **OS-296 — Implement PCI Device Discovery** `[🦀 Rust + 🔧 Assembly]`

  * Détecter les périphériques PCI.
  * Lire les configurations PCI.
  * Identifier les devices.

* [ ] **OS-297 — PCI Device Tests** `[🦀 Rust]`

  * Devices connus.
  * Device absent.
  * Configuration invalide.
  * Plusieurs devices.

---

### Interrupt Controller

* [ ] **OS-298 — Define Interrupt Controller Interface** `[🦀 Rust]`

  * Définir l'abstraction générique.
  * Associer interruptions et devices.

* [ ] **OS-299 — Implement Interrupt Controller Support** `[🦀 Rust + 🔧 Assembly]`

  * Initialiser le contrôleur d'interruptions.
  * Configurer les lignes d'interruption.
  * Router les interruptions vers les drivers.

* [ ] **OS-300 — Implement Device Interrupt Registration** `[🦀 Rust]`

  * Permettre à un driver d'enregistrer son handler.
  * Vérifier les collisions.
  * Nettoyer les handlers à la désactivation.

* [ ] **OS-301 — Interrupt Safety Tests** `[🦀 Rust]`

  * Interrupt inconnue.
  * Interrupt multiple.
  * Handler absent.
  * Handler désactivé.

---

### Timer Device

* [ ] **OS-302 — Define Timer Device Interface** `[🦀 Rust]`

  * Définir l'abstraction timer.
  * Définir les opérations nécessaires au scheduler.

* [ ] **OS-303 — Implement Hardware Timer Driver** `[🦀 Rust + 🔧 Assembly]`

  * Initialiser le timer.
  * Générer les ticks.
  * Configurer la fréquence.

* [ ] **OS-304 — Integrate Timer with Scheduler** `[🦀 Rust]`

  * Connecter le timer au scheduler.
  * Déclencher la preemption.

* [ ] **OS-305 — Timer Driver Tests** `[🦀 Rust]`

  * Fréquence.
  * Ticks.
  * Interruptions.
  * Scheduler integration.

---

### Console Device

* [ ] **OS-306 — Define Console Device Interface** `[🦀 Rust]`

  * Définir l'interface console.
  * Read / write.
  * Initialisation.

* [ ] **OS-307 — Implement Early Console Driver** `[🦀 Rust]`

  * Permettre au kernel de produire des logs très tôt au boot.
  * Supporter une console minimale.

* [ ] **OS-308 — Implement Console Output Buffer** `[🦀 Rust]`

  * Bufferiser les sorties.
  * Gérer les écritures concurrentes.
  * Éviter les corruptions.

* [ ] **OS-309 — Console Driver Tests** `[🦀 Rust]`

  * Output.
  * Buffer.
  * Overflow.
  * Concurrent writes.

---

### Keyboard Device

* [ ] **OS-310 — Define Keyboard Driver Interface** `[🦀 Rust]`

  * Définir les événements clavier.
  * Key press.
  * Key release.
  * Scancode.

* [ ] **OS-311 — Implement Keyboard Driver** `[🦀 Rust + 🔧 Assembly]`

  * Initialiser le périphérique.
  * Lire les événements.
  * Traduire les scancodes.

* [ ] **OS-312 — Implement Keyboard Input Buffer** `[🦀 Rust]`

  * Buffer d'entrée.
  * Blocking read.
  * Wake-up des processus.

* [ ] **OS-313 — Keyboard Interrupt Integration** `[🦀 Rust]`

  * Connecter le clavier au système d'interruptions.
  * Transmettre les événements au TTY futur.

* [ ] **OS-314 — Keyboard Driver Tests** `[🦀 Rust]`

  * Key press.
  * Key release.
  * Buffer.
  * Overflow.
  * Invalid scancode.

---

### Storage Device

* [ ] **OS-315 — Define Block Device Interface** `[🦀 Rust]`

  * Définir l'interface générique.
  * Read block.
  * Write block.
  * Flush.

* [ ] **OS-316 — Implement RAM Block Device** `[🦀 Rust]`

  * Device de stockage en mémoire.
  * Support pour les tests.

* [ ] **OS-317 — Implement QEMU Storage Driver** `[🦀 Rust]`

  * Détecter le disque virtuel.
  * Lire les blocks.
  * Écrire les blocks.

* [ ] **OS-318 — Integrate Storage Driver with VFS** `[🦀 Rust]`

  * Connecter le block device au filesystem.
  * Permettre au VFS d'accéder au stockage.

* [ ] **OS-319 — Storage Driver Tests** `[🦀 Rust]`

  * Read.
  * Write.
  * Flush.
  * Invalid block.
  * Out-of-range.

---

### Network Device Foundation

* [ ] **OS-320 — Define Network Device Interface** `[🦀 Rust]`

  * Définir l'interface réseau générique.
  * Packet receive.
  * Packet transmit.

* [ ] **OS-321 — Define Network Device Buffer** `[🦀 Rust]`

  * Définir les buffers réseau.
  * Ownership des buffers.
  * Lifecycle.

* [ ] **OS-322 — Implement QEMU Network Device Foundation** `[🦀 Rust]`

  * Détecter le device réseau virtuel.
  * Initialiser le driver.
  * Recevoir/transmettre des buffers.

* [ ] **OS-323 — Network Interrupt Integration** `[🦀 Rust]`

  * Connecter le device réseau au système d'interruptions.
  * Réveiller les processus concernés.

> La stack TCP/IP complète sera traitée dans une future sous-phase Network Stack.

---

### Device Memory Mapping

* [ ] **OS-324 — Define MMIO Model** `[🦀 Rust]`

  * Définir Memory-Mapped I/O.
  * Définir les régions réservées aux devices.
  * Définir les permissions.

* [ ] **OS-325 — Implement MMIO Mapping** `[🦀 Rust]`

  * Mapper les régions hardware.
  * Vérifier les adresses.
  * Vérifier les permissions.

* [ ] **OS-326 — Implement Device Memory Protection** `[🦀 Rust]`

  * Empêcher les processus user-space d'accéder directement au hardware.
  * Exiger une capability appropriée.

* [ ] **OS-327 — MMIO Security Tests** `[🦀 Rust]`

  * Adresse invalide.
  * Mapping non autorisé.
  * Accès user-space.
  * Accès sans capability.

---

### Device Capabilities

* [ ] **OS-328 — Define Device Capabilities** `[🦀 Rust]`

  * Définir :

    * `DEVICE_READ`
    * `DEVICE_WRITE`
    * `DEVICE_CONTROL`
    * `DEVICE_MAP`

* [ ] **OS-329 — Implement Device Capability Enforcement** `[🦀 Rust]`

  * Vérifier les capabilities avant chaque opération privilégiée.

* [ ] **OS-330 — Implement Device Ownership** `[🦀 Rust]`

  * Associer un device à un propriétaire kernel ou processus.
  * Empêcher les accès concurrents non autorisés.

* [ ] **OS-331 — Device Security Tests** `[🦀 Rust + 🐍 Python]`

  * Accès sans capability.
  * Device inexistant.
  * Device déjà utilisé.
  * Accès inter-processus.

---

### Device Lifecycle

* [ ] **OS-332 — Implement Device Initialization Lifecycle** `[🦀 Rust]`

  * `discover`
  * `probe`
  * `init`
  * `ready`

* [ ] **OS-333 — Implement Device Shutdown Lifecycle** `[🦀 Rust]`

  * `shutdown`
  * Flush.
  * Nettoyage.
  * Libération des ressources.

* [ ] **OS-334 — Device Failure Handling** `[🦀 Rust]`

  * Détection d'un driver défaillant.
  * Marquage du device indisponible.
  * Nettoyage sécurisé.

* [ ] **OS-335 — Device Lifecycle Tests** `[🦀 Rust]`

  * Init.
  * Shutdown.
  * Failure.
  * Reinitialization.

---

### Python Reference Model

* [ ] **OS-336 — Implement Python Device Model** `[🐍 Python]`

  * Simuler les devices.
  * Simuler le lifecycle.
  * Simuler les opérations.

* [ ] **OS-337 — Implement Python Device Registry** `[🐍 Python]`

  * Enregistrement.
  * Lookup.
  * Activation.
  * Désactivation.

* [ ] **OS-338 — Implement Python Interrupt Model** `[🐍 Python]`

  * Simuler les interruptions.
  * Simuler les handlers.
  * Simuler les événements devices.

* [ ] **OS-339 — Implement Python Block Device Model** `[🐍 Python]`

  * Simuler un disque.
  * Read / write.
  * Erreurs.

* [ ] **OS-340 — Cross-Implementation Device Tests** `[🐍 Python + 🦀 Rust]`

  * Comparer Python / Rust.
  * Vérifier les invariants.
  * Vérifier les erreurs.

---

### Driver Isolation

* [ ] **OS-341 — Define Driver Isolation Model** `[📄 Markdown]`

  * Définir les limites de confiance des drivers.
  * Identifier les opérations dangereuses.
  * Définir les futures possibilités de driver isolation.

* [ ] **OS-342 — Implement Driver Resource Ownership** `[🦀 Rust]`

  * Chaque driver possède explicitement ses ressources.
  * Empêcher les collisions.

* [ ] **OS-343 — Driver Resource Cleanup** `[🦀 Rust]`

  * Nettoyer les ressources lors d'un crash ou shutdown.
  * Libérer IRQ, MMIO et buffers.

* [ ] **OS-344 — Driver Isolation Tests** `[🦀 Rust]`

  * Ressource déjà utilisée.
  * Driver défaillant.
  * Cleanup incomplet.
  * Accès hors ownership.

---

### Agent Device Access

* [ ] **OS-345 — Define Agent Device Contract** `[📄 Markdown]`

  * Définir comment un agent peut accéder aux devices.
  * Aucun accès hardware implicite.
  * Accès uniquement via capabilities.

* [ ] **OS-346 — Implement Agent Device Capability Profile** `[🦀 Rust]`

  * Définir les profils :

    * no-device ;
    * console ;
    * storage ;
    * network ;
    * custom device.

* [ ] **OS-347 — Implement Agent Device Access API** `[🦀 Rust]`

  * Fournir les primitives user-space nécessaires.
  * Encapsuler les syscalls device.

* [ ] **OS-348 — Agent Device Isolation Tests** `[🦀 Rust]`

  * Agent sans device.
  * Agent avec console.
  * Agent avec réseau.
  * Accès non autorisé.

---

### Driver Testing

* [ ] **OS-349 — Driver Unit Test Framework** `[🦀 Rust]`

  * Tester les drivers sans hardware réel.
  * Mock devices.
  * Mock interrupts.

* [ ] **OS-350 — Driver Integration Test Harness** `[🦀 Rust + 🐚 Shell]`

  * Boot QEMU.
  * Détecter les devices.
  * Initialiser les drivers.
  * Vérifier leur état.

* [ ] **OS-351 — Driver Stress Tests** `[🦀 Rust]`

  * I/O répétées.
  * Interruptions fréquentes.
  * Plusieurs devices.
  * Épuisement des buffers.

* [ ] **OS-352 — Driver Fuzzing** `[🦀 Rust]`

  * Fuzzer les données entrantes.
  * Fuzzer les commandes.
  * Fuzzer les metadata devices.
  * Vérifier l'absence de crash kernel.

* [ ] **OS-353 — Driver Regression Suite** `[🦀 Rust + 🐍 Python]`

  * Centraliser les invariants.
  * Vérifier les régressions.
  * Comparer avec le modèle Python.

---

### Definition of Done

* [ ] Device architecture définie.
* [ ] Device registry fonctionnel.
* [ ] Hardware discovery fonctionnelle.
* [ ] Interrupt controller intégré.
* [ ] Timer driver fonctionnel.
* [ ] Console driver fonctionnel.
* [ ] Keyboard driver fonctionnel.
* [ ] Storage driver fonctionnel.
* [ ] Network device foundation fonctionnelle.
* [ ] MMIO support.
* [ ] Device capabilities.
* [ ] Device ownership.
* [ ] Device lifecycle.
* [ ] Driver resource cleanup.
* [ ] Python reference model.
* [ ] Tests Python / Rust.
* [ ] QEMU integration tests.
* [ ] Driver stress tests.
* [ ] Driver fuzzing.
* [ ] Agent device access contrôlé par capabilities.

**Principe fondamental :**

> **Le kernel possède et contrôle les devices.**
>
> **Les drivers traduisent les abstractions kernel en opérations hardware.**
>
> **Les processus user-space n'accèdent jamais directement au hardware.**
>
> **Un agent ne peut utiliser un device que s'il possède explicitement la capability correspondante.**

```text
                         USER SPACE
                              │
             ┌────────────────┼────────────────┐
             │                │                │
           Agent            Shell          Runtime
             │                │                │
             └────────────────┼────────────────┘
                              │
                           Syscalls
                              │
══════════════════════════════╪════════════════════════
                              │
                         KERNEL SPACE
                              │
                       Device Manager
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
       Console             Storage             Network
        Driver              Driver              Driver
          │                   │                   │
          ▼                   ▼                   ▼
       Keyboard              Disk                 NIC
```

**Invariant de sécurité :**

```text
Process
   │
   ▼
Syscall
   │
   ▼
Capability Check
   │
   ├── DENY ──► Error
   │
   ▼
Device Manager
   │
   ▼
Driver
   │
   ▼
Hardware
```


# 14.8 — TTY & Terminal

**Objectif** : fournir une abstraction terminal complète au-dessus des drivers clavier/console, des file descriptors et des syscalls, afin que les processus user-space puissent communiquer avec un terminal sans accéder directement au matériel.

**Principe** : le kernel fournit les primitives TTY et le contrôle des terminaux. La logique applicative — shell, commandes, agent runtime — reste en user-space.

---

## 14.8.1 — TTY Architecture

### OS-354 — Define TTY Architecture

Définir l'architecture générale du sous-système TTY.

**Requirements**

* définir la relation entre :

  * keyboard driver
  * console driver
  * TTY
  * file descriptors
  * processes
  * syscalls
* définir les responsabilités kernel/user-space
* documenter les flux `stdin/stdout/stderr`
* définir le modèle de terminal attaché à un processus
* documenter les interactions avec le scheduler et les processus bloqués

**Definition of Done**

* architecture documentée
* frontières kernel/user-space explicites
* flux d'entrée/sortie documentés
* aucun couplage avec le shell ou l'agent runtime

---

### OS-355 — Define TTY Data Model

Définir les structures représentant un TTY.

**Requirements**

* `TTY`
* `TTYId`
* input buffer
* output buffer
* foreground process/group
* terminal state
* terminal configuration
* référence vers console
* référence vers input device

**Definition of Done**

* modèle Rust défini
* invariants documentés
* états valides/invalides testés

---

### OS-356 — Define TTY Driver Interface

Créer l'interface générique permettant au kernel de gérer différents terminaux.

**Requirements**

* attach
* detach
* read input
* write output
* flush
* configure
* interrupt/input notification

**Definition of Done**

* trait/interface défini
* console TTY implémentable dessus
* aucune dépendance directe au keyboard hardware

---

### OS-357 — Implement TTY Registry

Créer le registre central des TTY.

**Requirements**

* création
* lookup par `TTYId`
* suppression
* enumeration
* lifecycle management
* validation des identifiants

**Definition of Done**

* registre fonctionnel
* IDs uniques
* cleanup correct
* tests unitaires complets

---

## 14.8.2 — Input Line Discipline

### OS-358 — Define Line Discipline

Définir la couche responsable du traitement de l'entrée clavier avant exposition au processus.

**Requirements**

* raw mode
* canonical mode
* line buffering
* character processing
* backspace
* enter
* EOF
* control characters

**Definition of Done**

* modèle documenté
* séparation claire entre driver clavier et line discipline

---

### OS-359 — Implement Canonical Input Mode

Implémenter le mode terminal canonique.

**Requirements**

* accumulation des caractères
* retour de ligne comme frontière de lecture
* backspace
* bufferisation
* lecture bloquante jusqu'à disponibilité d'une ligne

**Definition of Done**

* `read()` retourne une ligne complète
* comportement déterministe
* tests sur lignes vides, longues et multiples

---

### OS-360 — Implement Raw Input Mode

Implémenter le mode raw.

**Requirements**

* chaque caractère disponible peut être consommé immédiatement
* aucune transformation de ligne
* aucun buffering canonique

**Definition of Done**

* caractère disponible immédiatement après réception
* tests raw/canonical séparés

---

### OS-361 — Implement Terminal Control Characters

Supporter les caractères de contrôle fondamentaux.

**Requirements**

* Backspace
* Enter
* EOF
* interrupt
* suspend
* erase
* kill line

**Definition of Done**

* mapping configurable
* comportement documenté
* tests unitaires

---

## 14.8.3 — TTY Input Buffer

### OS-362 — Implement TTY Input Buffer

Créer le buffer d'entrée du terminal.

**Requirements**

* FIFO
* bounded capacity
* push
* pop
* peek
* clear
* overflow handling

**Definition of Done**

* buffer thread/process safe
* overflow déterministe
* tests de capacité et concurrence

---

### OS-363 — Integrate Keyboard Driver With TTY

Connecter le driver clavier au sous-système TTY.

**Flow**

```text
Keyboard interrupt
        ↓
Keyboard driver
        ↓
Input event
        ↓
TTY input buffer
        ↓
Line discipline
        ↓
Process stdin
```

**Definition of Done**

* les événements clavier atteignent le TTY
* aucun accès direct du processus au driver
* tests d'intégration

---

### OS-364 — Implement TTY Input Blocking

Permettre à un processus de dormir lorsqu'aucune entrée n'est disponible.

**Requirements**

* process blocking
* wait queue
* wakeup on input
* scheduler integration

**Definition of Done**

* `read(stdin)` bloque correctement
* arrivée d'une entrée réveille le processus
* aucun busy loop

---

## 14.8.4 — TTY Output

### OS-365 — Implement TTY Output Buffer

Créer le buffer de sortie.

**Requirements**

* FIFO
* bounded capacity
* write
* flush
* overflow handling

**Definition of Done**

* buffer testé
* comportement déterministe

---

### OS-366 — Connect TTY Output To Console

Connecter le TTY au console driver.

**Flow**

```text
Process
   ↓
write(stdout)
   ↓
File descriptor
   ↓
TTY
   ↓
TTY output buffer
   ↓
Console driver
   ↓
Display
```

**Definition of Done**

* un processus user-space peut écrire vers stdout
* aucune dépendance directe au matériel

---

### OS-367 — Implement TTY Flush

Implémenter le flush du terminal.

**Requirements**

* flush explicite
* flush automatique selon configuration
* traitement du buffer vide
* synchronisation

**Definition of Done**

* données correctement propagées à la console
* tests de flush

---

## 14.8.5 — Standard File Descriptors

### OS-368 — Define stdin/stdout/stderr Model

Définir les trois file descriptors standards.

```text
stdin  → TTY input
stdout → TTY output
stderr → TTY output
```

**Definition of Done**

* modèle documenté
* FDs initialisés lors du lancement du processus user-space

---

### OS-369 — Attach TTY To Process

Permettre d'associer un TTY à un processus.

**Requirements**

* controlling terminal
* process → TTY association
* attach
* detach
* validation

**Definition of Done**

* association sécurisée
* isolation entre processus respectée

---

### OS-370 — Implement TTY File Operations

Exposer le TTY via le modèle de file descriptors.

**Requirements**

* `read`
* `write`
* `close`
* `ioctl`/terminal control abstraction

**Definition of Done**

* TTY accessible via les syscalls existants
* aucun syscall spécifique au shell

---

## 14.8.6 — Terminal Sessions

### OS-371 — Define Terminal Session Model

Définir la notion de session terminal.

**Requirements**

* session ID
* controlling TTY
* session leader
* process groups

**Definition of Done**

* modèle documenté
* relations session/process/TTY définies

---

### OS-372 — Implement Process Groups

Ajouter les groupes de processus nécessaires au contrôle du terminal.

**Requirements**

* process group ID
* create/join
* lookup
* lifecycle
* isolation

**Definition of Done**

* groupes fonctionnels
* tests parent/enfant et groupes multiples

---

### OS-373 — Implement Foreground Process Group

Permettre au TTY de déterminer quel groupe reçoit les entrées terminal.

**Definition of Done**

* un seul foreground group par TTY
* input routé correctement
* changement de foreground contrôlé

---

### OS-374 — Implement Background Process Handling

Gérer les processus qui tentent d'utiliser un TTY sans être foreground.

**Requirements**

* detection
* policy
* blocking/error behavior
* audit event

**Definition of Done**

* comportement déterministe
* aucune possibilité de contourner le contrôle du TTY

---

## 14.8.7 — Terminal Control

### OS-375 — Define Terminal Configuration

Créer la configuration du terminal.

**Requirements**

* input mode
* output mode
* control characters
* echo
* signal behavior
* buffer configuration

**Definition of Done**

* configuration sérialisable
* defaults définis

---

### OS-376 — Implement Terminal Echo

Afficher automatiquement les caractères saisis lorsque le mode echo est actif.

**Definition of Done**

* echo configurable
* raw/canonical compatibility testée

---

### OS-377 — Implement Terminal Erase

Supporter l'effacement d'un caractère et d'une ligne.

**Definition of Done**

* backspace visuel correct
* buffer et écran synchronisés

---

### OS-378 — Implement Terminal Signals

Connecter les caractères de contrôle aux mécanismes de processus.

**Examples**

* interrupt
* terminate
* suspend

**Definition of Done**

* signal generation séparée de la line discipline
* foreground process group ciblé correctement

---

## 14.8.8 — Pseudo-Terminals

### OS-379 — Define PTY Architecture

Définir l'architecture des pseudo-terminals.

**Requirements**

* PTY master
* PTY slave
* bidirectional communication
* process attachment

**Definition of Done**

* modèle documenté
* distinction PTY/TTY physique claire

---

### OS-380 — Implement PTY Master

Créer le côté master.

**Definition of Done**

* lecture/écriture fonctionnelles
* buffer indépendant

---

### OS-381 — Implement PTY Slave

Créer le côté slave exposé au processus.

**Definition of Done**

* compatible avec l'interface TTY
* utilisable comme stdin/stdout/stderr

---

### OS-382 — Implement PTY Integration

Connecter master et slave.

```text
PTY Master
    ↕
PTY transport
    ↕
PTY Slave
    ↓
Process
```

**Definition of Done**

* communication bidirectionnelle
* isolation
* lifecycle cleanup

---

## 14.8.9 — TTY Security

### OS-383 — Define TTY Capability Model

Définir les capabilities nécessaires aux opérations sensibles sur un terminal.

**Requirements**

* read TTY
* write TTY
* control TTY
* attach TTY
* configure TTY

**Definition of Done**

* permissions explicites
* default deny pour les opérations privilégiées

---

### OS-384 — Implement TTY Access Checks

Appliquer les capabilities lors des opérations TTY.

**Definition of Done**

* accès non autorisé refusé
* processus ne pouvant pas prendre le contrôle arbitraire d'un TTY

---

### OS-385 — Implement TTY Isolation Tests

Tester l'isolation entre processus.

**Tests**

* processus A ne lit pas le TTY de B
* processus A ne contrôle pas le TTY de B
* background process ne contourne pas le foreground
* capability absente → deny

---

## 14.8.10 — Python Reference Model

### OS-386 — Implement Python TTY Model

Créer le modèle de référence Python.

**Requirements**

* TTY
* input buffer
* output buffer
* line discipline
* terminal configuration
* process attachment

---

### OS-387 — Implement Python TTY Sessions

Reproduire le modèle session/process group/foreground group.

---

### OS-388 — Cross-Test Rust/Python TTY Behavior

Comparer l'implémentation Rust au modèle Python.

**Definition of Done**

* mêmes inputs → mêmes transitions
* mêmes erreurs
* mêmes états observables

---

## 14.8.11 — Agent Terminal

### OS-389 — Define Agent Terminal Contract

Définir comment un agent user-space utilise un terminal.

**Principle**

```text
Agent Process
     ↓
stdin/stdout/stderr
     ↓
TTY
     ↓
Kernel
```

Le kernel ne connaît pas la notion de LLM ou d'agent.

---

### OS-390 — Implement Agent stdin/stdout

Permettre à un agent user-space d'utiliser les FDs standards.

**Definition of Done**

* agent lit stdin
* agent écrit stdout
* agent écrit stderr
* aucune API spéciale agent dans le kernel

---

### OS-391 — Implement Agent PTY Support

Permettre au runtime agent d'utiliser un PTY lorsqu'il doit piloter un autre processus interactif.

**Definition of Done**

* agent peut créer/consommer un PTY via les interfaces autorisées
* capabilities obligatoires
* isolation testée

---

### OS-392 — Agent Terminal Isolation Test

Créer un scénario complet :

```text
Agent A
  ↓
PTY / TTY
  ↓
Process B
```

Tester :

* input
* output
* process isolation
* capability enforcement
* cleanup

---

## 14.8.12 — TTY Observability

### OS-393 — Define TTY Metrics

Définir les métriques :

* bytes read
* bytes written
* input buffer utilization
* output buffer utilization
* blocked readers
* blocked writers
* active TTYs
* active PTYs

---

### OS-394 — Implement TTY Audit Events

Tracer les opérations sensibles :

* TTY creation
* attach
* detach
* configuration change
* foreground group change
* capability denial
* PTY creation

---

### OS-395 — Implement TTY Diagnostics

Ajouter des informations de diagnostic accessibles au kernel/debug tooling.

**Definition of Done**

* état d'un TTY inspectable
* buffers inspectables
* processus attachés visibles
* aucun secret exposé

---

## 14.8.13 — Testing & Stress

### OS-396 — TTY Unit Test Suite

Tester :

* buffers
* modes
* line discipline
* control characters
* configuration
* lifecycle

---

### OS-397 — TTY Concurrency Tests

Tester :

* plusieurs readers
* plusieurs writers
* blocking
* wakeup
* concurrent close
* process termination

---

### OS-398 — TTY Fuzz Tests

Fuzzer :

```text
keyboard input
      ↓
line discipline
      ↓
TTY state
```

Tester les séquences arbitraires de caractères et changements de configuration.

---

### OS-399 — PTY Stress Tests

Tester :

* création massive de PTYs
* destruction rapide
* gros volumes d'input/output
* processus concurrents
* process termination

---

### OS-400 — QEMU TTY Integration Test

Valider le sous-système complet dans QEMU.

**Scenario**

```text
Kernel boot
   ↓
TTY initialization
   ↓
User-space process
   ↓
stdin
   ↓
TTY
   ↓
process
   ↓
stdout
   ↓
console
```

**Definition of Done**

* boot QEMU
* TTY initialisé
* processus user-space lancé
* entrée clavier reçue
* sortie affichée
* aucun accès hardware direct depuis user-space

---

# Definition of Done — 14.8

La phase **TTY & Terminal** est terminée lorsque :

* TTY architecture définie
* TTY registry fonctionnel
* keyboard → TTY fonctionnel
* input/output buffers fonctionnels
* canonical/raw modes fonctionnels
* line discipline implémentée
* stdin/stdout/stderr attachés au TTY
* blocking/wakeup intégré au scheduler
* terminal sessions supportées
* process groups supportés
* foreground/background terminal control fonctionnel
* terminal configuration disponible
* control characters supportés
* PTY master/slave fonctionnels
* capabilities TTY appliquées
* isolation entre processus validée
* Python reference model disponible
* Rust/Python cross-tests disponibles
* agent user-space capable d'utiliser stdin/stdout/stderr
* observabilité et audit disponibles
* stress/fuzz tests disponibles
* QEMU integration test fonctionnel

**Architecture finale :**

```text
┌──────────────────────────────────────────────┐
│                 USER SPACE                   │
│                                              │
│  Shell      Agent Runtime      Coreutils     │
│    │              │                │        │
│    └──────────────┴────────────────┘        │
│                   │                          │
│            stdin/stdout/stderr               │
└───────────────────┼──────────────────────────┘
                    │
                 syscalls
                    │
┌───────────────────▼──────────────────────────┐
│                   KERNEL                     │
│                                              │
│  File Descriptors                           │
│        │                                     │
│       TTY                                    │
│     ┌──┴───┐                                 │
│ Input     Output                             │
│ Buffer    Buffer                             │
│    │         │                               │
│ Line      Console                            │
│ Discipline Driver                            │
│    │         │                               │
│ Keyboard   Display                           │
│ Driver     Hardware                          │
│                                              │
│  Scheduler / IPC / Capabilities / Memory    │
└──────────────────────────────────────────────┘
```

**Invariant architectural :**

> Le kernel fournit le terminal.
> Le shell et l'agent utilisent le terminal.
> Le kernel ne sait pas ce qu'est un shell, un LLM ou un agent.


# 14.9 — Init & User Space

**Objectif** : construire le premier environnement user-space du système, démarré par le kernel via un processus `init`, avec gestion du lancement des services, environnement de processus, montage du userland et supervision des processus fondamentaux.

**Principe** : `init` est le premier processus user-space. Le kernel crée et supervise le processus, mais ne connaît pas les services qu'il démarre. La politique de démarrage appartient au user-space.

---

## 14.9.1 — User Space Architecture

### OS-401 — Define User Space Architecture

Définir l'architecture complète du userland.

**Requirements**

* définir :

  * kernel
  * init
  * system services
  * shell
  * coreutils
  * agent runtime
* définir les frontières kernel/user-space
* documenter les interfaces utilisées par init
* définir le modèle de lancement des processus

**Definition of Done**

* architecture documentée
* aucune dépendance du kernel vers un service user-space
* init clairement identifié comme premier processus

---

### OS-402 — Define User Space ABI

Définir l'ABI minimale nécessaire au userland.

**Requirements**

* syscall ABI
* process creation
* memory allocation
* filesystem
* file descriptors
* IPC
* TTY
* time
* error handling

**Definition of Done**

* ABI documentée
* version identifiable
* compatibility rules définies

---

### OS-403 — Define User Space Layout

Définir la structure filesystem du userland.

```text
/
├── bin/
├── sbin/
├── lib/
├── etc/
├── dev/
├── proc/
├── tmp/
├── var/
├── home/
└── agents/
```

**Definition of Done**

* layout documenté
* responsabilités de chaque répertoire définies
* montage nécessaire identifié

---

## 14.9.2 — Init Process

### OS-404 — Define Init Process Contract

Définir le contrat du processus PID 1.

**Requirements**

* PID = 1
* premier processus user-space
* initialisation du userland
* lancement des services
* adoption des processus orphelins
* supervision
* shutdown

**Definition of Done**

* contrat documenté
* responsabilités kernel/init séparées

---

### OS-405 — Implement Init Entry Point

Créer le point d'entrée de `init`.

**Definition of Done**

* kernel peut charger init
* init commence son exécution en user-space
* retour d'init correctement géré

---

### OS-406 — Implement Init Environment

Construire l'environnement initial du processus.

**Requirements**

* arguments
* environment variables
* current working directory
* root filesystem
* stdin
* stdout
* stderr

**Definition of Done**

* environnement initial cohérent
* FDs standards attachés au TTY

---

### OS-407 — Implement Init Bootstrap

Implémenter la séquence de bootstrap.

```text
Kernel
  ↓
Memory
  ↓
Devices
  ↓
VFS
  ↓
TTY
  ↓
Create PID 1
  ↓
init
  ↓
User Space
```

**Definition of Done**

* ordre d'initialisation documenté
* chaque étape vérifiée
* failure handling défini

---

## 14.9.3 — Program Loader

### OS-408 — Define Executable Format

Définir le format des exécutables user-space.

**Requirements**

* headers
* code segment
* data segment
* read-only data
* entry point
* relocation model
* permissions

**Definition of Done**

* format documenté
* loader contract défini

---

### OS-409 — Implement Executable Parser

Créer le parser du format exécutable.

**Definition of Done**

* headers validés
* segments validés
* invalid binaries rejetés
* tests corruption/malformed input

---

### OS-410 — Implement User Program Loader

Charger un programme dans un address space.

**Requirements**

* fichier → memory mappings
* code RX
* data RW
* stack
* entry point
* initial registers

**Definition of Done**

* programme chargé
* isolation mémoire respectée
* permissions appliquées

---

### OS-411 — Implement Process Exec

Permettre à un processus de remplacer son image mémoire par un programme.

**Definition of Done**

* address space remplacé
* ancien mapping nettoyé
* FDs conservés selon règles définies
* exécution au nouvel entry point

---

### OS-412 — Implement Loader Security Validation

Vérifier les exécutables avant chargement.

**Requirements**

* segment bounds
* alignment
* address validation
* permission validation
* entry point validation
* integer overflow protection

**Definition of Done**

* binaries malformés refusés
* tests adversariaux disponibles

---

## 14.9.4 — Process Bootstrap

### OS-413 — Implement User Stack Initialization

Créer la stack initiale du processus.

**Requirements**

* argc
* argv
* environment
* alignment
* stack permissions

**Definition of Done**

* programme reçoit correctement ses arguments
* stack inaccessible hors de son address space

---

### OS-414 — Implement Process Environment

Ajouter le modèle d'environnement user-space.

**Requirements**

* environment variables
* lookup
* set
* unset
* inheritance

**Definition of Done**

* environnement hérité lors du spawn
* isolation entre processus

---

### OS-415 — Implement Working Directory

Supporter le current working directory.

**Requirements**

* process CWD
* `chdir`
* inheritance
* path resolution

**Definition of Done**

* filesystem operations utilisent correctement le CWD

---

## 14.9.5 — Process Supervision

### OS-416 — Define Service Model

Définir le modèle des services user-space.

**Requirements**

* service name
* executable
* arguments
* environment
* capabilities
* restart policy
* dependencies

**Definition of Done**

* modèle indépendant du kernel
* service configuration documentée

---

### OS-417 — Implement Init Service Registry

Créer le registre des services gérés par init.

**Definition of Done**

* register
* lookup
* start
* stop
* status

---

### OS-418 — Implement Service Spawn

Permettre à init de lancer un service.

**Flow**

```text
init
 ↓
spawn
 ↓
capability profile
 ↓
address space
 ↓
executable loader
 ↓
process
```

**Definition of Done**

* service lancé avec capabilities explicites
* environnement contrôlé

---

### OS-419 — Implement Service Restart

Ajouter le redémarrage automatique.

**Requirements**

* restart policy
* crash detection
* restart limit
* backoff

**Definition of Done**

* boucle de crash contrôlée
* service peut être désactivé après seuil

---

### OS-420 — Implement Service Dependencies

Supporter les dépendances entre services.

**Requirements**

* dependency graph
* ordering
* dependency failure
* cycle detection

**Definition of Done**

* ordre de démarrage déterministe
* cycles rejetés

---

## 14.9.6 — Process Reaping

### OS-421 — Implement Init Child Reaping

PID 1 doit récupérer les processus orphelins.

**Definition of Done**

* processus orphelin adopté
* exit status récupéré
* aucun zombie permanent

---

### OS-422 — Implement Exit Status Registry

Permettre à init de conserver les informations minimales sur les processus terminés.

**Requirements**

* PID
* exit code
* termination reason
* timestamp

**Definition of Done**

* informations récupérables
* cleanup après expiration

---

## 14.9.7 — Device User Space

### OS-423 — Define `/dev` Model

Définir l'exposition des devices au user-space.

**Requirements**

* device nodes
* permissions
* capabilities
* lifecycle

**Definition of Done**

* `/dev` intégré au VFS
* aucun accès hardware direct

---

### OS-424 — Implement Console Device

Exposer le terminal système via `/dev`.

**Definition of Done**

* console accessible via FD
* permissions appliquées

---

### OS-425 — Implement Device Capability Enforcement

Vérifier les capabilities lors de l'ouverture des devices.

**Definition of Done**

* accès refusé sans capability
* audit des refus

---

## 14.9.8 — Virtual Kernel Interfaces

### OS-426 — Define `/proc` Model

Définir un filesystem virtuel exposant l'état du système.

**Potential entries**

```text
/proc/
├── cpuinfo
├── meminfo
├── uptime
├── processes/
└── self/
```

**Definition of Done**

* architecture définie
* aucune donnée privée exposée par défaut

---

### OS-427 — Implement `/proc/self`

Permettre à un processus de consulter ses propres informations.

**Definition of Done**

* PID
* memory information
* capabilities
* file descriptors selon policy

---

### OS-428 — Implement `/proc/processes`

Exposer une vue contrôlée des processus.

**Definition of Done**

* processus visibles selon policy
* isolation respectée

---

### OS-429 — Implement `/proc/system`

Exposer les informations système nécessaires au diagnostic.

**Requirements**

* CPU
* memory
* uptime
* scheduler
* devices

**Definition of Done**

* informations cohérentes avec le kernel
* read-only

---

## 14.9.9 — User Space Security

### OS-430 — Define Init Capability Profile

Définir les capabilities minimales de PID 1.

**Requirements**

* process management
* service spawn
* filesystem management nécessaire
* IPC nécessaire
* device access strictement limité

**Definition of Done**

* profile documenté
* aucun accès inutile

---

### OS-431 — Implement Service Capability Profiles

Chaque service reçoit uniquement les capabilities nécessaires.

```text
Service A
 ├── filesystem: /var/a
 ├── ipc: channel-a
 └── network: denied

Service B
 ├── filesystem: /var/b
 ├── ipc: channel-b
 └── network: allowed
```

**Definition of Done**

* least privilege
* capabilities explicites
* absence de capability = deny

---

### OS-432 — Implement User Space Isolation Tests

Tester :

* filesystem isolation
* memory isolation
* IPC isolation
* device isolation
* capability isolation
* process isolation

**Definition of Done**

* cross-process access refusé
* privilege escalation tests présents

---

## 14.9.10 — Shutdown & Lifecycle

### OS-433 — Define System Shutdown Protocol

Définir la séquence d'arrêt.

```text
shutdown request
      ↓
init
      ↓
stop services
      ↓
flush filesystem
      ↓
close devices
      ↓
kernel shutdown
```

---

### OS-434 — Implement Graceful Service Shutdown

Permettre aux services de terminer proprement.

**Requirements**

* shutdown signal
* timeout
* forced termination

**Definition of Done**

* services disposent d'un délai
* processus bloqués finalement terminés

---

### OS-435 — Implement Init Shutdown

PID 1 orchestre l'arrêt complet du userland.

**Definition of Done**

* tous les services arrêtés
* filesystem flush
* devices released

---

### OS-436 — Implement Kernel Shutdown Handoff

Permettre au kernel de reprendre la main après arrêt du userland.

**Definition of Done**

* état cohérent
* aucun processus user-space actif
* shutdown QEMU fonctionnel

---

## 14.9.11 — Python Reference Model

### OS-437 — Implement Python Init Model

Créer le modèle Python de :

* init
* services
* process lifecycle
* supervision
* restart

---

### OS-438 — Implement Python Program Loader Model

Modéliser :

* executable
* segments
* address space
* entry point
* stack

---

### OS-439 — Cross-Test Rust/Python User Space

Comparer les transitions observables :

```text
spawn
exec
exit
restart
shutdown
```

**Definition of Done**

* mêmes inputs
* mêmes états
* mêmes erreurs attendues

---

## 14.9.12 — Agent User Space

### OS-440 — Define Agent User Space Contract

Définir l'agent comme un programme user-space standard.

**Important :**

```text
Agent ≠ kernel primitive
Agent = user-space process
```

Le kernel ne possède aucune connaissance spécifique de :

* LLM
* MCP
* prompt
* model
* tool
* workflow

---

### OS-441 — Implement Minimal Agent Process

Créer un programme minimal représentant un agent.

**Requirements**

* PID
* address space
* stdin
* stdout
* capabilities
* filesystem workspace

**Definition of Done**

* agent démarre comme n'importe quel processus
* aucune API kernel spécifique aux agents

---

### OS-442 — Implement Agent Capability Profile

Créer un profil minimal.

**Potential capabilities**

```text
process:
  spawn: limited

filesystem:
  workspace: /agents/<id>

ipc:
  own_channels: allowed

network:
  policy-controlled

devices:
  denied
```

**Definition of Done**

* least privilege
* capabilities explicitement attribuées

---

### OS-443 — Agent Lifecycle Test

Tester :

```text
init
 ↓
spawn agent
 ↓
load agent binary
 ↓
agent runs
 ↓
agent communicates
 ↓
agent exits
 ↓
init reaps
```

**Definition of Done**

* scénario complet fonctionnel

---

## 14.9.13 — Boot to User Space

### OS-444 — Implement Kernel → Init Handoff

Faire fonctionner la transition complète.

```text
BIOS/UEFI
   ↓
boot
   ↓
kernel
   ↓
memory
   ↓
scheduler
   ↓
devices
   ↓
VFS
   ↓
TTY
   ↓
PID 1
   ↓
init
```

**Definition of Done**

* kernel bootable
* init exécuté en ring/user mode
* scheduler actif

---

### OS-445 — Implement Init → Service Boot

Faire démarrer les premiers services.

**Definition of Done**

* init démarre les services configurés
* dépendances respectées
* crashes gérés

---

### OS-446 — Implement Boot Failure Recovery

Définir le comportement lorsqu'une étape critique échoue.

**Examples**

* init absent
* filesystem unavailable
* executable corrupt
* service crash loop
* TTY unavailable

**Definition of Done**

* failure modes documentés
* kernel reste dans un état sûr
* pas de fallback implicite dangereux

---

### OS-447 — QEMU User Space Boot Test

Test end-to-end :

```text
QEMU
 ↓
Kernel
 ↓
PID 1
 ↓
init
 ↓
service
 ↓
agent process
 ↓
TTY
```

**Definition of Done**

* boot entièrement automatisé
* logs exploitables
* exit code déterministe

---

# Definition of Done — 14.9

La phase **Init & User Space** est terminée lorsque :

* architecture user-space définie
* ABI définie
* filesystem layout défini
* PID 1 fonctionnel
* init bootstrap fonctionnel
* executable loader fonctionnel
* process `exec` fonctionnel
* user stack initialisée
* argv/environment supportés
* current working directory supporté
* service model fonctionnel
* service registry fonctionnel
* service spawning fonctionnel
* restart policy fonctionnelle
* dependencies supportées
* orphan processes reaped
* `/dev` exposé via VFS
* `/proc` minimal fonctionnel
* capabilities user-space appliquées
* service isolation validée
* graceful shutdown fonctionnel
* Python reference model disponible
* Rust/Python cross-tests disponibles
* agent exécuté comme processus user-space standard
* agent capability profile fonctionnel
* kernel → init → service → agent validé sous QEMU

## Architecture obtenue

```text
┌───────────────────────────────────────────────────────┐
│                    USER SPACE                         │
│                                                       │
│                      PID 1                            │
│                      init                             │
│                  /          \                         │
│             services      services                    │
│                 │             │                       │
│            coreutils      agent runtime               │
│                               │                       │
│                            Agent A                    │
│                            Agent B                    │
│                                                       │
│              Shell / Coreutils / Applications         │
└──────────────────────────┬────────────────────────────┘
                           │
                       Syscalls
                           │
┌──────────────────────────▼────────────────────────────┐
│                       KERNEL                          │
│                                                       │
│ Process Manager │ Scheduler │ Memory │ Capabilities  │
│                                                       │
│ Syscalls │ IPC │ VFS │ TTY │ Devices                 │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### Invariant architectural

> **Le kernel exécute des processus.**
>
> **Init construit le userland.**
>
> **Les services vivent en user-space.**
>
> **Les agents sont des processus user-space comme les autres.**
>
> **Le kernel ne sait pas ce qu'est un agent.**



# 14.10 — Shell

**Objectif** : construire le premier shell user-space du système, capable de lire des commandes depuis un TTY, de parser une ligne, de résoudre des programmes, de créer des processus et d'attendre leur terminaison.

**Principe** : le shell est une application user-space. Il n'a aucun privilège spécial. Il utilise uniquement les syscalls, le VFS, les file descriptors, l'IPC et le TTY disponibles à n'importe quel processus autorisé.

---

## 14.10.1 — Shell Architecture

### OS-448 — Define Shell Architecture

Définir l'architecture du shell.

**Requirements**

* input loop
* parser
* command resolver
* process launcher
* job manager
* builtin commands
* environment
* history
* signal handling
* terminal integration

**Definition of Done**

* architecture documentée
* séparation parser/exécution claire
* shell entièrement user-space

---

### OS-449 — Define Shell Process Contract

Définir le contrat d'un processus shell.

**Requirements**

* stdin attaché au TTY
* stdout attaché au TTY
* stderr attaché au TTY
* working directory
* environment
* capabilities minimales

**Definition of Done**

* shell peut démarrer comme processus standard
* aucune capability kernel spécifique au shell

---

### OS-450 — Implement Shell Entry Point

Créer le programme principal du shell.

**Flow**

```text
main
 ↓
initialize environment
 ↓
attach terminal
 ↓
initialize parser
 ↓
command loop
```

**Definition of Done**

* shell démarre depuis init
* shell reste en user-space

---

## 14.10.2 — Command Line Reader

### OS-451 — Implement Command Input Loop

Lire continuellement les commandes depuis stdin.

**Requirements**

* TTY read
* EOF handling
* empty line handling
* error handling

**Definition of Done**

* shell lit une commande
* traite la commande
* recommence

---

### OS-452 — Implement Shell Prompt

Afficher un prompt interactif.

Exemple :

```text
hexos$
```

**Requirements**

* configurable
* CWD disponible
* prompt écrit via stdout

---

### OS-453 — Implement Prompt Context

Permettre au prompt d'utiliser :

* username
* hostname
* current directory
* process status
* environment variables

**Definition of Done**

* expansion configurable
* aucun accès direct au kernel

---

## 14.10.3 — Lexer

### OS-454 — Define Shell Token Model

Définir les tokens du shell.

**Tokens**

```text
WORD
STRING
PIPE
REDIRECT_IN
REDIRECT_OUT
REDIRECT_APPEND
BACKGROUND
SEMICOLON
PAREN_OPEN
PAREN_CLOSE
```

**Definition of Done**

* token model documenté
* positions source conservées

---

### OS-455 — Implement Shell Lexer

Transformer une ligne en tokens.

**Example**

```text
cat file.txt | grep error > result.txt
```

devient :

```text
WORD(cat)
WORD(file.txt)
PIPE
WORD(grep)
WORD(error)
REDIRECT_OUT
WORD(result.txt)
```

**Definition of Done**

* lexer déterministe
* erreurs syntaxiques détectées

---

### OS-456 — Implement Shell Quoting

Supporter :

* single quotes
* double quotes
* escaped characters

**Definition of Done**

* espaces dans les arguments correctement préservés
* quotes correctement interprétées

---

### OS-457 — Shell Lexer Fuzz Tests

Fuzzer les entrées arbitraires.

**Tests**

* quotes non fermées
* escapes
* unicode
* chaînes très longues
* tokens invalides

---

## 14.10.4 — Parser

### OS-458 — Define Shell AST

Créer l'AST du shell.

**Example**

```text
Pipeline
├── Command
│   ├── cat
│   └── file.txt
└── Command
    ├── grep
    └── error
```

---

### OS-459 — Implement Command Parser

Parser :

```text
command arg1 arg2
```

---

### OS-460 — Implement Pipeline Parser

Parser :

```text
cmd1 | cmd2 | cmd3
```

**Definition of Done**

* AST correctement construit
* nombre arbitraire de commandes supporté selon les limites définies

---

### OS-461 — Implement Redirection Parser

Supporter :

```text
cmd < input
cmd > output
cmd >> output
```

---

### OS-462 — Implement Background Parser

Supporter :

```text
cmd &
```

---

### OS-463 — Implement Command Sequencing

Supporter :

```text
cmd1 ; cmd2
```

---

### OS-464 — Parser Error Model

Définir les erreurs :

* unexpected token
* missing argument
* unterminated quote
* invalid redirection
* invalid pipeline

**Definition of Done**

* erreurs structurées
* position de l'erreur disponible

---

## 14.10.5 — Command Resolution

### OS-465 — Define PATH Resolution

Définir comment le shell recherche un exécutable.

```text
PATH=/bin:/sbin:/usr/bin
```

**Flow**

```text
command
 ↓
builtin?
 ↓ no
PATH lookup
 ↓
executable
```

---

### OS-466 — Implement Executable Lookup

Chercher un programme dans le PATH.

**Definition of Done**

* premier executable valide sélectionné
* erreurs explicites si introuvable

---

### OS-467 — Implement Absolute Path Execution

Supporter :

```text
/bin/echo
```

---

### OS-468 — Implement Relative Path Execution

Supporter :

```text
./program
```

---

## 14.10.6 — Process Execution

### OS-469 — Implement Command Spawn

Lancer une commande externe.

**Flow**

```text
Shell
 ↓
spawn
 ↓
process
 ↓
exec
 ↓
program
```

---

### OS-470 — Implement Foreground Execution

Le shell attend la terminaison :

```text
shell
 ↓
spawn child
 ↓
wait
 ↓
child exits
 ↓
shell resumes
```

**Definition of Done**

* shell récupère exit status

---

### OS-471 — Implement Background Execution

Supporter :

```text
long_task &
```

Le shell ne bloque pas sur le processus.

---

### OS-472 — Implement Exit Status

Exposer le code retour de la dernière commande.

```text
$ echo $?
```

**Definition of Done**

* exit code conservé
* signal termination distinguée si applicable

---

## 14.10.7 — Builtins

### OS-473 — Define Builtin Interface

Créer l'interface :

```text
Builtin {
    name
    execute(args, environment)
}
```

---

### OS-474 — Implement `cd`

Changer le working directory du shell.

**Important**

`cd` doit être builtin car un processus enfant ne peut pas modifier le CWD de son parent.

---

### OS-475 — Implement `pwd`

Afficher le CWD courant.

---

### OS-476 — Implement `echo`

Afficher des arguments.

---

### OS-477 — Implement `export`

Modifier l'environnement du shell.

---

### OS-478 — Implement `unset`

Supprimer une variable d'environnement.

---

### OS-479 — Implement `exit`

Terminer le shell.

---

### OS-480 — Implement `env`

Afficher l'environnement courant.

---

### OS-481 — Implement `which`

Résoudre l'emplacement d'un executable.

---

### OS-482 — Implement `help`

Afficher les builtins disponibles.

---

## 14.10.8 — Redirections

### OS-483 — Implement stdin Redirection

Supporter :

```text
cmd < file
```

**Requirements**

* open file
* duplicate FD
* attach to stdin
* close temporary FD

---

### OS-484 — Implement stdout Redirection

Supporter :

```text
cmd > file
```

---

### OS-485 — Implement stdout Append

Supporter :

```text
cmd >> file
```

---

### OS-486 — Implement stderr Redirection

Supporter :

```text
cmd 2> error.log
```

---

### OS-487 — Implement Combined Redirections

Supporter les combinaisons :

```text
cmd < input > output 2> errors
```

**Definition of Done**

* ordre des redirections respecté
* FDs correctement nettoyés

---

## 14.10.9 — Pipelines

### OS-488 — Define Shell Pipeline Execution

Définir le modèle :

```text
cmd1 | cmd2 | cmd3
```

**Flow**

```text
cmd1 stdout
     ↓
    pipe
     ↓
cmd2 stdin
     ↓
    pipe
     ↓
cmd3 stdin
```

---

### OS-489 — Implement Pipeline Process Creation

Créer tous les processus nécessaires.

**Definition of Done**

* chaque commande possède son propre process
* pipes connectés correctement

---

### OS-490 — Implement Pipeline FD Wiring

Configurer :

```text
stdin
stdout
stderr
```

pour chaque processus.

---

### OS-491 — Implement Pipeline Wait

Attendre correctement les processus du pipeline.

**Definition of Done**

* aucun zombie
* exit status final défini

---

### OS-492 — Pipeline Stress Tests

Tester :

```text
A | B | C | D | E
```

avec gros volumes de données.

---

## 14.10.10 — Job Control

### OS-493 — Define Shell Job Model

Définir :

```text
Job
├── job id
├── process group
├── processes
├── state
└── command
```

États :

```text
RUNNING
STOPPED
DONE
FAILED
```

---

### OS-494 — Implement Job Registry

Le shell conserve les jobs actifs.

---

### OS-495 — Implement Foreground Job

Connecter le process group au TTY.

---

### OS-496 — Implement Background Job

Lancer un job sans attendre.

---

### OS-497 — Implement `jobs`

Afficher :

```text
[1] Running  long_task
[2] Stopped  editor
```

---

### OS-498 — Implement `fg`

Ramener un job au foreground.

---

### OS-499 — Implement `bg`

Reprendre un job en background.

---

### OS-500 — Implement Job Control Signals

Gérer les interactions :

```text
Ctrl-C
Ctrl-Z
```

avec les process groups.

---

## 14.10.11 — Shell History

### OS-501 — Define History Model

Définir :

* history entry
* index
* timestamp
* command

---

### OS-502 — Implement History Storage

Stocker les commandes.

**Requirements**

* bounded history
* persistence optionnelle
* corruption handling

---

### OS-503 — Implement History Navigation

Supporter :

```text
↑
↓
```

dans le terminal interactif.

---

### OS-504 — Implement `history`

Afficher l'historique.

---

## 14.10.12 — Environment Expansion

### OS-505 — Implement Variable Expansion

Supporter :

```text
$HOME
$PATH
$USER
```

---

### OS-506 — Implement Special Variables

Supporter :

```text
$?
$$
```

---

### OS-507 — Implement Environment Expansion Tests

Tester :

* variables absentes
* variables vides
* nested syntax
* escaping
* quotes

---

## 14.10.13 — Shell Security

### OS-508 — Define Shell Capability Profile

Le shell doit recevoir uniquement les capabilities nécessaires.

```text
filesystem:
  cwd: allowed
  read: allowed
  write: policy-controlled

process:
  spawn: allowed

device:
  direct: denied
```

---

### OS-509 — Validate Executable Permissions

Le shell ne contourne jamais les contrôles du kernel.

**Definition of Done**

* executable inaccessible → deny
* filesystem inaccessible → deny
* capability absente → deny

---

### OS-510 — Shell Security Tests

Tester :

* path traversal
* inaccessible executable
* restricted filesystem
* capability denial
* malformed executable
* hostile environment

---

### OS-511 — Shell Input Fuzzing

Fuzzer :

```text
input
 ↓
lexer
 ↓
parser
 ↓
AST
 ↓
execution
```

Aucune entrée utilisateur ne doit provoquer :

* panic
* corruption
* privilege escalation
* kernel access

---

## 14.10.14 — Python Reference Model

### OS-512 — Implement Python Shell Lexer

Créer le modèle Python du lexer.

---

### OS-513 — Implement Python Shell Parser

Créer le modèle Python du parser/AST.

---

### OS-514 — Implement Python Shell Execution Model

Modéliser :

* process spawn
* pipes
* redirections
* jobs
* exit status

---

### OS-515 — Cross-Test Rust/Python Shell

Comparer :

```text
input
 ↓
tokens
 ↓
AST
 ↓
execution plan
```

entre les deux implémentations.

---

## 14.10.15 — Agent Shell Interaction

### OS-516 — Define Agent Shell Contract

Un agent peut utiliser le shell comme n'importe quel programme user-space autorisé.

```text
Agent
 ↓
spawn
 ↓
Shell
 ↓
command
 ↓
process
```

Le kernel reste totalement agnostique.

---

### OS-517 — Implement Agent Shell Session

Permettre à un agent de créer une session shell contrôlée.

**Requirements**

* PTY
* stdin/stdout
* process group
* capabilities

---

### OS-518 — Agent Command Isolation Test

Tester :

```text
Agent A
 ↓
Shell
 ↓
Command
```

avec :

* filesystem restrictions
* process restrictions
* network restrictions
* capability enforcement
* PTY isolation

---

### OS-519 — Agent Shell Lifecycle Test

Scénario complet :

```text
init
 ↓
agent
 ↓
PTY
 ↓
shell
 ↓
command
 ↓
process
 ↓
result
 ↓
shell
 ↓
agent
```

**Definition of Done**

* résultat récupéré
* aucun accès kernel privilégié

---

## 14.10.16 — QEMU Integration

### OS-520 — Boot Into Shell

Faire démarrer :

```text
QEMU
 ↓
Kernel
 ↓
Init
 ↓
Shell
 ↓
TTY
```

---

### OS-521 — Execute First Command

Supporter :

```text
hexos$ echo hello
hello
```

---

### OS-522 — Execute Pipeline In QEMU

Tester :

```text
hexos$ echo hello | grep hello
hello
```

---

### OS-523 — Execute Redirection In QEMU

Tester :

```text
hexos$ echo hello > /tmp/test
hexos$ cat /tmp/test
hello
```

---

### OS-524 — Execute Background Job In QEMU

Tester :

```text
hexos$ long_task &
[1] Running
```

---

### OS-525 — Full Interactive Shell Test

Scénario :

```text
boot
 ↓
init
 ↓
shell
 ↓
command
 ↓
builtin
 ↓
external process
 ↓
pipeline
 ↓
redirection
 ↓
background job
 ↓
exit
```

**Definition of Done**

* test automatisé
* sortie déterministe
* exit code vérifié

---

# Definition of Done — 14.10

La phase **Shell** est terminée lorsque :

* shell user-space fonctionnel
* TTY interaction fonctionnelle
* prompt fonctionnel
* lexer fonctionnel
* quoting fonctionnel
* parser AST fonctionnel
* PATH resolution fonctionnelle
* process spawning fonctionnel
* foreground/background execution fonctionnels
* exit status disponible
* builtins principaux disponibles
* redirections disponibles
* pipelines disponibles
* job control disponible
* process groups intégrés
* history disponible
* environment expansion disponible
* capabilities appliquées
* fuzz/security tests disponibles
* Python reference model disponible
* Rust/Python cross-tests disponibles
* agent capable d'utiliser une session shell contrôlée
* boot QEMU → kernel → init → shell validé

## Architecture obtenue

```text
┌────────────────────────────────────────────────────────┐
│                    USER SPACE                          │
│                                                        │
│                     Shell                              │
│              ┌────────┼────────┐                       │
│            Parser   Jobs    Builtins                   │
│              │         │         │                     │
│              └─────────┼─────────┘                     │
│                        │                               │
│                     Syscalls                           │
│                        │                               │
│        ┌───────────────┼────────────────┐              │
│        ↓               ↓                ↓              │
│     Process           Pipe             VFS             │
│                                                        │
│              Agent Runtime / Agents                    │
└────────────────────────┬───────────────────────────────┘
                         │
                    Syscall ABI
                         │
┌────────────────────────▼───────────────────────────────┐
│                       KERNEL                           │
│                                                       │
│ Process │ Scheduler │ Memory │ Capabilities           │
│                                                       │
│ Syscalls │ IPC │ VFS │ TTY │ Devices                 │
└───────────────────────────────────────────────────────┘
```

### Invariant architectural

> **Le shell est un programme.**
>
> **Une commande est un processus.**
>
> **Un pipeline est un ensemble de processus reliés par IPC.**
>
> **Le TTY appartient au système, pas au shell.**
>
> **Le kernel ne sait pas que le shell existe.**
>
> **Un agent peut utiliser un shell, mais le kernel ne sait pas qu'il est un agent.**


# 14.11 — Coreutils

**Objectif** : construire les premières commandes système natives du userland HexOS.

**Principe** : les Coreutils sont des programmes user-space ordinaires. Ils n'ont aucun accès privilégié au kernel et utilisent exclusivement les interfaces publiques du système : syscalls, VFS, file descriptors, IPC, processus, TTY et `/proc`.

---

## 14.11.1 — Coreutils Architecture

### OS-526 — Define Coreutils Architecture

Définir l'organisation des commandes système.

**Requirements**

* command layout
* executable naming
* shared library strategy
* error handling
* exit status conventions
* stdout/stderr conventions
* argument parsing
* common utilities

**Definition of Done**

* architecture documentée
* chaque utility est un processus user-space indépendant
* aucune dépendance directe au kernel

---

### OS-527 — Define Coreutils Runtime Library

Créer les abstractions communes aux utilities.

**Requirements**

* argument parsing
* stdout/stderr
* filesystem helpers
* path handling
* error formatting
* exit codes

**Definition of Done**

* bibliothèque réutilisable
* aucune logique métier spécifique à une commande

---

### OS-528 — Define Exit Code Convention

Définir les codes de retour.

```text
0 → success
1 → generic failure
2 → invalid arguments
126 → executable unavailable
127 → command not found
```

**Definition of Done**

* convention documentée
* toutes les utilities la respectent

---

## 14.11.2 — `echo`

### OS-529 — Implement `echo`

Supporter :

```text
echo hello
```

```text
echo hello world
```

**Definition of Done**

* arguments affichés sur stdout
* newline par défaut
* exit status correct

---

### OS-530 — Implement Echo Options

Supporter au minimum :

```text
-n
```

pour supprimer le newline.

---

## 14.11.3 — `pwd`

### OS-531 — Implement `pwd`

Afficher le current working directory.

```text
hexos$ pwd
/home/agent
```

**Definition of Done**

* utilise l'interface filesystem
* aucun accès direct kernel

---

## 14.11.4 — `ls`

### OS-532 — Define Directory Listing API

Définir les abstractions communes pour parcourir un répertoire.

---

### OS-533 — Implement `ls`

Supporter :

```text
ls
ls /tmp
ls /home
```

---

### OS-534 — Implement `ls -l`

Afficher :

* permissions
* owner
* size
* timestamp
* name

---

### OS-535 — Implement `ls -a`

Afficher les fichiers cachés.

---

### OS-536 — Implement `ls Error Handling`

Gérer :

* directory absent
* permission denied
* invalid path
* non-directory target

---

## 14.11.5 — `cat`

### OS-537 — Implement `cat`

Supporter :

```text
cat file.txt
```

---

### OS-538 — Implement Multiple File Cat

Supporter :

```text
cat a.txt b.txt c.txt
```

---

### OS-539 — Implement stdin Cat

Supporter :

```text
cat
```

et :

```text
echo hello | cat
```

---

### OS-540 — Implement Cat Error Handling

Tester :

* file absent
* permission denied
* directory target
* broken FD

---

## 14.11.6 — `mkdir`

### OS-541 — Implement `mkdir`

Supporter :

```text
mkdir test
```

---

### OS-542 — Implement Recursive `mkdir`

Supporter :

```text
mkdir -p a/b/c
```

---

### OS-543 — Implement Directory Permissions

Supporter les permissions initiales.

---

## 14.11.7 — `touch`

### OS-544 — Implement `touch`

Créer un fichier absent.

```text
touch file.txt
```

---

### OS-545 — Implement Timestamp Update

Mettre à jour les timestamps d'un fichier existant.

---

## 14.11.8 — `cp`

### OS-546 — Implement File Copy

Supporter :

```text
cp source destination
```

---

### OS-547 — Implement Recursive Copy

Supporter :

```text
cp -r directory destination
```

---

### OS-548 — Implement Copy Metadata

Préserver selon les règles définies :

* permissions
* timestamps
* file type

---

### OS-549 — Copy Large File Tests

Tester des fichiers dépassant plusieurs buffers mémoire.

**Definition of Done**

* aucun chargement obligatoire du fichier entier en mémoire
* streaming par chunks

---

## 14.11.9 — `mv`

### OS-550 — Implement `mv`

Supporter :

```text
mv source destination
```

---

### OS-551 — Implement Cross-Directory Move

Tester les déplacements entre répertoires.

---

### OS-552 — Implement Move Collision Handling

Définir le comportement lorsqu'une destination existe.

---

## 14.11.10 — `rm`

### OS-553 — Implement `rm`

Supporter :

```text
rm file.txt
```

---

### OS-554 — Implement Recursive `rm`

Supporter :

```text
rm -r directory
```

---

### OS-555 — Implement Force Mode

Supporter :

```text
rm -f file
```

---

### OS-556 — Implement Safe Recursive Delete

Empêcher les comportements dangereux liés aux chemins.

**Requirements**

* path resolution correcte
* symlink policy si supportée
* root filesystem protection
* capability enforcement

**Definition of Done**

* aucune suppression hors du scope autorisé

---

## 14.11.11 — `rmdir`

### OS-557 — Implement `rmdir`

Supprimer uniquement les répertoires vides.

---

## 14.11.12 — `head` / `tail`

### OS-558 — Implement `head`

Supporter :

```text
head file.txt
```

---

### OS-559 — Implement `head -n`

Supporter :

```text
head -n 20 file.txt
```

---

### OS-560 — Implement `tail`

Supporter :

```text
tail file.txt
```

---

### OS-561 — Implement `tail -n`

Supporter :

```text
tail -n 20 file.txt
```

---

## 14.11.13 — `grep`

### OS-562 — Define Search Pattern API

Définir l'abstraction de recherche dans un flux.

---

### OS-563 — Implement Basic `grep`

Supporter :

```text
grep error logfile
```

---

### OS-564 — Implement stdin `grep`

Supporter :

```text
cat logfile | grep error
```

---

### OS-565 — Implement Recursive `grep`

Supporter :

```text
grep -r error /var/log
```

---

### OS-566 — Implement Case-Insensitive Search

Supporter :

```text
grep -i error logfile
```

---

### OS-567 — Grep Streaming Tests

Tester de gros fichiers sans charger l'intégralité en mémoire.

---

## 14.11.14 — `find`

### OS-568 — Implement Basic `find`

Supporter :

```text
find /home
```

---

### OS-569 — Implement Name Filtering

Supporter :

```text
find /home -name "*.txt"
```

---

### OS-570 — Implement File Type Filtering

Supporter :

```text
find /home -type f
find /home -type d
```

---

### OS-571 — Find Traversal Security

Tester :

* traversal
* permissions
* cycles
* profondeur maximale
* filesystem boundaries

---

## 14.11.15 — Process Utilities

### OS-572 — Implement `ps`

Afficher les processus.

```text
hexos$ ps
PID   STATE    NAME
1     RUNNING  init
2     RUNNING  shell
3     RUNNING  agent
```

---

### OS-573 — Implement Process Metadata

Afficher :

* PID
* PPID
* state
* CPU usage
* memory usage
* process name

---

### OS-574 — Implement `kill`

Supporter l'envoi de signaux.

```text
kill 42
```

---

### OS-575 — Implement Signal Options

Supporter :

```text
kill -TERM 42
kill -KILL 42
```

---

### OS-576 — Process Permission Tests

Tester qu'un processus ne peut pas tuer arbitrairement un autre processus.

---

## 14.11.16 — System Utilities

### OS-577 — Implement `uname`

Afficher :

* OS name
* kernel version
* architecture

---

### OS-578 — Implement `uptime`

Afficher le temps depuis le boot.

---

### OS-579 — Implement `free`

Afficher la mémoire disponible.

```text
hexos$ free
TOTAL   USED   FREE
...
```

---

### OS-580 — Implement `mount`

Afficher les mounts.

---

### OS-581 — Implement `df`

Afficher l'utilisation des filesystems.

---

### OS-582 — Implement `du`

Calculer l'espace utilisé par un répertoire.

---

## 14.11.17 — File Inspection

### OS-583 — Implement `stat`

Afficher les metadata d'un fichier.

---

### OS-584 — Implement `file`

Identifier le type d'un fichier.

---

### OS-585 — Implement `wc`

Supporter :

```text
wc file.txt
```

avec :

* lines
* words
* bytes

---

### OS-586 — Implement `sort`

Trier un flux texte.

---

### OS-587 — Implement `uniq`

Supprimer les lignes consécutives dupliquées.

---

### OS-588 — Implement `tee`

Supporter :

```text
command | tee output.txt
```

---

## 14.11.18 — Text Processing

### OS-589 — Implement `cut`

Supporter la sélection de colonnes/champs.

---

### OS-590 — Implement `tr`

Supporter les transformations caractère par caractère.

---

### OS-591 — Implement `diff`

Comparer deux fichiers texte.

---

### OS-592 — Text Utility Streaming Tests

Tester toutes les utilities sur :

* gros fichiers
* stdin
* pipes
* Unicode
* lignes très longues

---

## 14.11.19 — Filesystem Utilities

### OS-593 — Implement `chmod`

Modifier les permissions selon les capacités autorisées.

---

### OS-594 — Implement `chown`

Modifier owner/group selon les permissions disponibles.

---

### OS-595 — Implement `ln`

Créer des liens selon le modèle filesystem supporté.

---

### OS-596 — Implement `readlink`

Lire la destination d'un symbolic link si les symlinks sont supportés.

---

## 14.11.20 — Environment Utilities

### OS-597 — Implement `env`

Afficher l'environnement.

---

### OS-598 — Implement `printenv`

Afficher une variable spécifique.

---

### OS-599 — Implement `true`

Retourner :

```text
0
```

---

### OS-600 — Implement `false`

Retourner :

```text
1
```

---

## 14.11.21 — Shell Integration

### OS-601 — Register Coreutils In `/bin`

Installer les executables :

```text
/bin/
├── cat
├── cp
├── echo
├── false
├── find
├── grep
├── head
├── kill
├── ls
├── mkdir
├── mv
├── ps
├── pwd
├── rm
├── rmdir
├── sort
├── stat
├── tail
├── tee
├── touch
├── true
├── uname
├── wc
└── ...
```

---

### OS-602 — Configure Default PATH

Configurer :

```text
PATH=/bin:/sbin:/usr/bin
```

---

### OS-603 — Shell/Coreutils Integration Tests

Tester :

```text
ls | grep
cat | grep | wc
find | sort
echo | tee
```

---

## 14.11.22 — Agent Utilities

### OS-604 — Define Agent Coreutils Contract

Les agents utilisent les mêmes utilities que les autres processus.

**Principle**

```text
Agent
 ↓
Shell / direct exec
 ↓
Coreutils
 ↓
Syscalls
 ↓
Kernel
```

Aucune commande spéciale agent.

---

### OS-605 — Agent Filesystem Utility Test

Tester :

```text
agent
 ↓
mkdir
 ↓
touch
 ↓
write
 ↓
cat
 ↓
grep
 ↓
rm
```

avec workspace isolé.

---

### OS-606 — Agent Process Utility Test

Tester :

```text
agent
 ↓
spawn
 ↓
ps
 ↓
kill
```

avec capabilities contrôlées.

---

## 14.11.23 — Capability Security

### OS-607 — Define Utility Capability Requirements

Documenter les capabilities nécessaires par utility.

Exemple :

```text
ls
 └── filesystem.read

cat
 └── filesystem.read

mkdir
 └── filesystem.write

rm
 └── filesystem.delete

ps
 └── process.inspect

kill
 └── process.signal
```

---

### OS-608 — Enforce Utility Capabilities

Les utilities ne doivent jamais contourner les contrôles du kernel.

---

### OS-609 — Coreutils Security Tests

Tester :

* unauthorized read
* unauthorized write
* unauthorized delete
* process isolation
* capability denial
* path traversal
* malformed paths

---

## 14.11.24 — Python Reference Model

### OS-610 — Implement Python Coreutils Model

Créer des modèles Python pour les opérations principales.

---

### OS-611 — Cross-Test Filesystem Utilities

Comparer Rust/Python sur :

```text
create
read
write
copy
move
delete
list
stat
```

---

### OS-612 — Cross-Test Process Utilities

Comparer :

```text
ps
kill
process state
exit status
```

---

## 14.11.25 — Testing

### OS-613 — Coreutils Unit Test Suite

Chaque utility doit avoir ses propres tests.

---

### OS-614 — Coreutils Integration Tests

Tester les utilities ensemble.

---

### OS-615 — Coreutils Pipeline Tests

Tester :

```text
cat | grep | sort | uniq | wc
```

---

### OS-616 — Coreutils Filesystem Stress Tests

Tester :

* milliers de fichiers
* répertoires profonds
* gros fichiers
* petits fichiers
* fichiers vides
* noms longs

---

### OS-617 — Coreutils Fuzz Tests

Fuzzer :

* arguments
* paths
* options
* input streams

---

### OS-618 — Coreutils Resource Limit Tests

Vérifier que les utilities respectent :

* CPU quota
* memory quota
* file descriptor limits
* process limits

---

## 14.11.26 — QEMU Validation

### OS-619 — Build Coreutils Into Root Filesystem

Intégrer les binaries dans l'image HexOS.

---

### OS-620 — QEMU Basic Filesystem Test

Tester :

```text
hexos$ mkdir test
hexos$ cd test
hexos$ touch hello.txt
hexos$ echo hello > hello.txt
hexos$ cat hello.txt
hello
```

---

### OS-621 — QEMU Pipeline Test

Tester :

```text
hexos$ echo hello | grep hello | wc
```

---

### OS-622 — QEMU Filesystem Test

Tester :

```text
mkdir
touch
cp
mv
ls
cat
rm
```

---

### OS-623 — QEMU Process Test

Tester :

```text
ps
kill
```

---

### OS-624 — QEMU Agent Test

Scénario :

```text
boot
 ↓
init
 ↓
agent
 ↓
workspace
 ↓
coreutils
 ↓
result
```

---

### OS-625 — Full Coreutils Regression

Exécuter automatiquement l'ensemble des tests Coreutils dans QEMU.

**Definition of Done**

* image construite automatiquement
* QEMU lancé automatiquement
* commandes exécutées
* outputs vérifiés
* exit codes vérifiés
* filesystem final vérifié

---

# Definition of Done — 14.11

La phase **Coreutils** est terminée lorsque :

* architecture Coreutils définie
* runtime library disponible
* conventions exit codes définies
* `echo`
* `pwd`
* `ls`
* `cat`
* `mkdir`
* `touch`
* `cp`
* `mv`
* `rm`
* `rmdir`
* `head`
* `tail`
* `grep`
* `find`
* `ps`
* `kill`
* `uname`
* `uptime`
* `free`
* `mount`
* `df`
* `du`
* `stat`
* `file`
* `wc`
* `sort`
* `uniq`
* `tee`
* `cut`
* `tr`
* `diff`
* `chmod`
* `chown`
* `ln`
* `readlink`
* `env`
* `printenv`
* `true`
* `false`

sont disponibles selon le périmètre défini.

En plus :

* utilities intégrées au PATH
* pipelines fonctionnels
* stdin/stdout/stderr fonctionnels
* filesystem correctement utilisé
* capabilities appliquées
* agent capable d'utiliser les utilities
* Python reference model disponible
* cross-tests disponibles
* fuzzing disponible
* stress tests disponibles
* QEMU regression suite fonctionnelle

---

# Architecture après 14.11

```text
┌──────────────────────────────────────────────────────────┐
│                       USER SPACE                         │
│                                                          │
│  ┌──────────────┐                                        │
│  │    Agent     │                                        │
│  └──────┬───────┘                                        │
│         │                                                 │
│         │       ┌──────────────┐                         │
│         └──────►│    Shell     │                         │
│                 └──────┬───────┘                         │
│                        │                                  │
│                 ┌──────▼───────┐                          │
│                 │  Coreutils   │                          │
│                 ├──────────────┤                          │
│                 │ ls cat grep  │                          │
│                 │ cp mv rm     │                          │
│                 │ ps kill ...  │                          │
│                 └──────┬───────┘                          │
│                        │                                  │
│                  User-space API                           │
└────────────────────────┼─────────────────────────────────┘
                         │
                      Syscalls
                         │
┌────────────────────────▼─────────────────────────────────┐
│                         KERNEL                            │
│                                                          │
│ Process │ Scheduler │ Memory │ Capabilities              │
│                                                          │
│ Syscalls │ IPC │ VFS │ TTY │ Devices                    │
└──────────────────────────────────────────────────────────┘
```

### Invariant architectural

> **Coreutils ne sont pas des primitives kernel.**
>
> **`ls` utilise le VFS.**
>
> **`ps` utilise les interfaces de processus.**
>
> **`kill` utilise les mécanismes de signaux.**
>
> **`cat` utilise les file descriptors.**
>
> **Le shell orchestre les programmes.**
>
> **Les agents utilisent exactement les mêmes primitives que les autres programmes.**
>
> **Le kernel ne connaît aucune de ces commandes.**


# 14.12 — Agent Runtime

**Objectif** : construire le runtime user-space permettant d'exécuter, superviser et faire communiquer des agents sur HexOS.

**Principe fondamental** :

```text
Agent Runtime ≠ Kernel
Agent Runtime = User-space system service
Agent = Process managed by the Runtime
```

Le runtime ne doit pas transformer le kernel en framework AI.

Le kernel fournit :

* processus
* mémoire
* capacités
* syscalls
* IPC
* filesystem
* TTY
* devices
* scheduling

Le runtime construit au-dessus :

* agent lifecycle
* agent identity
* agent workspace
* agent communication
* tool execution
* model interaction
* agent supervision
* runtime state

---

# 14.12.1 — Runtime Architecture

### OS-626 — Define Agent Runtime Architecture

Définir l'architecture du runtime.

**Requirements**

Identifier les composants :

```text
Agent Runtime
├── Agent Manager
├── Lifecycle Manager
├── Agent Registry
├── Workspace Manager
├── Capability Manager
├── IPC Manager
├── Execution Manager
├── State Manager
├── Tool Adapter
├── Model Adapter
└── Supervisor
```

**Definition of Done**

* architecture documentée
* responsabilités séparées
* aucune dépendance runtime → kernel internals

---

### OS-627 — Define Agent Runtime Contract

Définir le contrat public du runtime.

**Requirements**

* agent creation
* start
* stop
* pause
* resume
* status
* communication
* workspace
* capabilities
* resource limits
* termination

---

### OS-628 — Define Agent Identity Model

Créer l'identité logique d'un agent.

```text
AgentIdentity
├── agent_id
├── name
├── version
├── owner
├── runtime
└── metadata
```

**Definition of Done**

* identité unique
* immutable ID
* metadata séparées de l'identité

---

### OS-629 — Define Agent State Model

Définir les états :

```text
CREATED
STARTING
RUNNING
BLOCKED
PAUSED
STOPPING
STOPPED
FAILED
TERMINATED
```

**Definition of Done**

* transitions valides documentées
* transitions invalides rejetées

---

# 14.12.2 — Agent Registry

### OS-630 — Implement Agent Registry

Créer le registre des agents.

**Requirements**

* register
* lookup
* unregister
* list
* state tracking

---

### OS-631 — Implement Agent PID Mapping

Associer :

```text
Agent ID
    ↕
Process PID
```

**Definition of Done**

* mapping cohérent
* processus mort détecté
* agent state mis à jour

---

### OS-632 — Implement Agent Lifecycle Registry

Conserver :

* creation time
* start time
* stop time
* exit reason
* PID
* state

---

### OS-633 — Agent Registry Persistence

Définir ce qui doit survivre au redémarrage.

**Important**

Séparer :

```text
Runtime state
     ≠
Agent persistent state
```

---

# 14.12.3 — Agent Lifecycle

### OS-634 — Implement Agent Create

Créer un nouvel agent.

**Flow**

```text
create
  ↓
identity
  ↓
workspace
  ↓
capability profile
  ↓
resource limits
  ↓
READY
```

---

### OS-635 — Implement Agent Start

Démarrer l'agent.

```text
Agent Runtime
      ↓
spawn
      ↓
process
      ↓
exec
      ↓
agent
```

---

### OS-636 — Implement Agent Stop

Arrêt gracieux.

**Requirements**

* stop request
* grace period
* forced termination
* cleanup

---

### OS-637 — Implement Agent Pause

Suspendre temporairement l'exécution.

**Definition of Done**

* process suspendu
* état persisté côté runtime
* resources correctement comptabilisés

---

### OS-638 — Implement Agent Resume

Reprendre un agent suspendu.

---

### OS-639 — Implement Agent Restart

Redémarrer un agent après arrêt ou crash.

**Requirements**

* restart policy
* backoff
* restart count
* crash reason

---

### OS-640 — Agent Lifecycle State Machine Tests

Tester toutes les transitions :

```text
CREATED → STARTING
STARTING → RUNNING
RUNNING → PAUSED
PAUSED → RUNNING
RUNNING → STOPPING
STOPPING → STOPPED
RUNNING → FAILED
FAILED → STARTING
```

et les transitions invalides.

---

# 14.12.4 — Agent Process Model

### OS-641 — Define Agent Process Contract

Un agent est un processus standard avec :

```text
PID
Address Space
File Descriptors
Capabilities
Workspace
Resource Limits
```

---

### OS-642 — Implement Agent Process Bootstrap

Construire l'environnement initial.

**Requirements**

* stdin/stdout/stderr
* CWD
* environment
* workspace
* capabilities

---

### OS-643 — Implement Agent Environment

Variables spécifiques au runtime.

Exemple :

```text
AGENT_ID
AGENT_NAME
AGENT_WORKSPACE
AGENT_RUNTIME
```

---

### OS-644 — Implement Agent Process Cleanup

Nettoyer après terminaison :

* IPC channels
* file descriptors
* temporary resources
* runtime registry
* workspace handles

---

# 14.12.5 — Agent Workspace

### OS-645 — Define Agent Workspace Model

Chaque agent possède un espace de travail isolé.

```text
/agents/
├── agent-a/
│   ├── workspace/
│   ├── state/
│   └── tmp/
│
└── agent-b/
    ├── workspace/
    ├── state/
    └── tmp/
```

---

### OS-646 — Implement Workspace Creation

Créer automatiquement le workspace.

---

### OS-647 — Implement Workspace Mount

Associer le workspace au processus.

---

### OS-648 — Implement Workspace Isolation

Garantir :

```text
Agent A
  X
Agent B workspace
```

---

### OS-649 — Implement Workspace Cleanup

Définir la politique :

* conserver
* supprimer
* archiver

---

### OS-650 — Workspace Security Tests

Tester :

* traversal
* symlink escape
* unauthorized access
* mount escape
* cross-agent access

---

# 14.12.6 — Agent Capabilities

### OS-651 — Define Agent Capability Profiles

Créer des profils :

```text
minimal
standard
developer
network
operator
```

---

### OS-652 — Implement Minimal Agent Profile

Exemple :

```text
process.spawn: limited
filesystem.workspace: read/write
ipc.own: allowed
network: denied
devices: denied
```

---

### OS-653 — Implement Capability Assignment

Attribuer les capabilities au démarrage.

---

### OS-654 — Implement Runtime Capability Requests

Un agent peut demander une capability supplémentaire.

**Important**

```text
Agent
  ↓
Runtime request
  ↓
Policy evaluation
  ↓
Kernel capability grant
```

L'agent ne peut jamais s'attribuer lui-même une capability.

---

### OS-655 — Implement Capability Revocation

Permettre au runtime de retirer une capability.

---

### OS-656 — Capability Escalation Tests

Tester :

```text
Agent
 ↓
request privilege
 ↓
policy deny
 ↓
kernel deny
```

---

# 14.12.7 — Resource Management

### OS-657 — Define Agent Resource Contract

Définir les ressources contrôlables :

```text
CPU
Memory
Processes
File Descriptors
IPC
Storage
Network
```

---

### OS-658 — Implement CPU Limits

Associer un quota CPU à chaque agent.

---

### OS-659 — Implement Memory Limits

Associer un quota mémoire.

---

### OS-660 — Implement Process Limits

Limiter le nombre de processus enfants.

---

### OS-661 — Implement File Descriptor Limits

Limiter les FDs.

---

### OS-662 — Implement Storage Quotas

Limiter l'espace workspace.

---

### OS-663 — Resource Enforcement Tests

Tester :

* CPU exhaustion
* memory exhaustion
* fork/process exhaustion
* FD exhaustion
* storage exhaustion

---

# 14.12.8 — Agent IPC

### OS-664 — Define Agent IPC Model

Définir la communication inter-agents.

```text
Agent A
   │
   │ message
   ▼
IPC
   │
   ▼
Agent B
```

---

### OS-665 — Implement Agent Channels

Créer des channels logiques.

```text
channel:
    sender
    receiver
    permissions
    queue
```

---

### OS-666 — Implement Agent Messaging API

API user-space :

```text
send(agent_id, message)
receive()
```

---

### OS-667 — Implement Agent Message Envelope

Définir :

```text
Message
├── message_id
├── sender
├── receiver
├── timestamp
├── type
├── payload
└── correlation_id
```

---

### OS-668 — Implement Agent Request/Response

Supporter :

```text
Agent A
   │ request
   ▼
Agent B
   │ response
   ▼
Agent A
```

---

### OS-669 — Implement Agent Event Messaging

Supporter les messages one-way.

---

### OS-670 — Agent IPC Authorization

Chaque channel possède une policy.

```text
Agent A → Agent B : allowed
Agent A → Agent C : denied
```

---

### OS-671 — Agent IPC Isolation Tests

Tester :

* unauthorized send
* unauthorized receive
* spoofed sender
* cross-agent channel access
* message replay

---

# 14.12.9 — Agent Execution

### OS-672 — Define Agent Execution Model

Définir comment le runtime lance une unité de travail.

```text
Agent
 ↓
Task
 ↓
Execution
 ↓
Result
```

---

### OS-673 — Define Agent Task Model

```text
Task
├── task_id
├── agent_id
├── input
├── state
├── priority
├── deadline
└── result
```

---

### OS-674 — Implement Task Creation

Créer une tâche agent.

---

### OS-675 — Implement Task Queue

Queue interne user-space.

---

### OS-676 — Implement Task Execution

Associer une tâche à un processus/thread agent.

---

### OS-677 — Implement Task Cancellation

Permettre l'annulation.

---

### OS-678 — Implement Task Timeout

Ajouter un deadline.

---

### OS-679 — Implement Task Retry

Supporter :

```text
retry_count
backoff
retry_policy
```

---

# 14.12.10 — Model Adapter

### OS-680 — Define Model Adapter Interface

Le runtime doit abstraire le modèle.

```text
ModelAdapter
├── generate()
├── stream()
├── metadata()
└── health()
```

---

### OS-681 — Implement Local Model Adapter

Permettre l'utilisation d'un modèle local.

**Important**

Le kernel ne connaît pas le modèle.

---

### OS-682 — Implement Remote Model Adapter

Permettre un modèle distant.

---

### OS-683 — Define Model Request

```text
ModelRequest
├── messages
├── parameters
├── tools
├── context
└── metadata
```

---

### OS-684 — Define Model Response

```text
ModelResponse
├── content
├── tool_calls
├── usage
├── finish_reason
└── metadata
```

---

### OS-685 — Model Adapter Error Model

Gérer :

* timeout
* unavailable
* invalid response
* rate limit
* transport error

---

# 14.12.11 — Tool Execution

### OS-686 — Define Tool Adapter Interface

Abstraire les outils externes.

```text
ToolAdapter
├── discover()
├── describe()
├── execute()
└── health()
```

---

### OS-687 — Implement Tool Permission Model

Un agent ne peut appeler qu'un outil autorisé.

```text
Agent
 ↓
Tool request
 ↓
Policy
 ↓
Capability
 ↓
Tool adapter
```

---

### OS-688 — Implement Tool Invocation

Supporter :

```text
tool_name
arguments
timeout
correlation_id
```

---

### OS-689 — Implement Tool Result Model

```text
ToolResult
├── success
├── output
├── error
├── metadata
└── evidence
```

---

### OS-690 — Implement Tool Timeout

Limiter les appels longs.

---

### OS-691 — Implement Tool Cancellation

Permettre d'annuler une invocation.

---

### OS-692 — Tool Invocation Audit

Tracer :

* agent
* tool
* timestamp
* authorization result
* execution result
* duration

---

# 14.12.12 — MCP Integration

### OS-693 — Define MCP Runtime Adapter

MCP doit être intégré au runtime comme protocole user-space.

```text
Agent
 ↓
Agent Runtime
 ↓
MCP Client
 ↓
MCP Server
```

---

### OS-694 — Implement MCP Client

Supporter :

* connection
* discovery
* tool listing
* invocation
* response

---

### OS-695 — Implement MCP IPC Transport

Permettre MCP au-dessus de l'IPC lorsque client/server sont locaux.

**Important**

```text
MCP ≠ kernel IPC
```

MCP reste un protocole user-space.

---

### OS-696 — Implement MCP Network Transport

Supporter les MCP servers distants.

---

### OS-697 — MCP Capability Enforcement

Un agent ne peut utiliser MCP que si sa policy l'autorise.

---

### OS-698 — MCP Security Tests

Tester :

* unauthorized tool
* malformed response
* timeout
* connection failure
* capability denial
* server impersonation

---

# 14.12.13 — Agent Supervisor

### OS-699 — Define Agent Supervisor

Le supervisor surveille :

* process
* health
* resource usage
* task state
* crashes

---

### OS-700 — Implement Agent Heartbeat

Ajouter un heartbeat.

---

### OS-701 — Implement Agent Health State

États :

```text
HEALTHY
DEGRADED
UNRESPONSIVE
FAILED
```

---

### OS-702 — Implement Crash Detection

Détecter :

* process exit
* panic
* resource kill
* timeout

---

### OS-703 — Implement Automatic Restart

Appliquer la restart policy.

---

### OS-704 — Implement Crash Backoff

Éviter :

```text
crash
restart
crash
restart
crash
restart
...
```

---

### OS-705 — Supervisor Failure Tests

Tester :

* crash loop
* heartbeat timeout
* resource exhaustion
* dependency failure

---

# 14.12.14 — Agent Dependencies

### OS-706 — Define Agent Dependency Model

Un agent peut dépendre d'autres services/agents.

```text
Agent A
  ↓
Agent B
  ↓
Tool Service
```

---

### OS-707 — Implement Dependency Graph

Supporter :

* dependencies
* optional dependencies
* cycles
* ordering

---

### OS-708 — Implement Dependency Readiness

Un agent ne démarre que lorsque ses dépendances nécessaires sont disponibles.

---

### OS-709 — Dependency Failure Handling

Définir :

* retry
* degraded mode
* shutdown
* restart

---

# 14.12.15 — Agent State

### OS-710 — Define Persistent Agent State

Séparer :

```text
Process memory
       ≠
Runtime state
       ≠
Persistent agent state
```

---

### OS-711 — Implement Agent State Store

Stocker des données persistantes.

---

### OS-712 — Implement State Transactions

Garantir les mises à jour atomiques.

---

### OS-713 — Implement State Recovery

Restaurer l'état après restart.

---

### OS-714 — Agent State Isolation

Agent A ne peut pas lire :

```text
Agent B state
```

sans autorisation.

---

# 14.12.16 — Agent Context

### OS-715 — Define Agent Context Model

Définir le contexte runtime :

```text
AgentContext
├── identity
├── task
├── state
├── capabilities
├── workspace
├── resources
└── metadata
```

---

### OS-716 — Implement Context Construction

Construire le contexte avant exécution.

---

### OS-717 — Implement Context Limits

Limiter :

* context size
* state size
* metadata size

---

### OS-718 — Context Isolation Tests

Tester les frontières entre agents.

---

# 14.12.17 — Runtime API

### OS-719 — Define Runtime API

API permettant de gérer les agents :

```text
create_agent()
start_agent()
stop_agent()
pause_agent()
resume_agent()
get_agent()
list_agents()
send_message()
get_status()
```

---

### OS-720 — Implement Runtime CLI Interface

Exposer une interface CLI minimale.

```text
agent create
agent start
agent stop
agent status
agent list
agent logs
```

---

### OS-721 — Implement Runtime API Server

Créer éventuellement un serveur local user-space.

**Important**

Ce serveur n'est pas une primitive kernel.

---

### OS-722 — Runtime API Authentication

Protéger les opérations sensibles.

---

# 14.12.18 — Agent Logs

### OS-723 — Define Agent Logging Model

```text
LogEntry
├── timestamp
├── agent_id
├── level
├── message
└── metadata
```

---

### OS-724 — Implement Agent stdout Capture

Capturer stdout selon policy.

---

### OS-725 — Implement Agent stderr Capture

Capturer stderr.

---

### OS-726 — Implement Agent Log Storage

Stockage borné et rotation.

---

### OS-727 — Implement Agent Logs CLI

Supporter :

```text
agent logs <id>
```

---

# 14.12.19 — Runtime Security

### OS-728 — Define Runtime Threat Model

Documenter :

* malicious agent
* compromised tool
* compromised model output
* malicious MCP server
* hostile input
* resource exhaustion
* capability abuse

---

### OS-729 — Implement Runtime Input Validation

Valider :

* agent IDs
* task IDs
* tool arguments
* IPC messages
* state updates

---

### OS-730 — Implement Runtime Default Deny

Toute opération non explicitement autorisée est refusée.

---

### OS-731 — Implement Runtime Audit Log

Tracer les opérations sensibles :

```text
agent created
capability granted
tool invoked
MCP connected
state changed
agent terminated
```

---

### OS-732 — Runtime Security Regression Suite

Tester systématiquement :

* capability escalation
* workspace escape
* process escape
* IPC abuse
* tool abuse
* state access
* resource exhaustion

---

# 14.12.20 — Python Reference Runtime

### OS-733 — Implement Python Agent Model

Modéliser :

* identity
* state
* lifecycle
* capabilities
* workspace
* resources

---

### OS-734 — Implement Python Agent Registry

---

### OS-735 — Implement Python Agent Lifecycle

---

### OS-736 — Implement Python Agent IPC

---

### OS-737 — Implement Python Task Model

---

### OS-738 — Implement Python Tool Model

---

### OS-739 — Implement Python Supervisor

---

### OS-740 — Cross-Test Rust/Python Runtime

Comparer les transitions :

```text
create
start
execute
communicate
pause
resume
stop
restart
```

---

# 14.12.21 — Runtime Testing

### OS-741 — Agent Runtime Unit Tests

Tester tous les composants isolément.

---

### OS-742 — Agent Runtime Integration Tests

Tester :

```text
Runtime
 ↓
Process
 ↓
Syscalls
 ↓
IPC
 ↓
VFS
```

---

### OS-743 — Multi-Agent Integration Test

Scénario :

```text
Agent A
   │
   │ message
   ▼
Agent B
   │
   ▼
Tool
```

---

### OS-744 — Agent Resource Stress Test

Tester plusieurs agents simultanés.

---

### OS-745 — Agent Crash Recovery Test

Tester :

```text
agent
 ↓
crash
 ↓
supervisor
 ↓
restart
 ↓
agent
```

---

### OS-746 — Agent Security Fuzzing

Fuzzer :

* agent configuration
* IPC messages
* tool arguments
* state
* runtime API

---

### OS-747 — Runtime Determinism Tests

Vérifier que les opérations déterministes du runtime produisent les mêmes résultats à entrée identique.

**Important**

La partie LLM peut être non déterministe.

Le runtime ne doit pas l'être inutilement.

---

# 14.12.22 — QEMU End-to-End

### OS-748 — Build Agent Runtime Into Userland

Intégrer le runtime à l'image HexOS.

---

### OS-749 — Boot Runtime Service

Faire démarrer :

```text
Kernel
 ↓
Init
 ↓
Agent Runtime
```

---

### OS-750 — Create First Agent In QEMU

Tester :

```text
hexos$ agent create demo
```

---

### OS-751 — Start Agent In QEMU

```text
hexos$ agent start demo
```

---

### OS-752 — Inspect Agent

```text
hexos$ agent status demo
```

---

### OS-753 — Agent Workspace Test

```text
hexos$ agent exec demo
```

Puis vérifier :

```text
/agents/demo/workspace
```

---

### OS-754 — Agent IPC Test

Créer deux agents :

```text
agent-a → message → agent-b
```

---

### OS-755 — Agent Tool Test

Tester :

```text
Agent
 ↓
Runtime
 ↓
Tool Adapter
 ↓
Tool
 ↓
Result
```

---

### OS-756 — Agent MCP Test

Tester :

```text
Agent
 ↓
Runtime
 ↓
MCP Client
 ↓
MCP Server
 ↓
Tool
```

---

### OS-757 — Agent Crash Recovery Test

Tester :

```text
Agent
 ↓
crash
 ↓
Supervisor
 ↓
restart
```

---

### OS-758 — Full Agent OS Test

Scénario complet :

```text
┌───────────────────────────────────────────┐
│                 HexOS                     │
│                                           │
│ Kernel                                    │
│   ↓                                       │
│ Init                                      │
│   ↓                                       │
│ Agent Runtime                             │
│   ├── Agent A                             │
│   ├── Agent B                             │
│   └── Agent C                             │
│        │                                  │
│        ├── IPC                            │
│        ├── Workspace                      │
│        ├── Tools                          │
│        └── MCP                            │
│                                           │
└───────────────────────────────────────────┘
```

**Definition of Done**

* boot automatisé
* runtime démarré
* agents créés
* agents isolés
* agents communiquent
* tools exécutés
* MCP fonctionnel
* crash recovery fonctionnel
* resource limits vérifiées
* security tests passés
* logs disponibles

---

# Definition of Done — 14.12

La phase **Agent Runtime** est terminée lorsque :

* architecture runtime définie
* agent identity disponible
* agent registry disponible
* lifecycle complet fonctionnel
* agent = processus user-space
* workspace isolé
* capabilities intégrées
* resource limits intégrées
* agent IPC fonctionnel
* task model fonctionnel
* model adapter disponible
* tool adapter disponible
* MCP adapter disponible
* supervisor disponible
* crash recovery disponible
* dependency model disponible
* persistent state disponible
* context model disponible
* runtime API disponible
* CLI disponible
* logs disponibles
* threat model documenté
* default deny appliqué
* audit disponible
* Python reference runtime disponible
* Rust/Python cross-tests disponibles
* unit/integration/stress/fuzz tests disponibles
* QEMU end-to-end validé

---

# Architecture finale — Agent OS Layer

```text
┌──────────────────────────────────────────────────────────────┐
│                         USER SPACE                           │
│                                                              │
│  ┌────────────────────── AGENT RUNTIME ────────────────────┐ │
│  │                                                         │ │
│  │ Agent Manager      Supervisor       State Manager       │ │
│  │      │                  │                 │              │ │
│  │      ├──────────────┬───┴─────────────┐   │              │ │
│  │      ↓              ↓                 ↓   ↓              │ │
│  │  Agent A          Agent B           Agent C              │ │
│  │      │              │                 │                  │ │
│  │      ├──────────────┼─────────────────┤                  │ │
│  │      │              │                 │                  │ │
│  │     IPC          Workspace        Capabilities           │ │
│  │      │                                │                  │ │
│  │      └──────────────┬─────────────────┘                  │ │
│  │                     ↓                                    │ │
│  │              Tool / Model / MCP                          │ │
│  │                     │                                    │ │
│  └─────────────────────┼────────────────────────────────────┘ │
│                        │                                     │
│                  User-space APIs                             │
└────────────────────────┼─────────────────────────────────────┘
                         │
                      Syscalls
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                           KERNEL                             │
│                                                             │
│ Process │ Scheduler │ Memory │ Capabilities                 │
│                                                             │
│ Syscalls │ IPC │ VFS │ TTY │ Devices                       │
└─────────────────────────────────────────────────────────────┘
```

# Les invariants fondamentaux

> **1. Un agent est un processus.**

> **2. Le runtime est un programme user-space.**

> **3. Le kernel ne connaît ni LLM, ni MCP, ni tools.**

> **4. Le runtime ne peut pas contourner le kernel.**

> **5. Policy décide ce qui est autorisé.**

> **6. Capability représente ce qui est accordé.**

> **7. Kernel enforce ce qui est accordé.**

> **8. MCP est un protocole user-space.**

> **9. IPC est une primitive kernel.**

> **10. Un agent compromis reste enfermé dans son process, ses capabilities, son workspace et ses quotas.**




# PHASE 15 — AGENTIC COMPUTER

> **Vision long terme — cette phase est volontairement challengeable.**
>
> L'objectif n'est pas de supposer que les interfaces graphiques vont disparaître.
> L'objectif est de construire un système dans lequel l'interface utilisateur
> n'est plus une dépendance fondamentale du système informatique.
>
> Le computer doit pouvoir être contrôlé par :
>
> - langage naturel
> - voix
> - terminal
> - interface graphique
> - API
> - agents
> - automatisations
>
> Toutes ces interfaces convergent vers la même couche :
>
> **Intent → Agent Runtime → Capabilities → Kernel → Execution**

---

# 15.0 — Vision & Architecture

## Goal

Transformer Hexagents en une plateforme permettant à un humain de contrôler un ordinateur principalement par **intention**, plutôt que par manipulation explicite d'applications.

Le système doit permettre :

```text
Human
  │
  │ natural language / voice / UI / CLI
  ▼
Intent Layer
  │
  ▼
Agent Runtime
  │
  ▼
Capabilities / Policy
  │
  ▼
Hexagents Kernel
  │
  ▼
System Resources





