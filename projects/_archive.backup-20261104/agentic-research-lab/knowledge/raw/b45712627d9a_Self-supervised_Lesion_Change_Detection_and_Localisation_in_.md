---
type: Concept
title: "Self-supervised Lesion Change Detection and Localisation in Longitudinal Multiple Sclerosis Brain Imaging"
source: "http://arxiv.org/abs/2106.00919v1"
tags: [research-loop,autonomous-agent]
created: "2026-09-22T18:27:19.282570Z"
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Self-supervised Lesion Change Detection and Localisation in Longitudinal Multiple Sclerosis Brain Imaging

**Source:** http://arxiv.org/abs/2106.00919v1
**Authors:**
**Tags:** `research-loop,autonomous-agent`

## Core Methodology & Findings

Longitudinal imaging forms an essential component in the management and follow-up of many medical conditions. The presence of lesion changes on serial imaging can have significant impact on clinical decision making, highlighting the important role for automated change detection. Lesion changes can represent anomalies in serial imaging, which implies a limited availability of annotations and a wide variety of possible changes that need to be considered. Hence, we introduce a new unsupervised anomaly detection and localisation method trained exclusively with serial images that do not contain any lesion changes. Our training automatically synthesises lesion changes in serial images, introducing detection and localisation pseudo-labels that are used to self-supervise the training of our model. Given the rarity of these lesion changes in the synthesised images, we train the model with the imbalance robust focal Tversky loss. When compared to supervised models trained on different datasets, our method shows competitive performance in the detection and localisation of new demyelinating lesions on longitudinal magnetic resonance imaging in multiple sclerosis patients. Code for the models will be made available on GitHub.

## Algorithm / Pipeline

The methodology involves a structured approach as described in the source material.

## Data Structures

Uses standard data storage and retrieval mechanisms for simulation and analysis.

## Threat Model & Limitations

Potential challenges may include scalability, computational cost, and generalization to unseen scenarios.

## Limitations

limited availability of annotations and a wide variety of possible changes that need to be considered. Hence, we introduce a new unsupervised anomaly
