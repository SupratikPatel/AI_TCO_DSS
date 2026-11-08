# Stitch implementation tokens

Retrieved 2026-11-08 from project 12247395809959632226. Original HTML,
downloaded screenshots and complete design-system JSON are preserved locally;
`manifest.json` records every resource and its actual raster size.

Canonical light: 2b49b16649ff4d66a9ce09206ede2ff5. Canonical dark:
01e280423d614d30bb7b5af1f83640d4. The dark screen's `dark-theme-override`
takes precedence over its initial light Tailwind config and global design prose.

| Token | Light | Dark |
| --- | --- | --- |
| Canvas | #f9f9ff | #0b0f17 |
| Panel | #ffffff | #131926 |
| Muted surface | #f1f3ff | #101520 |
| Raised surface | #e9edff | #161d2a |
| Text | #141b2b | #f1f5f9 |
| Secondary text | #404750 | #94a3b8 |
| Border | #c0c7d2 | #222c3d |
| Divider | #e1e8fd | #1f2839 |
| Primary action | #0072b2 | #38bdf8 |
| Primary text | #00598c | #38bdf8 |

Geometry: sidebar 280 CSS px, header 64 px, main horizontal padding 24 px,
sidebar padding 20 px, five equal KPI columns with 12 px gaps, 24 px between
KPIs and tab panel, chart/accounting columns approximately 1.45:1 with 24 px gap.
Panels use 8 px radii, controls 4 px, crisp 1 px borders and 36 px input heights.

Type: Inter for interface text, JetBrains Mono for values, quantitative labels
and axes. Fonts are served locally. Titles use 18–21 px, body 12–13 px,
quantitative labels 10–11 px.

Chart series preserve ledger C-004: centralized on-premise blue #0072B2 (solid,
4 px), EU rental #009E73 (dash-dot), C #E69F00 (solid), A #CC79A7 (dashed),
B/D black (dotted, readable slate in dark), hybrid #E69F00 (dashed).
Memory segments use blue, sky blue, green, yellow and purple in contract order.
