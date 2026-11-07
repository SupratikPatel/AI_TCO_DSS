<!-- ===================================================================== -->
<!-- SPLIT FILE: specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md                  -->
<!-- PURPOSE: Module 4 (4-Tier Cloud TCO, EU Sovereignty & Personnel OpEx) -->
<!-- ===================================================================== -->

# Module 4: 4-Tier Financial TCO, EU FinOps & Cross-Border Personnel Arbitrage Engine

Projects 60-month cumulative TCO curves ($m \in [1, 60]$) comparing Sovereign On-Premise / Nearshore-Managed Architectures against Four Cloud Baselines.

## 1. The Four Cloud Comparison Baselines

### Baseline A: Subsidized Prosumer Subscriptions ($100–$200/mo per seat)
- Models `Claude Max 20x ($200/mo)`, `Claude Max 5x ($100/mo)`, `ChatGPT Pro ($200/mo)`.
- **Hard Enterprise Compliance Gate:** Mark `baseline_a_eligible = False` if:
  1. `strict_eu_sovereignty == True` (Consumer plans lack EU regional data pinning and enterprise DPA guarantees).
  2. `require_third_party_harness == True` (Providers block 3rd-party harnesses from consumer OAuth tokens and enforce strict weekly rate caps).

### Baseline B: Global Metered Frontier API (Pay-As-You-Go)
$$\text{Monthly API Cost}_{\text{Global}} = N_{\text{users}} \times \text{Days} \times \left[ \left(\hat{T}_{\text{in}} \cdot (1 - r_{\text{cache}}) \cdot P_{\text{in}}\right) + \left(\hat{T}_{\text{in}} \cdot r_{\text{cache}} \cdot P_{\text{cache\_read}}\right) + \left(\hat{T}_{\text{out}} \cdot \mu_{\text{think}} \cdot P_{\text{out}}\right) \right] \times \kappa_{\text{mega}} \times \nu_{\text{verify}} \times (1 - 0.50 \cdot r_{\text{batch}})$$
- Where $\hat{T}_{\text{in}} = (T_{\text{in}} + S_{\text{effective}}) \times \tau_{\text{tokenizer}}$ and $\hat{T}_{\text{out}} = T_{\text{out}} \times \tau_{\text{tokenizer}}$.
- **Prompt Caching & Batch API Modifiers:**
  - *Prompt Cache Read ($P_{\text{cache\_read}}$):* Bills at **5% to 10%** of base input price (`5%` on `Claude Sonnet 5.5`, `10%` on `Opus 5.5`).
  - *Asynchronous Batch Discount ($r_{\text{batch}}$):* Deferrable overnight workloads routed via Batch APIs (Anthropic, OpenAI, Google, Mistral) receive a **50% price reduction**.
- *Empirical Spend Range:* Light office users cost **$16–$353/mo per 70–100 users**; standard `Claude Code` developers average **$13/active day ($150–$250/mo)**; heavy agentic developers running 80+ turn mega-sessions burn **$80/day ($2,400/mo) up to $12,000/mo**.

### Baseline C: EU-Sovereign Metered Enterprise API & Dedicated EU Cloud Rental
1. **EU-Pinned Frontier API (Vertex AI Frankfurt / Azure OpenAI Sweden/Germany):**
   $$\text{Monthly API Cost}_{\text{EU}} = \left(\text{Monthly API Cost}_{\text{Global}} \times 1.10 \text{ [EU Residency Surcharge]}\right) + \text{Enterprise Gateway/SLA Fee}$$
   - OpenAI EU Data Residency (models from March 2026+) and Claude on AWS Bedrock EU / Google Vertex AI EU carry an explicit **+10% regional processing premium** (Anthropic's direct API only offers global or US-only processing).
   - **The "Compliance Tax & Subsidy Multiplier" KPI:** Measures $\text{Monthly API Cost}_{\text{EU}} - \text{Baseline A}$. Organizations forced off $200 consumer plans onto un-subsidized EU Vertex AI for heavy coding agents break even on local hardware in **1 to 5 months** instead of 25+ months.
2. **Dedicated EU Sovereign GPU Rental (Hetzner / Scaleway Benchmark):**
   - Renting a dedicated open-weights GPU server in Europe costs **€1,197/mo on Hetzner** or **€2,093/mo on Scaleway**, vs. **~€505/mo amortized hardware CapEx** (over 36 months) for a purchased RTX Pro 6000 Blackwell before server chassis, electricity, and engineering FTE costs.
3. **The EU Multimodal License Guardrail (`Llama 4` Commercial Ban):**
   - Flag any model under the `Meta Llama 4 Multimodal License` as **Non-Compliant / Prohibited for EU Enterprises** (`eu_commercial_license_valid = False`), as Meta's license denies rights to companies with their principal place of business in the EU. Recommend **Apache 2.0** (`Qwen 3.5/3.8`, `gpt-oss-120b`, `Mistral Small 4`) or **MIT** (`DeepSeek V4/V4.1`) alternatives.

### Baseline D: Open-Weights Market Output Value & The Inverse MoE Rental Paradox
Prices the exact token volume a local machine physically generates during active working hours at serverless open-weights rates (OpenRouter / DeepSeek API):
$$\text{Monthly Produced Tokens} = H_{\text{active}} \times 3600 \times \text{TPS}_{\text{effective}} \times \text{Utilization Ratio}$$
$$\text{Market Value of Output (€/mo)} = \frac{\text{Monthly Produced Tokens}}{10^6} \times P_{\text{openrouter\_out}}$$

1. **The Inverse MoE Rental Paradox:**
   - **Hardware Ownership prices Total Storage ($P_{\text{total}}$)**, whereas **Cloud APIs price Active Compute Work ($P_{\text{active}}$)**:
     - Dense `Qwen 3.8-27B` ($P_{\text{active}} = 27\text{B}$) fits on a $1,299 Mac Mini, yet costs **$1.875–$2.91/1M output tokens** to rent (~**$3.53 per benchmark task**). A single-user $4,999 DGX Spark generating 11.6 TPS for 176 hrs/mo produces ~7.35M tokens/mo worth just **$13.78–$21.39/mo** on OpenRouter.
     - Sparse `GLM 5.3 Flash` ($320\text{B total} / 18\text{B active}$) requires a $3,450–$6,950 128GB machine to own, yet rents for **$0.092/1M tokens** (~20× cheaper than 27B).
     - Sparse `DeepSeek V4.1 Flash` ($552\text{B total} / 16\text{B active}$) requires a $9,499 256GB Mac Studio (costing **~$5.50/1M tokens** locally over 3 years), yet rents for **$0.60–$1.20/1M tokens** (~**$0.60 per benchmark task**—$6\times$ cheaper to rent than the 27B model).
2. **The 80.6-Year `Kimi K3.1 Pro` Single-Stream Break-Even Wall:**
   - `Kimi K3.1 Pro` (104B active) lists at **$10.00/1M output tokens**. Buying **8× DGX Sparks ($55,600)** requires generating **5.6 billion tokens** to break even. At the measured **2.2 TPS** single-stream speed, generating 5.6B tokens takes **~80.6 years**.
3. **The Cloud API Electricity Parity Point:**
   - Reading a 1M-token prompt on DeepSeek's API costs **$0.15** off-peak. Reading that same 1M prompt on a local 16× AMD MI50 rig (5 hours at 2.5 kW = 12.5 kWh) costs **~$2.27 in electricity alone** (at €0.172–€0.18/kWh)—making local electricity **$15\times$ more expensive than the cloud API call**.

---

## 2. Sovereign On-Premise TCO & Hidden Enterprise Costs

### 2.1 Turnkey CapEx & The Data Center Infrastructure Multiplier
$$\text{CapEx}_{\text{total}} = \left(N_{\text{nodes}} \times \text{Unit Street Price}\right) \times \mu_{\text{datacenter}} + \text{Cabling/Switch Kit}$$
- **Per-Seat / Desk Appliance ($\mu_{\text{datacenter}} = 1.0$):** Plugs into standard office power/networking.
- **Heterogeneous Scavenged Multi-GPU Appliance ($\mu_{\text{datacenter}} = 1.05$):** Standard high-wattage desktop PSU (1,000W–1,200W) with standard PCIe slots.
- **Enterprise 8-GPU Server Rack ($\mu_{\text{datacenter}} \in [1.3, 2.5]$):** Accounts for InfiniBand/RoCE switches ($2,000–$5,000/node), enterprise PDUs/UPS, precision liquid/air cooling infrastructure, colocation rack setup, and N+1 hardware redundancy.

### 2.2 Industrial vs. Office Electricity & Cooling PUE
$$\text{Energy OpEx}_{\text{monthly}} = N_{\text{units}} \times \left(\frac{H_{\text{active}} \cdot W_{\text{load}} + H_{\text{idle}} \cdot W_{\text{idle}}}{1000}\right) \times \text{PUE} \times \text{Electricity Rate (€/kWh)}$$
- **German Electricity Rate Tiers (2026 BDEW Benchmarks):**
  - *German SME Industrial Rate (`de-industrial-bdew`):* **€0.172 / kWh** (a 600W GPU under 24/7 full load costs ~€75/mo before PUE).
  - *German Commercial Office Rate (`de-office`):* **€0.280 / kWh**.
- **Cooling PUE Overhead:** Data center cooling accounts for **40%–54% of total facility power** (`PUE = 1.15 to 1.50`, adding $1,000–$2,000/kW/year). Also enforce a **Thermal Throttling Warning**: GPUs operating above $85^\circ\text{C}$ suffer a **30% throughput drop** and accelerated silicon failure.

### 2.3 The 70% GPU Utilization Viability Threshold
- Empirical enterprise case studies demonstrate that self-hosting centralized GPU clusters only achieves net cost savings over Cloud APIs when **sustained GPU utilization exceeds 70%** (typically requiring predictable batch pipelines or $\ge 8,000$ conversations/day, or monthly API bills $> \$50,000/\text{mo}$).
- If calculated cluster utilization falls below `0.55` (45%+ idle time), display an **Idle Capacity Financial Warning** noting that fixed amortization, idle wattage, and MLOps FTE costs will likely exceed PAYG API bills.

### 2.4 The Financial Cost of Conversational Eviction
When sizing workstations or servers for multi-agent teams, under-provisioning system RAM triggers the Conversational Eviction Tax:
$$\text{Monthly Eviction Loss (€)} = N_{\text{evictions/mo}} \times \left(\frac{\text{Rebuild Tokens}}{10^6} \times P_{\text{compute\_equivalent}} + \frac{\text{Wait Hours} \times \text{Dev Hourly Rate}}{N_{\text{agents}}}\right)$$
- An enterprise team of 12 developers on 128GB workstations losing 26 minutes per task over 30 monthly project iterations loses **€845/month per developer** in wasted salary time—paying for the 256GB ECC RAM upgrade in **under two months**.

### 2.5 Intra-EU Engineering Salary Arbitrage (Munich HQ vs. Romania EU Branch)
Self-hosted inference servers require ongoing MLOps/Platform engineering (installing/updating `vLLM`, patching OS/drivers, monitoring Prometheus/Grafana metrics, managing LiteLLM/Bifrost access keys, and evaluating new open-weights releases). Cloud API prices include this operations labor; on-premise TCO must price it explicitly:

$$\text{Personnel OpEx}_{\text{monthly}} = \frac{\text{FTE Allocation} \times \text{Annual Gross Salary (€)} \times \left(1 + \tau_{\text{employer\_social\_tax}}\right)}{12}$$

- **The Intra-EU Nearshoring Sovereignty Rule:**
  Because **Romania**, **Poland**, and **Portugal** are full EU/EEA member states, an enterprise headquartered in **Munich, Germany** can assign MLOps engineers in its **Bucharest or Cluj-Napoca branch** to remotely administer Munich/Frankfurt GPU clusters **100% within EU jurisdiction** (zero GDPR Chapter V third-country transfer, full EU sovereignty compliance).
- **2026 Calibrated Regional MLOps Compensation & Employer Tax Multipliers:**
  1. **Munich, Germany (`de-munich-hq`):**
     - *Base Salary (2026):* Mid-Level MLOps: **€94,000–€107,000**; Senior MLOps/AI Infrastructure: **€115,000–€131,000**; Principal/Lead: **€150,000–€165,000**.
     - *German Employer Social Tax (`Lohnnebenkosten / Arbeitgeberbrutto`):* $\tau_{\text{employer}} = \mathbf{0.21}$ (+21% employer pension, health, unemployment, nursing care, and statutory accident insurance).
     - *True Employer Cost (1.0 FTE Senior Munich):* $€120,000 \times 1.21 = \mathbf{€145,200/\text{yr}}$ (**€12,100/month**; or **€6,050/month** at 0.5 FTE). Additionally, Germany averages a **7.7-month recruitment delay** for AI/MLOps roles.
  2. **Berlin / Hamburg, Germany (`de-berlin-hamburg`):**
     - *Base Salary (2026):* Mid-Level: **€82,000–€93,000**; Senior: **€98,000–€110,000**; $\tau_{\text{employer}} = \mathbf{0.21}$.
     - *True Employer Cost (1.0 FTE Senior Berlin):* $€100,000 \times 1.21 = \mathbf{€121,000/\text{yr}}$ (**€10,083/month**).
  3. **Romania EU Branch — Cluj-Napoca / Bucharest (`ro-cluj-bucharest`):**
     - *Base Salary (2026):* Mid-Level DevOps/MLOps: **€52,000–€65,000**; Senior DevOps/MLOps: **€69,600–€85,000** (€5,800–€7,100/mo gross).
     - *Romanian Employer Social Tax (`CAM — Contribuția asiguratorie pentru muncă`):* $\tau_{\text{employer}} = \mathbf{0.0225}$ (**+2.25%** statutory employer tax, or ~**4%** including private clinic/meal benefits, as CAS/CASS are deducted from employee gross).
     - *True Employer Cost (1.0 FTE Senior Romania):* $€75,000 \times 1.04 = \mathbf{€78,000/\text{yr}}$ (**€6,500/month**; or **€3,250/month** at 0.5 FTE—a **46.3% personnel OpEx reduction** vs. Munich with zero EU compliance compromise).
  4. **Poland / Portugal EU Hubs (`pl-warsaw-krakow`):**
     - *True Employer Cost (1.0 FTE Senior):* **~€85,000–€96,000/yr** (**€7,100–€8,000/month**).

### 2.6 Enterprise Software Licensing Tax (`NVIDIA NIM` vs. Open-Source `vLLM`)
- Running open-source `vLLM`, `SGLang`, or `llama.cpp` costs **€0/year** in software licensing.
- If an enterprise mandates vendor-supported **NVIDIA AI Enterprise / NIM containers** on workstation/server GPUs (e.g., 4× RTX Pro 6000), add **$4,500 (€4,150) per GPU per year** ($18,000/yr for a 4-GPU node).

### 2.7 Sovereign On-Premise 60-Month TCO Integration Formula
$$\text{TCO}_{\text{OnPrem}}(m) = \text{CapEx}_{\text{total}} - \text{ResaleValue}(m) + \sum_{i=1}^{m} \left(\text{Energy OpEx}_i + \text{Personnel OpEx}_i + \text{NIM Licensing}_i + \text{Opportunity Cost}_i + \text{WaitPenalty}_i + \text{EvictionLoss}_i\right)$$
- **Capital Opportunity Cost:** Evaluates $\text{CapEx} \times \frac{r_{\text{capital}}}{12}$ reflecting conservative treasury yields (4.5% risk-free rate).
- **Developer Wait-Time Penalty:**
  $$\text{WaitPenalty}_{\text{monthly}} = (H_{\text{local wait}} - H_{\text{cloud wait}}) \times \text{Developer Hourly Opportunity Cost}$$
- **Hybrid Routing Simulator ("Local Deferrable + Frontier Decidable"):**
  Provides a slider `local_offload_ratio` ($0\% \rightarrow 100\%$) routing high-volume deferrable turns to local hardware while escalating hard architectural tasks to EU Frontier APIs.