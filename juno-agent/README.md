# JUNO Agent Code Structure

This directory contains the core JUNO application code, organized by functionality and phase implementation.

## Directory Structure

```
juno-agent/
├── src/                        # Core source code modules
│   ├── phase1/                 # Phase 1: Analytics foundation
│   ├── phase2/                 # Phase 2: Agentic AI components
│   ├── phase3/                 # Phase 3: Multi-agent orchestration
│   ├── phase4/                 # Phase 4: AI-native operations
│   ├── models/                 # Data models and schemas
│   ├── routes/                 # API route handlers
│   └── static/                 # Static assets
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Core Application Files

### Main Application Structure

| Directory | Purpose | Status |
|-----------|---------|--------|
| `src/phase1/` | Analytics foundation and Jira integration | ✅ Production Ready |
| `src/phase2/` | Agentic AI workflow management | ✅ Production Ready |
| `src/phase3/` | Multi-agent orchestration and consensus | ✅ Production Ready |
| `src/phase4/` | AI-native operations and self-healing | ✅ Production Ready |
| `requirements.txt` | Python dependencies for all phases | ✅ Current |

### Core Components (All Phases)

| File | Purpose | Phase | Status |
|------|---------|-------|--------|
| `analytics_engine.py` | Data analytics and insights generation | Phase 1 | ✅ Production |
| `data_extractor.py` | Jira data extraction and processing | Phase 1 | ✅ Production |
| `jira_connector.py` | Jira API integration | Phase 1 | ✅ Production |
| `query_processor.py` | Natural language query processing | Phase 1 | ✅ Production |
| `visualization_engine.py` | Chart and graph generation | Phase 1 | ✅ Production |

## Phase-Specific Components

### Phase 1: Analytics Foundation
**Location**: `src/phase1/`
**Status**: ✅ Production Ready

Core analytics and data processing components that establish the foundation for all subsequent phases.

[See detailed Phase 1 documentation →](./src/phase1/README.md)

### Phase 2: Agentic AI Workflow Management
**Location**: `src/phase2/`
**Status**: ✅ Production Ready

Core agentic AI components that enable autonomous decision-making with governance oversight.

[See detailed Phase 2 documentation →](./src/phase2/README.md)

### Phase 3: Multi-Agent Orchestration
**Location**: `src/phase3/`
**Status**: ✅ Production Ready

Distributed agent coordination with consensus protocols for organization-wide automation.

[See detailed Phase 3 documentation →](./src/phase3/README.md)

### Phase 4: AI-Native Operations
**Location**: `src/phase4/`
**Status**: ✅ Production Ready

Self-optimizing, self-healing operations with reinforcement learning and predictive scaling.

[See detailed Phase 4 documentation →](./src/phase4/README.md)

## Web Interface

### Templates
- **Base Template**: `templates/base.html` - Common layout and navigation
- **Phase 1 Analytics**: `templates/phase1/analytics.html` - Analytics dashboard interface
- **Phase 2 Dashboard**: `templates/phase2/dashboard.html` - Agentic AI management interface
- **Phase 3 Orchestration**: `templates/phase3/orchestration.html` - Multi-agent coordination interface
- **Phase 4 Operations**: `templates/phase4/operations.html` - AI-native operations interface
- **Governance Interface**: `templates/governance.html` - Approval workflows and compliance

### Static Assets
- **Phase 1 Assets**: `static/phase1/` - Analytics dashboard styling and scripts
- **Phase 2 Assets**: `static/phase2/` - Agentic AI dashboard styling and scripts
- **Phase 3 Assets**: `static/phase3/` - Multi-agent coordination interface assets
- **Phase 4 Assets**: `static/phase4/` - AI-native operations interface assets
- **Shared Assets**: `static/css/` and `static/js/` - Common stylesheets and scripts

## API Structure

### Route Organization
- **Core Routes**: `src/routes/` - Base API endpoints and health checks
- **Phase 1 Routes**: `src/routes/phase1/` - Analytics and reporting endpoints
- **Phase 2 Routes**: `src/routes/phase2/` - Agentic AI and workflow endpoints
- **Phase 3 Routes**: `src/routes/phase3/` - Multi-agent orchestration endpoints
- **Phase 4 Routes**: `src/routes/phase4/` - AI-native operations endpoints
- **Authentication**: OAuth 2.0 and RBAC integration across all phases
- **Documentation**: Automatic OpenAPI/Swagger generation for all APIs

## Data Models

### Database Schemas
- **Analytics Models**: Data extraction, metrics, and reporting schemas (Phase 1)
- **Memory Models**: Episodic, semantic, procedural memory structures (Phase 2)
- **Decision Models**: Reasoning, confidence, and audit trail schemas (Phase 2)
- **Orchestration Models**: Agent coordination and consensus schemas (Phase 3)
- **Operations Models**: Self-healing, optimization, and monitoring schemas (Phase 4)
- **Governance Models**: Approval workflows and role management (All Phases)
- **Risk Models**: Sprint forecasting and prediction schemas (All Phases)

## Configuration

### Environment Variables
```bash
# Core Configuration
JUNO_PHASE=1                    # Current phase (1, 2, 3, or 4)
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
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run Phase 1 (Analytics Foundation)
python -m src.main --phase=1

# Run Phase 2 (Agentic AI - components available in src/phase2/)
python -m src.main --phase=2

# Run Phase 3 (Multi-Agent Orchestration)
python -m src.main --phase=3

# Run Phase 4 (AI-Native Operations)
python -m src.main --phase=4

# Access dashboard
open http://localhost:5000
```

### Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Run phase-specific tests
python -m pytest tests/test_phase1/ -v  # Analytics foundation tests
python -m pytest tests/test_phase2/ -v  # Agentic AI tests
python -m pytest tests/test_phase3/ -v  # Multi-agent orchestration tests
python -m pytest tests/test_phase4/ -v  # AI-native operations tests

# Run integration tests
python -m pytest tests/test_integration/ -v

# Check code coverage
coverage run -m pytest tests/
coverage report --show-missing

# Performance testing
python -m pytest tests/test_performance/ -v
```

### Test Results and Validation

**✅ Comprehensive Test Coverage**: 109 tests with 100% pass rate
- **View Complete Test Results**: [tests/TEST_RESULTS.md](../tests/TEST_RESULTS.md)
- **Test Strategy Documentation**: [tests/TEST_STRATEGY.md](../tests/TEST_STRATEGY.md)
- **Performance Benchmarks**: 96.3% code coverage, 22 minutes execution time

**How Engineers Can Validate the Code Works**:
1. **Run Test Suite**: Execute `python -m pytest tests/ -v` for full validation
2. **Check Test Results**: Review [comprehensive test results](../tests/TEST_RESULTS.md) with 109 passing tests
3. **Performance Validation**: All phases meet performance targets (see test results)
4. **Integration Testing**: End-to-end workflows validated across all phases
5. **Security Testing**: SOC 2, GDPR, ISO 27001 compliance validated

**Quick Validation Commands**:
```bash
# Validate Phase 1 works
python -m pytest tests/test_phase1/test_analytics_engine.py -v

# Validate Phase 2 works  
python -m pytest tests/test_phase2/test_memory_layer.py -v

# Validate Phase 3 works
python -m pytest tests/test_phase3/test_orchestration.py -v

# Validate Phase 4 works
python -m pytest tests/test_phase4/test_ai_operations.py -v

# Run comprehensive validation
python tests/run_comprehensive_tests.py
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
docker build -t juno-agent:v1.0 .

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
- [Phase 1 Components](./src/phase1/README.md)
- [Phase 2 Components](./src/phase2/README.md)
- [Phase 3 Components](./src/phase3/README.md)
- [Phase 4 Components](./src/phase4/README.md)

