# 🔄 Project Boucle: Self-Healing Scraper & Adaptive ETL Pipeline

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![Architecture](https://img.shields.io/badge/Architecture-SLM%20%2B%20RAG-green)
![Data Engine](https://img.shields.io/badge/Data%20Engine-Polars%20%7C%20DuckDB-orange)
![License](https://img.shields.io/badge/license-MIT-informational)

An enterprise-grade, resilient web scraping and ETL pipeline designed to automatically detect DOM/schema drift and auto-heal selectors using a local Small Language Model (SLM) grounded in official Selenium documentation.

---

## 🎯 The Problem & The Solution

- **The Problem:** Traditional Web Scrapers break whenever target websites update their DOM structure, class names, or layout—requiring manual maintenance and disrupting downstream data pipelines.
- **The Solution:** *Project Boucle* introduces a **Self-Healing Loop**. When a selector fails (`NoSuchElementException`), the pipeline captures the HTML context, queries a local vector store containing Selenium documentation (RAG), and uses a lightweight SLM (Qwen2.5-Coder / Phi-3 via Ollama) to generate a valid, compliant selector on the fly.

---

## 🏗️ Architecture

```mermaid
flowchart TD
    A[Selenium Web Scraper] -->|Attempts Extraction| B{Element Found?}
    B -->|Yes| C[Pydantic Schema Validation]
    B -->|No / DOM Drift| D[Self-Healing Handler]
    
    subgraph Self-Healing Loop
        D -->|1. Extract HTML Snippet| E[Local RAG Engine - ChromaDB]
        E -->|2. Query Selenium Docs Context| F[Local SLM - Ollama]
        F -->|3. Propose Valid Selector| A
    end

    C -->|Valid Data| G[Polars / DuckDB Transformation]
    G --> H[Automated Trend Reports & Analytics]
    
    subgraph Quality & Observability
        I[structlog - Audit Logs]
        J[Data Drift Metrics]
    end
