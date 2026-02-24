# main.py - Our URL Shortener API

# ============================================
# IMPORTS
# ============================================

from fastapi import FastAPI, HTTPException, Depends, Request, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from cache import (cache_url, get_cached_url,get_cache_stats,test_connection)
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_fastapi_instrumentator import Instrumentator
import os

# Our own modules
from database import engine, Base, get_db
from models import URL, Click
from schemas import URLCreate, URLResponse, StatsResponse
from helpers import generate_short_code, is_expired

# ============================================
# CREATE TABLES
# ============================================

# This creates tables if they don't exist
# Safe to run multiple times (won't recreate)
Base.metadata.create_all(bind=engine)

# CUSTOM METRICS - Add after imports, before app creation
# Counters (always increase)
urls_created_total = Counter(
    'urlshortener_urls_created_total',
    'Total number of URLs created',
    ['is_custom']
)

redirects_total = Counter(
    'urlshortener_redirects_total',
    'Total number of redirects',
    ['short_code']
)

cache_operations = Counter(
    'urlshortener_cache_operations_total',
    'Total cache operations',
    ['operation', 'result']
)

# Gauges (can go up or down)
active_urls_gauge = Gauge(
    'urlshortener_active_urls',
    'Number of active URLs in database'
)

database_connections = Gauge(
    'urlshortener_database_connections',
    'Number of active database connections'
)

# Histograms (track distributions)
redirect_duration = Histogram(
    'urlshortener_redirect_duration_seconds',
    'Time spent processing redirects',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

# Info
app_info = Info('urlshortener_app', 'Application information')

app_info.info({
    'version': '1.0.0',
    'environment': 'production'
})

# ============================================
# CREATE APP
# ============================================

app = FastAPI(
    title="K4sCloud URL Shortener",
    description="Shorten URLs and track clicks",
    version="1.0.0",
    docs_url="/api/v1/docs",      
    redoc_url="/api/v1/redoc",    
    openapi_url="/api/v1/openapi.json"
)

# IMMEDIATELY add CORS (before any @app.get or @app.post!)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://short.k4scloud.com",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# CREATE API ROUTER WITH /api/v1 PREFIX
# ============================================

api_v1_router = APIRouter(prefix="/api/v1")

# Base URL for our short links
# Read from environment variable
BASE_URL = os.getenv("BASE_URL", "https://short.k4scloud.com")


# Instrument FastAPI
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


# ==================================================================================
# CREATE API ROUTER WITH /api/v1 PREFIX
# ==================================================================================

# ============================================
# ROOT ENDPOINT
# ============================================

@app.get("/")
def root():
    """API information"""
    return {
        "app": "K4sCloud URL Shortener",
        "version": "1.0.0",
        "api": "/api/v1",
        "endpoints": {
            "shorten": "POST /api/v1/shorten",
            "redirect": "GET /{short_code}",
            "stats": "GET /api/v1/stats/{short_code}"
        },
        "docs": "/api/v1/docs"
    }

# ============================================
# REDIRECT ENDPOINT
# ============================================

@app.get("/{short_code}")  # ← Must be @app NOT @api_v1_router
def redirect_url(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):

    """Redirect short URL to original URL"""

    # START TIMER
    import time
    start_time = time.time()
    
    # Reserved words
    RESERVED_WORDS = [
        "api", "health", "docs", "redoc", 
        "openapi.json", "shorten", "stats", "cache"
    ]
    if short_code in RESERVED_WORDS:
        raise HTTPException(status_code=404, detail="Not found")
    
    # Check cache first
    cached_url = get_cached_url(short_code)
    
    if cached_url:
        # TRACK CACHE HIT
        cache_operations.labels(operation='get', result='hit').inc()

        url_record = db.query(URL).filter(
            URL.short_code == short_code
        ).first()
        
        if url_record:
            click = Click(
                url_id=url_record.id,
                user_agent=request.headers.get("user-agent"),
                referer=request.headers.get("referer")
            )
            db.add(click)
            url_record.clicks += 1
            db.commit()

        # TRACK REDIRECT
        redirects_total.labels(short_code=short_code).inc()
        
        # RECORD DURATION
        redirect_duration.observe(time.time() - start_time)
        
        return RedirectResponse(url=cached_url, status_code=307)
    
    # Cache miss - query database
    cache_operations.labels(operation='get', result='miss').inc()

    url_record = db.query(URL).filter(
        URL.short_code == short_code
    ).first()
    
    if not url_record:
        raise HTTPException(
            status_code=404,
            detail=f"Short URL '{short_code}' not found!"
        )
    
    if not url_record.is_active:
        raise HTTPException(
            status_code=410,
            detail="This URL has been deactivated!"
        )
    
    if is_expired(url_record.expires_at):
        raise HTTPException(
            status_code=410,
            detail="This URL has expired!"
        )
    
    # Cache for next time
    cache_url(short_code, url_record.original_url)
    
    # Record click
    click = Click(
        url_id=url_record.id,
        user_agent=request.headers.get("user-agent"),
        referer=request.headers.get("referer")
    )
    db.add(click)
    url_record.clicks += 1
    db.commit()

    # TRACK REDIRECT
    redirects_total.labels(short_code=short_code).inc()
    
    # RECORD DURATION
    redirect_duration.observe(time.time() - start_time)
    
    return RedirectResponse(
        url=url_record.original_url,
        status_code=307
    )

# =================================================================================
# API v1 ENDPOINTS (with prefix)
# =================================================================================

# ============================================
# HEALTH CHECK ENDPOINT
# ============================================

@api_v1_router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Simple health check.
    Used by Uptime Kuma to monitor our service!
    """

    # Check database
    try:
        # Use SQLAlchemy text() for raw SQL
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        print(f"Database health check failed: {e}")

    # Check Redis
    redis_status = "healthy" if test_connection() else "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded",
        "timestamp": datetime.now(timezone.utc),
        "dependencies": {
            "database": db_status,
            "cache": redis_status
        }
    }

# ============================================
# SHORTEN ENDPOINT
# ============================================

@api_v1_router.post("/shorten", response_model=URLResponse)
def shorten_url(
    # 'data' comes from request body (JSON)
    # FastAPI automatically validates using URLCreate schema
    data: URLCreate,

    # 'db' is injected by FastAPI using get_db()
    # This gives us a database session
    db: Session = Depends(get_db)
):

    """
    Shorten a URL.

    - Takes a long URL
    - Optionally accepts custom slug
    - Optionally accepts expiry hours
    - Returns shortened URL
    """

    # ── STEP 1: Convert URL to string ──────
    # Pydantic's HttpUrl is an object, we need string
    original_url = str(data.original_url)

    # ── STEP 2: Handle custom slug ─────────
    if data.custom_slug:
        # Check if custom slug already taken
        existing = db.query(URL).filter(
            URL.short_code == data.custom_slug
        ).first()

        # If found, someone already has this slug!
        if existing:
            # HTTPException sends error response to client
            # 400 = Bad Request (client's fault)
            raise HTTPException(
                status_code=400,
                detail=f"Slug '{data.custom_slug}' is already taken!"
            )

        # Use the custom slug
        short_code = data.custom_slug
        is_custom = True

    else:
        # ── STEP 3: Generate unique short code ─
        # Keep trying until we find one that's not taken
        max_attempts = 10
        attempts = 0

        while attempts < max_attempts:
            # Generate a random code
            short_code = generate_short_code()

            # Check if it exists in database
            existing = db.query(URL).filter(
                URL.short_code == short_code
            ).first()

            # If not found, we can use it!
            if not existing:
                break

            attempts += 1

        # If we couldn't find unique code after 10 tries
        if attempts == max_attempts:
            raise HTTPException(
                status_code=500,
                detail="Could not generate unique code. Try again!"
            )

        is_custom = False

    # ── STEP 4: Calculate expiry ───────────
    expires_at = None

    if data.expires_in_hours:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=data.expires_in_hours)

    # ── STEP 5: Save to database ───────────
    # Create URL object (Python)
    url_record = URL(
        original_url=original_url,
        short_code=short_code,
        is_custom=is_custom,
        expires_at=expires_at,
        clicks=0,
        is_active=True
    )

    # Add to session
    db.add(url_record)

    # Commit to database (actually saves!)
    db.commit()

    # Refresh to get auto-set values (id, created_at)
    db.refresh(url_record)

    # ── STEP 6: Build response ─────────────
    # Construct the full short URL
    short_url = f"{BASE_URL}/{short_code}"

    # -------Metrics scrapping ----------------
    urls_created_total.labels(is_custom=str(is_custom)).inc()
    
    # Update gauge
    active_count = db.query(URL).filter(URL.is_active).count()
    active_urls_gauge.set(active_count)

    # Return response matching URLResponse schema
    return URLResponse(
        short_code=url_record.short_code,
        short_url=short_url,
        original_url=url_record.original_url,
        created_at=url_record.created_at,
        expires_at=url_record.expires_at,
        clicks=url_record.clicks
    )


# ============================================
# STATS ENDPOINT
# ============================================

@api_v1_router.get("/stats/{short_code}", response_model=StatsResponse)
def get_stats(
    short_code: str,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a short URL.

    Returns click count and other details.
    """

    # Find URL
    url_record = db.query(URL).filter(
        URL.short_code == short_code
    ).first()

    # Not found?
    if not url_record:
        raise HTTPException(
            status_code=404,
            detail=f"Short URL '{short_code}' not found!"
        )

    return StatsResponse(
        short_code=url_record.short_code,
        original_url=url_record.original_url,
        total_clicks=url_record.clicks,
        created_at=url_record.created_at,
        expires_at=url_record.expires_at,
        is_active=url_record.is_active
    )

@api_v1_router.get("/cache/stats")
def cache_statistics():
    """
    View Redis cache statistics.
    Shows hits, misses, memory usage.
    """
    return get_cache_stats()

# ============================================
# MOUNT THE API v1 ROUTER
# ============================================

app.include_router(api_v1_router)