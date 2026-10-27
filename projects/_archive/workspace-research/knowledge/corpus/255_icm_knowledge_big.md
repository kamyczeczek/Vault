---
type: Concept
id: 255_icm_knowledge_big
title: "ICM_knowledge.md (part 256/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

The core principle is the same everywhere: categorical nesting by domain, with descriptive names, keeping files small and focused. Here's how that maps to each language ecosystem.

JavaScript / TypeScript (Vue, Quasar, Node)

├── modules/          # Feature modules (self-contained)

│  ├── auth/

│  │  ├── index.ts      # Module entry, re-exports

│  │  ├── store.ts      # Pinia store (composition API)

│  │  ├── api.ts       # API calls for this module

│  │  ├── types.ts      # Types/interfaces for this module

│  │  ├── AuthLogin.vue    # Components named descriptively

│  │  ├── AuthRegister.vue

│  │  └── components/     # Sub-components if needed

│  │    └── AuthFormField.vue

│  └── dashboard/

│    ├── index.ts

│    ├── store.ts

│    ├── api.ts

│    └── DashboardOverview.vue

├── services/          # Shared services (API client, DB, etc.)

│  ├── apiClient.ts      # Centralized fetch wrapper

│  ├── db/

│  │  ├── client.ts

│  │  └── tables/

│  │    ├── userSettings.ts

│  │    └── sessionHistory.ts

│  └── fileWatcher.ts

├── stores/           # Global stores (app-wide state)

│  └── globalAppState.ts

├── components/         # Shared components (used across modules)

│  ├── AppHeader.vue

│  └── ConfirmDialog.vue

├── composables/        # Shared composables

│  └── useWindowResize.ts

├── types/           # Global types

│  └── appTypes.ts

├── layouts/          # Page layouts

├── pages/           # Route pages

├── router/           # Vue Router config

├── boot/            # Startup/init files

├── css/            # Global styles

└── utils/           # Platform detection, formatters

└── platformDetection.ts

#### Key conventions:

Each feature module has index.ts, store.ts, api.ts, types.ts

Components are PascalCase: UserProfileCard.vue

Everything else is camelCase: apiClient.ts, useAuth.ts

Path aliases: @/ for src/, @modules/, @components/, @stores/

#### Apply the same categorical nesting using Rust's module system:

├── main.rs             # Entry point, minimal — just init and run

├── app.rs             # Application setup, config, state

├── lib.rs             # Library entry (if crate is also a lib)

├── commands/            # Tauri commands or CLI handlers

│  ├── mod.rs           # Re-exports all command modules

│  ├── file_operations.rs     # File read/write/watch commands

│  ├── window_management.rs    # Window creation/positioning

│  └── backend_lifecycle.rs    # Start/stop/health-check backend

├── services/            # Business logic, reusable across commands

│  ├── mod.rs

│  ├── process_manager.rs     # Spawn/kill/monitor child processes

│  ├── port_allocator.rs      # Find available ports

│  └── log_writer.rs        # Write structured logs to files

├── models/             # Data structures, enums, types

│  ├── mod.rs

│  ├── app_config.rs        # Config structs

│  └── backend_state.rs      # Backend process state

├── platform/            # OS-specific code
