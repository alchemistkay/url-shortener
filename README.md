# K4sCloud URL Shortener

A production-ready URL shortening service built with FastAPI, PostgreSQL, Redis, and Docker.

##  Features
- Custom short URLs
- Click tracking & analytics
- Redis caching for performance
- Beautiful modern UI
- RESTful API with versioning
- Docker containerized
- SSL/TLS enabled
- Monitored with Uptime Kuma

##  Tech Stack
- **Backend:** FastAPI, Python 3.11
- **Database:** PostgreSQL 17
- **Cache:** Redis 7
- **Frontend:** HTML5, CSS3, JavaScript
- **Web Server:** Nginx
- **Reverse Proxy:** Traefik
- **Containerization:** Docker
- **Monitoring:** Uptime Kuma

##  Architecture
                    Internet
                       ↓
                  Port 443 (HTTPS)
                       ↓
              ┌────────────────┐
              │    Traefik     │ ← Reverse Proxy + SSL
              │  (Container)   │
              └────────┬───────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ↓              ↓              ↓
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│   Frontend   │ │   API    │ │  Redirects   │
│   (Nginx)    │ │ FastAPI  │ │  /{code}     │
│  Container   │ │Container │ │              │
└──────────────┘ └────┬─────┘ └──────────────┘
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
  ┌──────────┐ ┌──────────┐ ┌──────────┐
  │PostgreSQL│ │  Redis   │ │  Uptime  │
  │(Storage) │ │ (Cache)  │ │   Kuma   │
  └──────────┘ └──────────┘ └──────────┘

## 🔗 Live Demo
https://short.k4scloud.com