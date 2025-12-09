# Deployment Documentation

## Overview

This document covers deployment strategies for the FastAPI backend application with Clean Architecture, including containerization, environment management, monitoring, and production best practices.

## Architecture for Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer                            │
│                   (nginx / cloud LB)                         │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│   FastAPI App (Pod 1)   │     │   FastAPI App (Pod 2)   │
│   - Presentation Layer  │     │   - Presentation Layer  │
│   - Application Layer   │     │   - Application Layer   │
│   - Domain Layer        │     │   - Domain Layer        │
│   - Infrastructure      │     │   - Infrastructure      │
└─────────────────────────┘     └─────────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         ▼                                         ▼
┌─────────────────────┐               ┌─────────────────────┐
│     PostgreSQL      │               │      MongoDB        │
│   (User Entity)     │               │   (Log Entity)      │
└─────────────────────┘               └─────────────────────┘
```

## Deployment Options

### 1. Docker Compose (Single Server)

Simple deployment for small scale or development.

### 2. Kubernetes (Production)

Scalable deployment for high-availability production environments.

### 3. Cloud Platform Deployment

Platform-specific deployment for AWS, GCP, Azure.

## Docker Compose Deployment

### Production Configuration

```yaml
# docker-compose.production.yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: .docker/production/python/Dockerfile
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - POSTGRE_DATABASE_URL=postgresql+asyncpg://admin:${DB_PASSWORD}@postgresql:5432/app_db
      - MONGODB_URL=mongodb://mongodb:27017
      - MONGODB_DB_NAME=app_db
    depends_on:
      postgresql:
        condition: service_healthy
      mongodb:
        condition: service_healthy
    ports:
      - "8080:8080"
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health-check"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgresql:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=app_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d app_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  mongodb:
    image: mongo:7.0
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD}
    volumes:
      - mongo_data:/data/db
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  mongo_data:

networks:
  app-network:
    driver: bridge
```

### Environment Variables

```env
# .env.production
APP_NAME=backend-fastapi-app
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# PostgreSQL
POSTGRE_DATABASE_URL=postgresql+asyncpg://admin:secure_password@postgresql:5432/app_db
DB_PASSWORD=secure_password

# MongoDB
MONGODB_URL=mongodb://admin:mongo_password@mongodb:27017
MONGODB_DB_NAME=app_db
MONGO_PASSWORD=mongo_password

# Server
HOST=0.0.0.0
PORT=8080
RELOAD=false

# Security
SECRET_KEY=your-super-secret-key-here
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

### Production Deployment Commands

```bash
# Build production images
make prod-build

# Start production services
make prod-up

# Check service status
make status

# View logs
make prod-logs

# Stop services
make prod-down
```

## Kubernetes Deployment

### Namespace Configuration

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: fastapi-app
```

### ConfigMap and Secrets

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: fastapi-app
data:
  APP_NAME: "backend-fastapi-app"
  ENVIRONMENT: "production"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  HOST: "0.0.0.0"
  PORT: "8080"
  RELOAD: "false"
  MONGODB_DB_NAME: "app_db"

---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: fastapi-app
type: Opaque
stringData:
  POSTGRE_DATABASE_URL: "postgresql+asyncpg://admin:password@postgresql:5432/app_db"
  MONGODB_URL: "mongodb://admin:password@mongodb:27017"
  SECRET_KEY: "your-super-secret-key"
```

### PostgreSQL Deployment

```yaml
# k8s/postgresql.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgresql
  namespace: fastapi-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgresql
  template:
    metadata:
      labels:
        app: postgresql
    spec:
      containers:
      - name: postgresql
        image: postgres:16-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_USER
          value: "admin"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: postgres-password
        - name: POSTGRES_DB
          value: "app_db"
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: postgresql
  namespace: fastapi-app
spec:
  selector:
    app: postgresql
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432
  type: ClusterIP
```

### MongoDB Deployment

```yaml
# k8s/mongodb.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb
  namespace: fastapi-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:7.0
        ports:
        - containerPort: 27017
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          value: "admin"
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: mongo-password
        volumeMounts:
        - name: mongo-storage
          mountPath: /data/db
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: mongo-storage
        persistentVolumeClaim:
          claimName: mongo-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: mongodb
  namespace: fastapi-app
spec:
  selector:
    app: mongodb
  ports:
    - protocol: TCP
      port: 27017
      targetPort: 27017
  type: ClusterIP
```

### Application Deployment

```yaml
# k8s/app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
  namespace: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
      - name: fastapi-app
        image: your-registry/fastapi-app:latest
        ports:
        - containerPort: 8080
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health-check
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health-check
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-app
  namespace: fastapi-app
spec:
  selector:
    app: fastapi-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

### Ingress Configuration

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fastapi-app-ingress
  namespace: fastapi-app
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: fastapi-app-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: fastapi-app
            port:
              number: 80
```

## Database Migrations in Production

### Running Migrations

```bash
# In Docker
docker exec -it fastapi-app poetry run alembic upgrade head

# In Kubernetes
kubectl exec -it deployment/fastapi-app -n fastapi-app -- poetry run alembic upgrade head
```

### Migration Strategy

1. **Before Deployment**: Run migrations before deploying new app version
2. **Backward Compatible**: Ensure migrations are backward compatible
3. **Rollback Plan**: Always have a rollback migration ready

## Health Checks

### Application Health Check

The `/health-check` endpoint provides comprehensive health status:

```python
# app/presentation/api/system.py
@router.get("/health-check")
async def health_check():
    health = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": get_app_version(),
        "checks": {}
    }

    # PostgreSQL check
    try:
        await check_postgresql_connection()
        health["checks"]["postgresql"] = "healthy"
    except Exception as e:
        health["checks"]["postgresql"] = f"unhealthy: {str(e)}"
        health["status"] = "unhealthy"

    # MongoDB check
    try:
        await check_mongodb_connection()
        health["checks"]["mongodb"] = "healthy"
    except Exception as e:
        health["checks"]["mongodb"] = f"unhealthy: {str(e)}"
        health["status"] = "unhealthy"

    return health
```

## Monitoring and Logging

### Logging Configuration

```python
# app/infrastructure/configs/logging.py
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json" if ENVIRONMENT == "production" else "default",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["console"],
    },
}
```

### Prometheus Metrics (Future)

```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)

    return response
```

## Backup and Recovery

### PostgreSQL Backup

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgresql"

# Create backup
pg_dump -h postgresql -U admin -d app_db > "$BACKUP_DIR/backup_$DATE.sql"

# Compress
gzip "$BACKUP_DIR/backup_$DATE.sql"

# Clean old backups (keep last 7 days)
find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete
```

### MongoDB Backup

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mongodb"

# Create backup
mongodump --uri="mongodb://admin:password@mongodb:27017/app_db" --out="$BACKUP_DIR/$DATE"

# Compress
tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" "$BACKUP_DIR/$DATE"

# Clean up
rm -rf "$BACKUP_DIR/$DATE"
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
```

## Security Configuration

### SSL/TLS Setup

```nginx
# nginx.conf
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/ssl/certs/api.yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/api.yourdomain.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://fastapi-app:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Security Headers

Security headers are automatically added by middleware:

```python
# app/infrastructure/web/middleware.py
class SecurityHeadersMiddleware:
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
```

## Scaling

### Horizontal Scaling

```bash
# Kubernetes
kubectl scale deployment fastapi-app --replicas=5 -n fastapi-app

# Auto-scaling
kubectl autoscale deployment fastapi-app --cpu-percent=70 --min=3 --max=10 -n fastapi-app
```

### Database Scaling

**PostgreSQL**: Consider read replicas for read-heavy workloads
**MongoDB**: Can be scaled with replica sets

## Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   kubectl logs deployment/fastapi-app -n fastapi-app
   docker-compose logs fastapi-app
   ```

2. **Database connection issues**
   ```bash
   # Check database connectivity
   kubectl exec -it deployment/fastapi-app -n fastapi-app -- python -c "
   from app.infrastructure.persistence.postgresql.database import postgres_manager
   import asyncio
   asyncio.run(postgres_manager.connect())
   "
   ```

3. **Memory issues**
   ```bash
   kubectl top pods -n fastapi-app
   docker stats
   ```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: make ci

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push Docker image
        run: |
          docker build -t ${{ secrets.REGISTRY }}/fastapi-app:${{ github.sha }} .
          docker push ${{ secrets.REGISTRY }}/fastapi-app:${{ github.sha }}
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/fastapi-app \
            fastapi-app=${{ secrets.REGISTRY }}/fastapi-app:${{ github.sha }} \
            -n fastapi-app
```

This comprehensive deployment documentation covers all aspects of deploying and maintaining the FastAPI Clean Architecture application in production environments.
