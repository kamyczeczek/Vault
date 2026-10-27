---
type: Concept
id: 00_pdf_inspector_fast_local_parsing
title: "Stop Paying For PDF Parsing: PDF Inspector and Fast Local Extraction"
tags: [agentic, pdf-parsing, rust, performance, document-ingestion]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Stop Paying For PDF Parsing: PDF Inspector and Fast Local Extraction

## Overview
PDF Inspector is an open-source, Rust-based tool from Firecracker designed to process PDFs locally without waiting on OCR. It classifies and extracts native text, tables, code blocks, and structured markdown at high speed (e.g., 200 PDFs in under 3 seconds; 24 pages in 185 milliseconds).

## Core Architecture & Mechanisms
1. **Document Parsing:** Reads document bytes and converts them into a navigational object graph / content stream.
2. **Smart Sampling Classification:**
   - Instead of reading text on every page, it inspects only **8 pages** (first, last, and six evenly spaced pages through the middle).
   - Looks at signals (image coverage ratio, font decodability, vector shapes) without reading text (since PDFs are printing instructions).
   - Classifies document into types: *Text-based* (skips heavy page-by-page extraction), *Scanned/Image-based*, or *Mixed* (triggers full page traversal).
3. **Glyph Decoding & Extraction:** Decodes vector glyph representations into characters while recording spatial bounding coordinates.
4. **Layout & Table Reconstruction:** Reconstructs reading order, columns, lines, and tables from the raw content stream, converting everything into clean, structured markdown for LLMs without relying on AI models.

## Ecosystem & Companion Tools
- **AnyDoc:** Companion Rust-powered open-source tool for turning non-PDF documents (Excel, Word, RTFs) into clean markdown.
- **Hybrid Endpoints:** For pages requiring OCR or scanned inputs, fallback vision models convert images to text where applicable.
