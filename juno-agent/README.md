# JUNO Agent Code Structure

This directory contains the core JUNO application code, organized by functionality and phase implementation.

## Directory Structure

```
juno-agent/
├── src/                        # Core source code modules
│   ├── phase2/                 # Phase 2: Agentic AI components
│   ├── phase3/                 # Phase 3: Multi-agent orchestration
│   ├── phase4/                 # Phase 4: AI-native operations
│   ├── models/                 # Data models and schemas
│   ├── routes/                 # API route handlers
│   └── static/                 # Static assets
├── templates/                  # Jinja2 web templates
│   ├── phase2/                 # Phase 2 dashboard templates
│   └── base.html               # Base template
├── static/                     # Static web assets
│   ├── phase2/                 # Phase 2 CSS/JS
│   └── css/                    # Shared stylesheets
├── app_phase2.py               # Main Phase 2 Flask application
├── requirements-phase2.txt     # Phase 2 Python dependencies
└── README.md                   # This file
```

## Core Application Files

### Main Applications

| File | Purpose | Phase |
|------|---------|-------|
| `app_phase2.py` | Main Flask application for Phase 2 agentic capabilities | 2 |
| `requirements-phase2.txt` | Python dependencies for Phase 2 features | 2 |

### Legacy Components (Phase 1)

| File | Purpose | Status |
|------|---------|--------|
| `analytics_engine.py` | Data analytics and insights generation | ✅ Production |
| `data_extractor.py` | Jira data extraction and processing | ✅ Production |
| `jira_connector.py` | Jira API integration | ✅ Production |
| `openai_integration.py` | OpenAI GPT integration | ✅ Production |
| `query_processor.py` | Natural language query processing | ✅ Production |
| `visualization_engine.py` | Chart and graph generation | ✅ Production |

## Phase-Specific Components

### Phase 2: Agentic AI Workflow Management
**Location**: `src/phase2/`
**Status**: ✅ Production Ready

Core agentic AI components that enable autonomous decision-making with governance oversight.

[See detailed Phase 2 documentation →](./src/phase2/README.md)

### Phase 3: Multi-Agent Orchestration
**Location**: `src/phase3/`
**Status**: ✅ Code Complete

Distributed agent coordination with consensus protocols for organization-wide automation.

[See detailed Phase 3 documentation →](./src/phase3/README.md)

### Phase 4: AI-Native Operations
**Location**: `src/phase4/`
**Status**: ✅ Code Complete

Self-optimizing, self-healing operations with reinforcement learning and predictive scaling.

[See detailed Phase 4 documentation →](./src/phase4/README.md)

## Web Interface

### Templates
- **Base Template**: `templates/base.html` - Common layout and navigation
- **Phase 2 Dashboard**: `templates/phase2/dashboard.html` - Agentic AI management interface
- **Governance Interface**: `templates/phase2/governance.html` - Approval workflows

### Static Assets
- **Phase 2 Styles**: `static/phase2/css/dashboard.css` - Modern dashboard styling
- **Phase 2 Scripts**: `static/phase2/js/dashboard.js` - Interactive functionality
- **Shared Assets**: `static/css/` - Common stylesheets

## API Structure

### Route Organization
- **Core Routes**: `src/routes/` - Base API endpoints
- **Phase 2 Routes**: `src/routes/phase2/` - Agentic AI endpoints
- **Authentication**: OAuth 2.0 and RBAC integration
- **Documentation**: Automatic OpenAPI/Swagger generation

## Data Models

### Database Schemas
- **Memory Models**: Episodic, semantic, procedural memory structures
- **Decision Models**: Reasoning, confidence, and audit trail schemas
- **Governance Models**: Approval workflows and role management
- **Risk Models**: Sprint forecasting and prediction schemas

## Configuration

### Environment Variables
```bash
# Core Configuration
JUNO_PHASE=2                    # Current phase (1, 2, 3, or 4)
DATABASE_URL=sqlite:///juno.db  # Database connection
REDIS_URL=redis://localhost:6379 # Cache connection

# AI Integration
OPENAI_API_KEY=your-key         # OpenAI GPT access
GPT_MODEL=gpt-4                 # Preferred model

# Jira Integration
JIRA_URL=https://company.atlassian.net
JIRA_USERNAME=username
JIRA_API_TOKEN=token

# Security
SECRET_KEY=your-secret-key      # Flask session key
OAUTH_CLIENT_ID=client-id       # OAuth configuration
OAUTH_CLIENT_SECRET=secret      # OAuth secret
```

## Development Workflow

### Local Development
```bash
# Install dependencies
pip install -r requirements-phase2.txt

# Set up environment
cp .env.phase2.example .env
# Edit .env with your configuration

# Run Phase 2 application
python app_phase2.py

# Access dashboard
open http://localhost:5000
```

### Testing
```bash
# Run component tests
python -m pytest tests/test_phase2/ -v

# Run integration tests
python -m pytest tests/test_integration/ -v

# Check code coverage
coverage run -m pytest tests/
coverage report
```

### Code Quality
```bash
# Format code
black juno-agent/

# Check style
flake8 juno-agent/

# Type checking
mypy juno-agent/
```

## Architecture Patterns

### Microservices Design
- **Service Separation**: Each phase can run independently
- **API Gateway**: Centralized routing and authentication
- **Event-Driven**: Asynchronous communication between components
- **Database Per Service**: Isolated data stores for each phase

### Scalability Patterns
- **Horizontal Scaling**: Multiple instances behind load balancer
- **Caching Strategy**: Redis for session and computation caching
- **Database Optimization**: Connection pooling and query optimization
- **Background Processing**: Celery for async task execution

### Security Patterns
- **Zero Trust**: All requests authenticated and authorized
- **Encryption**: TLS 1.3 in transit, AES-256 at rest
- **Audit Logging**: Comprehensive activity tracking
- **Role-Based Access**: Granular permission management

## Deployment

### Production Deployment
```bash
# Build Docker image
docker build -t juno-agent:v2.0 .

# Deploy to Kubernetes
kubectl apply -f k8s/

# Scale deployment
kubectl scale deployment juno-core --replicas=3
```

### Health Monitoring
```bash
# Health check endpoint
curl http://localhost:5000/health

# Metrics endpoint
curl http://localhost:5000/metrics

# Ready check
curl http://localhost:5000/ready
```

## Contributing

### Adding New Features
1. Create feature branch from `master`
2. Implement in appropriate phase directory
3. Add comprehensive tests
4. Update documentation
5. Submit pull request

### Code Standards
- **Documentation**: All functions must have docstrings
- **Type Hints**: Full type annotation required
- **Testing**: >90% code coverage
- **Security**: Security review for all changes

---

For detailed component documentation, see the README files in each phase directory:
- [Phase 2 Components](./src/phase2/README.md)
- [Phase 3 Components](./src/phase3/README.md)
- [Phase 4 Components](./src/phase4/README.md)

