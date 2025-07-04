# Deployment Documentation

## Overview

This document covers deployment strategies for the FastAPI backend application, including containerization, environment management, monitoring, and production best practices.

## Deployment Options

### 1. Docker Compose (Recommended for Small Scale)

Simple deployment using Docker Compose for single-server deployments.

### 2. Kubernetes (Recommended for Production)

Scalable deployment using Kubernetes for high-availability production environments.

### 3. Cloud Platform Deployment

Platform-specific deployment guides for major cloud providers.

## Docker Compose Deployment

### Production Configuration

```yaml
# docker-compose.production.yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - MONGODB_URL=mongodb://mongodb:27017
      - MONGODB_DB_NAME=app_db
    depends_on:
      - mongodb
    ports:
      - "8080:8080"
    restart: unless-stopped
    networks:
      - app-network

  mongodb:
    image: mongo:7.0
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=secure_password
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"
    restart: unless-stopped
    networks:
      - app-network

volumes:
  mongodb_data:

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

# Database
MONGODB_URL=mongodb://admin:secure_password@mongodb:27017/app_db?authSource=admin
MONGODB_DB_NAME=app_db

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

---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: fastapi-app
type: Opaque
data:
  MONGODB_URL: bW9uZ29kYjovL21vbmdvZGI6MjcwMTcvYXBwX2Ri  # base64 encoded
  SECRET_KEY: eW91ci1zdXBlci1zZWNyZXQta2V5LWhlcmU=  # base64 encoded
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
              name: mongodb-secret
              key: password
        volumeMounts:
        - name: mongodb-storage
          mountPath: /data/db
      volumes:
      - name: mongodb-storage
        persistentVolumeClaim:
          claimName: mongodb-pvc

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

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongodb-pvc
  namespace: fastapi-app
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
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
        env:
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: MONGODB_URL
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: SECRET_KEY
        envFrom:
        - configMapRef:
            name: app-config
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

## Cloud Platform Deployment

### AWS ECS Deployment

```json
{
  "family": "fastapi-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "fastapi-app",
      "image": "your-ecr-registry/fastapi-app:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        },
        {
          "name": "DEBUG",
          "value": "false"
        }
      ],
      "secrets": [
        {
          "name": "MONGODB_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:mongodb-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/fastapi-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/health-check || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

### Google Cloud Run

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/fastapi-app:$COMMIT_SHA', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/fastapi-app:$COMMIT_SHA']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'fastapi-app'
      - '--image'
      - 'gcr.io/$PROJECT_ID/fastapi-app:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
```

### Azure Container Instances

```yaml
# azure-container-instance.yaml
apiVersion: 2019-12-01
location: eastus
name: fastapi-app
properties:
  containers:
  - name: fastapi-app
    properties:
      image: your-acr.azurecr.io/fastapi-app:latest
      resources:
        requests:
          cpu: 1.0
          memoryInGb: 2.0
      ports:
      - port: 8080
        protocol: TCP
      environmentVariables:
      - name: ENVIRONMENT
        value: production
      - name: DEBUG
        value: false
      - name: MONGODB_URL
        secureValue: mongodb://mongodb:27017/app_db
  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
    ports:
    - protocol: tcp
      port: 8080
```

## Environment Management

### Development Environment

```bash
# Start development environment
make dev

# Environment variables
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
RELOAD=true
```

### Staging Environment

```bash
# Deploy to staging
docker-compose -f docker-compose.staging.yaml up -d

# Environment variables
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
RELOAD=false
```

### Production Environment

```bash
# Deploy to production
make prod-up

# Environment variables
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
RELOAD=false
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

    location / {
        proxy_pass http://fastapi-app:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Environment Secrets

```bash
# Create secrets
kubectl create secret generic app-secrets \
  --from-literal=mongodb-url="mongodb://admin:password@mongodb:27017/app_db" \
  --from-literal=secret-key="your-super-secret-key"

# Or using sealed secrets
echo -n "mongodb://admin:password@mongodb:27017/app_db" | base64
```

### Security Headers

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.yourdomain.com", "*.yourdomain.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Monitoring and Logging

### Application Monitoring

```python
# app/middleware/monitoring.py
from prometheus_client import Counter, Histogram, generate_latest
import time

REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)

    return response
```

### Logging Configuration

```python
# app/configs/logging.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
```

### Health Checks

```python
# app/routers/system.py
@router.get("/health-check")
async def health_check():
    """Comprehensive health check."""
    health = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": get_app_version(),
        "checks": {}
    }

    # Database health
    try:
        await User.find_one({})
        health["checks"]["database"] = "healthy"
    except Exception as e:
        health["checks"]["database"] = f"unhealthy: {str(e)}"
        health["status"] = "unhealthy"

    # Memory usage
    import psutil
    memory = psutil.virtual_memory()
    health["checks"]["memory"] = {
        "used_percent": memory.percent,
        "available_gb": round(memory.available / 1024**3, 2)
    }

    return health
```

## Backup and Recovery

### Database Backup

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="app_db"

# Create backup
mongodump --uri="mongodb://admin:password@mongodb:27017/$DB_NAME" --out="$BACKUP_DIR/$DATE"

# Compress backup
tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" "$BACKUP_DIR/$DATE"

# Clean up old backups (keep last 7 days)
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete
```

### Kubernetes Backup

```yaml
# k8s/backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: mongodb-backup
  namespace: fastapi-app
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: mongodb-backup
            image: mongo:7.0
            command:
            - /bin/bash
            - -c
            - |
              mongodump --uri="$MONGODB_URL" --out="/backup/$(date +%Y%m%d_%H%M%S)"
            env:
            - name: MONGODB_URL
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: MONGODB_URL
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

## Performance Optimization

### Application Optimization

```python
# app/configs/app.py
class AppSettings(BaseSettings):
    # Worker configuration
    workers: int = Field(default=4, ge=1, le=10)
    worker_class: str = "uvicorn.workers.UvicornWorker"
    max_requests: int = Field(default=1000, ge=100)
    max_requests_jitter: int = Field(default=100, ge=10)

    # Connection pooling
    mongodb_max_pool_size: int = Field(default=100, ge=10)
    mongodb_min_pool_size: int = Field(default=10, ge=1)
```

### Database Optimization

```python
# app/models/user.py
class User(BaseEntity):
    class Settings:
        indexes = [
            # Compound indexes for common queries
            IndexModel([("email", 1), ("deleted_at", 1)]),
            IndexModel([("username", 1), ("deleted_at", 1)]),
            IndexModel([("is_active", 1), ("created_at", -1)]),
            # Partial indexes for active users only
            IndexModel(
                [("email", 1)],
                partialFilterExpression={"deleted_at": None}
            ),
        ]
```

### Caching Strategy

```python
# app/services/cache.py
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='redis', port=6379, db=0)

def cache_result(expiry=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiry, json.dumps(result))
            return result
        return wrapper
    return decorator
```

## Continuous Deployment

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Build and push Docker image
        run: |
          docker build -t fastapi-app:${{ github.sha }} .
          docker tag fastapi-app:${{ github.sha }} ${{ secrets.ECR_REGISTRY }}/fastapi-app:${{ github.sha }}
          docker push ${{ secrets.ECR_REGISTRY }}/fastapi-app:${{ github.sha }}

      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster production --service fastapi-app --force-new-deployment
```

### Blue-Green Deployment

```bash
# Blue-Green deployment script
#!/bin/bash
NEW_VERSION=$1
CURRENT_VERSION=$(kubectl get deployment fastapi-app -o jsonpath='{.spec.template.spec.containers[0].image}')

echo "Deploying version: $NEW_VERSION"
echo "Current version: $CURRENT_VERSION"

# Update deployment with new version
kubectl set image deployment/fastapi-app fastapi-app=$NEW_VERSION

# Wait for rollout to complete
kubectl rollout status deployment/fastapi-app

# Run health checks
HEALTH_CHECK_URL="http://api.yourdomain.com/health-check"
for i in {1..10}; do
    if curl -f $HEALTH_CHECK_URL; then
        echo "Health check passed"
        break
    fi
    echo "Health check failed, retrying in 10s..."
    sleep 10
done

# If health checks fail, rollback
if [ $? -ne 0 ]; then
    echo "Deployment failed, rolling back..."
    kubectl rollout undo deployment/fastapi-app
    exit 1
fi

echo "Deployment successful!"
```

## Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   # Check logs
   kubectl logs deployment/fastapi-app
   docker-compose logs fastapi-app

   # Check resource limits
   kubectl describe pod <pod-name>
   ```

2. **Database connection issues**
   ```bash
   # Test database connectivity
   kubectl exec -it deployment/fastapi-app -- python -c "from app.configs.database import test_connection; test_connection()"
   ```

3. **Memory issues**
   ```bash
   # Check memory usage
   kubectl top pods
   docker stats
   ```

### Performance Issues

1. **Slow database queries**
   ```python
   # Enable query profiling
   db.set_profiling_level(2)
   db.system.profile.find().sort(ts: -1).limit(5)
   ```

2. **High CPU usage**
   ```bash
   # Check application metrics
   curl http://localhost:8080/metrics
   ```

### Scaling Issues

1. **Horizontal scaling**
   ```bash
   # Scale up replicas
   kubectl scale deployment fastapi-app --replicas=5

   # Auto-scaling
   kubectl autoscale deployment fastapi-app --cpu-percent=70 --min=3 --max=10
   ```

2. **Database scaling**
   ```bash
   # MongoDB replica set
   rs.initiate()
   rs.add("mongodb-secondary:27017")
   rs.add("mongodb-arbiter:27017", {arbiterOnly: true})
   ```

## Maintenance

### Regular Tasks

1. **Update dependencies**
   ```bash
   # Update Python packages
   poetry update

   # Update Docker images
   docker-compose pull
   ```

2. **Clean up old data**
   ```python
   # Clean up old soft-deleted records
   await User.find({
       "deleted_at": {"$lt": datetime.now() - timedelta(days=365)}
   }).delete()
   ```

3. **Backup verification**
   ```bash
   # Test backup restoration
   mongorestore --drop --uri="mongodb://test-server:27017/test_db" /backup/latest/
   ```

### Monitoring Alerts

```yaml
# alertmanager.yml
groups:
- name: fastapi-app
  rules:
  - alert: HighMemoryUsage
    expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage detected"

  - alert: DatabaseDown
    expr: up{job="mongodb"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "MongoDB is down"
```

This comprehensive deployment documentation covers all aspects of deploying and maintaining the FastAPI application in production environments.
