---
type: Concept
id: 256_icm_knowledge_big
title: "ICM_knowledge.md (part 257/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

│  ├── mod.rs           # Conditional compilation re-exports

│  ├── macos.rs          # macOS-specific (menus, notifications)

│  ├── windows.rs

│  └── linux.rs

└── utils/             # Small, focused helpers

└── path_resolver.rs      # Resolve app paths, home dir, etc.

#### Key conventions:

mod.rs in each directory for re-exports (like index.ts)

snake_case for everything: files, functions, variables, modules

Descriptive module names: backend_lifecycle.rs not backend.rs

Keep main.rs thin — delegate to app.rs or modules immediately

Group by responsibility, not by Rust convention alone

Include lib.rs when the crate should be usable as a library

Follow categorical nesting for headers, with source files mirroring the structure. Every module should be structured for library extraction from day one.

include/              # Public headers (categorical nesting)

├── core/              # Core functionality

│  ├── memory_allocator.h

│  ├── string_operations.h

│  └── error_codes.h

├── arch/              # Architecture-specific

│  ├── arm64.h

│  ├── x86_64.h

│  └── riscv32.h

├── os/               # OS-specific abstractions

│  ├── linux_syscalls.h

│  ├── darwin_syscalls.h

│  └── windows_syscalls.h

├── fmt/              # File format parsers

│  ├── elf_parser.h

│  ├── macho_parser.h

│  └── pe_parser.h

└── sys/              # System-level interfaces

└── thread_pool.h

src/                # Implementation files (mirror include/ structure)

│  ├── memory_allocator.c

│  ├── string_operations.c

│  └── error_codes.c

│  ├── arm64.c

│  └── x86_64.c

├── linux_syscalls.c

└── darwin_syscalls.c

tests/               # Test files (mirror src/ structure)

│  ├── test_memory_allocator.c

│  └── test_string_operations.c

└── integration/

└── test_full_pipeline.c

#### Key conventions:

include/ and src/ mirror each other's structure

Category directories by domain: core/, arch/, os/, fmt/, sys/

snake_case for all file names

Header names describe what's inside: memory_allocator.h not mem.h

One header + one source per logical unit

Headers define the full API contract (see Function Documentation section)

Each category directory is a potential standalone library

Swift (macOS / iOS)

├── App/              # App entry, lifecycle

│  ├── AppMain.swift

│  └── AppDelegate.swift

├── Features/            # Feature modules

│  ├── Camera/

│  │  ├── CameraManager.swift

│  │  ├── CameraPreviewView.swift

│  │  └── CameraPermissions.swift

│  └── Recording/

│    ├── RecordingSession.swift

│    ├── RecordingOverlay.swift

│    └── RecordingStorage.swift

├── Services/            # Shared services

│  ├── FileStorageService.swift

│  └── NotificationService.swift

├── Models/             # Data models

│  ├── RecordingMetadata.swift

│  └── UserPreferences.swift

├── Views/             # Shared UI components

│  ├── PermissionRequestView.swift

│  └── StatusIndicator.swift

├── Extensions/           # Swift extensions
