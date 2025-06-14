# Jira AI Analytics Agent - Quick Start Guide

## Overview

The Jira AI Analytics Agent is an enterprise-grade solution that transforms natural language queries into actionable Jira insights. This quick start guide will help you get the system running in under 30 minutes.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Jira Cloud instance with API access
- 4GB+ RAM for development

## Step 1: Backend Setup

1. **Clone and Setup Environment**
```bash
# Navigate to the backend directory
cd jira-ai-agent

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Configure Jira Connection**
```bash
# Set environment variables
export JIRA_BASE_URL="https://your-company.atlassian.net"
export JIRA_EMAIL="your-email@company.com"
export JIRA_API_TOKEN="your-api-token"
```

3. **Start Backend Server**
```bash
python src/main.py
# Server will start on http://localhost:5000
```

## Step 2: Frontend Setup

1. **Install Dependencies**
```bash
cd jira-ai-dashboard
npm install
```

2. **Start Development Server**
```bash
npm run dev
# Dashboard will open on http://localhost:5173
```

## Step 3: Test the System

1. **Open the Dashboard**
   - Navigate to http://localhost:5173
   - You should see the Jira AI Analytics Dashboard

2. **Try Sample Queries**
   - "How many tickets are assigned to John Doe?"
   - "Show me the status distribution for project DEMO"
   - "List all bugs from last month"

3. **Verify API Endpoints**
   - Visit http://localhost:5000/api/nlp/test-queries
   - Should return JSON with sample queries

## Common Issues

**Authentication Error**: Verify your Jira API token and permissions
**Connection Error**: Check your Jira base URL and network connectivity
**Import Error**: Ensure all dependencies are installed in the virtual environment

## Next Steps

- Configure your actual Jira projects
- Customize the dashboard for your team's needs
- Explore advanced analytics features
- Set up production deployment

For detailed documentation, see the complete Jira AI Analytics Agent Documentation.

