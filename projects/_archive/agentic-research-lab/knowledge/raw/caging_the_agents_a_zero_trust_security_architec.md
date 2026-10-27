---
type: Concept
title: "Caging the Agents: A Zero Trust Security Architecture for Autonomous AI in Healthcare"
source: "http://arxiv.org/abs/2603.17419v1"
tags: [agentic, scientific-discovery]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Caging the Agents: A Zero Trust Security Architecture for Autonomous AI in Healthcare

**Source:** http://arxiv.org/abs/2603.17419v1
**Tags:** `agentic, scientific-discovery`

## Core Methodology & Findings

**Authors:** Saikat Maiti

### Abstract
Autonomous AI agents powered by large language models are being deployed in production with capabilities including shell execution, file system access, database queries, and multi-party communication. Recent red teaming research demonstrates that these agents exhibit critical vulnerabilities in realistic settings: unauthorized compliance with non-owner instructions, sensitive information disclosure, identity spoofing, cross-agent propagation of unsafe practices, and indirect prompt injection through external resources [7]. In healthcare environments processing Protected Health Information, every such vulnerability becomes a potential HIPAA violation. This paper presents a security architecture deployed for nine autonomous AI agents in production at a healthcare technology company. We develop a six-domain threat model for agentic AI in healthcare covering credential exposure, execution capability abuse, network egress exfiltration, prompt integrity failures, database access risks, and fleet configuration drift. We implement four-layer defense in depth: (1) kernel level workload isolation using gVisor on Kubernetes, (2) credential proxy sidecars preventing agent containers from accessing raw secrets, (3) network egress policies restricting each agent to allowlisted destinations, and (4) a prompt integrity framework with structured metadata envelopes and untrusted content labeling. We report results from 90 days of deployment including four HIGH severity findings discovered and remediated by an automated security audit agent, progressive fleet hardening across three VM image generations, and defense coverage mapped to all eleven attack patterns from recent literature. All configurations, audit tooling, and the prompt integrity framework are released as open source.
