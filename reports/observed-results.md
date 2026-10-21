# Observed batch statistics

Generated from original attempts. Metrics count every main-experiment attempt, including retries; missing values are excluded, never replaced by zero. The 40 archived access incidents are separate experiments, not extra votes or replacements.

| Lot | Attempts | Cells attempted | Correct / 20 | Wrong | Invalid SQL | No evaluated SQL |
|---|---:|---:|---:|---:|---:|---:|
| A | 20 | 20 | 19/20 | 1 | 0 | 0 |
| B | 20 | 20 | 18/20 | 2 | 0 | 0 |
| C | 20 | 20 | 11/20 | 9 | 0 | 0 |
| D | 24 | 20 | 15/20 | 4 | 0 | 1 |
| E | 20 | 20 | 13/20 | 6 | 1 | 0 |

Detailed metric coverage, means, medians and totals: [model-statistics.json](../evidence/model-statistics.json). Family counts: [five-model-summary-en.csv](../five-model-summary-en.csv).

| Lot | Median latency ms (observed/attempts) | Input tokens total (observed/attempts) | Output tokens total (observed/attempts) | Native cost total (observed/attempts) |
|---|---|---|---|---|
| A | 739.3 (20/20) | 12814 (20/20) | 4576 (20/20) | N/A (0/20) |
| B | 627.85 (20/20) | 12814 (20/20) | 5027 (20/20) | N/A (0/20) |
| C | 2093.9 (20/20) | 11194 (20/20) | 2714 (20/20) | 0 (20/20) |
| D | 410.2 (24/24) | 11978 (19/24) | 2586 (19/24) | N/A (0/24) |
| E | 2896.65 (20/20) | 11858 (20/20) | 3469 (20/20) | 0 (20/20) |
