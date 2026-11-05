---
type: Concept
title: "Byzantine Fault Tolerant Distributed Quickest Change Detection"
source: "http://arxiv.org/abs/1306.2086v2"
tags: [research-loop,autonomous-agent]
created: "2026-09-22T18:52:25.934619Z"
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Byzantine Fault Tolerant Distributed Quickest Change Detection

**Source:** http://arxiv.org/abs/1306.2086v2
**Authors:**
**Tags:** `research-loop,autonomous-agent`

## Core Methodology & Findings

We introduce and solve the problem of Byzantine fault tolerant distributed quickest change detection in both continuous and discrete time setups. In this problem, multiple sensors sequentially observe random signals from the environment and send their observations to a control center that will determine whether there is a change in the statistical behavior of the observations. We assume that the signals are independent and identically distributed across sensors. An unknown subset of sensors are compromised and will send arbitrarily modified and even artificially generated signals to the control center. It is shown that the performance of the the so-called CUSUM statistic, which is optimal when all sensors are honest, will be significantly degraded in the presence of even a single dishonest sensor. In particular, instead of in a logarithmically the detection delay grows linearly with the average run length (ARL) to false alarm. To mitigate such a performance degradation, we propose a fully distributed low complexity detection scheme. We show that the proposed scheme can recover the log scaling. We also propose a centralized group-wise scheme that can further reduce the detection delay.

## Algorithm / Pipeline

The methodology involves a structured approach as described in the source material.

## Data Structures

Uses standard data storage and retrieval mechanisms for simulation and analysis.

## Threat Model & Limitations

Known risks/challenges: problem of Byzantine fault tolerant distributed quickest change detection in both continuous and discrete time setups.; problem, multiple sensors sequentially observe random signals from the environment and send their observations to a control center that will determine whether there is a change in the statistical behavior of the observations.

## Limitations

Limitations and scope are described in the original publication.
