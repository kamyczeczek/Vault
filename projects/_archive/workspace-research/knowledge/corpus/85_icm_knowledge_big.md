---
type: Concept
id: 85_icm_knowledge_big
title: "ICM_knowledge.md (part 86/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

, you saw those seven layers. This is the same stack, viewed from a different angle. 2.2 showed you the layers. This lesson shows you the pattern that connects them: templates all the way down.

------

Memory in traditional computing

Templates need to be filled with something, and that something has to be stored somewhere. Which brings us to memory.

In traditional computing, memory is a hierarchy. At the top, closest to the processor, you have registers. Tiny, incredibly fast. Maybe 64 bits each. A handful of values the CPU can access in a single cycle.

One level up in size, you have the cache. Still fast, still small, measured in kilobytes or megabytes. This is where the machine keeps data it thinks it will need again. The principle is called locality: if you accessed something once, you will probably access it again. If you accessed this address, you will probably access a nearby address. Cache exploits that pattern.

Then you have main memory: RAM. Random access memory. Larger, slower, measured in gigabytes. This is what most people think of when they think of computer memory. It holds the working state of programs. When you open an application, its code and data load from the disk into RAM so the processor can access them without waiting for the slow process of reading from storage.

Below that, you have disks (solid state or spinning magnetic platters). Terabytes. Persistent. When you save a file, this is where it goes. And below that, archival storage: tape, cold storage, the stuff you back up and rarely touch.

The whole system is a trade-off between speed and capacity. Fast memory is expensive and small. Cheap memory is slow but large. So we build hierarchies. We move data between levels based on how often it is accessed. We predict what we will need and stage it closer to the processor.

But here is the part that matters for what comes next. In all of this, there is a hard boundary between code and data. The instructions that tell the machine what to do are kept separate from the information the machine operates on. Mixing them is considered a security vulnerability. It is how buffer overflow attacks work: you trick the machine into treating data as code. The separation is foundational. It is baked into the architecture.

Until it is not.

------

Memory in AI systems

When people talk about AI memory, they usually mean one of two things. Either the model's training (the patterns baked into the weights through exposure to data) or the context window (the text the model can see during a single conversation). But if you are building with these systems, there is a lot more going on. There is a hierarchy here too. And it rhymes with the one we just talked about, but the differences matter.

Model weights
