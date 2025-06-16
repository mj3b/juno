# Phase 1: Analytics Foundation Deployment Guide

## Overview

Phase 1 establishes the analytics foundation for JUNO, providing essential data extraction, analysis, and visualization capabilities. This phase creates the baseline metrics and team adoption necessary for subsequent agentic AI phases.

**Deployment Time**: 1-2 weeks  
**Complexity**: Low  
**Team Size**: 1-20 teams  
**Prerequisites**: Jira access, basic infrastructure

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Infrastructure Setup](#infrastructure-setup)
4. [Application Deployment](#application-deployment)
5. [Configuration](#configuration)
6. [Testing and Validation](#testing-and-validation)
7. [Monitoring and Observability](#monitoring-and-observability)
8. [Security Configuration](#security-configuration)
9. [Troubleshooting](#troubleshooting)
10. [Next Steps](#next-steps)

## Architecture Overview

### Phase 1 Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Phase 1: Analytics Foundation            │
├─────────────────────────────────────────────────────────────┤
│                    Web Dashboard (React)                    │
├─────────────────────────────────────────────────────────────┤
│                    API Gateway (FastAPI)                    │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│ Data        │ Analytics   │ Visualiz.   │ Query             │
│ Extractor   │ Engine      │ Engine      │ Processor         │
├─────────────┴─────────────┴─────────────┴───────────────────┤
│                    Database Layer                           │
│               PostgreSQL + Redis Cache                      │
├─────────────────────────────────────────────────────────────┤
│                 External Integrations                       │
│                 Jira API + Confluence                       │
└─────────────────────────────────────────────────────────────┘
```

### Core Services

| Service | Purpose | Technology | Port |
|---------|---------|------------|------|
| **Data Extractor** | Jira API integration and data normalization | Python/FastAPI | 8001 |
| **Analytics Engine** | Statistical analysis and trend detection | Python/Pandas | 8002 |
| **Visualization Engine** | Chart generation and dashboard rendering | Python/Plotly | 8003 |
| **Query Processor** | Natural language query interpretation | Python/NLP | 8004 |
| **Web Dashboard** | User interface and visualization | React/Vite | 3000 |
| **API Gateway** | Request routing and authentication | FastAPI | 8000 |

## Prerequisites

### System Requirements

**Minimum Infrastructure**:
- 2 CPU cores, 4GB RAM
- 50GB storage
- Network access to Jira instance

**Recommended Infrastructure**:
- 4 CPU cores, 8GB RAM
- 100GB SSD storage
- Load balancer for high availability

### Required Access

- **Jira Administrator Access**: For API token generation and webhook configuration
- **Infrastructure Access**: Deployment environment (Docker/Kubernetes)
- **DNS Management**: For custom domain configuration (optional)

### Software Dependencies

```bash
# Core runtime
Python 3.11+
Node.js 18+
PostgreSQL 14+
Redis 6+

# Container runtime (choose one)
Docker 20.10+
Kubernetes 1.24+
```

## Infrastructure Setup

### Option 1: Docker Compose (Recommended for Development)

1. **Create deployment directory**:
```bash
mkdir juno-phase1-deployment
cd juno-phase1-deployment
```

2. **Create docker-compose.yml**:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: juno_analytics
      POSTGRES_USER: juno
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  juno-analytics:
    image: juno/analytics:latest
    environment:
      - DATABASE_URL=postgresql://juno:${POSTGRES_PASSWORD}@postgres:5432/juno_analytics
      - REDIS_URL=redis://redis:6379
      - JIRA_BASE_URL=${JIRA_BASE_URL}
      - JIRA_API_TOKEN=${JIRA_API_TOKEN}
      - JIRA_EMAIL=${JIRA_EMAIL}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  juno-dashboard:
    image: juno/dashboard:latest
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - juno-analytics

volumes:
  postgres_data:
  redis_data:
```

3. **Create environment file**:
```bash
# .env
POSTGRES_PASSWORD=your_secure_password
JIRA_BASE_URL=https://your-company.atlassian.net
JIRA_API_TOKEN=your_jira_api_token
JIRA_EMAIL=your-email@company.com
```

### Option 2: Kubernetes (Recommended for Production)

1. **Create namespace**:
```bash
kubectl create namespace juno-analytics
```

2. **Deploy PostgreSQL**:
```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: juno-analytics
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14
        env:
        - name: POSTGRES_DB
          value: "juno_analytics"
        - name: POSTGRES_USER
          value: "juno"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: juno-analytics
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

3. **Deploy JUNO Analytics**:
```yaml
# juno-analytics-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: juno-analytics
  namespace: juno-analytics
spec:
  replicas: 2
  selector:
    matchLabels:
      app: juno-analytics
  template:
    metadata:
      labels:
        app: juno-analytics
    spec:
      containers:
      - name: juno-analytics
        image: juno/analytics:latest
        env:
        - name: DATABASE_URL
          value: "postgresql://juno:$(POSTGRES_PASSWORD)@postgres-service:5432/juno_analytics"
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: JIRA_BASE_URL
          valueFrom:
            configMapKeyRef:
              name: juno-config
              key: jira-base-url
        - name: JIRA_API_TOKEN
          valueFrom:
            secretKeyRef:
              name: jira-secret
              key: api-token
        - name: JIRA_EMAIL
          valueFrom:
            configMapKeyRef:
              name: juno-config
              key: jira-email
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: juno-analytics-service
  namespace: juno-analytics
spec:
  selector:
    app: juno-analytics
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
```

## Application Deployment

### Step 1: Clone Repository

```bash
git clone https://github.com/mj3b/juno.git
cd juno
```

### Step 2: Build Application Images

```bash
# Build analytics backend
cd juno-agent
docker build -t juno/analytics:latest .

# Build dashboard frontend
cd ../juno-dashboard
docker build -t juno/dashboard:latest .
```

### Step 3: Database Setup

```bash
# Run database migrations
docker run --rm \
  -e DATABASE_URL=postgresql://juno:password@localhost:5432/juno_analytics \
  juno/analytics:latest \
  python -m alembic upgrade head

# Create initial admin user
docker run --rm \
  -e DATABASE_URL=postgresql://juno:password@localhost:5432/juno_analytics \
  juno/analytics:latest \
  python -c "from src.auth import create_admin_user; create_admin_user('admin@company.com', 'secure_password')"
```

### Step 4: Deploy Services

**Docker Compose**:
```bash
docker-compose up -d
```

**Kubernetes**:
```bash
kubectl apply -f k8s/
```

## Configuration

### Jira Integration Setup

1. **Generate Jira API Token**:
   - Go to Jira → Profile → Personal Access Tokens
   - Create new token with read permissions
   - Copy token for configuration

2. **Configure Jira Connection**:
```bash
# Test Jira connectivity
curl -H "Authorization: Bearer ${JIRA_API_TOKEN}" \
     "${JIRA_BASE_URL}/rest/api/3/myself"
```

3. **Set up Jira Webhooks** (Optional for real-time updates):
```json
{
  "name": "JUNO Analytics Webhook",
  "url": "https://your-juno-instance.com/api/v1/webhooks/jira",
  "events": [
    "jira:issue_created",
    "jira:issue_updated",
    "jira:issue_deleted"
  ]
}
```

### Analytics Configuration

1. **Configure data extraction schedule**:
```yaml
# config/analytics.yaml
data_extraction:
  schedule: "0 */6 * * *"  # Every 6 hours
  batch_size: 1000
  projects:
    - "PROJ1"
    - "PROJ2"
  
analytics:
  retention_days: 365
  aggregation_intervals:
    - daily
    - weekly
    - monthly
```

2. **Set up custom metrics**:
```python
# config/custom_metrics.py
CUSTOM_METRICS = {
    "velocity_trend": {
        "calculation": "moving_average",
        "window": 6,  # sprints
        "threshold": 0.8
    },
    "defect_density": {
        "calculation": "defects_per_story_point",
        "threshold": 0.1
    }
}
```

## Testing and Validation

### Health Checks

```bash
# Check service health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "jira": "connected"
  }
}
```

### Data Extraction Test

```bash
# Test Jira data extraction
curl -X POST http://localhost:8000/api/v1/extract/test \
     -H "Content-Type: application/json" \
     -d '{"project": "DEMO", "limit": 10}'

# Expected response:
{
  "status": "success",
  "extracted": 10,
  "sample_data": [...]
}
```

### Analytics Validation

```bash
# Test analytics generation
curl http://localhost:8000/api/v1/analytics/velocity?project=DEMO

# Expected response:
{
  "project": "DEMO",
  "velocity": {
    "current": 42.5,
    "trend": "increasing",
    "confidence": 0.87
  }
}
```

### Dashboard Access

1. **Open dashboard**: http://localhost:3000
2. **Login with admin credentials**
3. **Verify data visualization**:
   - Sprint velocity charts
   - Defect density trends
   - Team performance metrics

## Monitoring and Observability

### Application Metrics

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'juno-analytics'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### Key Metrics to Monitor

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `juno_data_extraction_duration` | Time to extract data from Jira | > 30s |
| `juno_analytics_generation_time` | Time to generate analytics | > 10s |
| `juno_api_request_duration` | API response time | > 2s |
| `juno_database_connections` | Active database connections | > 80% of pool |
| `juno_jira_api_errors` | Jira API error rate | > 5% |

### Log Configuration

```yaml
# logging.yaml
version: 1
formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: default
  file:
    class: logging.FileHandler
    filename: /var/log/juno/analytics.log
    level: DEBUG
    formatter: default
loggers:
  juno:
    level: DEBUG
    handlers: [console, file]
    propagate: no
root:
  level: INFO
  handlers: [console]
```

## Security Configuration

### Authentication Setup

1. **Configure OAuth 2.0** (Recommended):
```yaml
# config/auth.yaml
oauth:
  provider: "azure"  # or "google", "okta"
  client_id: "${OAUTH_CLIENT_ID}"
  client_secret: "${OAUTH_CLIENT_SECRET}"
  redirect_uri: "https://your-domain.com/auth/callback"
  scopes: ["openid", "profile", "email"]
```

2. **Set up API key authentication**:
```bash
# Generate API key for service-to-service communication
python -c "
import secrets
print('API_KEY=' + secrets.token_urlsafe(32))
"
```

### Data Encryption

1. **Database encryption at rest**:
```sql
-- Enable transparent data encryption
ALTER DATABASE juno_analytics SET encryption = 'on';
```

2. **API encryption in transit**:
```yaml
# nginx.conf
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    location / {
        proxy_pass http://juno-analytics:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Access Control

```yaml
# config/rbac.yaml
roles:
  viewer:
    permissions:
      - "analytics:read"
      - "dashboard:view"
  analyst:
    permissions:
      - "analytics:read"
      - "analytics:export"
      - "dashboard:view"
      - "reports:generate"
  admin:
    permissions:
      - "*"

users:
  - email: "analyst@company.com"
    roles: ["analyst"]
  - email: "admin@company.com"
    roles: ["admin"]
```

## Troubleshooting

### Common Issues

**Issue**: Jira connection fails
```bash
# Check Jira connectivity
curl -v -H "Authorization: Bearer ${JIRA_API_TOKEN}" \
     "${JIRA_BASE_URL}/rest/api/3/myself"

# Common solutions:
# 1. Verify API token is valid
# 2. Check network connectivity
# 3. Verify Jira URL format
```

**Issue**: Database connection errors
```bash
# Check database connectivity
docker exec -it postgres psql -U juno -d juno_analytics -c "SELECT 1;"

# Common solutions:
# 1. Verify database credentials
# 2. Check database is running
# 3. Verify network connectivity
```

**Issue**: Slow analytics generation
```bash
# Check database performance
docker exec -it postgres psql -U juno -d juno_analytics -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"

# Common solutions:
# 1. Add database indexes
# 2. Optimize queries
# 3. Increase database resources
```

### Performance Tuning

1. **Database optimization**:
```sql
-- Add indexes for common queries
CREATE INDEX idx_issues_created_date ON issues(created_date);
CREATE INDEX idx_issues_project_key ON issues(project_key);
CREATE INDEX idx_issues_status ON issues(status);
```

2. **Caching configuration**:
```python
# config/cache.py
CACHE_CONFIG = {
    "analytics_ttl": 3600,  # 1 hour
    "dashboard_ttl": 300,   # 5 minutes
    "jira_data_ttl": 1800   # 30 minutes
}
```

3. **Resource allocation**:
```yaml
# k8s resource limits
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

## Next Steps

### Phase 1 Success Criteria

Before proceeding to Phase 2, ensure:

- [ ] **Data Extraction**: Successfully extracting data from all Jira projects
- [ ] **Analytics Generation**: Generating velocity, defect, and lead time metrics
- [ ] **Dashboard Functionality**: Teams can view and interact with analytics
- [ ] **Performance**: Sub-5 second dashboard load times
- [ ] **Adoption**: At least 80% of target teams using the system weekly

### Preparing for Phase 2

1. **Baseline Metrics**: Establish 3-6 months of historical data
2. **Team Training**: Ensure teams understand analytics and insights
3. **Process Integration**: Integrate analytics into sprint planning and retrospectives
4. **Stakeholder Buy-in**: Demonstrate value to leadership for Phase 2 approval

### Phase 2 Prerequisites

- [ ] **AI Services**: Secure OpenAI API access or Azure OpenAI deployment
- [ ] **Enhanced Infrastructure**: Kubernetes cluster for agentic AI components
- [ ] **Governance Framework**: Define approval workflows and decision boundaries
- [ ] **Security Review**: Complete security assessment for autonomous operations

### Migration Path

```bash
# Export Phase 1 data for Phase 2 migration
python scripts/export_analytics_data.py --format=json --output=/data/phase1_export.json

# Validate data integrity
python scripts/validate_export.py --file=/data/phase1_export.json
```

## Support and Resources

### Documentation
- [JUNO Architecture Overview](../architecture/system-overview.md)
- [API Reference](../reference/api-reference.md)
- [Phase 2 Deployment Guide](./phase2-agentic-ai.md)

### Community Support
- GitHub Issues: [https://github.com/mj3b/juno/issues](https://github.com/mj3b/juno/issues)
- Documentation: [https://github.com/mj3b/juno/tree/master/docs](https://github.com/mj3b/juno/tree/master/docs)

### Enterprise Support
- Technical Support: Contact your JUNO enterprise representative
- Professional Services: Available for custom deployment and integration
- Training Programs: Available for team onboarding and best practices

---

**Deployment Status**: ✅ Production Ready  
**Last Updated**: June 2025 
**Version**: 1.0.0

