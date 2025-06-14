# Jira AI Analytics Agent - API Reference

## Base URL
```
http://localhost:5000/api
```

## Authentication
All endpoints require Jira API token authentication configured via environment variables.

## Natural Language Processing Endpoints

### POST /nlp/query
Process natural language query and return results.

**Request Body:**
```json
{
  "query": "How many tickets are assigned to John Doe?",
  "project_key": "DEMO",
  "time_range": "last_month"
}
```

**Response:**
```json
{
  "status": "success",
  "intent": "assignee_count",
  "entities": {
    "assignee": "John Doe",
    "project": "DEMO",
    "time_range": "last_month"
  },
  "results": {
    "total_assignees": 12,
    "target_assignee_count": 23,
    "average_per_assignee": 8.5
  }
}
```

### POST /nlp/parse
Parse query without execution (for validation).

### GET /nlp/test-queries
Get list of sample queries for testing.

## Analytics Endpoints

### GET /analytics/velocity
Generate velocity analysis.

**Parameters:**
- `project_key`: Jira project key
- `time_range`: Time period (last_month, last_quarter, etc.)
- `sprint_duration`: Sprint duration in days

### GET /analytics/defects
Generate defect analysis.

**Parameters:**
- `project_key`: Jira project key
- `time_range`: Time period
- `severity`: Filter by severity level

### GET /analytics/lead_time
Generate lead time analysis.

### GET /analytics/trends
Generate trend analysis.

### GET /analytics/metrics-list
Get list of available metrics.

## Jira Integration Endpoints

### GET /jira/test-connection
Test Jira API connection.

### POST /jira/sync-data
Synchronize data from Jira.

### GET /jira/projects
Get list of Jira projects.

### GET /jira/users
Get list of Jira users.

## Visualization Endpoints

### POST /visualization/chart
Generate chart data.

**Request Body:**
```json
{
  "chart_type": "velocity_trend",
  "data_source": "analytics_result",
  "format": "plotly"
}
```

### GET /visualization/export
Export chart as image.

## Error Responses

All endpoints return consistent error format:

```json
{
  "status": "error",
  "error_code": "AUTHENTICATION_FAILED",
  "message": "Invalid Jira API token",
  "details": "Please check your JIRA_API_TOKEN environment variable"
}
```

## Rate Limiting

- 100 requests per minute per IP
- 1000 requests per hour per API token
- Rate limit headers included in responses

## Status Codes

- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `429`: Rate Limited
- `500`: Internal Server Error

