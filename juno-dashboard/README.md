# JUNO Dashboard

React-based modern dashboard interface for JUNO Enterprise Agentic AI Platform.

## Overview

The JUNO Dashboard provides a comprehensive web interface for monitoring and managing all phases of the JUNO platform, from basic analytics to advanced AI-native operations.

## Features

### Phase 1: Analytics Foundation
- Sprint velocity tracking and trend analysis
- Defect density monitoring and quality metrics
- Team performance dashboards
- Historical data visualization

### Phase 2: Agentic AI Management
- Real-time agentic AI status monitoring
- Memory layer utilization tracking (episodic, semantic, procedural, working)
- Reasoning engine decision audit trails
- Risk forecasting with probability scoring
- Governance framework compliance monitoring

### Phase 3: Multi-Agent Orchestration
- Agent network topology visualization
- Consensus status monitoring (Raft protocol)
- Task coordination and distribution tracking
- Performance metrics and health monitoring

### Phase 4: AI-Native Operations
- Reinforcement learning optimization status
- ML threat detection monitoring
- Predictive scaling recommendations
- Self-healing incident tracking

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Components**: Tailwind CSS with custom components
- **Charts**: Recharts for data visualization
- **State Management**: React hooks and context
- **Routing**: React Router

## Development

### Prerequisites
- Node.js 18+
- npm or yarn

### Setup
```bash
cd juno-dashboard
npm install
npm run dev
```

### Build
```bash
npm run build
```

## Integration

The dashboard integrates with the JUNO Agent backend via REST API endpoints:
- Phase 2 API: `http://localhost:5000/api/phase2/`
- Phase 3 API: `http://localhost:5000/api/phase3/`
- Phase 4 API: `http://localhost:5000/api/phase4/`

## Architecture

```
juno-dashboard/
├── src/
│   ├── components/          # Reusable UI components
│   │   └── ui/             # Base UI components
│   ├── hooks/              # Custom React hooks
│   ├── assets/             # Static assets
│   └── App.jsx             # Main application component
├── public/                 # Public assets
└── package.json           # Dependencies and scripts
```

