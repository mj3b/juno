# JUNO: The Agentic AI Workflow Manager

**"JIRA tracks. JUNO explains. Now JUNO acts."**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18+-61dafb.svg)](https://reactjs.org/)
[![Enterprise Ready](https://img.shields.io/badge/enterprise-ready-green.svg)](https://github.com/mj3b/juno)

---

## 🏗️ **Build Versions**

| Version | Status | Description | Use Case |
|---------|--------|-------------|----------|
| **Phase 1** | ✅ **Stable** | AI Analyst for Jira | Production-ready Q&A and analytics |
| **Phase 2** | 🚧 **Development** | Agentic AI Workflow Manager | Autonomous workflow management |

---

## 🎯 **Choose Your Build**

### **Phase 1: AI Analyst (Stable Production)**
> **"JIRA tracks. JUNO explains."**

**Perfect for teams wanting:**
- ✅ Natural language Jira analytics
- ✅ Intelligent Q&A and reporting
- ✅ Enterprise GPT integration
- ✅ Production-ready stability

**Key Capabilities:**
- Conversational AI interface for Jira data
- Advanced analytics and velocity tracking
- Multi-provider GPT support (OpenAI, Azure)
- Real-time dashboards and visualizations

### **Phase 2: Agentic Workflow Manager (Development)**
> **"JIRA tracks. JUNO explains. Now JUNO acts."**

**Perfect for teams wanting:**
- 🚀 Proactive risk management
- 🚀 Autonomous triage resolution
- 🚀 Transparent AI reasoning
- 🚀 Human-in-the-loop governance

**Key Capabilities:**
- All Phase 1 features PLUS:
- Sprint Risk Forecast with predictive analytics
- Autonomous Stale Triage Resolution
- Memory layer with persistent learning
- Lead/PM approval workflows
- Comprehensive audit trails

---

## 🚀 **Quick Start - Phase 1 (Stable)**

### **Installation**
```bash
# Clone repository
git clone https://github.com/mj3b/juno.git
cd juno

# Backend setup
cd juno-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../juno-dashboard
npm install

# Configuration
cp .env.example .env
# Edit .env with your Jira and GPT settings
```

### **Phase 1 Configuration**
```bash
# Required: Jira connection
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token

# Enterprise GPT (choose one or multiple)
OPENAI_API_KEY=your-openai-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_DEPLOYMENT=your-deployment

# Provider selection
GPT_PREFERRED_PROVIDER=openai  # Options: openai, azure, local
```

### **Launch Phase 1**
```bash
# Start backend
cd juno-agent
python src/main.py

# Start frontend
cd ../juno-dashboard
npm run dev

# Access at http://localhost:5173
```

---

## 🚀 **Quick Start - Phase 2 (Development)**

### **Prerequisites**
- Phase 1 working installation
- Lead/PM training completion
- Understanding of agentic AI concepts

### **Phase 2 Installation**
```bash
# Use existing Phase 1 installation
cd juno

# Install Phase 2 dependencies
cd juno-agent
pip install -r requirements-phase2.txt

# Phase 2 configuration
cp .env.phase2.example .env
# Edit with Phase 2 settings
```

### **Phase 2 Configuration**
```bash
# All Phase 1 settings PLUS:

# Phase 2: Agentic capabilities
JUNO_PHASE=2
MEMORY_ENABLED=true
AUTONOMOUS_ACTIONS=true
SUPERVISOR_MODE=true

# Governance and compliance
AUDIT_TRAIL_ENABLED=true
CONFIDENCE_THRESHOLD=0.8
ESCALATION_ENABLED=true
LEAD_PM_APPROVAL_REQUIRED=true

# Advanced features
RISK_FORECAST_ENABLED=true
STALE_TRIAGE_ENABLED=true
WORKFLOW_OPTIMIZATION=true
```

### **Launch Phase 2**
```bash
# Start Phase 2 backend
cd juno-agent
python src/main.py --phase2

# Start enhanced dashboard
cd ../juno-dashboard
npm run dev:phase2

# Access at http://localhost:5173
```

---

## 📊 **Feature Comparison**

| Feature | Phase 1 | Phase 2 |
|---------|---------|---------|
| **Natural Language Q&A** | ✅ Full | ✅ Enhanced |
| **Jira Analytics** | ✅ Full | ✅ Enhanced |
| **Enterprise GPT** | ✅ Multi-provider | ✅ Enhanced usage |
| **Real-time Dashboards** | ✅ Full | ✅ Enhanced |
| **Sprint Risk Forecast** | ❌ | ✅ **New** |
| **Autonomous Triage** | ❌ | ✅ **New** |
| **Memory & Learning** | ❌ | ✅ **New** |
| **Transparent Reasoning** | ❌ | ✅ **New** |
| **Lead/PM Workflows** | ❌ | ✅ **New** |
| **Audit Trails** | Basic | ✅ **Comprehensive** |
| **Confidence Scoring** | ❌ | ✅ **New** |
| **Proactive Actions** | ❌ | ✅ **New** |

---

## 🏗️ **Architecture Evolution**

### **Phase 1 Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ React           │    │ Flask           │    │ Enterprise      │
│ Dashboard       │◄──►│ API             │◄──►│ GPT             │
│                 │    │                 │    │ (OpenAI/Azure)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Interactive     │    │ Jira            │    │ Analytics       │
│ Visualizations  │    │ Connector       │    │ Engine          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Phase 2 Architecture (Agentic)**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Agent           │    │ Memory &        │    │ Reasoning &     │
│ Orchestration   │◄──►│ Context         │◄──►│ Decision        │
│ Layer           │    │ Layer           │    │ Layer           │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Action          │    │ Observability   │    │ Human-in-Loop   │
│ Execution       │    │ & Governance    │    │ Governance      │
│ Layer           │    │ Layer           │    │ Layer           │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              Phase 1 Foundation (Enhanced)                      │
│  React Dashboard + Flask API + Enterprise GPT + Jira Connector  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔗 **Enterprise GPT Integration**

### **Supported Providers**
- **OpenAI**: Direct API integration with GPT-3.5-turbo and GPT-4
- **Azure OpenAI**: Enterprise-grade deployment with compliance features
- **Local NLP**: Fast pattern matching for common queries

### **Phase 2 Enhanced GPT Usage**
- **Reasoning Generation**: GPT creates transparent explanations for decisions
- **Risk Analysis**: GPT analyzes sprint data to predict delivery risks
- **Pattern Recognition**: GPT identifies workflow optimization opportunities
- **Natural Language Actions**: GPT translates decisions into human-readable explanations

### **Configuration Examples**
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_DEPLOYMENT=your-deployment

# Provider Selection
GPT_PREFERRED_PROVIDER=openai  # Options: openai, azure, local

# Phase 2: Enhanced GPT usage
GPT_REASONING_MODEL=gpt-4  # For complex reasoning tasks
GPT_ANALYSIS_MODEL=gpt-3.5-turbo  # For data analysis
GPT_EXPLANATION_MODEL=gpt-3.5-turbo  # For user explanations
```

---

## 🎓 **Migration Path**

### **Phase 1 → Phase 2 Upgrade**
```bash
# 1. Backup your Phase 1 configuration
cp .env .env.phase1.backup

# 2. Install Phase 2 dependencies
pip install -r requirements-phase2.txt

# 3. Update configuration
cp .env.phase2.example .env
# Merge your Phase 1 settings

# 4. Initialize Phase 2 components
python src/phase2/setup.py --init

# 5. Test Phase 2 features
python src/main.py --phase2 --test-mode
```

### **Rollback to Phase 1**
```bash
# Simple rollback if needed
cp .env.phase1.backup .env
python src/main.py  # Runs Phase 1 by default
```

---

## 🔧 **Development & Contribution**

### **Phase 1 Development**
- Focus on stability and performance
- Enterprise GPT optimization
- Analytics engine enhancements
- UI/UX improvements

### **Phase 2 Development**
- Agentic AI capabilities
- Memory and learning systems
- Governance frameworks
- Advanced automation

### **Contributing**
- **Phase 1**: Production stability and enterprise features
- **Phase 2**: Cutting-edge agentic AI capabilities
- See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines

---

## 📚 **Documentation**

### **Phase 1 Documentation**
- **[User Guide](docs/USER_GUIDE.md)**: Complete Phase 1 usage guide
- **[API Reference](docs/API_REFERENCE.md)**: REST API documentation
- **[Enterprise Setup](docs/ENTERPRISE_SETUP.md)**: Production deployment
- **[Troubleshooting](docs/TROUBLESHOOTING.md)**: Common issues and solutions

### **Phase 2 Documentation**
- **[Phase 2 Strategy](docs/phase2/PHASE2_STRATEGY.md)**: Implementation strategy
- **[Governance Framework](docs/phase2/GOVERNANCE.md)**: Lead/PM workflows
- **[Memory Architecture](docs/phase2/MEMORY_ARCHITECTURE.md)**: Technical details
- **[Migration Guide](docs/phase2/MIGRATION.md)**: Phase 1 → Phase 2 upgrade

---

## 🏆 **Recognition & Research**

**Phase 2 Implementation follows McKinsey's latest research on agentic AI transformation:**
- Breaks the "gen AI paradox" (78% deploy, 80% see no impact)
- Implements vertical vs horizontal AI deployment
- Establishes "Agentic AI Mesh" architecture patterns
- Demonstrates responsible AI governance

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌟 **What's Next**

### **Phase 1 Roadmap**
- Enhanced enterprise integrations
- Performance optimizations
- Additional analytics capabilities
- Mobile-responsive improvements

### **Phase 2 Roadmap**
- Multi-agent coordination
- Advanced predictive analytics
- Organization-wide deployment
- Industry-specific adaptations

### **Phase 3 Vision**
- Autonomous software delivery
- Cross-platform orchestration
- AI-driven process optimization
- Enterprise AI mesh deployment

---

**Choose your path: Stable analytics with Phase 1, or cutting-edge agentic AI with Phase 2.**

*JUNO: Transforming software development through intelligent workflow management.*  mj3b

