# Catalog item files

Each hardware item is one file `data/catalog/hardware/<id>.json`, and each model item is one file `data/catalog/models/<id>.json`. The file name must equal the item's `id`. Files with another extension are ignored. A new valid file appears on the next catalog load (new repository instance or Dashboard restart) without code changes. Check every change with `uv run ai-tco-validate`.

**Provenance.** Every number needs a Provenance_Record. Wrap it as `{"value": …, "source_id": …, "tier": …, "accessed": "YYYY-MM-DD"}` (a *Sourced* value). Money also needs `"currency": "EUR"` or `"USD"`; the repository converts EUR to USD with `data/reference/fx.json`. `source_id` must exist in `data/sources.json`, `tier` must equal that source's tier, and values from YT-01 to YT-22 need `"note": "single-source"`.

## Hardware item

```json
{
  "id": "mac-studio-m5-max-128gb",
  "name": "Mac Studio (M5 Max 128GB)",
  "vendor": "Apple",
  "deployment_mode": "per-seat-workstation",
  "memory_architecture": "apple-unified",
  "interconnect": "Thunderbolt-5-RDMA",
  "supported_native_precisions": ["FP16", "BF16", "INT8", "INT4", "INT3"],
  "valid_node_counts": {"value": [1], "source_id": "ASSUMPTION-MVP", "tier": "assumption", "accessed": "2026-11-07"},
  "gpus_per_unit": {"value": 1, "source_id": "ASSUMPTION-MVP", "tier": "assumption", "accessed": "2026-11-07"},
  "advertised_memory_gb": {"value": 128, "source_id": "SPEC-03", "tier": "assumption", "accessed": "2026-11-07"},
  "os_reserved_memory_ratio": {"value": 0.195, "source_id": "YT-02", "tier": "community", "accessed": "2026-11-07", "note": "single-source"},
  "tuned_max_usable_memory_gb": {"value": 115, "source_id": "YT-02", "tier": "community", "accessed": "2026-11-07", "note": "single-source"},
  "memory_bandwidth_gbs": {"value": 546, "source_id": "SPEC-03", "tier": "assumption", "accessed": "2026-11-07"},
  "base_prefill_tps_at_32k": {"value": 1650, "source_id": "YT-21", "tier": "community", "accessed": "2026-11-07", "note": "single-source"},
  "idle_watts": {"value": 10, "source_id": "SPEC-03", "tier": "assumption", "accessed": "2026-11-07"},
  "load_watts": {"value": 140, "source_id": "SPEC-03", "tier": "assumption", "accessed": "2026-11-07"},
  "street_price": {"value": 5099, "currency": "EUR", "source_id": "SPEC-03", "tier": "assumption", "accessed": "2026-11-07"},
  "datacenter_multiplier": {"value": 1.0, "source_id": "SPEC-02", "tier": "assumption", "accessed": "2026-11-07"},
  "cabling_kits": [],
  "lifecycle_clocks": {
    "software_support_years": {"value": 5.0, "source_id": "SPEC-03", "tier": "assumption", "accessed": "2026-11-07"},
    "resale_value_retention_3yr": {"value": 0.60, "source_id": "YT-22", "tier": "community", "accessed": "2026-11-07", "note": "single-source"},
    "cuda_or_rocm_status": "active-flagship"
  }
}
```

| Field | Required | Unit | Meaning |
|---|---|---|---|
| `id` | required | — | Unique item id; equals the file name without `.json` |
| `name` | required | — | Display name |
| `vendor` | required | — | Manufacturer |
| `deployment_mode` | required | — | One of `per-seat-workstation`, `centralized-server`, `disaggregated-pd`, `tiered-offload-appliance`, `heterogeneous-routed`, `wireless-egpu-appliance`, `cloud-rental` |
| `memory_architecture` | required | — | `apple-unified`, `amd-unified` or `discrete`; selects the usable-memory rule |
| `interconnect` | required | — | Node interconnect, e.g. `NVLink`, `PCIe-Gen5`, `Thunderbolt-5-RDMA`, `Unified-Single`; sets α_scaling |
| `supported_native_precisions` | required | — | List of precisions the hardware runs natively (`FP16`, `BF16`, `FP8`, `INT8`, `INT4`, `INT3`, `INT2`) |
| `valid_node_counts` | required | nodes | Sourced list of allowed node counts, subset of {1, 2, 4, 8} |
| `gpus_per_unit` | required | GPUs | Sourced GPU count per unit (NVIDIA NIM licences are per GPU) |
| `advertised_memory_gb` | required | GB | Sourced advertised memory per node (VRAM or unified memory) |
| `os_reserved_memory_ratio` | optional | fraction | Sourced share of unified memory the OS keeps, in [0, 1); unified memory only |
| `tuned_max_usable_memory_gb` | optional | GB | Sourced usable memory after the macOS wired-memory override |
| `linux_max_usable_memory_gb` | optional | GB | Sourced usable memory under the Linux AMD override |
| `system_ram_offload_gb` | optional | GB | Sourced system RAM usable as weight offload (tiered-offload appliances) |
| `system_ram_total_installed_gb` | optional | GB | Sourced installed host system RAM per node |
| `memory_bandwidth_gbs` | required | GB/s | Sourced memory bandwidth per node |
| `base_prefill_tps_at_32k` | optional | tokens/s | Sourced prefill speed at 32K context |
| `prefill_tps_at_1m` | optional | tokens/s | Sourced prefill speed at 1M context |
| `idle_watts` | required | W | Sourced idle power per unit |
| `load_watts` | required | W | Sourced load power per unit |
| `street_price` | required | EUR or USD | Money: purchase price per unit |
| `msrp` | optional | EUR or USD | Money: list price per unit |
| `datacenter_multiplier` | required | factor | Sourced CapEx multiplier for racks, cooling and installation, in [1.0, 2.5] |
| `cabling_kits` | optional | — | List of `{"nodes": n, "price": Money}` interconnect kits per node count |
| `lifecycle_clocks` | required | — | Object: `software_support_years` (Sourced, years), `resale_value_retention_3yr` (Sourced, fraction in [0, 1]), `cuda_or_rocm_status` (`active-flagship`, `supported`, `deprecated-legacy`), optional `requires_nvidia_nim_license` and `warning_notes` |

## Model item

```json
{
  "id": "qwen-3-8-27b",
  "name": "Qwen 3.8-27B",
  "family": "Qwen",
  "type": "open-weights",
  "license_type": "Apache-2.0",
  "architecture": "dense",
  "attention_mechanism": "hybrid-sparse",
  "total_parameters_billions": {"value": 27, "source_id": "SPEC-03", "tier": "assumption", "accessed": "2026-11-07"},
  "active_parameters_billions": {"value": 27, "source_id": "SPEC-03", "tier": "assumption", "accessed": "2026-11-07"},
  "calibrated_weights_gb": [
    {"precision": "INT4", "value": {"value": 16.7, "source_id": "SPEC-03", "tier": "assumption", "accessed": "2026-11-07"}}
  ],
  "token_agreement_rates": [],
  "num_layers": {"value": 64, "source_id": "SPEC-03", "tier": "assumption", "accessed": "2026-11-07"},
  "active_kv_layer_ratio": {"value": 0.25, "source_id": "YT-16", "tier": "community", "accessed": "2026-11-07", "note": "single-source"},
  "num_kv_heads": {"value": 4, "source_id": "ASSUMPTION-MVP", "tier": "assumption", "accessed": "2026-11-07"},
  "head_dim": {"value": 256, "source_id": "ASSUMPTION-MVP", "tier": "assumption", "accessed": "2026-11-07"},
  "max_context_length": {"value": 262144, "source_id": "SPEC-03", "tier": "assumption", "accessed": "2026-11-07"},
  "open_weights_output_price_per_1m": {"value": 1.875, "currency": "USD", "source_id": "SPEC-03", "tier": "assumption", "accessed": "2026-11-07"}
}
```

| Field | Required | Unit | Meaning |
|---|---|---|---|
| `id` | required | — | Unique item id; equals the file name without `.json` |
| `name` | required | — | Display name |
| `family` | required | — | Model family; `Claude` applies the 1.30 tokenizer inflation |
| `type` | required | — | `open-weights` or `commercial-api` |
| `license_type` | optional | — | `Apache-2.0` (default), `MIT`, `Llama-4-EU-Ban`, `Proprietary-API` |
| `architecture` | required | — | `dense` or `moe` |
| `attention_mechanism` | optional | — | `standard-mha-gqa` (default), `multi-head-latent`, `hybrid-sparse` |
| `total_parameters_billions` | optional | billion parameters | Sourced total parameter count |
| `active_parameters_billions` | optional | billion parameters | Sourced parameters read per token (equals total for dense models) |
| `calibrated_weights_gb` | optional | GB | List of `{"precision", "value"}` with measured weight footprints per precision |
| `token_agreement_rates` | optional | fraction | List of `{"precision", "value"}` with token agreement against full precision |
| `num_layers` | optional | layers | Sourced transformer layer count (needed for the KV formula) |
| `active_kv_layer_ratio` | optional | fraction | Sourced share of layers with a growing KV cache (1.0 if absent) |
| `num_kv_heads` | optional | heads | Sourced KV head count (needed for the KV formula) |
| `head_dim` | optional | dimensions | Sourced head dimension (needed for the KV formula) |
| `max_context_length` | required | tokens | Sourced maximum context length |
| `supports_builtin_mtp` | optional | — | `true` if the model has built-in multi-token prediction |
| `open_weights_output_price_per_1m` | optional | USD per 1M tokens | Money: hosted output price of the open model (Baseline D) |
| `api_prices` | optional | USD per 1M tokens | Commercial APIs only (then required): `input_per_1m`, `output_per_1m`, `cache_read_per_1m`, each Money |
| `eu_pinned_endpoint` | optional | — | Commercial APIs only: Sourced `true`/`false`, whether an EU-pinned endpoint exists |
| `api_decode_tps` | optional | tokens/s | Sourced decode speed of the API |
| `api_ttft_s` | optional | s | Sourced time to first token of the API |

Quality scores (AA v5, Terminal-Bench, SWE-bench) are not model fields. They are Benchmark_Records in `data/benchmarks/quality.json`.
