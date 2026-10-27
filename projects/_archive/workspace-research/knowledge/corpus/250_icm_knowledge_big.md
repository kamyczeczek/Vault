---
type: Concept
id: 250_icm_knowledge_big
title: "ICM_knowledge.md (part 251/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

— OFX pixel pointers ARE Metal buffer objects.

reinterpret_cast<id>(float\*)

No pointer-to-pointer buffers

— for temporal frames, bind each as separate buffer index (3-30, max 28).

Pipeline state caching

— cache per

MTLCommandQueue

with mutex. Compile once, reuse.

fastMathEnabled

deprecated in macOS 15

@available(macOS 15.0, *)

Visibility on load

— set initial state in constructor. Hide slots 2-6 dropdowns too.

codesign --force --sign -

post-build. Unsigned = won't load.

Bounds checking

if ((id.x >= w) || (id.y >= h)) return;

first line of every kernel.

Thread group size

threadExecutionWidth

, don't hardcode.

setOpen(true)

— so they appear expanded when the user selects them.

Shader Development

Color preservation

— never decay/multiply colors. Source pixel taken exactly.

Bilinear sampling

crush_sample()

for all displaced UV lookups. Integer truncation causes visible banding/stairstepping when effects are stacked.

— "content falls DOWN" = sample from

py + dripDist

. Think "where does the replacement come from."

Per-column noise

— multi-octave hash for jagged edges. Gap columns stay clean.

Self-animation

— layered sine waves at irrational ratios (0.4, 0.17, 0.07). Modulate intensity, not regions.

Analog, not digital

— FBM noise for particle drift, jitter off grid, smooth continuous motion. Sine waves feel robotic. FBM feels alive.

SPAZ safety

— skip temporal effects (7, 10) and Depth-Splatting (11). Constrain ranges per-effect.

Dissolution = posterize, not dim

— reduce bit depth + channel noise. Never

result.rgb *= 0.5

Glow = screen blend

1 - (1-a)(1-b)

. Never additive

which clips to white.

Depth splatting centering

— depth mapped as

(luma - 0.5) * 2.0

so mid-grey = zero displacement. S-curve compression prevents pinching at extremes.

Point size visibility

— quantize output to cell grid, not blur around sample point. Each cell renders as one visible point with the cell center's color.

Shader compilation failure = white frames

— if Metal shader has undefined variables, it fails silently and everything renders white. Check for stale variable references after refactoring.

DaVinci Resolve Specifics

Plugin appears under CRUSH_ grouping

in OpenFX panel.

Restart Resolve

after every install — plugins cached at startup.

OFX plugins directory

/Library/OFX/Plugins/

~/Library/OFX/Plugins/

Maximum 31 Metal buffer bindings

(indices 0-30).

------

Adding a New Effect

src/crush/new_effect.crush

with JSON schema (see existing files)

Add shader function to

MetalKernel.mm

kMasterKernelSource

crush_effectname()

to the switch in

CrushKernel

If adding to SPAZ: update

safeEffects[]

in CrushPlugin.cpp with constrained param ranges

python3 build.py

— generates all 6 slots of params, visibility, fetch

cmake --build build

#### Install and restart Resolve

------

david vogel\Developer Resources\ADVANCED Coding Best Practices.md

ADVANCED: Coding Best Practices
