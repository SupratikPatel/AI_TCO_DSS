> **Active architecture decision - 2026-11-07:** The MVP frontend is a dedicated React/TypeScript web application with Vite, Tailwind and shadcn/ui, backed by FastAPI and the existing Python services. Streamlit is the legacy prototype. Read [the web migration contract](09_WEB_FRONTEND_MIGRATION.md) and [the Stitch design reference](08_MVP_DESIGN_REFERENCE.md) before implementation. Where historical UI instructions below conflict, Requirement 43 and the migration contract take precedence.

<!-- ===================================================================== -->
<!-- SPLIT FILE: specs/00_INDEX_AND_AGENT_ROUTER.md                        -->
<!-- PURPOSE: Master Executive Summary & Context Router for AI Agents      -->
<!-- ===================================================================== -->

# Project Specification: Enterprise AI Infrastructure Decision Support System (TCO for Sovereign AI)

## 1. Executive Summary & Core Objective
Build a modular, production-grade **Enterprise AI Infrastructure Decision Support System (DSS)** in Python (Python 3.12/Pydantic/FastAPI backend; React/TypeScript/Vite/Tailwind/shadcn/ui frontend; Plotly.js charts). The system translates corporate financial health, real LiteLLM/Bifrost proxy traffic logs, and European regulatory data sovereignty mandates into deterministic physical inference metrics, hardware procurement architectures, and 60-month Total Cost of Ownership (TCO) projections.

### The Eight Evaluated Deployment Archetypes
1. **Sovereign On-Premise Per-Seat Workstations:** Dedicated local hardware per developer (Apple Mac Mini M6/M5 Pro, Mac Studio M5 Max/Ultra, secondary-market M3 Ultra, NVIDIA DGX Spark GB10, RTX 5060 Ti / RTX 5090 desktop towers, AMD Strix/Gorgon Halo).
2. **Sovereign Centralized Multi-GPU / Multi-Node Clusters:** Shared internal inference servers running continuous batching (`vLLM`, `SGLang`, `vLLM-MLX`) across 1, 2, 4, or 8 GPUs/nodes (4×–8× RTX Pro 6000 Blackwell, 8× H100/H200 SXM, 4× DGX Sparks via ring cable, clustered Mac Studios via Thunderbolt 5 RDMA mesh).
3. **Disaggregated Prefill-Decode Clusters (PD-Disagg):** Asymmetric compute topologies separating compute-bound prompt ingestion from bandwidth-bound token generation over 200 Gbps RoCE (e.g., 2× DGX Sparks for prompt prefill + 1× RTX Pro 6000 Blackwell for 1.8 TB/s token decode).
4. **Hybrid Tiered-Memory Appliances & 3-Tier Offloading:** Systems running 3-tier offload engines (`Strata`, `Engram`, `Project Maya`) partitioning weights across GPU VRAM ("Desk"), DDR4/DDR5 System RAM ("Shelf"), and NVMe SSDs ("Basement") (e.g., Olares One compact appliances, Dual-EPYC 512GB DDR4 server arbitrage rigs, RTX 5070 + 64GB DDR5 desktops).
5. **Heterogeneous Modality & Semantic Routing Appliances:** Multi-tiered asymmetric local servers separating heavy authority reasoning from fast worker agents, routing vision encoders to integrated CPU graphics (iGPU via OpenVINO) and real-time security screening / audio processing to dedicated NPUs (e.g., RTX 3090 primary + RTX 3060 worker + RTX 2000 Ada router + Intel Core Ultra iGPU/NPU).
6. **Wireless eGPU Appliances (`WiCi One` / Virtual Network GPUs):** Standalone Wi-Fi 7 network appliances (Intel Core Ultra 7 + NVMe SSD + RTX 5060 Ti / RTX 5090) utilizing `InferSSD` expert offloading to share local GPU compute over LAN.
7. **EU-Sovereign Metered Enterprise Cloud APIs & Dedicated EU GPU Rentals:** Pay-As-You-Go (PAYG) frontier endpoints pinned to EU jurisdictions via LiteLLM/Bifrost (Vertex AI EU, Azure OpenAI EU with +10% residency surcharges) and dedicated European bare-metal GPU servers (Hetzner, Scaleway).
8. **Global Cloud APIs & Subsidized Prosumer Subscriptions:** Unpinned global PAYG endpoints (OpenRouter, DeepSeek/Moonshot APIs, neoclouds) and flat-rate prosumer tiers ($100–$200/mo Claude Max, ChatGPT Pro), modeling compliance boundaries, rate caps, and third-party harness bans.

---

## Active document authority

Read progress.md first, then CLAUDE.md, Requirement 43, specs/09_WEB_FRONTEND_MIGRATION.md,
specs/08_MVP_DESIGN_REFERENCE.md and the revised Tasks 8-13 under .kiro/specs/ai-tco-dss-mvp/.
The numbered domain documents retain the mathematical background; historical
Streamlit paths and framework recommendations do not define the target frontend.
Tasks 1-7 remain completed history; the previous Task 8 backend work is reusable.

## 2. AI Coding Agent Context Router (Read Only What You Need)

To prevent context-window bloat and token drift during implementation, this specification is partitioned into **five domain-isolated modules**. Coding agents must **only load the files required for their active task**:

| Active Development Task / Phase | Required Specification Files to Load | Files to Ignore |
|---|---|---|
| **Task A: Schema & Contract Implementation** (`src/core/schemas.py`) | `00_INDEX_AND_AGENT_ROUTER.md` + `04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` | `01`, `02`, `03`, `05` |
| **Task B: Seed Catalog & Benchmark Database** (`src/core/seed_catalog.py`) | `03_CALIBRATED_2026_SEED_DATA.md` + `04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` | `01`, `02`, `05` |
| **Task C: Physical VRAM, Bandwidth & Prefill Engine** (`src/core/sizing_engine.py`) | `01_WORKLOAD_AND_PHYSICS_ENGINE.md` + `04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` | `02`, `03`, `05` |
| **Task D: Financial TCO, EU FinOps & Break-Even Engine** (`src/core/tco_engine.py`) | `02_TCO_FINOPS_AND_EU_COMPLIANCE.md` + `04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` | `01`, `03`, `05` |
| **Task E: LiteLLM / Bifrost Log Parser** (`src/core/litellm_parser.py`) | `01_WORKLOAD_AND_PHYSICS_ENGINE.md` (Section 1) + `04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` | `02`, `03`, `05` |
| **Task F: Frontend Dashboard, Plotly Views & Agentic Chat** (`src/ui/` & `src/agent/`) | `05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md` + `04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` | `01`, `02`, `03` |

---

## 3. High-Level System Architecture & Component Mapping

```text
enterprise-ai-dss/
├── specs/                                  # Domain-isolated specifications
│   ├── 00_INDEX_AND_AGENT_ROUTER.md
│   ├── 01_WORKLOAD_AND_PHYSICS_ENGINE.md
│   ├── 02_TCO_FINOPS_AND_EU_COMPLIANCE.md
│   ├── 03_CALIBRATED_2026_SEED_DATA.md
│   ├── 04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md
│   └── 05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md
├── src/
│   ├── core/                               # Deterministic Math & Data Layer (Zero UI)
│   │   ├── schemas.py                      # Pydantic v2 core contracts
│   │   ├── seed_catalog.py                 # 2026 Hardware, Models, AA v5 & EU Salary seeds
│   │   ├── sizing_engine.py                # 4-Stage VRAM, MLA/GQA, Offload & Prefill math
│   │   ├── tco_engine.py                   # 4-Tier Cloud, Inverse MoE & Cross-Border TCO
│   │   └── litellm_parser.py               # CSV/JSON LiteLLM & Bifrost proxy log profiler
│   ├── ui/                                 # Decoupled Visualization Layer
│   │   ├── theme.py                        # Okabe-Ito palette & IBCS constants
│   │   ├── charts.py                       # Pure Plotly Figure Factories (Views 1–5)
│   │   └── app.py                          # Streamlit (@st.fragment) 3-Tier UI
│   └── agent/                              # Natural Language Tool-Calling DSS Interface
│       └── tools.py                        # Strict deterministic wrapper around core engine
├── tests/
│   └── test_engines.py                     # Comprehensive Pytest empirical benchmark suite
├── pyproject.toml
└── README.md
```
## Extension Seams (post-MVP)

| Feature | Existing interface | Package directory | Existing modules requiring changes |
|---|---|---|---|
| FastAPI adapter (implemented in MVP) | size, project_tco, recommend, evaluate_scenario | src/ai_tco_dss/api/ | none; adapter already calls services |
| MCP adapter | size, project_tco, recommend, evaluate_scenario | src/ai_tco_dss/mcp/ | none |
| Benchmark scraper | BenchmarkRecord | src/ai_tco_dss/ingestion/ | none; writes validated catalog JSON |
| Workload importer | WorkloadProfile | src/ai_tco_dss/ingestion/ | none; produces the existing load_workload file format |
| Database repository | CatalogRepository | src/ai_tco_dss/catalog/ | none; inject repo into services |
| Catalog entry form | BenchmarkRecord, CatalogRepository | src/ai_tco_dss/api/ | api/app.py; add validated write endpoints; React form in frontend/ |
| Views 3–5 | size, project_tco, evaluate_scenario | src/ai_tco_dss/api/ | api/app.py only if extra transport needed; charts in frontend/ |
| Agentic chatbot | size, project_tco, recommend, evaluate_scenario | src/ai_tco_dss/agent/ | none; tool wrappers keep arithmetic in Python |
