# JUNO Deployment Guide

## System Requirements

### Backend (Flask API)
- Python 3.11+
- Virtual environment with dependencies from requirements.txt
- Environment variables:
  - JIRA_BASE_URL: Your Jira instance URL
  - JIRA_EMAIL: Jira user email
  - JIRA_API_TOKEN: Jira API token
  - DATABASE_URL: SQLite/PostgreSQL database URL (optional)

### Frontend (React Dashboard)
- Node.js 20+
- Built static files in dist/ directory
- Web server (nginx, Apache, or static hosting)

## Deployment Options

### Option 1: Local Development
1. Backend: `cd juno-agent && source venv/bin/activate && python src/main.py`
2. Frontend: `cd juno-dashboard && npm run dev`

### Option 2: Production Deployment
1. Backend: Deploy Flask app using Gunicorn/uWSGI
2. Frontend: Deploy built files to static hosting (Netlify, Vercel, S3)

### Option 3: Docker Deployment
- Create Dockerfiles for both backend and frontend
- Use docker-compose for orchestration

## Configuration

### Backend Configuration
```bash
export JIRA_BASE_URL="https://your-company.atlassian.net"
export JIRA_EMAIL="your-email@company.com"
export JIRA_API_TOKEN="your-api-token"
```

### Frontend Configuration
- Update API base URL in frontend code to point to deployed backend
- Configure CORS settings in Flask app for production domain

## Security Considerations
- Use HTTPS in production
- Secure API tokens and credentials
- Configure proper CORS settings
- Implement rate limiting
- Use environment variables for sensitive data

## Monitoring and Logging
- Flask app includes logging for API requests
- Monitor API rate limits and usage
- Set up error tracking and alerting

## Scaling Considerations
- Use Redis for caching frequent queries
- Implement database connection pooling
- Consider load balancing for high traffic
- Use CDN for frontend assets

