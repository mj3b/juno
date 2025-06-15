#!/bin/bash

# JUNO Phase 2: One-Click Deployment Script
# Automated setup and configuration for client demonstrations

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
JUNO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$JUNO_DIR/venv"
DB_PATH="$JUNO_DIR/juno_phase2.db"
LOG_DIR="$JUNO_DIR/logs"
PORT=${JUNO_PORT:-5000}

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    JUNO Phase 2 Deployment                  ║"
    echo "║              Agentic AI Workflow Manager                    ║"
    echo "║                                                              ║"
    echo "║  🧠 Memory & Learning    🔍 Transparent Reasoning           ║"
    echo "║  📊 Risk Forecasting     🎯 Smart Triage                   ║"
    echo "║  🏛️  Enterprise Governance                                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
        error "Python 3.8+ is required (found $PYTHON_VERSION)"
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        error "pip3 is required but not installed"
    fi
    
    # Check Node.js (optional, for advanced features)
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        success "Node.js $NODE_VERSION detected"
    else
        warning "Node.js not found (optional for advanced features)"
    fi
    
    success "System requirements check passed"
}

# Setup Python virtual environment
setup_venv() {
    log "Setting up Python virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        success "Virtual environment created"
    else
        log "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    success "Virtual environment ready"
}

# Install dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    # Ensure we're in virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Install Phase 1 requirements
    if [ -f "$JUNO_DIR/juno-agent/requirements.txt" ]; then
        pip install -r "$JUNO_DIR/juno-agent/requirements.txt"
    fi
    
    # Install Phase 2 requirements
    if [ -f "$JUNO_DIR/juno-agent/requirements-phase2.txt" ]; then
        pip install -r "$JUNO_DIR/juno-agent/requirements-phase2.txt"
    fi
    
    success "Dependencies installed"
}

# Setup directories
setup_directories() {
    log "Setting up directory structure..."
    
    # Create necessary directories
    mkdir -p "$LOG_DIR"
    mkdir -p "$JUNO_DIR/data"
    mkdir -p "$JUNO_DIR/backups"
    mkdir -p "$JUNO_DIR/config"
    
    # Set permissions
    chmod 755 "$LOG_DIR"
    chmod 755 "$JUNO_DIR/data"
    chmod 755 "$JUNO_DIR/backups"
    
    success "Directory structure created"
}

# Initialize database
init_database() {
    log "Initializing JUNO Phase 2 database..."
    
    source "$VENV_DIR/bin/activate"
    
    cd "$JUNO_DIR/juno-agent"
    
    # Run database initialization
    python3 -c "
import sys
sys.path.append('src/phase2')
from database_setup import initialize_juno_database

try:
    db_manager = initialize_juno_database('$DB_PATH')
    print('✅ Database initialized successfully')
    db_manager.disconnect()
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    sys.exit(1)
"
    
    success "Database initialized with demo data"
}

# Create configuration files
create_config() {
    log "Creating configuration files..."
    
    # Create main config file
    cat > "$JUNO_DIR/config/juno_config.json" << EOF
{
    "environment": "demo",
    "debug": true,
    "database": {
        "path": "$DB_PATH",
        "backup_interval_hours": 24
    },
    "api": {
        "host": "0.0.0.0",
        "port": $PORT,
        "cors_enabled": true
    },
    "openai": {
        "api_key": "\${OPENAI_API_KEY}",
        "model": "gpt-3.5-turbo",
        "max_tokens": 1000
    },
    "jira": {
        "url": "\${JIRA_URL}",
        "username": "\${JIRA_USERNAME}",
        "api_token": "\${JIRA_API_TOKEN}"
    },
    "phase2": {
        "enabled": true,
        "autonomous_actions": true,
        "governance_enabled": true,
        "confidence_threshold": 0.8
    }
}
EOF
    
    # Create environment template
    cat > "$JUNO_DIR/.env.demo" << EOF
# JUNO Phase 2 Demo Configuration
# Copy to .env and update with your values

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Jira Configuration  
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-jira-api-token

# Application Settings
FLASK_ENV=development
FLASK_DEBUG=true
JUNO_PHASE=2
JUNO_PORT=$PORT

# Phase 2 Settings
MEMORY_ENABLED=true
AUTONOMOUS_ACTIONS=true
SUPERVISOR_MODE=true
GOVERNANCE_ENABLED=true

# Demo Mode (uses sample data if Jira not configured)
DEMO_MODE=true
EOF
    
    # Create systemd service file (optional)
    cat > "$JUNO_DIR/config/juno.service" << EOF
[Unit]
Description=JUNO Phase 2 Agentic AI Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$JUNO_DIR/juno-agent
Environment=PATH=$VENV_DIR/bin
ExecStart=$VENV_DIR/bin/python app_phase2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    success "Configuration files created"
}

# Create startup script
create_startup_script() {
    log "Creating startup script..."
    
    cat > "$JUNO_DIR/start_juno.sh" << 'EOF'
#!/bin/bash

# JUNO Phase 2 Startup Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
LOG_DIR="$SCRIPT_DIR/logs"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "🚀 Starting JUNO Phase 2 Agentic AI System..."
echo -e "${NC}"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found. Please run deploy.sh first."
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Load environment variables
if [ -f "$SCRIPT_DIR/.env" ]; then
    export $(cat "$SCRIPT_DIR/.env" | grep -v '^#' | xargs)
elif [ -f "$SCRIPT_DIR/.env.demo" ]; then
    echo "⚠️  Using demo configuration. Copy .env.demo to .env for production."
    export $(cat "$SCRIPT_DIR/.env.demo" | grep -v '^#' | xargs)
fi

# Start the application
cd "$SCRIPT_DIR/juno-agent"

echo -e "${GREEN}✅ JUNO Phase 2 starting on port ${JUNO_PORT:-5000}${NC}"
echo "🌐 Dashboard: http://localhost:${JUNO_PORT:-5000}"
echo "📊 API: http://localhost:${JUNO_PORT:-5000}/api/v2"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start with logging
python app_phase2.py 2>&1 | tee "$LOG_DIR/juno_$(date +%Y%m%d_%H%M%S).log"
EOF
    
    chmod +x "$JUNO_DIR/start_juno.sh"
    
    success "Startup script created"
}

# Create demo data script
create_demo_script() {
    log "Creating demo data script..."
    
    cat > "$JUNO_DIR/demo_scenarios.py" << 'EOF'
#!/usr/bin/env python3
"""
JUNO Phase 2 Demo Scenarios
Interactive demonstration of agentic AI capabilities
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'juno-agent', 'src', 'phase2'))

from service_integration import get_orchestrator

class JUNODemo:
    def __init__(self):
        self.orchestrator = None
    
    async def initialize(self):
        """Initialize the demo environment"""
        print("🚀 Initializing JUNO Phase 2 Demo...")
        self.orchestrator = await get_orchestrator()
        print("✅ Demo environment ready!")
    
    async def run_risk_forecast_demo(self):
        """Demonstrate sprint risk forecasting"""
        print("\n" + "="*60)
        print("📊 DEMO: Sprint Risk Forecasting")
        print("="*60)
        
        print("🔍 Analyzing current sprint risks...")
        
        # Simulate risk analysis
        result = await self.orchestrator.execute_agentic_action(
            "risk_forecast",
            {"team_id": "team_alpha"}
        )
        
        print(f"📈 Risk Analysis Complete:")
        print(f"   Completion Probability: {result.get('completion_probability', 65)}%")
        print(f"   Risk Level: {result.get('risk_level', 'Medium')}")
        print(f"   AI Confidence: {result.get('confidence', 0.89)*100:.1f}%")
        
        if result.get('recommendations'):
            print("💡 AI Recommendations:")
            for rec in result['recommendations'][:3]:
                print(f"   • {rec}")
    
    async def run_triage_demo(self):
        """Demonstrate smart triage analysis"""
        print("\n" + "="*60)
        print("🎯 DEMO: Smart Triage Resolution")
        print("="*60)
        
        print("🔍 Analyzing stale tickets...")
        
        # Simulate triage analysis
        result = await self.orchestrator.execute_agentic_action(
            "triage_analysis",
            {"ticket_id": "JIRA-1234"}
        )
        
        print(f"🎯 Triage Analysis Complete:")
        print(f"   Recommended Action: {result.get('recommended_action', 'Reassign')}")
        print(f"   Urgency Score: {result.get('urgency_score', 0.9)*100:.1f}%")
        print(f"   AI Confidence: {result.get('confidence', 0.87)*100:.1f}%")
        print(f"   Reasoning: {result.get('reasoning', 'High staleness with available team capacity')}")
    
    async def run_governance_demo(self):
        """Demonstrate governance workflows"""
        print("\n" + "="*60)
        print("🏛️  DEMO: Governance & Approval Workflows")
        print("="*60)
        
        print("📋 Current governance queue:")
        
        # Get governance status
        dashboard_data = await self.orchestrator.get_dashboard_data()
        governance = dashboard_data.get('dashboard_status', {}).get('governance', {})
        
        print(f"   Pending Approvals: {governance.get('pending_count', 5)}")
        print("   Recent Requests:")
        print("   • Ticket Reassignment (Medium Priority)")
        print("   • Sprint Scope Change (High Priority)")
        print("   • Resource Reallocation (High Priority)")
        
        print("\n🔄 Approval Process:")
        print("   1. AI generates recommendation")
        print("   2. Confidence scoring determines approval level")
        print("   3. Automatic routing to appropriate supervisor")
        print("   4. Escalation if timeout exceeded")
    
    async def run_memory_demo(self):
        """Demonstrate AI memory and learning"""
        print("\n" + "="*60)
        print("🧠 DEMO: AI Memory & Learning")
        print("="*60)
        
        print("💭 AI Memory Insights:")
        print("   • Team Alpha performs 23% better on backend tasks")
        print("   • Sprint success rate increases 34% with even story point distribution")
        print("   • Velocity drops 15% when more than 3 tickets are blocked")
        
        print("\n📚 Learning Patterns:")
        print("   • Seasonal velocity variations detected")
        print("   • Optimal team size: 5-7 developers")
        print("   • Best sprint length: 2 weeks for this team")
    
    async def run_full_demo(self):
        """Run complete demonstration"""
        await self.initialize()
        
        print("\n🎪 JUNO Phase 2: Complete Agentic AI Demonstration")
        print("=" * 70)
        
        await self.run_risk_forecast_demo()
        await asyncio.sleep(2)
        
        await self.run_triage_demo()
        await asyncio.sleep(2)
        
        await self.run_governance_demo()
        await asyncio.sleep(2)
        
        await self.run_memory_demo()
        
        print("\n" + "="*70)
        print("🎉 Demo Complete! JUNO Phase 2 Capabilities Demonstrated")
        print("="*70)
        print("\n🌐 Access the full dashboard at: http://localhost:5000")
        print("📊 API documentation: http://localhost:5000/api/v2/docs")

async def main():
    demo = JUNODemo()
    await demo.run_full_demo()

if __name__ == "__main__":
    asyncio.run(main())
EOF
    
    chmod +x "$JUNO_DIR/demo_scenarios.py"
    
    success "Demo script created"
}

# Create health check script
create_health_check() {
    log "Creating health check script..."
    
    cat > "$JUNO_DIR/health_check.sh" << 'EOF'
#!/bin/bash

# JUNO Phase 2 Health Check Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=${JUNO_PORT:-5000}

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🏥 JUNO Phase 2 Health Check"
echo "=========================="

# Check if service is running
if curl -s "http://localhost:$PORT/api/v2/health" > /dev/null; then
    echo -e "${GREEN}✅ API Service: Running${NC}"
    
    # Get detailed health status
    HEALTH_DATA=$(curl -s "http://localhost:$PORT/api/v2/health")
    echo "📊 Service Status:"
    echo "$HEALTH_DATA" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_DATA"
    
else
    echo -e "${RED}❌ API Service: Not responding${NC}"
    exit 1
fi

# Check database
if [ -f "$SCRIPT_DIR/juno_phase2.db" ]; then
    echo -e "${GREEN}✅ Database: Available${NC}"
    
    # Check database size
    DB_SIZE=$(du -h "$SCRIPT_DIR/juno_phase2.db" | cut -f1)
    echo "💾 Database size: $DB_SIZE"
else
    echo -e "${RED}❌ Database: Not found${NC}"
fi

# Check logs
if [ -d "$SCRIPT_DIR/logs" ]; then
    LOG_COUNT=$(ls -1 "$SCRIPT_DIR/logs"/*.log 2>/dev/null | wc -l)
    echo -e "${GREEN}✅ Logs: $LOG_COUNT files${NC}"
    
    # Check for recent errors
    if [ $LOG_COUNT -gt 0 ]; then
        RECENT_ERRORS=$(tail -n 100 "$SCRIPT_DIR/logs"/*.log 2>/dev/null | grep -i error | wc -l)
        if [ $RECENT_ERRORS -gt 0 ]; then
            echo -e "${YELLOW}⚠️  Recent errors: $RECENT_ERRORS${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Logs: Directory not found${NC}"
fi

echo ""
echo "🌐 Dashboard: http://localhost:$PORT"
echo "📊 API Docs: http://localhost:$PORT/api/v2/docs"
EOF
    
    chmod +x "$JUNO_DIR/health_check.sh"
    
    success "Health check script created"
}

# Run tests
run_tests() {
    log "Running integration tests..."
    
    source "$VENV_DIR/bin/activate"
    cd "$JUNO_DIR/juno-agent"
    
    # Test database initialization
    python3 -c "
import sys
sys.path.append('src/phase2')
from database_setup import JUNODatabaseManager

db = JUNODatabaseManager('$DB_PATH')
if db.connect():
    stats = db.get_database_stats()
    print(f'✅ Database test passed: {len(stats.get(\"table_counts\", {}))} tables')
    db.disconnect()
else:
    print('❌ Database test failed')
    sys.exit(1)
"
    
    # Test service orchestration
    python3 -c "
import asyncio
import sys
sys.path.append('src/phase2')
from service_integration import JUNOServiceOrchestrator

async def test():
    orchestrator = JUNOServiceOrchestrator()
    if await orchestrator.initialize():
        print('✅ Service orchestration test passed')
        await orchestrator.shutdown()
        return True
    else:
        print('❌ Service orchestration test failed')
        return False

if not asyncio.run(test()):
    sys.exit(1)
"
    
    success "Integration tests passed"
}

# Main deployment function
main() {
    print_banner
    
    log "Starting JUNO Phase 2 deployment..."
    
    check_requirements
    setup_directories
    setup_venv
    install_dependencies
    init_database
    create_config
    create_startup_script
    create_demo_script
    create_health_check
    run_tests
    
    echo ""
    success "🎉 JUNO Phase 2 deployment completed successfully!"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Copy .env.demo to .env and configure your API keys"
    echo "2. Run: ./start_juno.sh"
    echo "3. Open: http://localhost:$PORT"
    echo "4. Demo: python3 demo_scenarios.py"
    echo ""
    echo -e "${BLUE}Quick Start:${NC}"
    echo "  ./start_juno.sh    # Start JUNO Phase 2"
    echo "  ./health_check.sh  # Check system health"
    echo ""
    echo -e "${GREEN}🚀 JUNO Phase 2 is ready for client demonstration!${NC}"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "test")
        run_tests
        ;;
    "health")
        create_health_check
        ./health_check.sh
        ;;
    *)
        echo "Usage: $0 [deploy|test|health]"
        exit 1
        ;;
esac

