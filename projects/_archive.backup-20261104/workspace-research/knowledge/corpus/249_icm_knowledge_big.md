---
type: Concept
id: 249_icm_knowledge_big
title: "ICM_knowledge.md (part 250/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

— self-animating signal struggle. Three layered sine waves (0.4, 0.17, 0.07 Hz) modulate overall intensity. Slider controls bias: 0 = fully corrupted, 0.5 = equal war, 1 = signal winning. Whole frame breathes together — no patches, no flicker.

Point Cloud Detail (Effect 14)

#### Dissolves image into living, breathing soft particles. Key design decisions:

Analog feel

— particles jittered off the grid (90% cell offset), FBM noise for drift (not sine waves), each particle has unique timing from its cell seed

— particles break free with random burst direction + quadratic gravity (feels physical). Each particle has a random "break threshold" — as Flyaway increases, more particles detach progressively.

— flying particles shrink with distance (

1 / (1 + distance * 1.5)

) + alpha fade. Creates perspective.

Gravity direction

— user-controllable angle (270° = down). Particles can travel across the entire frame, not bounded by source region.

Depth Scatter

— dark regions scatter more, bright areas hold together. Creates the dissolving-from-shadows look.

Wide search radius

— up to 8 cells in each direction to find particles that have scattered/flown far.

------

Source Files

Core (hand-authored)

src/core/CrushPlugin.h/.cpp

— OFX effect class. N-slot render loop, SPAZ random logic, CHILL modulation, progressive slot reveal via

changedParam

. Function pointer arrays dispatch per-slot visibility/fetch.

src/core/CrushProcessor.h/.cpp

— OFX ImageProcessor subclass. Routes to Metal or CPU. Holds CrushRenderParams struct and temporal frame pointers (max 28).

src/core/MetalKernel.mm

— ALL Metal shader code as inline C strings:

— hash, noise, FBM, bilinear sampler (

crush_sample

kMasterKernelSource

— all 14 effect shaders + DECIMATE post-process + CrushKernel dispatch

kTemporalKernelSource

— CrushFeedbackKernel (effect 10) + CrushSlitScanKernel (effect 7)

#### Pipeline caches:

s_CrushPipelineMap

s_CrushTemporalPipelineMap

Build System

CMakeLists.txt

— CMake 3.15+, C++17, universal binary (arm64+x86_64), .ofx.bundle output

— macOS bundle metadata

— Python generator. 6-slot architecture (

MAX_SLOTS = 6

). Generates visibility, fetch, and param definitions for all slots.

------

CrushRenderParams Struct Layout (must match Metal shader struct)

int effectId, width, height, temporalFrameCount float time, frame, disintegrate int decimateDir // 0=down, 1=up, 2=left, 3=right float values[16]   // effect params (float) int intValues[16]  // effect params (int, parallel to values[])

------

Key Constraints & Gotchas

Canonical source. Shared subset extracted to [[ofx_metal_gotchas]] for CBA_, FUZZ_, SUBTRACKT_, GRAPHFX_.

OFX / Metal

setGPURenderArgs(p_Args)

is MANDATORY

— without it,

_pMetalCmdQ

is garbage and Metal crashes Resolve.

Don't add grouped params to the page

page->addChild(*group)

. Individual params use

setParent(*group)

only. Double-registration crashes Resolve.

Metal buffer casting
