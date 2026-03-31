#!/bin/bash

set -e

# Configuration
PROJECT_DIR="/home/deployer/url-shortener"
BACKUP_DIR="/home/deployer/backups"
REGISTRY="ghcr.io/alchemistkay/url-shortener"
LOG_FILE="/home/deployer/deployments/deploy.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

# Rollback function
rollback_api() {
    error "Rolling back API to previous version..."

    # Stop the failed container
    docker-compose stop api
    docker-compose rm -f api

    # Re-tag old image as :latest (this is the key!)
    docker tag "$OLD_API_IMAGE" "${REGISTRY}/backend:latest"

    # Start with the old image
    docker-compose up -d api

    # Wait for rollback to complete
    sleep 15

    # Check if rollback succeeded with retries
    MAX_ROLLBACK_RETRIES=30
    ROLLBACK_RETRY=0

    while [ $ROLLBACK_RETRY -lt $MAX_ROLLBACK_RETRIES ]; do
        if docker-compose exec -T api curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
            log "Rollback successful - API is healthy with old version"
            return 0
        fi
        ROLLBACK_RETRY=$((ROLLBACK_RETRY + 1))
        echo -n "."
        sleep 2
    done

    error "Rollback failed - API still unhealthy after rollback"
    docker-compose logs --tail=50 api
    return 1

}

# Create directories
mkdir -p "$BACKUP_DIR"
mkdir -p "$PROJECT_DIR"

log "=========================================="
log "Starting deployment..."
log "=========================================="

cd "$PROJECT_DIR"

# Debug: Show environment
log "DEBUG: POSTGRES_PASSWORD is set: $([ -n "$POSTGRES_PASSWORD" ] && echo 'YES' || echo 'NO')"
log "DEBUG: REDIS_PASSWORD is set: $([ -n "$REDIS_PASSWORD" ] && echo 'YES' || echo 'NO')"

# Manage environment configuration
log "Managing environment configuration..."
if [ -n "$POSTGRES_PASSWORD" ] && [ -n "$REDIS_PASSWORD" ]; then
    log "Creating .env file from CI secrets..."
    cat > .env << EOF
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
REDIS_PASSWORD=${REDIS_PASSWORD}
EOF
    chmod 600 .env
    log ".env file created/updated successfully"
else
    log "No passwords provided from CI, checking for existing .env..."
    if [ ! -f .env ]; then
        error ".env file not found and no passwords provided from CI"
        exit 1
    fi
    log "Using existing .env file"
fi

# Backup current state
log "Creating backup..."
BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"
docker-compose ps > "${BACKUP_DIR}/${BACKUP_NAME}/containers.txt" 2>&1 || true
cp .env "${BACKUP_DIR}/${BACKUP_NAME}/.env.backup" 2>&1 || true

# Get CURRENT running image ID (before pull)
OLD_API_IMAGE=$(docker inspect urlshortener-api --format='{{.Image}}' 2>/dev/null || echo "none")
OLD_FRONTEND_IMAGE=$(docker inspect urlshortener-frontend --format='{{.Image}}' 2>/dev/null || echo "none")

log "Current API image ID: ${OLD_API_IMAGE}"
log "Current Frontend image ID: ${OLD_FRONTEND_IMAGE}"

# Pull latest images from registry
log "Pulling latest images from GHCR..."
if ! docker pull "${REGISTRY}/backend:latest"; then
    error "Failed to pull backend image"
    exit 1
fi

if ! docker pull "${REGISTRY}/frontend:latest"; then
    error "Failed to pull frontend image"
    exit 1
fi

# Get NEW image IDs (after pull)
NEW_API_IMAGE=$(docker images "${REGISTRY}/backend:latest" --format='{{.ID}}')
NEW_FRONTEND_IMAGE=$(docker images "${REGISTRY}/frontend:latest" --format='{{.ID}}')

log "New API image ID: ${NEW_API_IMAGE}"
log "New Frontend image ID: ${NEW_FRONTEND_IMAGE}"

# Check if images actually changed
if [ "$OLD_API_IMAGE" = "sha256:$NEW_API_IMAGE" ]; then
    log "API image unchanged, skipping API deployment"
    API_UPDATED=false
else
    log "API image changed, will deploy new version"
    API_UPDATED=true
fi

# Restart API with new image
if [ "$API_UPDATED" = true ]; then
    log "Restarting API container..."
    docker-compose up -d api

    # Wait for API to be healthy
    log "Waiting for API health check..."
    MAX_RETRIES=60
    RETRY_COUNT=0

    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
	 # Check inside container (no port exposure needed)
        if docker-compose exec -T api curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
            log "API is healthy with new image!"
            break
        fi

        RETRY_COUNT=$((RETRY_COUNT + 1))

        if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
            error "API health check failed after ${MAX_RETRIES} attempts"

            # Attempt rollback
            if rollback_api; then
                error "Deployment failed but rollback successful"
                exit 1
            else
                error "Deployment AND rollback both failed - manual intervention required!"
                error "Old image ID: ${OLD_API_IMAGE}"
                exit 2
            fi
        fi

        echo -n "."
        sleep 2
    done
fi

# Restart Frontend
log "Restarting Frontend container..."
docker-compose up -d frontend

# Wait for frontend
sleep 5

# Final health checks
log "Running final health checks..."
if ! docker-compose exec -T api curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    error "Final API health check failed"
    exit 1
fi

if ! docker-compose exec -T frontend curl -sf http://localhost:80/ > /dev/null 2>&1; then
    error "Final frontend check failed"
    exit 1
fi

# Cleanup old images (keep last 3)
log "Cleaning up old images..."
docker images "${REGISTRY}/backend" --format '{{.ID}}' | tail -n +4 | xargs -r docker rmi -f 2>/dev/null || true
docker images "${REGISTRY}/frontend" --format '{{.ID}}' | tail -n +4 | xargs -r docker rmi -f 2>/dev/null || true

# Show running containers
log "Deployment successful! Running containers:"
docker-compose ps

log "=========================================="
log "Deployment completed successfully!"
log "=========================================="