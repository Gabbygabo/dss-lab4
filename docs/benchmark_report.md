# Storage Benchmark Report

| Format | Size (MB) | Write Time (s) | Median Read Time (s) |
|--------|-----------|----------------|----------------------|
| CSV | 10.22 | 2.126 | 0.388 |
| JSON | 46.51 | 1.44 | 2.29 |
| Parquet | 3.64 | 0.219 | 0.021 |
| PostgreSQL | N/A | N/A | N/A |

**Conclusion:** Parquet is the best format for model input and intermediate storage. CSV is best for source exchange.
