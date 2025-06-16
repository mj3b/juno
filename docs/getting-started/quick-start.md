# JUNO Phase 2: Quick Start Guide

## 🚀 Get Started in 15 Minutes

This quick start guide will have you running JUNO Phase 2 agentic capabilities in under 15 minutes.

### Prerequisites

- Python 3.11+
- Git
- Jira access (Cloud or Server)
- OpenAI API key or Azure OpenAI access

### Step 1: Clone and Setup (3 minutes)

```bash
# Clone repository
git clone https://github.com/mj3b/juno.git
cd juno

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r juno-agent/requirements-phase2.txt
```

### Step 2: Configure (5 minutes)

```bash
# Copy configuration template
cp .env.phase2.example .env

# Edit configuration (use your favorite editor)
nano .env
```

**Minimum Required Configuration:**
```bash
# Jira Integration
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-jira-api-token

# AI Provider
OPENAI_API_KEY=your-openai-api-key

# Phase 2 Settings
JUNO_PHASE=2
MEMORY_ENABLED=true
AUTONOMOUS_ACTIONS=true
SUPERVISOR_MODE=true
```

### Step 3: Initialize (2 minutes)

```bash
# Initialize database and governance
python juno-agent/src/phase2/quick_setup.py

# Run tests to verify installation
python juno-agent/src/phase2/test_suite.py --quick
```

### Step 4: Start Services (1 minute)

```bash
# Start JUNO Phase 2
python juno-agent/app.py --phase=2

# Open browser to http://localhost:5000
```

### Step 5: First Agentic Action (4 minutes)

1. **Access Dashboard**: Go to http://localhost:5000/dashboard
2. **Review Risk Forecast**: Check sprint risk predictions
3. **Approve Triage Action**: Review and approve a stale ticket recommendation
4. **View Reasoning**: Click "Why?" to see transparent AI reasoning

## 🎯 What You Just Deployed

### Immediate Capabilities

**🧠 Agentic Intelligence**
- JUNO now learns from your team's patterns
- Predicts sprint risks before they happen
- Takes autonomous actions with your approval
- Explains every decision with confidence scores

**🏛️ Governance & Control**
- All autonomous actions require approval
- Complete audit trail of AI decisions
- Role-based approval workflows
- Escalation procedures for complex decisions

### Quick Validation

**Test Sprint Risk Forecast:**
```bash
curl http://localhost:5000/api/v2/risk/forecast/SPRINT-ID
```

**Test Stale Triage:**
```bash
curl http://localhost:5000/api/v2/triage/analyze
```

**Check Governance Status:**
```bash
curl http://localhost:5000/api/v2/governance/pending
```

## 🔧 Quick Configuration

### Add Team Members to Governance

```python
# Run this in Python console
from juno-agent.src.phase2.governance_framework import GovernanceRoleManager

role_manager = GovernanceRoleManager()

# Add team lead
role_manager.assign_role("team.lead@company.com", "TEAM_LEAD", ["your_team"])

# Add project manager  
role_manager.assign_role("project.manager@company.com", "PROJECT_MANAGER", ["your_team"])
```

### Customize Risk Thresholds

Edit `.env`:
```bash
# Risk sensitivity (0.0 = very sensitive, 1.0 = very conservative)
RISK_THRESHOLD_LOW=0.3
RISK_THRESHOLD_MEDIUM=0.6
RISK_THRESHOLD_HIGH=0.8

# Autonomous action confidence threshold
AUTO_APPROVAL_THRESHOLD=0.85
```

## 📊 Immediate Value Demonstration

### Sprint Risk Prevention

JUNO will immediately start analyzing your sprints and predicting risks:

- **Velocity Risk**: Based on historical team performance
- **Scope Risk**: Analyzing story point distribution
- **Capacity Risk**: Team availability and workload
- **Dependency Risk**: Blocking tickets and external dependencies

### Intelligent Triage

JUNO identifies stale tickets and recommends actions:

- **Reassign**: To available team members
- **Escalate**: For high-priority blocked items
- **Defer**: For low-priority items without sprint assignment
- **Close**: For obsolete or duplicate tickets

### Transparent Reasoning

Every AI decision includes:

- **Confidence Score**: How certain JUNO is about the recommendation
- **Data Sources**: What information was used
- **Historical Context**: Similar past situations and outcomes
- **Impact Assessment**: Expected business and technical impact

## 🎪 Demo Scenarios

### Scenario 1: Sprint Risk Alert

1. JUNO detects velocity trending below target
2. Predicts 73% chance of sprint failure
3. Recommends scope reduction or capacity increase
4. Requires PM approval for scope changes

### Scenario 2: Stale Ticket Resolution

1. JUNO identifies ticket stale for 8 days
2. Analyzes assignee availability and workload
3. Recommends reassignment to available developer
4. Requires Team Lead approval for reassignment

### Scenario 3: Proactive Escalation

1. JUNO detects critical bug with no progress
2. Identifies dependency blocking resolution
3. Recommends escalation to Engineering Manager
4. Automatically creates escalation with context

## 🚨 Troubleshooting

### Common Issues

**"No Jira connection"**
```bash
# Test Jira connectivity
curl -u username:token https://your-company.atlassian.net/rest/api/2/myself
```

**"OpenAI API error"**
```bash
# Test OpenAI connectivity
curl -H "Authorization: Bearer your-api-key" https://api.openai.com/v1/models
```

**"No governance roles configured"**
```bash
# Quick role setup
python juno-agent/src/phase2/setup_demo_roles.py
```

### Getting Help

- **Logs**: Check `/var/log/juno/` for detailed error information
- **Health Check**: Visit http://localhost:5000/health
- **API Status**: Visit http://localhost:5000/api/v2/status
- **Documentation**: Full deployment guide in `docs/DEPLOYMENT_GUIDE.md`

## 🎯 Next Steps

### Immediate (First Week)

1. **Configure Team Roles**: Add all team members to governance
2. **Customize Thresholds**: Adjust risk and confidence settings
3. **Monitor Performance**: Review AI accuracy and approval rates
4. **Train Users**: Conduct governance workflow training

### Short Term (First Month)

1. **Optimize Settings**: Fine-tune based on usage patterns
2. **Expand Teams**: Roll out to additional teams
3. **Custom Rules**: Add team-specific governance rules
4. **Integration**: Connect with Slack/Teams for notifications

### Long Term (3-6 Months)

1. **Phase 3 Planning**: Multi-agent coordination capabilities
2. **Industry Customization**: Vertical-specific adaptations
3. **Advanced Analytics**: Custom reporting and dashboards
4. **Enterprise Integration**: SSO, LDAP, and compliance frameworks

## 🏆 Success Metrics

Track these metrics to measure JUNO Phase 2 impact:

**Efficiency Metrics:**
- Ticket resolution time reduction
- Sprint success rate improvement
- Velocity predictability increase
- Manual triage time savings

**Quality Metrics:**
- AI prediction accuracy
- User approval rate for recommendations
- Governance compliance rate
- Risk mitigation effectiveness

**Adoption Metrics:**
- Daily active users
- Autonomous actions executed
- Governance workflow usage
- User satisfaction scores

---

**🎉 Congratulations! You've successfully deployed JUNO Phase 2 agentic AI capabilities.**

Your team now has an AI teammate that learns, predicts, acts, and explains - all while maintaining human oversight and governance. Welcome to the future of agentic workflow management!

