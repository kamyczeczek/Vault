---
type: Concept
id: 248_icm_knowledge_big
title: "ICM_knowledge.md (part 249/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

(toggle) — deterministic random effect cycling. Picks from 11 safe effects (skips Slit-Scan, Digital Feedback, Depth-Splatting). Per-effect constrained param ranges prevent white frames.

SPAZ Intensity

(0-1) — 0 = mild params + long bursts, 1 = extreme params + short bursts

(toggle) — slow breathing intensity modulation. Layered sine waves scale all param values toward zero and back. Self-animating.

CHILL Speed

(0-1) — 0 = glacial (10+ sec cycles), 1 = moderate (2-3 sec cycles)

Generated Files (do not hand-edit)

files and generates into

src/generated/

EffectRegistry.gen.h

— plugin identity, effect enum, slot dropdown defines, global param defines, kMaxSlots

ParamDefs.gen.h

— all parameter #defines for all 6 slots ("" = slot 1, "C2"-"C6" prefixes)

ParamBindings.gen.h

— per-effect uniform structs

VisibilityLogic.gen.cpp

crushSetParamVisibility()

crushSetParamVisibility_C2()

crushDefineParams()

FetchDispatch.gen.cpp

crushFetchParams()

crushFetchParams_C2()

switch dispatch

N-Slot Plugin Architecture

CrushPlugin.cpp

, slot functions are dispatched via arrays:

static VisibilityFn s_VisibilityFns[kMaxSlots] = { crushSetParamVisibility, _C2, _C3, _C4, _C5, _C6 }; static FetchFn s_FetchFns[kMaxSlots] = { crushFetchParams, _C2, _C3, _C4, _C5, _C6 }; static const char* s_SlotParamNames[kMaxSlots] = { kParamEffectSelect, _2, _3, _4, _5, _6 };

The render loop iterates active slots, each creating a CrushProcessor pass.

------

Effects (14 total)

Key Technique

Bilinear-sampled UV displacement per channel

Pixel Sorting

Directional luma-weighted displacement with per-row noise

Macroblocking

floor() UV quantization with posterization

Datamoshing

Simulated motion vector accumulation

VHS Tracking

Sine noise + YIQ chroma degrade

Scanline Jitter

Row-based hash noise offset

Y-axis temporal offset (temporal, max 28 frames, per-buffer binding)

Screen Tearing

Horizontal sync-split

Turbulent Displacement

2D FBM noise UV warp

Digital Feedback

Blend with previous frame + scale/rotation (temporal)

Depth-Splatting

Luma-as-depth parallax, S-curve compression, voxel snap, soft point rendering

GITS-style directional streak corruption with Fight self-animation

CMYK plate separation with bilinear sampling, per-plate directional offset

Point Cloud

Particle dissolution with FBM-driven organic scatter, flyaway gravity physics

DECIMATOR Detail (Effect 12)

The flagship. Per-column/row vertical streaking with direction control, chromatic channel separation. Sub-effects:

Dissolution

— posterizes pixel data (reduces bit depth) + per-channel noise. NOT black pixels — actual data degradation.

— 7×7 neighborhood screen blend bloom. Never clips to white.

— horizontal banding with random dark bands
