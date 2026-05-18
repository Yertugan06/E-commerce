## SLO Definitions

| SLI | SLO Target | Measurement Window | Alert Threshold |
|-----|-----------|-------------------|-----------------|
| API Availability | >= 99.9% | 5 minutes rolling | < 99.9% for 5m |
| Read Latency p95 | < 1.0s | 5 minutes rolling | > 1.0s for 5m |
| Write Latency p95 | < 2.0s | 5 minutes rolling | > 2.0s for 5m |
| Auth Latency p95 | < 1.0s | 5 minutes rolling | > 1.0s for 5m |
| 5xx Error Rate | < 1% | 5 minutes rolling | > 1% for 5m |
| Checkout Failure Rate | < 5% | 5 minutes rolling | > 5% for 5m |
| Order Persistence | 0 errors | 5 minutes rolling | > 0 for 1m |
| Cart Consistency | 0 errors | 5 minutes rolling | > 0 for 1m |
| Active DB Connections | < 80 | 5 minutes rolling | > 80 for 5m |
