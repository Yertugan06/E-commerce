## SLO Definitions

| SLI | SLO Target | SLO Window | Alert Threshold | Measurement Source |
|-----|-----------|-----------|-----------------|-------------------|
| API Availability | >= 99.9% | 30-day rolling | < 99.9% for 5m | FastAPI Middleware |
| Checkout Success Rate | >= 99.5% | 7-day rolling | < 99.5% for 5m | Structured Application Logs |
| Cart Read Latency p95 | <= 300ms | 7-day rolling | > 300ms for 5m | ASGI / Access Logs |
| Order Read Latency p95 | <= 500ms | 7-day rolling | > 500ms for 5m | ASGI / Access Logs |
| Cart Update Latency p95 | <= 500ms | 7-day rolling | > 500ms for 5m | ASGI / Access Logs |
| Checkout Latency p95 | <= 2000ms | 7-day rolling | > 2000ms for 5m | ASGI / Access Logs |
| Auth Latency p95 | <= 1000ms | 7-day rolling | > 1000ms for 5m | ASGI / Access Logs |
| Cart Consistency Rate | >= 99.9% | 30-day rolling | < 99.9% for 5m | Application Validation |

## SLI Definition Details

| SLI Name | Definition | Measurement Source |
|----------|-----------|-------------------|
| API Availability | Count of HTTP responses < 500 / Total HTTP requests | FastAPI Middleware |
| Checkout Success Rate | Count of HTTP 200/201 responses for POST /checkout / Total POST /checkout requests | Structured Application Logs |
| Cart Read Latency | p95 response time of GET /cart | ASGI / Access Logs |
| Order Read Latency | p95 response time of GET /orders | ASGI / Access Logs |
| Cart Update Latency | p95 response time of POST /cart/items | ASGI / Access Logs |
| Checkout Latency | p95 response time of POST /checkout | ASGI / Access Logs |
| Auth Latency | p95 response time of POST /auth/login | ASGI / Access Logs |
| Cart Consistency Rate | Successful consistency validations / Total cart consistency checks | Application Validation |
