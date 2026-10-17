# Cross-indicator comparison

Use 데이터 비교 (/compare) to combine all connected country indicators, policy rates, FRED series, market quotes, euro-area PPI, Japan confidence and Korea monthly current account (ECOS key required).

- No fixed selection count; provider data availability still applies.
- Exact date bounds; original, index 100, relative change, absolute difference, Z-score.
- Optional monthly/quarterly/annual aggregation of observed values using last observation or mean; not a sum or frequency upsampling.
- Original mixed units shown in vertically stacked charts; normalized series can overlap.
- No gap filling. Common period restricts date range, not identical observation dates. Actual bucket observation dates are retained.
- These are observation dates, not publication dates. Baselines can differ with observation frequency. Relative changes of already-percent series are not percentage-point changes.
- Selection is a visualization tool, not causal inference.

Validation: python -m unittest test_comparison_engine
