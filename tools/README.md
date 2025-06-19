# JUNO Tools

This directory contains command-line tools and utilities for operating JUNO.

## Available Tools

### Core Operations
- **run_agent.py**: Main entry point to start JUNO
- **evaluate_agent.py**: Comprehensive agent evaluation
- **train_memory.py**: Memory layer training and optimization

### Deployment & Management
- **deploy_phase.py**: Phase-specific deployment tool
- **generate_reports.py**: Report generation utility

## Usage

### Starting JUNO
```bash
python tools/run_agent.py
```

### Evaluating Performance
```bash
python tools/evaluate_agent.py
```

### Training Memory Layer
```bash
python tools/train_memory.py
```

### Deploying Specific Phase
```bash
python tools/deploy_phase.py --phase 2 --environment staging
```

### Generating Reports
```bash
python tools/generate_reports.py
```

## Configuration

All tools use the central configuration system from `src/config.py`. Ensure environment variables are properly set:

- `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`
- `OPENAI_API_KEY`, `OPENAI_ENTERPRISE_KEY`
- `DATABASE_URL`, `REDIS_URL`, `ELASTICSEARCH_URL`

## Development

Tools are designed to be:
- **Modular**: Each tool focuses on a specific function
- **Configurable**: Environment-based configuration
- **Scriptable**: Suitable for automation and CI/CD

