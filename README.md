<p align="center">
  <img src="docs/img/banner-img.png" alt="K4sCloud URL Shortener" width="800"/>
</p>

<h1 align="center">K4sCloud URL Shortener</h1>

<p align="center">
  Production-grade URL shortening service with end-to-end observability,<br/>
  automated security scanning, and zero-downtime CI/CD.
</p>

<p align="center">
  <strong>Live Demo:</strong> <a href="https://short.k4scloud.com">short.k4scloud.com</a>
  &nbsp;|&nbsp;
  <a href="https://short.k4scloud.com/api/v1/docs">API Docs</a>
  &nbsp;|&nbsp;
  <a href="https://short.k4scloud.com/api/v1/health">Health Status</a>
</p>

<p align="center">

![CI/CD Pipeline](https://github.com/alchemistkay/url-shortener/actions/workflows/ci.yml/badge.svg?branch=main)
![codecov](https://codecov.io/gh/alchemistkay/url-shortener/branch/main/graph/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)
![Last Commit](https://img.shields.io/github/last-commit/alchemistkay/url-shortener?style=flat-square&color=blue)
![Repo Size](https://img.shields.io/github/repo-size/alchemistkay/url-shortener?style=flat-square)

</p>

---

## Tech Stack

**Backend**

![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL_17-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis_7-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)

**Infrastructure**

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![Traefik](https://img.shields.io/badge/Traefik_Proxy-24A1C1?style=for-the-badge&logo=traefikproxy&logoColor=white)

**Observability**

![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Uptime Kuma](https://img.shields.io/badge/Uptime_Kuma-5CDD8B?style=for-the-badge&logo=uptimekuma&logoColor=black)

**CI/CD & Security**

![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![CodeQL](https://img.shields.io/badge/CodeQL-000000?style=for-the-badge&logo=github&logoColor=white)
![Trivy](https://img.shields.io/badge/Trivy-1904DA?style=for-the-badge&logoColor=white)
![TruffleHog](https://img.shields.io/badge/TruffleHog-FF4500?style=for-the-badge&logoColor=white)

---

## Features

<table>
<tr>
<td align="center" width="33%">

**Core API**
- URL shortening + custom slugs
- Click tracking & analytics
- URL expiration (TTL)
- OpenAPI / Swagger UI

</td>
<td align="center" width="33%">

**Operational**
- Sub-5ms cache-hit responses
- 50–80% cache hit ratio
- Zero-downtime deployments
- Auto-rollback on failure

</td>
<td align="center" width="33%">

**Observability**
- 7 custom Prometheus metrics
- Grafana dashboards
- Uptime Kuma monitoring
- Structured health checks

</td>
</tr>
</table>

---

## Key Metrics

<table>
<tr>
<td align="center"><strong>&lt;5ms</strong><br/>Cache Hit Latency</td>
<td align="center"><strong>&lt;50ms</strong><br/>Cache Miss Latency</td>
<td align="center"><strong>99.9%+</strong><br/>Uptime</td>
<td align="center"><strong>85%+</strong><br/>Test Coverage</td>
<td align="center"><strong>193MB</strong><br/>Container Image</td>
<td align="center"><strong>10–15 min</strong><br/>Commit → Production</td>
</tr>
</table>

---

## Architecture

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,fastapi,postgres,redis,docker,nginx,prometheus,grafana&theme=dark" />
</p>

```mermaid
graph TD
    Client["🌐 Browser / API Client\nHTTPS :443"]

    subgraph VPS["VPS — Docker Network"]
        Traefik["⚡ Traefik\nReverse Proxy + SSL/TLS"]

        subgraph App["Application Layer"]
            Frontend["🗂 Nginx\nStatic Frontend"]
            API["🐍 FastAPI\nPython 3.11 · Uvicorn"]
        end

        subgraph Data["Data Layer"]
            PG[("🐘 PostgreSQL 17\nPersistent Store")]
            Redis[("⚡ Redis 7\nCache Layer")]
        end

        subgraph Obs["Observability Stack"]
            Prom["📊 Prometheus\nMetrics Scrape"]
            Graf["📈 Grafana\nDashboards"]
            Kuma["🟢 Uptime Kuma\nAvailability Monitor"]
        end
    end

    Client -->|"HTTPS request"| Traefik
    Traefik -->|"Host: / root path"| Frontend
    Traefik -->|"PathPrefix: /api/v1"| API
    Traefik -->|"GET /{short_code}"| API
    API -->|"persist / query"| PG
    API -->|"cache reads/writes\nTTL: 3600s"| Redis
    API -->|"/metrics endpoint"| Prom
    Prom --> Graf
    Kuma -->|"HTTP probe"| API
```

### Request Flow

| Request Type | Path | Cache | Latency |
|---|---|---|---|
| Redirect | `GET /{short_code}` | Redis → PostgreSQL | <5ms (hit) / <50ms (miss) |
| Shorten | `POST /api/v1/shorten` | Write-through | <50ms |
| Stats | `GET /api/v1/stats/{code}` | PostgreSQL read | <50ms |
| Health | `GET /api/v1/health` | — | <10ms |

---

## CI/CD Pipeline

> Fully automated 5-stage pipeline — from commit to production in 10–15 minutes with automatic rollback on failure.

```mermaid
flowchart LR
    S1["🔒 Stage 1\nSource Security"]
    S2["🔨 Stage 2\nBuild & Test"]
    S3["🧪 Stage 3\nIntegration Tests"]
    S4["📦 Stage 4\nRelease to GHCR"]
    S5["🚀 Stage 5\nDeploy to VPS"]

    S1 --> S2
    S2 --> S3
    S2 --> S4
    S3 --> S4
    S3 --> S5
    S4 --> S5

    style S1 fill:#21262d,stroke:#6e7681,color:#cdd9e5
    style S2 fill:#21262d,stroke:#6e7681,color:#cdd9e5
    style S3 fill:#21262d,stroke:#6e7681,color:#cdd9e5
    style S4 fill:#21262d,stroke:#6e7681,color:#cdd9e5
    style S5 fill:#0d1117,stroke:#2ea043,color:#2ea043
```

<table>
<thead>
<tr>
<th>Stage</th>
<th>Job</th>
<th>Tools</th>
<th>Quality Gate</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>1</strong></td>
<td>Source Security</td>
<td>
  <img src="https://img.shields.io/badge/TruffleHog-FF4500?style=flat-square&logoColor=white" alt="TruffleHog"/>
  <img src="https://img.shields.io/badge/CodeQL-000000?style=flat-square&logo=github&logoColor=white" alt="CodeQL"/>
  <img src="https://img.shields.io/badge/Ruff-000000?style=flat-square&logoColor=white" alt="Ruff"/>
  <img src="https://img.shields.io/badge/Black-000000?style=flat-square&logoColor=white" alt="Black"/>
  <img src="https://img.shields.io/badge/pip--audit-3776AB?style=flat-square&logo=python&logoColor=white" alt="pip-audit"/>
</td>
<td>Secret scan · SAST · Lint · Dependency CVEs</td>
</tr>
<tr>
<td><strong>2</strong></td>
<td>Build &amp; Test</td>
<td>
  <img src="https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white" alt="pytest"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/Trivy-1904DA?style=flat-square&logoColor=white" alt="Trivy"/>
  <img src="https://img.shields.io/badge/Anchore_SBOM-0087CC?style=flat-square&logoColor=white" alt="Anchore"/>
</td>
<td>Unit tests · 85%+ coverage · Container CVE scan · SBOM</td>
</tr>
<tr>
<td><strong>3</strong></td>
<td>Integration Tests</td>
<td>
  <img src="https://img.shields.io/badge/PostgreSQL_17-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Redis_7-DC382D?style=flat-square&logo=redis&logoColor=white" alt="Redis"/>
  <img src="https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white" alt="pytest"/>
</td>
<td>13 API tests · Real services (no mocks)</td>
</tr>
<tr>
<td><strong>4</strong></td>
<td>Release</td>
<td>
  <img src="https://img.shields.io/badge/GHCR-181717?style=flat-square&logo=github&logoColor=white" alt="GHCR"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"/>
</td>
<td>Multi-tag push · latest · SHA · semver</td>
</tr>
<tr>
<td><strong>5</strong></td>
<td>Deploy to Production</td>
<td>
  <img src="https://img.shields.io/badge/SSH_Deploy-000000?style=flat-square&logo=gnubash&logoColor=white" alt="SSH"/>
</td>
<td>Health check · Auto-rollback on failure</td>
</tr>
</tbody>
</table>

---

## API Documentation

<details>
<summary><strong>View API Reference</strong></summary>

### Base URL
```
https://short.k4scloud.com/api/v1
```

### Endpoints

**Create Short URL**
```http
POST /api/v1/shorten
Content-Type: application/json

{
  "original_url": "https://example.com",
  "custom_slug": "optional-custom-slug",
  "expires_in_hours": 24
}

Response: 200 OK
{
  "short_code": "abc123",
  "short_url": "https://short.k4scloud.com/abc123",
  "original_url": "https://example.com/",
  "clicks": 0,
  "created_at": "2026-03-05T12:00:00Z",
  "is_active": true
}
```

**Get URL Statistics**
```http
GET /api/v1/stats/{short_code}

Response: 200 OK
{
  "short_code": "abc123",
  "original_url": "https://example.com/",
  "total_clicks": 42,
  "is_active": true,
  "created_at": "2026-03-05T12:00:00Z"
}
```

**Redirect**
```http
GET /{short_code}

Response: 307 Temporary Redirect
Location: https://example.com/
```

**Health Check**
```http
GET /api/v1/health

Response: 200 OK
{
  "status": "healthy",
  "dependencies": {
    "database": "healthy",
    "cache": "healthy"
  }
}
```

**Cache Statistics**
```http
GET /api/v1/cache/stats

Response: 200 OK
{
  "total_keys": 150,
  "hits": 1200,
  "misses": 300
}
```

**Interactive Documentation**
- Swagger UI: `https://short.k4scloud.com/api/v1/docs`
- ReDoc: `https://short.k4scloud.com/api/v1/redoc`

</details>

---

## Deployment

### Production Deployment

Production deployment is fully automated via GitHub Actions:

1. Push code to `main` branch
2. CI/CD pipeline runs automatically (5 stages)
3. On success: images pushed to GHCR, SSH deploy to VPS
4. Post-deploy health checks — automatic rollback on failure

### Prerequisites
- Docker & Docker Compose
- PostgreSQL 17
- Redis 7
- Traefik reverse proxy (external network)

<details>
<summary><strong>Local Development Setup</strong></summary>

### Environment Variables
```bash
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<secure_password>
POSTGRES_DB=urlshortener

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=<secure_password>

CACHE_TTL=3600
BASE_URL=https://short.k4scloud.com
```

### Start Services
```bash
# Clone repository
git clone https://github.com/alchemistkay/url-shortener.git
cd url-shortener

# Create environment file
cp .env.example .env
# Edit .env with your credentials

# Start services
docker-compose up -d

# Verify deployment
curl http://localhost:8000/api/v1/health
```

</details>

---

## Monitoring & Observability

### Custom Prometheus Metrics

| Metric | Type | Description |
|---|---|---|
| `urlshortener_urls_created_total` | Counter | Total URLs shortened (labelled by `is_custom`) |
| `urlshortener_redirects_total` | Counter | Total redirects (labelled by `short_code`) |
| `urlshortener_cache_operations_total` | Counter | Cache ops (labelled by `operation`, `result`) |
| `urlshortener_active_urls` | Gauge | Current active URL count |
| `urlshortener_database_connections` | Gauge | Active DB connections |
| `urlshortener_redirect_duration_seconds` | Histogram | Redirect latency (buckets: 1ms–1s) |
| `urlshortener_app` | Info | App version and environment |

### Dashboards

Access from your Grafana instance:
- **URL Shortener Application Metrics** — request rate, latency p95/p99, error rate, cache hit ratio
- **Docker & Host Monitoring** — container health, resource utilization
- **Traefik Traffic Analysis** — routing, SSL, upstream health

---

## Performance Optimization

### Caching Strategy
- Cache-aside pattern with Redis
- TTL: 3600 seconds (configurable via `CACHE_TTL`)
- Cache hit: <5ms · Cache miss: <50ms
- Hit ratio: 50–80% in steady state

### Database
- Indexed `short_code` column for O(1) lookups
- SQLAlchemy connection pooling
- Prepared statements via ORM

### Container
- Multi-stage Docker build — 193MB final image (40% reduction)
- Nginx Alpine for static file serving with 30-day asset caching + GZIP

---

## Security

### Application Security
- HTTPS-only via Traefik with automatic Let's Encrypt renewal
- Input validation with Pydantic (`HttpUrl`, custom slug regex)
- SQL injection prevention via SQLAlchemy ORM
- Security headers on all responses

### Supply Chain & Container Security
- TruffleHog secret scanning on every push
- CodeQL SAST for Python and JavaScript
- pip-audit + safety for dependency CVEs
- Trivy container vulnerability scanning (CRITICAL/HIGH gates)
- Anchore SBOM generation per release
- Non-root container users

### Network Security
- Firewalled VPS — single ingress via Traefik
- Docker network isolation (separate networks for DB, cache, proxy)
- SSH key-based deployment (no password auth)
- Secrets delivered via SCP at deploy time (not env var expansion)

---

## Project Structure

```
url-shortener/
├── backend/
│   ├── main.py              # FastAPI application + all endpoints
│   ├── database.py          # PostgreSQL connection & session factory
│   ├── models.py            # SQLAlchemy ORM models (URL, Click)
│   ├── schemas.py           # Pydantic validation schemas
│   ├── cache.py             # Redis cache-aside implementation
│   ├── helpers.py           # Code generation & URL validation
│   ├── requirements.txt     # Pinned Python dependencies
│   ├── Dockerfile           # Multi-stage optimized build
│   └── tests/
│       ├── test_basic.py    # Unit tests
│       └── integration/
│           └── test_api.py  # 13 integration tests (real DB + Redis)
│
├── frontend/
│   ├── index.html           # Main UI (dark theme, glassmorphism)
│   ├── style.css            # Custom styling
│   ├── app.js               # Form handling, API calls, localStorage
│   ├── nginx.conf           # Static file serving + GZIP config
│   └── Dockerfile           # Nginx Alpine image
│
├── .github/
│   └── workflows/
│       └── ci.yml           # 5-stage CI/CD pipeline
│
├── docs/img/
│   └── banner-img.png       # README banner
│
├── docker-compose.yml       # Local development orchestration
└── README.md
```

---

## Future Roadmap

### Planned Features
- User authentication and personal dashboards
- Custom domains support
- Advanced analytics dashboard
- API rate limiting
- Link preview generation

### Infrastructure
- Kubernetes migration
- Multi-region deployment
- Database read replicas
- Advanced cache warming strategies

---

## Contributing

This is a portfolio project demonstrating production-grade DevOps practices. The codebase serves as a reference implementation for:
- Modern Python async web services (FastAPI)
- Docker containerization and multi-stage builds
- 5-stage CI/CD with automated security scanning
- Observability with Prometheus and Grafana
- Production deployment with Traefik and Docker

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Author

**Kay Alchemist**

[![GitHub](https://img.shields.io/badge/@alchemistkay-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/alchemistkay)
[![LinkedIn](https://img.shields.io/badge/Kwaku_Danso-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kwaku-danso-366196120)

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Last updated: March 2026</sub>
</p>
