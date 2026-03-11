# K4sCloud URL Shortener

Production-grade URL shortening service with comprehensive observability and automated CI/CD pipeline.

## Overview

A high-performance URL shortening service built with FastAPI, PostgreSQL, and Redis. Features full monitoring stack with Prometheus and Grafana, containerized deployment with Docker, and complete CI/CD automation using GitHub Actions.

**Live Demo:** https://short.k4scloud.com

## Architecture

### Technology Stack

**Backend**
- FastAPI (Python 3.11)
- PostgreSQL 17 (data persistence)
- Redis 7 (caching layer)
- Pydantic (data validation)

**Frontend**
- HTML5, CSS3, JavaScript
- Modern responsive design
- Glass morphism UI

**Infrastructure**
- Docker & Docker Compose
- Traefik (reverse proxy with SSL)
- Nginx (static file serving)

**Observability**
- Prometheus (metrics collection)
- Grafana (visualization)
- Uptime Kuma (availability monitoring)
- Custom application metrics

**CI/CD**
- GitHub Actions (5-stage pipeline)
- Automated testing (unit + integration)
- Security scanning (SAST, SCA, container vulnerabilities)
- Automatic deployment to production
- Rollback on failure

### System Architecture
```
Internet (HTTPS)
    |
    v
Traefik (Reverse Proxy + SSL Termination)
    |
    +---> Frontend (Nginx)
    |       |
    |       +---> index.html
    |
    +---> API (FastAPI)
            |
            +---> PostgreSQL (persistent storage)
            |
            +---> Redis (cache layer)
```

## Features

### Core Functionality
- URL shortening with auto-generated codes
- Custom slug support
- Click tracking and analytics
- QR code generation
- Cache-optimized redirects
- RESTful API with OpenAPI documentation

### Operational Features
- Health check endpoints
- Prometheus metrics export
- Cache statistics
- Database connection pooling
- Automatic failover

### Performance
- Sub-5ms response time (cache hits)
- 50-80% cache hit ratio
- Horizontal scalability ready
- Zero-downtime deployments

## API Documentation

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
  "custom_slug": "optional-custom-slug"
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

**Interactive API Documentation**
- Swagger UI: `https://short.k4scloud.com/api/v1/docs`
- ReDoc: `https://short.k4scloud.com/api/v1/redoc`

## Deployment

### Prerequisites
- Docker & Docker Compose
- PostgreSQL 17
- Redis 7
- Traefik reverse proxy

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

### Local Development
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

### Production Deployment

Production deployment is fully automated via GitHub Actions:

1. Push code to main branch
2. CI/CD pipeline runs automatically:
   - Stage 1: Security scanning
   - Stage 2: Build and test
   - Stage 3: Integration tests
   - Stage 4: Push images to GHCR
   - Stage 5: Deploy to production
3. Automatic rollback on failure

## CI/CD Pipeline

### Pipeline Stages

**Stage 1: Source Security**
- Secret scanning (TruffleHog)
- SAST with CodeQL
- Code linting (Ruff, Black)
- Dependency vulnerability scanning

**Stage 2: Build & Test**
- Unit tests with pytest
- Code coverage (80% minimum)
- Docker image builds
- SBOM generation
- Container vulnerability scanning (Trivy)

**Stage 3: Integration Tests**
- 13 comprehensive API tests
- Real PostgreSQL and Redis instances
- Health check validation
- Cache functionality testing

**Stage 4: Release**
- Push images to GitHub Container Registry
- Multi-tag strategy (latest, SHA, semantic version)
- Image signing

**Stage 5: Deploy**
- Automated deployment to production VPS
- Rolling restart with health checks
- Automatic rollback on failure
- Zero-downtime deployment

### Pipeline Duration
Average: 10-15 minutes from commit to production

## Monitoring

### Metrics Collected

**Application Metrics**
- Request rate (requests/second)
- Response time (p95, p99)
- Error rate
- Status code distribution

**Business Metrics**
- URLs shortened (total and rate)
- Redirects per minute
- Cache hit rate
- Most popular URLs

**Infrastructure Metrics**
- Container health
- Database connections
- Cache size
- Resource utilization

### Grafana Dashboards

Access dashboards at your Grafana instance:
- URL Shortener Application Metrics
- Docker & Host Monitoring
- Traefik Traffic Analysis

## Performance Optimization

### Caching Strategy
- Cache-aside pattern
- TTL: 3600 seconds
- Redis for hot data
- PostgreSQL for persistence

### Database Optimization
- Indexed short_code column
- Connection pooling
- Prepared statements

### Container Optimization
- Multi-stage Docker builds
- Optimized base images
- Final image size: 193MB (40% reduction from initial)

## Security

### Implemented Measures
- HTTPS-only with automatic SSL renewal
- Input validation with Pydantic
- SQL injection prevention (ORM)
- Rate limiting ready
- Security headers
- Regular dependency updates
- Automated vulnerability scanning

### Network Security
- Firewalled VPS
- Docker network isolation
- Traefik as single entry point
- Non-root container users

## Project Structure
```
url-shortener/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── cache.py             # Redis caching
│   ├── helpers.py           # Utility functions
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Container image
│   └── tests/               # Test suite
│       ├── test_basic.py
│       └── integration/
│
├── frontend/
│   ├── index.html           # Main page
│   ├── style.css            # Styling
│   ├── app.js               # Frontend logic
│   ├── nginx.conf           # Nginx configuration
│   └── Dockerfile           # Container image
│
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/CD pipeline
│
├── docker-compose.yml       # Local development
└── README.md
```

## Metrics & Results

### Performance
- Response time: <5ms (cache hits), <50ms (cache misses)
- Uptime: 99.9%+
- Cache hit ratio: 50-80%
- Container image size: 193MB

### Development Metrics
- Test coverage: 85%+
- CI/CD success rate: 100%
- Deployment frequency: Multiple per day
- Mean time to recovery: <2 minutes

## Future Enhancements

### Planned Features
- User authentication and dashboards
- Link expiration
- Custom domains
- Analytics dashboard
- API rate limiting
- Link preview generation

### Infrastructure Improvements
- Kubernetes migration
- Multi-region deployment
- Database replication
- Advanced caching strategies

## Contributing

This is a portfolio project demonstrating production-grade DevOps practices. While not actively seeking contributions, the codebase serves as a reference implementation for:
- Modern Python web applications
- Docker containerization
- CI/CD automation
- Observability implementation
- Production deployment patterns

## License

MIT License - see LICENSE file for details.

## Author

**Kay Alchemist**
- GitHub: [@alchemistkay](https://github.com/alchemistkay)
- LinkedIn: [Kwaku Danso](https://www.linkedin.com/in/kwaku-danso-366196120)
- Portfolio: []

## Acknowledgments

Built as a comprehensive learning project to demonstrate:
- Full-stack development capabilities
- DevOps and SRE best practices
- Production infrastructure design
- Automated deployment pipelines
- Enterprise-grade monitoring

---

**Last Updated:** March 2026
