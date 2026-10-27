---
type: Concept
title: "Scheduling and Checkpointing optimization algorithm for Byzantine fault tolerance in Cloud Clusters"
source: "http://arxiv.org/abs/1802.00951v1"
tags: [research-loop,autonomous-agent]
created: "2026-09-22T18:52:25.930432Z"
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Scheduling and Checkpointing optimization algorithm for Byzantine fault tolerance in Cloud Clusters

**Source:** http://arxiv.org/abs/1802.00951v1
**Authors:**
**Tags:** `research-loop,autonomous-agent`

## Core Methodology & Findings

Among those faults Byzantine faults offers serious challenge to fault tolerance mechanism, because it often go undetected at the initial stage and it can easily propagate to other VMs before a detection is made. Consequently some of the mission critical application such as air traffic control, online baking etc still staying away from the cloud for such reasons. However if a Byzantine faults is not detected and tolerated at initial stage then applications such as big data analytics can go completely wrong in spite of hours of computations performed by the entire cloud. Therefore in the previous work a fool-proof Byzantine fault detection has been proposed, as a continuation this work designs a scheduling algorithm (WSSS) and checkpoint optimization algorithm (TCC) to tolerate and eliminate the Byzantine faults before it makes any impact. The WSSS algorithm keeps track of server performance which is part of Virtual Clusters to help allocate best performing server to mission critical application. WSSS therefore ranks the servers based on a counter which monitors every Virtual Nodes (VN) for time and performance failures. The TCC algorithm works to generalize the possible Byzantine error prone region through monitoring delay variation to start new VNs with previous checkpointing. Moreover it can stretch the state interval for performing and error free VNs in an effect to minimize the space, time and cost overheads caused by checkpointing. The analysis is performed with plotting state transition and CloudSim based simulation. The result shows TCC reduces fault tolerance overhead exponentially and the WSSS allots virtual resources effectively

## Algorithm / Pipeline

The methodology involves a structured approach as described in the source material.

## Data Structures

Uses standard data storage and retrieval mechanisms for simulation and analysis.

## Threat Model & Limitations

Known risks/challenges: challenge to fault tolerance mechanism, because it often go undetected at the initial stage and it can easily propagate to other VMs before a detection is made.

## Limitations

Limitations and scope are described in the original publication.
