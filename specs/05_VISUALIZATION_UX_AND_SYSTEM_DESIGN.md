> **Active architecture decision - 2026-11-07:** The MVP frontend is a dedicated React/TypeScript web application with Vite, Tailwind and shadcn/ui, backed by FastAPI and the existing Python services. Streamlit is the legacy prototype. Read [the web migration contract](09_WEB_FRONTEND_MIGRATION.md) and [the Stitch design reference](08_MVP_DESIGN_REFERENCE.md) before implementation. Where historical UI instructions below conflict, Requirement 43 and the migration contract take precedence.

# Module 5: Visualization Software Design, Frontend UX Standards & Phased Execution Plan

## 0. Active web implementation target

The React/TypeScript frontend implements the actual Stitch design with Vite,
Tailwind CSS, editable shadcn/ui components and Plotly.js. FastAPI is now an MVP
adapter to the existing Python service layer. See specs/08_MVP_DESIGN_REFERENCE.md
and specs/09_WEB_FRONTEND_MIGRATION.md. The framework evaluation and Streamlit
execution plan below describe the earlier prototype decision, now superseded.

The domain concepts, progressive disclosure, chart semantics and auditability
remain relevant. Browser layout, styling, state, component and screenshot tests
replace Streamlit widget, CSS workaround and fragment requirements. API inputs and
outputs use Pydantic/OpenAPI contracts; all numerical computation stays in Python.
The root npm run dev launcher will start both frontend and API after implementation.

## 1. Python Visualization Framework Evaluation & Decoupled Architecture

To ensure the thesis software is both rapid to build and architected to production standards, the codebase strictly decouples the **Pure Python Calculation & Data Layer (`src/core/`)** from the **Visualization & UI Layer (`src/ui/`)** via **Plotly Figure Factories (`src/ui/charts.py`)**.

### 2026 Python Dashboard Framework Trade-Off Matrix

| Framework | Execution & Reactivity Model | Strengths for Enterprise AI DSS | Trade-Offs & Mitigation | 
| ----- | ----- | ----- | ----- | 
| **Streamlit 1.52+ + Plotly** *(Recommended Primary)* | Script rerun with `@st.fragment` partial reruns, `@st.cache_data`, and native `st.login` OIDC. | Fastest implementation of sliders, file uploaders (`LiteLLM` CSV/JSON), `st.chat_message` DSS assistant, and interactive Plotly charts. | Full-script reruns lag on heavy apps $\rightarrow$ **Mitigation:** Wrap each simulator card in `@st.fragment` so slider changes only recalculate the affected chart in $<50\text{ ms}$. | 
| **Plotly Dash 2.18+** *(Analytical Cross-Filtering)* | Explicit DAG callback graph connecting `dcc.Graph` selection events to multiple outputs. | Selecting a point on the *Pareto Frontier* or *Inverse MoE Scatter Plot* natively cross-filters the *60-Month TCO Timeline* and *Scorecard Table*. | Higher boilerplate for chat interfaces than Streamlit. | 
| **Reflex 0.8+** *(Full-Stack React/Next.js Compiler)* | Compiles pure Python state and components into a React frontend + FastAPI/Next.js backend (Vite+Rolldown). | Full multi-page SaaS layout control and streaming AI chat without writing JavaScript. | Longer initial build step than Streamlit. | 
| **NiceGUI 2.x** *(FastAPI + Vue/Quasar + WebSockets)* | Persistent WebSocket server-push with Tailwind CSS layout bindings. | Instant sub-millisecond UI updates for live proxy log monitoring. | Smaller data-science template ecosystem than Streamlit/Dash. | 

## 2. Executive Decision Support UX Principles (Tufte, Few, IBCS & NN/g Standards)

Executive decision support dashboards fail when they present walls of unorganized engineering metrics. The frontend must enforce four visual design laws:

### 2.1 The 5-Second Rule & 3-Tier Progressive Disclosure Layout

Executives must grasp the optimal architectural verdict within **5 seconds** of opening the app:

* **Tier 1 — Top Executive KPI Ribbon (Always Visible, Max 5 Cards):**

  1. `Recommended Architecture` (e.g., *"4× RTX Pro 6000 Server (Romania MLOps Managed)"* or *"EU Vertex AI + 70% OpenCode Local Hybrid"*).

  2. `Break-Even Horizon (t*)` (e.g., *"3.4 Months vs. EU Vertex AI PAYG"* with green/amber badge).

  3. `Monthly EU Compliance & Nearshore Savings` (e.g., *"+€2,800/mo saved via Cluj-Napoca MLOps vs. Munich HQ"*).

  4. `Agentic UX Speed (Effective TPS & TTFT)` (e.g., *"69 TPS | 1.8s TTFT — Meets Interactive Target"*).

  5. `Cluster Utilization & Viability Badge` (e.g., *"78% Utilization (>70% Threshold Met)"* or *"32% Utilization — Rent API Instead"*).

* **Tier 2 — Primary Comparative Visual Canvas (Tabbed Workspace):**

  * Organizes the 6 core Plotly visualizations into clean, uncluttered tabs with synchronized sidebar scenario controls (`Workload & Agent Fleets`, `Hardware & Memory Offload`, `EU FinOps & Staffing`).

* **Tier 3 — Expandable Engineering Physics & Audit Drawer (`st.expander`):**

  * Houses granular formulas, `sudo sysctl iogpu.wired_limit_mb` copy-paste terminal commands, Unsloth token-agreement tables, multi-agent eviction benchmarks, and raw JSON/CSV export buttons.

### 2.2 Semantic, Colorblind-Safe Financial Palette (Okabe-Ito / IBCS Aligned)

Approximately 8% of male executives have red-green color vision deficiency. Never encode compliance or OOM status using color alone; always pair **Okabe-Ito high-contrast hues** with **line geometry** (solid vs. dashed/dotted) and **explicit text badges**:

* **Sovereign Per-Seat Workstation:** Electric Cyan `#06B6D4` (Solid Line, `3px`)

* **Sovereign Centralized Server / PD-Disagg:** Royal Blue `#3B82F6` (Solid Line, `4px`)

* **Heterogeneous Modality / Scavenged Rig:** Indigo `#6366F1` (Solid Line, `3px`)

* **Dedicated EU Cloud GPU (Hetzner/Scaleway):** Emerald Teal `#10B981` (Dash-Dot Line, `2.5px`)

* **Baseline C (EU-Pinned Vertex/Azure API +10%):** Amber Gold `#F59E0B` (Solid Line, `3px`)

* **Baseline B / D (Global API / OpenRouter Value):** Violet `#8B5CF6` (Dotted Line, `2px`)

* **Baseline A (Non-Compliant Consumer Sub \$200/mo):** Muted Rose `#F43F5E` (Dashed Reference Line `2px` + `[NON-COMPLIANT / BLOCKED]` annotation)

* **OOM / Thermal / Eviction Warning:** High-Contrast Crimson `#EF4444` with diagonal hatch pattern fill (`pattern_shape="/"` in Plotly).

## 3. The Six Interactive Plotly Views (`src/ui/charts.py`)

1. **View 1: Horizontal Model-to-GPU Capacity, Multi-Agent State & AA v5 Staircase Chart**

   * Horizontal stacked bar chart (`px.bar(orientation='h')`): \[Active Weights in VRAM\] + \[Single-User Active KV Cache (MLA <0.9GB vs. GQA 129GB)\] + \[Parked Multi-Agent Context State in System RAM\] + \[OS Reservation\].

   * Displays each model's **AA v5 Intelligence Score** (`20.1` $\rightarrow$ `27.8` $\rightarrow$ `32.5` $\rightarrow$ `46.0` vs. `58.4`) and **Unsloth Token-Agreement Rate** (`81.6%`–`98.5%`).

   * Vertical threshold lines mark hardware VRAM and System RAM boundaries (`16GB`, `32GB`, `64GB`, `128GB`, `256GB`, `512GB`, `1TB`, `2TB`), dynamically highlighting **Conversational Eviction Risk** when multi-agent fleets exceed host memory.

2. **View 2: 60-Month Multi-Baseline TCO Break-Even & Utilization Chart**

   * Plots cumulative 60-month spend across Sovereign On-Premise, Heterogeneous Scavenged Rigs, Dedicated EU GPU Rental (Hetzner/Scaleway), Baselines A/B/C/D, and the Hybrid Split.

   * Annotates exact intersection points ($t^*$) and shades the **"Utilization Danger Zone (<70% GPU Utilization)"** where cloud APIs beat underutilized servers.

3. **View 3: Prefill (TTFT) vs. Thinking vs. Decode Latency & Eviction Waterfall**

   * Deconstructs an agentic turn into:
     $$[\text{Prompt Prefill + Harness Scaffolding}] + [\text{Eviction Re-Prefill Overhead}] + [\text{Reasoning Chain Decode}] + [\text{Output Decode}]$$

   * Interactive toggles for `MCP Code Mode Pruning (-75% prompt)`, `128GB RAM (30 Evictions / 85m)` vs. `256GB ECC RAM (0 Evictions / 59m)`, `M3 Ultra (151/core)` vs. `M5 Max/Ultra (531/core)`, and `1M-Token Prompt Cliff` (1.9 min on 8× Pro 6000 vs. 42.7 min on M3 Ultra vs. 7.9 hrs on EPYC+3090).

4. **View 4: The "Inverse MoE Rental Paradox" & Price-to-Intelligence Pareto Frontier**

   * Dual-subplot view:

     * *Left (Pareto Frontier):* AA v5 Intelligence Score (Y-axis) vs. Monthly 3-Year Amortized TCO (X-axis), filtering out `Llama 4` under EU residency rules.

     * *Right (Inverse MoE Paradox):* Hardware Ownership CapEx governed by $P_{\text{total}}$ (X-axis) vs. Cloud API Rental Cost per Benchmark Task governed by $P_{\text{active}}$ (Y-axis), highlighting why `Qwen 27B` costs \$3.53/task to rent on $1,299 hardware while `DeepSeek V4.1` costs \$0.60/task on $9,499 hardware.

5. **View 5: Cross-Border EU FinOps & "Three Clocks" Hardware Scorecard**

   * Side-by-side comparison of **Munich HQ MLOps Staffing (€120k + 21% tax)** vs. **Romania EU Branch Staffing (€75k + 2.25% CAM)** alongside the **Three Clocks Table** (Software Clock EOL warnings for V100/MI50, NVIDIA NIM \$4,500/GPU tax, Model Clock bloat headroom, and Money Clock annualized cost).

6. **View 6: Agentic DSS Chatbot with Deterministic Tool-Calling**

   * Natural language interface bound to `src/agent/tools.py` (`run_hardware_sizing_tool`, `run_tco_projection_tool`, `compare_eu_staffing_hubs_tool`, `evaluate_multi_agent_eviction_tool`). The LLM never computes math internally; it invokes the Pydantic engines and renders inline Plotly charts.

## 4. Repository Structure & 4-Phase Execution Plan

```text
enterprise-ai-dss/
├── specs/                                  # Modular specification files
│   ├── 00_INDEX_AND_AGENT_ROUTER.md
│   ├── 01_WORKLOAD_AND_PHYSICS_ENGINE.md
│   ├── 02_TCO_FINOPS_AND_EU_COMPLIANCE.md
│   ├── 03_CALIBRATED_2026_SEED_DATA.md
│   ├── 04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md
│   └── 05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md
├── src/
│   ├── core/
│   │   ├── schemas.py                      # Phase 1: Pydantic v2 strict contracts
│   │   ├── seed_catalog.py                 # Phase 1: 2026 Hardware, Models, AA v5 & EU Salary seeds
│   │   ├── sizing_engine.py                # Phase 1: 4-Stage VRAM, MLA/GQA, Offload & Prefill math
│   │   ├── tco_engine.py                   # Phase 1: 4-Tier Cloud, Inverse MoE & Munich/Romania TCO
│   │   └── litellm_parser.py               # Phase 2: CSV/JSON LiteLLM & Bifrost proxy log profiler
│   ├── ui/
│   │   ├── theme.py                        # Phase 3: Okabe-Ito palette & IBCS styling constants
│   │   ├── charts.py                       # Phase 3: Pure Plotly Figure Factory functions (Views 1-5)
│   │   └── app.py                          # Phase 3: Streamlit (@st.fragment) 3-Tier Executive UI
│   └── agent/
│       └── tools.py                        # Phase 4: Deterministic LLM tool-calling bindings
├── tests/
│   └── test_engines.py                     # Phase 1: Pytest verification suite for all 2026 benchmarks
├── pyproject.toml
└── README.md
```

### Sequential Verification Milestones (`pytest`)

1. **Phase 1 (Core Math & Pytest Suite):** Implement `src/core/` and verify:

   * `DeepSeek V4.1` MLA (<0.9GB KV @ 1M context) vs. Standard GQA (129GB FP16 / 41GB INT4 @ 1M context) vs. `Qwen 3.8-27B` Hybrid KV (34GB total @ 250K context).

   * Multi-Agent System RAM Eviction math (128GB vs. 256GB RAM: 30 context evictions, 10/12 failure rate vs. 0 evictions, 12/12 pass with 26-minute speedup).

   * macOS default 75% split traps on 16GB (`Gemma 4` fallback), 128GB (`103GB` blocking `111GB Flash Next`), and 256GB (`206GB` blocking `233.5GB DeepSeek 3-bit`) vs. `sysctl` override.

   * MoE Dual-Parameter Law (`35B-A3B` @ 78.8 TPS vs. `27B` @ 14.7 TPS; `gpt-oss-120B` @ 46 TPS vs. `70B` @ 5 TPS) and 1M-token prefill cliff (`1.9m` on 8× Pro 6000 vs. `42.7m` on M3 Ultra).

   * Harness scaffolding spread (`Claude Code 33k` vs. `DSH 4.2k`), MCP Code Mode pruning (`-75%`), and Anthropic `1.30x` tokenizer inflation.

   * Inverse MoE Rental Paradox (\$3.53/task on 27B vs. $0.60/task on DeepSeek V4.1), 80.6-year Kimi K3.1 break-even wall, 70% GPU utilization threshold, and Munich (`+21%` social tax) vs. Romania (`+2.25%` CAM) MLOps personnel arbitrage.

2. **Phase 2 (Log Ingestion):** Build `litellm_parser.py` to parse real proxy exports into `WorkloadProfile`.

3. **Phase 3 (Executive UI):** Build `theme.py`, `charts.py`, and `app.py` following the 3-tier progressive disclosure layout.

4. **Phase 4 (Agentic DSS):** Connect `agent/tools.py` to the chat UI for natural-language scenario simulation.