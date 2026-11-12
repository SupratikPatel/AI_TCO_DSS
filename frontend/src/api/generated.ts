// Generated from FastAPI OpenAPI. Run npm run types:generate.
export interface paths {
    "/api/v1/audit": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Audit */
        post: operations["audit_api_v1_audit_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/catalog": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Catalog */
        get: operations["catalog_api_v1_catalog_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/evaluate": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Evaluate */
        post: operations["evaluate_api_v1_evaluate_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/export/csv": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Export Csv */
        post: operations["export_csv_api_v1_export_csv_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/export/json": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Export Json */
        post: operations["export_json_api_v1_export_json_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/health": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Health */
        get: operations["health_api_v1_health_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/options": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Options */
        get: operations["options_api_v1_options_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/recommend": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Recommend */
        post: operations["recommend_api_v1_recommend_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenario/default": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Default Scenario
         * @description Centralize existing domain defaults rather than copying them into TypeScript.
         */
        get: operations["default_scenario_api_v1_scenario_default_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/scenario/validate": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Validate Scenario */
        post: operations["validate_scenario_api_v1_scenario_validate_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/size": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Size */
        post: operations["size_api_v1_size_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/tco": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Tco */
        post: operations["tco_api_v1_tco_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/workloads/default": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Default Workload */
        get: operations["default_workload_api_v1_workloads_default_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        /** AccountingRow */
        AccountingRow: {
            /** Key */
            key: string;
            /** Label */
            label: string;
            /** Note */
            note: string;
            /**
             * Sources
             * @default []
             */
            sources: components["schemas"]["AuditSource"][];
            trace: components["schemas"]["FormulaTrace"];
            /** Value */
            value: number;
        };
        /** ApiError */
        ApiError: {
            /** Code */
            code: string;
            /**
             * Fields
             * @default []
             */
            fields: string[];
            /** Message */
            message: string;
        };
        /** AuditFormula */
        AuditFormula: {
            /**
             * Input Units
             * @default
             */
            input_units: string;
            /** Section */
            section: string;
            trace: components["schemas"]["FormulaTrace"];
        };
        /** AuditProvenance */
        AuditProvenance: {
            /**
             * Accessed
             * Format: date
             */
            accessed: string;
            /** Path */
            path: string;
            tier: components["schemas"]["SourceTier"];
            /** Unit */
            unit?: string | null;
            /** Value */
            value?: string | null;
        };
        /** AuditRequest */
        AuditRequest: {
            /** Candidate Id */
            candidate_id: string;
            result: components["schemas"]["ScenarioResult-Input"];
        };
        /** AuditResult */
        AuditResult: {
            /** Candidate Id */
            candidate_id: string;
            /** Formulas */
            formulas: components["schemas"]["AuditFormula"][];
            fx: components["schemas"]["FxInfo"];
            /** Performance */
            performance: {
                [key: string]: components["schemas"]["Metric"] | null;
            };
            /** Sources */
            sources: components["schemas"]["AuditSource"][];
        };
        /** AuditSource */
        AuditSource: {
            /** Provenance */
            provenance: components["schemas"]["AuditProvenance"][];
            /** Publisher */
            publisher: string;
            /** Reference */
            reference?: string | null;
            /** Source Id */
            source_id: string;
            tier: components["schemas"]["SourceTier"];
            /** Title */
            title: string;
            /** Url */
            url?: string | null;
        };
        /** BaselineResult */
        BaselineResult: {
            a_monthly: components["schemas"]["Metric"];
            b_monthly: components["schemas"]["Metric"];
            /** Baseline A Eligible */
            baseline_a_eligible: boolean;
            /** Baseline A Ineligibility Reasons */
            baseline_a_ineligibility_reasons: string[];
            c_monthly: components["schemas"]["Metric"];
            /** Compliance Tax Delta Monthly */
            compliance_tax_delta_monthly: number;
            /**
             * Currency
             * @default USD
             * @constant
             */
            currency: "USD";
            /** Reference Model Id */
            reference_model_id: string;
        };
        /** BenchmarkConditions */
        BenchmarkConditions: {
            /** Accelerator Memory Gb */
            accelerator_memory_gb?: number | null;
            /** Cache State */
            cache_state?: string | null;
            /** Concurrency */
            concurrency?: number | null;
            kv_precision?: components["schemas"]["PrecisionFormat"] | null;
            /** Model Revision */
            model_revision?: string | null;
            /** Nodes */
            nodes?: number | null;
            /** Optimized Backend */
            optimized_backend?: boolean | null;
            /** Output Tokens */
            output_tokens?: number | null;
            /** Prompt Cache Hit Rate */
            prompt_cache_hit_rate?: number | null;
            /** Protocol */
            protocol?: string | null;
            /** Quantization */
            quantization?: string | null;
            /** Residency */
            residency?: ("resident" | "offload") | null;
            /** Runtime */
            runtime?: string | null;
            /** Runtime Version */
            runtime_version?: string | null;
            /** Speculative Config */
            speculative_config?: string | null;
            speculative_mode?: components["schemas"]["SpeculativeMode"] | null;
            /** System Ram Gb */
            system_ram_gb?: number | null;
        };
        /**
         * BenchmarkMetric
         * @enum {string}
         */
        BenchmarkMetric: "decode_tps" | "prefill_tps" | "aggregate_tps" | "ttft_s" | "aa_index_v5" | "terminal_bench" | "swe_bench";
        /** CandidateEvaluation */
        "CandidateEvaluation-Input": {
            /**
             * Api Has Eu Endpoint
             * @default false
             */
            api_has_eu_endpoint: boolean;
            /** Api Model Id */
            api_model_id: string | null;
            /** Archetype */
            archetype: string;
            /** Candidate Id */
            candidate_id: string;
            /** Capex */
            capex: number;
            /**
             * Components
             * @default []
             */
            components: components["schemas"]["CandidateEvaluation-Input"][];
            /** Cost 60M */
            cost_60m: number;
            /** Eu Compliant */
            eu_compliant: boolean;
            /** Failures */
            failures: components["schemas"]["FilterFailure"][];
            /** Hardware Id */
            hardware_id: string | null;
            kind: components["schemas"]["CandidateKind"];
            /** Label */
            label: string;
            /** Local Candidate Id */
            local_candidate_id: string | null;
            /** Model Id */
            model_id: string;
            /** Model Max Context Tokens */
            model_max_context_tokens?: number | null;
            /** Monthly Cost */
            monthly_cost: number;
            /** Nodes */
            nodes: number | null;
            /** Notes */
            notes: string[];
            performance: components["schemas"]["PerformanceResult"] | null;
            /** Popularity */
            popularity: number;
            precision: components["schemas"]["PrecisionFormat"] | null;
            price_origin: components["schemas"]["ValueOrigin"];
            quality: components["schemas"]["QualityScore"] | null;
            /** Rental Id */
            rental_id: string | null;
            /** Risk */
            risk: number;
            sizing: components["schemas"]["SizingResult"] | null;
            tco: components["schemas"]["TcoResult"] | null;
            /** Utilization */
            utilization: number | null;
        };
        /** CandidateEvaluation */
        "CandidateEvaluation-Output": {
            /**
             * Api Has Eu Endpoint
             * @default false
             */
            api_has_eu_endpoint: boolean;
            /** Api Model Id */
            api_model_id: string | null;
            /** Archetype */
            archetype: string;
            /** Candidate Id */
            candidate_id: string;
            /** Capex */
            capex: number;
            /**
             * Components
             * @default []
             */
            components: components["schemas"]["CandidateEvaluation-Output"][];
            /** Cost 60M */
            cost_60m: number;
            /** Eu Compliant */
            eu_compliant: boolean;
            /** Failures */
            failures: components["schemas"]["FilterFailure"][];
            /** Hardware Id */
            hardware_id: string | null;
            kind: components["schemas"]["CandidateKind"];
            /** Label */
            label: string;
            /** Local Candidate Id */
            local_candidate_id: string | null;
            /** Model Id */
            model_id: string;
            /** Model Max Context Tokens */
            model_max_context_tokens?: number | null;
            /** Monthly Cost */
            monthly_cost: number;
            /** Nodes */
            nodes: number | null;
            /** Notes */
            notes: string[];
            performance: components["schemas"]["PerformanceResult"] | null;
            /** Popularity */
            popularity: number;
            precision: components["schemas"]["PrecisionFormat"] | null;
            price_origin: components["schemas"]["ValueOrigin"];
            quality: components["schemas"]["QualityScore"] | null;
            /** Rental Id */
            rental_id: string | null;
            /** Risk */
            risk: number;
            sizing: components["schemas"]["SizingResult"] | null;
            tco: components["schemas"]["TcoResult"] | null;
            /** Utilization */
            utilization: number | null;
        };
        /**
         * CandidateKind
         * @enum {string}
         */
        CandidateKind: "onprem" | "api" | "rental" | "hybrid";
        /** CatalogItem */
        CatalogItem: {
            /** Id */
            id: string;
            /** Label */
            label: string;
        };
        /** CatalogOverview */
        CatalogOverview: {
            /** Counts */
            counts: [
                string,
                number
            ][];
            /** Default Active Users */
            default_active_users: number;
            fx: components["schemas"]["FxInfo"];
            /** Hardware */
            hardware: components["schemas"]["CatalogItem"][];
            /** Hubs */
            hubs: components["schemas"]["CatalogItem"][];
            /** Models */
            models: components["schemas"]["CatalogItem"][];
            /** Presets */
            presets: components["schemas"]["CatalogItem"][];
            /** Tariffs */
            tariffs: components["schemas"]["CatalogItem"][];
            /** Use Cases */
            use_cases: components["schemas"]["CatalogItem"][];
        };
        /**
         * Criterion
         * @enum {string}
         */
        Criterion: "tco_60m" | "quality" | "effective_tps" | "ttft" | "risk" | "popularity";
        /** CriterionScore */
        CriterionScore: {
            /** Contribution */
            contribution: number;
            criterion: components["schemas"]["Criterion"];
            /** Missing */
            missing: boolean;
            /** Normalised */
            normalised: number;
            /** Raw */
            raw: number | null;
            /** Weight */
            weight: number;
        };
        /**
         * CriterionWeights
         * @description Raw weights; non-negativity is checked by the ranking (Req 29.11), not here.
         */
        CriterionWeights: {
            /** Effective Tps */
            effective_tps: number;
            /** Popularity */
            popularity: number;
            /** Quality */
            quality: number;
            /** Risk */
            risk: number;
            /** Tco 60M */
            tco_60m: number;
            /** Ttft */
            ttft: number;
        };
        /** DecisionOptions */
        DecisionOptions: {
            /** @default saw */
            method: components["schemas"]["RankingMethod"];
            /** @default best-fit */
            preset: components["schemas"]["PresetId"];
            /** Reference Api Model Id */
            reference_api_model_id?: string | null;
            /**
             * Reward Excess Performance
             * @default false
             */
            reward_excess_performance: boolean;
            /** @default agentic-coding */
            use_case: components["schemas"]["UseCaseId"];
            weights?: components["schemas"]["CriterionWeights"] | null;
        };
        /**
         * ElectricityTariffTier
         * @enum {string}
         */
        ElectricityTariffTier: "de-industrial-bdew" | "de-office" | "eu-nordic";
        /** EnterpriseFinancials */
        EnterpriseFinancials: {
            /**
             * Capital Opportunity Rate
             * @default 0.045
             */
            capital_opportunity_rate: number;
            /**
             * Cooling Pue
             * @default 1.2
             */
            cooling_pue: number;
            /**
             * Cost Model
             * @default enterprise
             * @enum {string}
             */
            cost_model: "enterprise" | "self-managed";
            /**
             * Currency
             * @default USD
             * @enum {string}
             */
            currency: "EUR" | "USD";
            /**
             * Depreciation Years
             * @default 3
             */
            depreciation_years: number;
            /**
             * Developer Hourly Opportunity Cost
             * @default 72.57
             */
            developer_hourly_opportunity_cost: number;
            /**
             * Devops Fte Allocation
             * @default 0.5
             */
            devops_fte_allocation: number;
            /** @default de-industrial-bdew */
            electricity_tariff_tier: components["schemas"]["ElectricityTariffTier"];
            /**
             * Enable Nvidia Nim Licensing
             * @default false
             */
            enable_nvidia_nim_licensing: boolean;
            /** @default ro-cluj-bucharest */
            engineering_hub_location: components["schemas"]["EuEngineeringHub"];
            /**
             * Include Resale Value
             * @default false
             */
            include_resale_value: boolean;
            /**
             * Include Wait Time Penalty
             * @default false
             */
            include_wait_time_penalty: boolean;
            /**
             * Local Offload Ratio
             * @default 0.7
             */
            local_offload_ratio: number;
            /**
             * Max Capex Budget Usd
             * @default 100000
             */
            max_capex_budget_usd: number | null;
            /** Max Tco Budget Usd */
            max_tco_budget_usd?: number | null;
            /**
             * Nvidia Nim License Per Gpu Yr Usd
             * @default 4500
             */
            nvidia_nim_license_per_gpu_yr_usd: number;
            /**
             * Require Third Party Harness
             * @default true
             */
            require_third_party_harness: boolean;
            /**
             * Strict Eu Sovereignty
             * @default true
             */
            strict_eu_sovereignty: boolean;
            /** Subscription Plan Id */
            subscription_plan_id?: string | null;
        };
        /**
         * EuEngineeringHub
         * @enum {string}
         */
        EuEngineeringHub: "de-munich-hq" | "de-berlin-hamburg" | "ro-cluj-bucharest" | "pl-warsaw-krakow";
        /** ExportRequest */
        ExportRequest: {
            /**
             * Currency
             * @default USD
             * @enum {string}
             */
            currency: "USD" | "EUR";
            result: components["schemas"]["ScenarioResult-Input"];
        };
        /** FilterFailure */
        FilterFailure: {
            /** Measured */
            measured: string;
            /** Name */
            name: string;
            /** Threshold */
            threshold: string;
        };
        /**
         * FormulaTrace
         * @description Symbolic and substituted formula for the audit drawer (Req 36.1).
         */
        FormulaTrace: {
            /** Name */
            name: string;
            /** Result */
            result: number;
            /** Substituted */
            substituted: string;
            /** Symbolic */
            symbolic: string;
            /** Unit */
            unit: string;
        };
        /** FxInfo */
        FxInfo: {
            /** Is Override */
            is_override: boolean;
            /** Rate */
            rate: number;
            /**
             * Rate Date
             * Format: date
             */
            rate_date: string;
            /** Source Id */
            source_id: string;
        };
        /**
         * GatewayType
         * @enum {string}
         */
        GatewayType: "litellm-python" | "bifrost-compiled";
        /**
         * HarnessType
         * @enum {string}
         */
        HarnessType: "claude-code" | "codex" | "opencode" | "deepseek-dsh" | "custom-lean";
        /** Health */
        Health: {
            /**
             * Status
             * @default ok
             */
            status: string;
        };
        /**
         * Metric
         * @description A computed number with its Value_Origin.
         */
        Metric: {
            origin: components["schemas"]["ValueOrigin"];
            /** Unit */
            unit: string;
            /** Value */
            value: number;
        };
        /** MonthlyTcoPoint */
        MonthlyTcoPoint: {
            /** Baseline A Subscription Cumulative */
            baseline_a_subscription_cumulative: number;
            /** Baseline B Global Api Cumulative */
            baseline_b_global_api_cumulative: number;
            /** Baseline C Eu Sovereign Api Cumulative */
            baseline_c_eu_sovereign_api_cumulative: number;
            /** Baseline D Openrouter Value Cumulative */
            baseline_d_openrouter_value_cumulative: number | null;
            /** Eu Dedicated Rental Cumulative */
            eu_dedicated_rental_cumulative: number;
            /** Hybrid Split Cumulative */
            hybrid_split_cumulative: number;
            /** Month */
            month: number;
            /** On Prem Cumulative */
            on_prem_cumulative: number;
        };
        /** PerformanceResult */
        PerformanceResult: {
            decode_tps: components["schemas"]["Metric"] | null;
            effective_tps: components["schemas"]["Metric"] | null;
            prefill_1m_minutes?: components["schemas"]["Metric"] | null;
            prefill_tps: components["schemas"]["Metric"] | null;
            /** Traces */
            traces: components["schemas"]["FormulaTrace"][];
            ttft_s: components["schemas"]["Metric"] | null;
            /** Warnings */
            warnings: string[];
        };
        /**
         * PrecisionFormat
         * @enum {string}
         */
        PrecisionFormat: "FP16" | "BF16" | "FP8" | "INT8" | "INT4" | "INT3" | "INT2";
        /**
         * PresetId
         * @enum {string}
         */
        PresetId: "cheapest" | "best-fit" | "most-capable" | "popular";
        /** QualityScore */
        QualityScore: {
            benchmark: components["schemas"]["BenchmarkMetric"];
            /** Fallback Note */
            fallback_note: string | null;
            origin: components["schemas"]["ValueOrigin"];
            /** Value */
            value: number;
        };
        /** RankedCandidate */
        "RankedCandidate-Input": {
            /** Criteria */
            criteria: components["schemas"]["CriterionScore"][];
            /** D Minus */
            d_minus: number | null;
            /** D Plus */
            d_plus: number | null;
            evaluation: components["schemas"]["CandidateEvaluation-Input"];
            /** Rank */
            rank: number;
            /** Saw Rank */
            saw_rank: number;
            /** Saw Score */
            saw_score: number;
            /** Topsis Closeness */
            topsis_closeness: number | null;
            /** Topsis Rank */
            topsis_rank: number | null;
        };
        /** RankedCandidate */
        "RankedCandidate-Output": {
            /** Criteria */
            criteria: components["schemas"]["CriterionScore"][];
            /** D Minus */
            d_minus: number | null;
            /** D Plus */
            d_plus: number | null;
            evaluation: components["schemas"]["CandidateEvaluation-Output"];
            /** Rank */
            rank: number;
            /** Saw Rank */
            saw_rank: number;
            /** Saw Score */
            saw_score: number;
            /** Topsis Closeness */
            topsis_closeness: number | null;
            /** Topsis Rank */
            topsis_rank: number | null;
        };
        /**
         * RankingMethod
         * @enum {string}
         */
        RankingMethod: "saw" | "topsis";
        /** RecommendRequest */
        RecommendRequest: {
            scenario: components["schemas"]["Scenario"];
        };
        /** Recommendation */
        "Recommendation-Input": {
            /** Explanation */
            explanation: string | null;
            method: components["schemas"]["RankingMethod"];
            /** Ranked */
            ranked: components["schemas"]["RankedCandidate-Input"][];
            /** Ranking Error */
            ranking_error: string | null;
            /** Rejected */
            rejected: components["schemas"]["CandidateEvaluation-Input"][];
            use_case: components["schemas"]["UseCaseId"];
            /** Warnings */
            warnings: string[];
            weights_normalised: components["schemas"]["CriterionWeights"] | null;
        };
        /** Recommendation */
        "Recommendation-Output": {
            /** Explanation */
            explanation: string | null;
            method: components["schemas"]["RankingMethod"];
            /** Ranked */
            ranked: components["schemas"]["RankedCandidate-Output"][];
            /** Ranking Error */
            ranking_error: string | null;
            /** Rejected */
            rejected: components["schemas"]["CandidateEvaluation-Output"][];
            use_case: components["schemas"]["UseCaseId"];
            /** Warnings */
            warnings: string[];
            weights_normalised: components["schemas"]["CriterionWeights"] | null;
        };
        /**
         * RuntimeFormat
         * @enum {string}
         */
        RuntimeFormat: "auto" | "gguf" | "vllm" | "mlx";
        /** Scenario */
        Scenario: {
            decision: components["schemas"]["DecisionOptions"];
            financials: components["schemas"]["EnterpriseFinancials"];
            /** Fx Override */
            fx_override?: number | null;
            sizing: components["schemas"]["SizingOptions"];
            workload: components["schemas"]["WorkloadProfile"];
        };
        /** ScenarioRequest */
        ScenarioRequest: {
            scenario: components["schemas"]["Scenario"];
        };
        /** ScenarioResult */
        "ScenarioResult-Input": {
            baselines: components["schemas"]["BaselineResult"];
            /** Catalog Fingerprint */
            catalog_fingerprint?: string | null;
            /**
             * Engine Version
             * @default 0.1.4
             */
            engine_version: string;
            /** Fx Is Override */
            fx_is_override: boolean;
            /** Fx Rate */
            fx_rate: number;
            /**
             * Fx Rate Date
             * Format: date
             */
            fx_rate_date: string;
            /** Fx Source Id */
            fx_source_id: string;
            recommendation: components["schemas"]["Recommendation-Input"];
            scenario: components["schemas"]["Scenario"];
            /** Sources */
            sources: components["schemas"]["SourceEntry"][];
            timeline: components["schemas"]["TimelineResult"] | null;
            /** Warnings */
            warnings: string[];
        };
        /** ScenarioResult */
        "ScenarioResult-Output": {
            baselines: components["schemas"]["BaselineResult"];
            /** Catalog Fingerprint */
            catalog_fingerprint?: string | null;
            /**
             * Engine Version
             * @default 0.1.4
             */
            engine_version: string;
            /** Fx Is Override */
            fx_is_override: boolean;
            /** Fx Rate */
            fx_rate: number;
            /**
             * Fx Rate Date
             * Format: date
             */
            fx_rate_date: string;
            /** Fx Source Id */
            fx_source_id: string;
            recommendation: components["schemas"]["Recommendation-Output"];
            scenario: components["schemas"]["Scenario"];
            /** Sources */
            sources: components["schemas"]["SourceEntry"][];
            timeline: components["schemas"]["TimelineResult"] | null;
            /** Warnings */
            warnings: string[];
        };
        /** SimulationOptions */
        SimulationOptions: {
            /** Node Counts */
            node_counts: [
                string,
                number[]
            ][];
            /** Open Model Ids */
            open_model_ids: string[];
            /** Preset Weights */
            preset_weights: [
                string,
                components["schemas"]["CriterionWeights"]
            ][];
        };
        /** SizeRequest */
        SizeRequest: {
            /** Hardware Id */
            hardware_id: string;
            /** Model Id */
            model_id: string;
            /**
             * Nodes
             * @default 1
             */
            nodes: number;
            precision: components["schemas"]["PrecisionFormat"];
            scenario: components["schemas"]["Scenario"];
        };
        /** SizeResult */
        SizeResult: {
            aa_index_v5: components["schemas"]["QualityScore"] | null;
            performance: components["schemas"]["PerformanceResult"] | null;
            sizing: components["schemas"]["SizingResult"];
            workload: components["schemas"]["WorkloadResult"];
        };
        /** SizingOptions */
        SizingOptions: {
            /**
             * Apply Mac Wired Memory Override
             * @default false
             */
            apply_mac_wired_memory_override: boolean;
            benchmark_conditions?: components["schemas"]["BenchmarkConditions"] | null;
            /**
             * Enable Optimized Backend
             * @default true
             */
            enable_optimized_backend: boolean;
            /**
             * Gpu Memory Utilization
             * @default 0.9
             */
            gpu_memory_utilization: number;
            /** @default FP16 */
            kv_precision: components["schemas"]["PrecisionFormat"];
            /**
             * Linux Amd Override
             * @default false
             */
            linux_amd_override: boolean;
            /** Performance Prompt Tokens */
            performance_prompt_tokens?: number | null;
            /**
             * Repo Workspace Gb
             * @default 4
             */
            repo_workspace_gb: number;
            /** Requested Nodes */
            requested_nodes?: number | null;
            /** @default auto */
            runtime_format: components["schemas"]["RuntimeFormat"];
            /**
             * Runtime Overhead Gb
             * @default 2
             */
            runtime_overhead_gb: number;
            /** @default none */
            speculative_mode: components["schemas"]["SpeculativeMode"];
            /**
             * Target Context Length
             * @default 128000
             */
            target_context_length: number;
            /** @default INT4 */
            weight_precision: components["schemas"]["PrecisionFormat"];
        };
        /** SizingResult */
        SizingResult: {
            /** Agent State Memory Required Gb */
            agent_state_memory_required_gb: number;
            /** Alpha Scaling */
            alpha_scaling: number;
            /**
             * Context Eviction Risk
             * @default false
             */
            context_eviction_risk: boolean;
            /**
             * Eu Commercial License Valid
             * @default true
             */
            eu_commercial_license_valid: boolean;
            /** Hardware Id */
            hardware_id: string;
            /** Is Feasible */
            is_feasible: boolean;
            /** Kv Per Token Bytes */
            kv_per_token_bytes: number;
            /** Kv Pool Gb */
            kv_pool_gb: number;
            /** M Kv Single Gb */
            m_kv_single_gb: number;
            /** Max Concurrent Users */
            max_concurrent_users: number;
            /** Max Usable Context */
            max_usable_context: number;
            /**
             * Meets 128K Agentic Context Floor
             * @default true
             */
            meets_128k_agentic_context_floor: boolean;
            /** Memory Breakdown */
            memory_breakdown: [
                string,
                number
            ][];
            /** Model Id */
            model_id: string;
            /** Nodes Required */
            nodes_required: number;
            /** Oom Reason */
            oom_reason?: string | null;
            precision: components["schemas"]["PrecisionFormat"];
            /** Requested Nodes */
            requested_nodes: number;
            /**
             * Thunderbolt Mesh Cables
             * @default 0
             */
            thunderbolt_mesh_cables: number;
            /** Token Agreement Rate */
            token_agreement_rate?: number | null;
            /** Traces */
            traces: components["schemas"]["FormulaTrace"][];
            /**
             * Triggered Mac Default Split Trap
             * @default false
             */
            triggered_mac_default_split_trap: boolean;
            /** Usable Memory Default Gb */
            usable_memory_default_gb: number;
            /** Usable Memory Gb */
            usable_memory_gb: number;
            /** Usable System Ram Gb */
            usable_system_ram_gb: number | null;
            /** Warnings */
            warnings: string[];
            weights: components["schemas"]["Metric"];
        };
        /** SourceEntry */
        SourceEntry: {
            /** Publisher */
            publisher: string;
            /** Reference */
            reference?: string | null;
            /** Source Id */
            source_id: string;
            tier: components["schemas"]["SourceTier"];
            /** Title */
            title: string;
            /** Url */
            url?: string | null;
        };
        /**
         * SourceTier
         * @enum {string}
         */
        SourceTier: "official" | "third_party" | "community" | "formula" | "assumption";
        /**
         * SpeculativeMode
         * @enum {string}
         */
        SpeculativeMode: "none" | "apple-mtp-dflash" | "built-in-mtp" | "external-draft";
        /** TcoAccounting */
        TcoAccounting: {
            /** Break Even Month */
            break_even_month: number | null;
            /** Candidate Id */
            candidate_id: string;
            fx: components["schemas"]["FxInfo"];
            /** Includes Resale */
            includes_resale: boolean;
            /** Rows */
            rows: components["schemas"]["AccountingRow"][];
            /** Utilization Text */
            utilization_text: string;
        };
        /** TcoRequest */
        TcoRequest: {
            /** Candidate Id */
            candidate_id: string;
            scenario: components["schemas"]["Scenario"];
        };
        /** TcoResponse */
        TcoResponse: {
            accounting: components["schemas"]["TcoAccounting"] | null;
            baselines: components["schemas"]["BaselineResult"];
            candidate: components["schemas"]["CandidateEvaluation-Output"];
            timeline: components["schemas"]["TimelineResult"] | null;
        };
        /** TcoResult */
        TcoResult: {
            aggregate_tps: components["schemas"]["Metric"] | null;
            /** Capacity Insufficient */
            capacity_insufficient: boolean;
            /** Capacity Tokens Month */
            capacity_tokens_month: number | null;
            capex: components["schemas"]["Metric"];
            /** Cost 60M */
            cost_60m: number;
            /** Gpu Count */
            gpu_count: number;
            /** Meets 70 Percent Utilization Threshold */
            meets_70_percent_utilization_threshold: boolean;
            /** Monthly Opex */
            monthly_opex: [
                string,
                number
            ][];
            /** Monthly Opex Total */
            monthly_opex_total: number;
            /** Munich Vs Romania Personnel Savings Monthly */
            munich_vs_romania_personnel_savings_monthly: number;
            /** Resale Retention 3Yr */
            resale_retention_3yr: number;
            /** Traces */
            traces: components["schemas"]["FormulaTrace"][];
            /** Units */
            units: number;
            /** Utilization */
            utilization: number | null;
            /** Warnings */
            warnings: string[];
        };
        /**
         * ThinkingEffortPreset
         * @enum {string}
         */
        ThinkingEffortPreset: "none" | "low" | "medium" | "extra-high";
        /** TimelineResult */
        TimelineResult: {
            /** Anchor Candidate Id */
            anchor_candidate_id: string;
            /** Break Even Months */
            break_even_months: [
                string,
                number | null
            ][];
            /** Hybrid Api Model Id */
            hybrid_api_model_id: string;
            /** Include Resale */
            include_resale: boolean;
            /** Points */
            points: components["schemas"]["MonthlyTcoPoint"][];
            /** Rental Id */
            rental_id: string;
            single_stream_break_even_years?: components["schemas"]["Metric"] | null;
        };
        /**
         * UseCaseId
         * @enum {string}
         */
        UseCaseId: "writing-email" | "summarisation-rag" | "coding-assistant" | "agentic-coding";
        /** ValueOrigin */
        ValueOrigin: {
            /**
             * Origin
             * @enum {string}
             */
            origin: "measured" | "formula";
            /** Source Ids */
            source_ids: string[];
        };
        /**
         * WorkScheduleMode
         * @enum {string}
         */
        WorkScheduleMode: "interactive-workday" | "unattended-background-loop";
        /** WorkloadProfile */
        WorkloadProfile: {
            /**
             * Active Hours Per Month
             * @default 176
             */
            active_hours_per_month: number;
            /**
             * Active Users
             * @default 25
             */
            active_users: number;
            /**
             * Avg Input Tokens
             * @default 15000
             */
            avg_input_tokens: number;
            /**
             * Avg Output Tokens
             * @default 1500
             */
            avg_output_tokens: number;
            /**
             * Batch Api Eligible Ratio
             * @default 0.2
             */
            batch_api_eligible_ratio: number;
            /**
             * Concurrent Agent Instances
             * @default 8
             */
            concurrent_agent_instances: number;
            /**
             * Context Length P50
             * @default 32000
             */
            context_length_p50: number;
            /**
             * Context Length P90
             * @default 128000
             */
            context_length_p90: number;
            /**
             * Context Length P99
             * @default 250000
             */
            context_length_p99: number;
            /** Custom Scaffolding Tokens */
            custom_scaffolding_tokens?: number | null;
            /**
             * Daily Requests Per User
             * @default 40
             */
            daily_requests_per_user: number;
            /** @default litellm-python */
            gateway_type: components["schemas"]["GatewayType"];
            /** @default claude-code */
            harness_type: components["schemas"]["HarnessType"];
            /**
             * Has Verification Agent Layer
             * @default false
             */
            has_verification_agent_layer: boolean;
            /**
             * Max Acceptable Ttft Seconds
             * @default 15
             */
            max_acceptable_ttft_seconds: number | null;
            /**
             * Mcp Code Mode Pruning
             * @default false
             */
            mcp_code_mode_pruning: boolean;
            /**
             * Mega Session Ratio
             * @default 0.35
             */
            mega_session_ratio: number;
            /**
             * Min Acceptable Tps
             * @default 20
             */
            min_acceptable_tps: number | null;
            /**
             * Peak Concurrent Requests
             * @default 5
             */
            peak_concurrent_requests: number;
            /**
             * Prompt Cache Hit Rate
             * @default 0.5
             */
            prompt_cache_hit_rate: number;
            /**
             * Reasoning Token Multiplier
             * @default 2.5
             */
            reasoning_token_multiplier: number;
            /** @default medium */
            thinking_effort_preset: components["schemas"]["ThinkingEffortPreset"];
            /** @default interactive-workday */
            work_schedule_mode: components["schemas"]["WorkScheduleMode"];
            /**
             * Working Days Per Month
             * @default 22
             */
            working_days_per_month: number;
        };
        /** WorkloadResult */
        WorkloadResult: {
            /** Kappa Mega */
            kappa_mega: number;
            /** Monthly Output Demand */
            monthly_output_demand: number;
            /** Monthly Requests */
            monthly_requests: number;
            /** Monthly Tokens */
            monthly_tokens: number;
            /** Nu Verify */
            nu_verify: number;
            /** Out Think */
            out_think: number;
            /** S Effective */
            s_effective: number;
            /** T In Hat */
            t_in_hat: number;
            /** T Out Hat */
            t_out_hat: number;
            /** Tau */
            tau: number;
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    audit_api_v1_audit_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AuditRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AuditResult"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
        };
    };
    catalog_api_v1_catalog_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CatalogOverview"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
        };
    };
    evaluate_api_v1_evaluate_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ScenarioRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ScenarioResult-Output"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
        };
    };
    export_csv_api_v1_export_csv_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ExportRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
        };
    };
    export_json_api_v1_export_json_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ExportRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
        };
    };
    health_api_v1_health_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Health"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
        };
    };
    options_api_v1_options_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SimulationOptions"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
        };
    };
    recommend_api_v1_recommend_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RecommendRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Recommendation-Output"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
        };
    };
    default_scenario_api_v1_scenario_default_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Scenario"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
        };
    };
    validate_scenario_api_v1_scenario_validate_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["Scenario"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Scenario"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
        };
    };
    size_api_v1_size_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SizeRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SizeResult"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
        };
    };
    tco_api_v1_tco_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["TcoRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TcoResponse"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
        };
    };
    default_workload_api_v1_workloads_default_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["WorkloadProfile"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiError"];
                };
            };
        };
    };
}
