"""
JUNO Phase 2: Main Flask Application
Complete agentic AI application with web dashboard, API endpoints, and governance integration.
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
from typing import Dict, List, Any, Optional

# Import Phase 2 components
from src.phase2.memory_layer import MemoryLayer, MemoryType, MemoryEntry
from src.phase2.reasoning_engine import ReasoningEngine, ReasoningLevel, DecisionContext
from src.phase2.sprint_risk_forecast import SprintRiskForecaster, RiskLevel
from src.phase2.velocity_analysis import VelocityAnalyzer, TrendDirection
from src.phase2.stale_triage_resolution import StaleTriageEngine, TriageAction, StalenessLevel
from src.phase2.governance_framework import (
    GovernanceRoleManager, ApprovalWorkflowEngine, ComplianceMonitor, 
    GovernanceDashboard, GovernanceRole, GovernanceAction, ActionCategory
)

# Import Phase 1 components for backward compatibility
from src.jira_connector import JiraConnector
from src.analytics_engine import AnalyticsEngine
from src.enterprise_gpt_integration import EnterpriseGPTIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/juno/application.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JUNOPhase2App:
    """
    Main JUNO Phase 2 application with complete agentic AI capabilities.
    """
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = os.getenv('SECRET_KEY', 'juno-phase2-secret-key')
        
        # Enable CORS for API access
        CORS(self.app)
        
        # Initialize Phase 2 components
        self.memory_layer = MemoryLayer()
        self.reasoning_engine = ReasoningEngine()
        self.risk_forecaster = SprintRiskForecaster()
        self.velocity_analyzer = VelocityAnalyzer()
        self.triage_engine = StaleTriageEngine()
        
        # Initialize governance system
        self.role_manager = GovernanceRoleManager()
        self.workflow_engine = ApprovalWorkflowEngine(self.role_manager)
        self.compliance_monitor = ComplianceMonitor()
        self.governance_dashboard = GovernanceDashboard(self.workflow_engine, self.compliance_monitor)
        
        # Initialize Phase 1 components for backward compatibility
        self.jira_connector = JiraConnector()
        self.analytics_engine = AnalyticsEngine()
        self.gpt_integration = EnterpriseGPTIntegration()
        
        # Setup routes
        self._setup_routes()
        
        # Initialize database
        self._init_database()
        
        logger.info("JUNO Phase 2 Application initialized successfully")
    
    def _init_database(self):
        """Initialize Phase 2 database tables."""
        try:
            # Create database connection
            conn = sqlite3.connect('juno_phase2.db')
            cursor = conn.cursor()
            
            # Create memories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_id TEXT UNIQUE NOT NULL,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    context TEXT,
                    confidence REAL,
                    created_at TIMESTAMP,
                    team_id TEXT,
                    tags TEXT
                )
            ''')
            
            # Create audit log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    decision_id TEXT NOT NULL,
                    decision_type TEXT NOT NULL,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    reasoning TEXT,
                    confidence REAL,
                    outcome TEXT,
                    metadata TEXT
                )
            ''')
            
            # Create governance actions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS governance_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_id TEXT UNIQUE NOT NULL,
                    action_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    proposed_by TEXT NOT NULL,
                    team_id TEXT NOT NULL,
                    impact_level TEXT NOT NULL,
                    confidence_score REAL,
                    reasoning TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            ''')
            
            # Create approval requests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS approval_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT UNIQUE NOT NULL,
                    action_id TEXT NOT NULL,
                    approver_role TEXT NOT NULL,
                    approver_id TEXT,
                    status TEXT DEFAULT 'pending',
                    priority TEXT,
                    deadline TIMESTAMP,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    approval_reason TEXT,
                    rejection_reason TEXT
                )
            ''')
            
            # Create team preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS team_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id TEXT UNIQUE NOT NULL,
                    preferences TEXT NOT NULL,
                    updated_at TIMESTAMP
                )
            ''')
            
            # Create users table for governance
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    teams TEXT,
                    created_at TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _setup_routes(self):
        """Setup all application routes."""
        
        # Main dashboard routes
        @self.app.route('/')
        def index():
            """Main dashboard - redirect based on phase."""
            phase = os.getenv('JUNO_PHASE', '1')
            if phase == '2':
                return redirect(url_for('phase2_dashboard'))
            else:
                return redirect(url_for('phase1_dashboard'))
        
        @self.app.route('/phase1')
        def phase1_dashboard():
            """Phase 1 dashboard - analytics and insights."""
            return render_template('phase1/dashboard.html', 
                                 title="JUNO Phase 1 - AI Analyst")
        
        @self.app.route('/phase2')
        def phase2_dashboard():
            """Phase 2 dashboard - agentic workflow manager."""
            user_id = session.get('user_id', 'demo_user')
            role = session.get('user_role', 'TEAM_LEAD')
            
            # Get dashboard data
            dashboard_data = self.governance_dashboard.get_dashboard_data(
                user_id, GovernanceRole(role.lower())
            )
            
            return render_template('phase2/dashboard.html', 
                                 title="JUNO Phase 2 - Agentic Workflow Manager",
                                 dashboard_data=dashboard_data)
        
        # Health and status endpoints
        @self.app.route('/health')
        def health_check():
            """Application health check."""
            return jsonify({
                "status": "healthy",
                "phase": os.getenv('JUNO_PHASE', '1'),
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "memory_layer": "operational",
                    "reasoning_engine": "operational",
                    "risk_forecaster": "operational",
                    "governance": "operational"
                }
            })
        
        @self.app.route('/api/v2/status')
        def api_status():
            """API status and capabilities."""
            return jsonify({
                "api_version": "2.0",
                "phase": "2",
                "capabilities": {
                    "memory_learning": True,
                    "transparent_reasoning": True,
                    "risk_forecasting": True,
                    "autonomous_actions": True,
                    "governance_workflows": True
                },
                "endpoints": {
                    "risk_forecast": "/api/v2/risk/forecast",
                    "triage_analysis": "/api/v2/triage/analyze",
                    "governance": "/api/v2/governance",
                    "memory": "/api/v2/memory",
                    "reasoning": "/api/v2/reasoning"
                }
            })
        
        # Phase 2 API endpoints
        self._setup_risk_api()
        self._setup_triage_api()
        self._setup_governance_api()
        self._setup_memory_api()
        self._setup_reasoning_api()
        
        # Phase 1 compatibility endpoints
        self._setup_phase1_api()
    
    def _setup_risk_api(self):
        """Setup risk forecasting API endpoints."""
        
        @self.app.route('/api/v2/risk/forecast/<sprint_id>')
        def get_risk_forecast(sprint_id):
            """Get risk forecast for specific sprint."""
            try:
                # Get sprint data from Jira
                sprint_data = self.jira_connector.get_sprint_data(sprint_id)
                
                if not sprint_data:
                    return jsonify({"error": "Sprint not found"}), 404
                
                # Generate risk assessment
                risk_assessment = self.risk_forecaster.predict_sprint_risk(sprint_data)
                
                # Generate reasoning
                context = DecisionContext(
                    decision_type="risk_forecast",
                    input_data=sprint_data,
                    team_context={"team": sprint_data.get("team_id")},
                    historical_data=[]
                )
                
                reasoning = self.reasoning_engine.generate_reasoning(context, ReasoningLevel.DETAILED)
                
                return jsonify({
                    "sprint_id": sprint_id,
                    "risk_assessment": risk_assessment,
                    "reasoning": {
                        "explanation": reasoning.explanation,
                        "confidence": reasoning.confidence,
                        "factors": reasoning.factors
                    },
                    "recommendations": self.risk_forecaster.generate_mitigation_recommendations(risk_assessment),
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Risk forecast error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/v2/risk/teams/<team_id>')
        def get_team_risk_overview(team_id):
            """Get risk overview for team."""
            try:
                # Get active sprints for team
                active_sprints = self.jira_connector.get_active_sprints(team_id)
                
                team_risks = []
                for sprint in active_sprints:
                    sprint_data = self.jira_connector.get_sprint_data(sprint['id'])
                    risk_assessment = self.risk_forecaster.predict_sprint_risk(sprint_data)
                    team_risks.append({
                        "sprint_id": sprint['id'],
                        "sprint_name": sprint['name'],
                        "overall_risk": risk_assessment["overall_risk"],
                        "completion_probability": risk_assessment["completion_probability"]
                    })
                
                return jsonify({
                    "team_id": team_id,
                    "active_sprints": len(active_sprints),
                    "risks": team_risks,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Team risk overview error: {e}")
                return jsonify({"error": str(e)}), 500
    
    def _setup_triage_api(self):
        """Setup triage resolution API endpoints."""
        
        @self.app.route('/api/v2/triage/analyze', methods=['POST'])
        def analyze_stale_tickets():
            """Analyze stale tickets and generate recommendations."""
            try:
                data = request.get_json()
                team_id = data.get('team_id')
                
                if not team_id:
                    return jsonify({"error": "team_id required"}), 400
                
                # Get stale tickets from Jira
                stale_tickets = self.jira_connector.get_stale_tickets(team_id)
                
                # Analyze tickets
                recommendations = self.triage_engine.analyze_stale_tickets(stale_tickets)
                
                # Format response
                response = {
                    "team_id": team_id,
                    "analyzed_tickets": len(stale_tickets),
                    "recommendations": [],
                    "timestamp": datetime.now().isoformat()
                }
                
                for rec in recommendations:
                    response["recommendations"].append({
                        "ticket_id": rec.ticket_id,
                        "recommended_action": rec.recommended_action.value,
                        "confidence": rec.confidence,
                        "reasoning": rec.reasoning,
                        "urgency_score": rec.urgency_score,
                        "approval_required": rec.approval_required,
                        "auto_executable": rec.auto_executable
                    })
                
                return jsonify(response)
                
            except Exception as e:
                logger.error(f"Triage analysis error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/v2/triage/execute', methods=['POST'])
        def execute_triage_action():
            """Execute approved triage action."""
            try:
                data = request.get_json()
                ticket_id = data.get('ticket_id')
                action = data.get('action')
                user_id = session.get('user_id', 'demo_user')
                
                if not ticket_id or not action:
                    return jsonify({"error": "ticket_id and action required"}), 400
                
                # Create governance action
                governance_action = GovernanceAction(
                    action_id=f"triage_{ticket_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    action_type=action,
                    category=ActionCategory.TICKET_MANAGEMENT,
                    description=f"Execute {action} on ticket {ticket_id}",
                    proposed_by="juno_ai",
                    team_id=data.get('team_id', 'default'),
                    impact_level=data.get('impact_level', 'medium'),
                    confidence_score=data.get('confidence', 0.8),
                    reasoning=data.get('reasoning', ''),
                    data_sources=["jira_api"],
                    affected_tickets=[ticket_id],
                    estimated_impact={},
                    requires_approval=True,
                    approval_threshold=0.7,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=24),
                    metadata=data
                )
                
                # Submit for approval
                request_id = self.workflow_engine.submit_for_approval(governance_action)
                
                return jsonify({
                    "ticket_id": ticket_id,
                    "action": action,
                    "request_id": request_id,
                    "status": "submitted_for_approval",
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Triage execution error: {e}")
                return jsonify({"error": str(e)}), 500
    
    def _setup_governance_api(self):
        """Setup governance API endpoints."""
        
        @self.app.route('/api/v2/governance/pending')
        def get_pending_approvals():
            """Get pending approval requests."""
            try:
                user_role = session.get('user_role', 'TEAM_LEAD')
                role = GovernanceRole(user_role.lower())
                
                pending_requests = self.workflow_engine.get_pending_approvals(role)
                
                response = {
                    "pending_count": len(pending_requests),
                    "requests": [],
                    "timestamp": datetime.now().isoformat()
                }
                
                for req in pending_requests:
                    response["requests"].append({
                        "request_id": req.request_id,
                        "action_id": req.action_id,
                        "priority": req.priority,
                        "deadline": req.deadline.isoformat(),
                        "created_at": req.created_at.isoformat(),
                        "status": req.status.value
                    })
                
                return jsonify(response)
                
            except Exception as e:
                logger.error(f"Governance pending error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/v2/governance/approve', methods=['POST'])
        def approve_request():
            """Approve or reject governance request."""
            try:
                data = request.get_json()
                request_id = data.get('request_id')
                approved = data.get('approved', False)
                reason = data.get('reason', '')
                user_id = session.get('user_id', 'demo_user')
                
                if not request_id:
                    return jsonify({"error": "request_id required"}), 400
                
                # Process approval
                success = self.workflow_engine.process_approval(
                    request_id, user_id, approved, reason
                )
                
                if success:
                    return jsonify({
                        "request_id": request_id,
                        "approved": approved,
                        "reason": reason,
                        "processed_by": user_id,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    return jsonify({"error": "Failed to process approval"}), 400
                
            except Exception as e:
                logger.error(f"Governance approval error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/v2/governance/dashboard/<user_id>')
        def get_governance_dashboard(user_id):
            """Get governance dashboard data."""
            try:
                user_role = session.get('user_role', 'TEAM_LEAD')
                role = GovernanceRole(user_role.lower())
                
                dashboard_data = self.governance_dashboard.get_dashboard_data(user_id, role)
                
                return jsonify(dashboard_data)
                
            except Exception as e:
                logger.error(f"Governance dashboard error: {e}")
                return jsonify({"error": str(e)}), 500
    
    def _setup_memory_api(self):
        """Setup memory layer API endpoints."""
        
        @self.app.route('/api/v2/memory/store', methods=['POST'])
        def store_memory():
            """Store new memory entry."""
            try:
                data = request.get_json()
                
                memory_entry = MemoryEntry(
                    entry_id=data.get('entry_id'),
                    memory_type=MemoryType(data.get('memory_type')),
                    content=data.get('content'),
                    context=data.get('context', {}),
                    confidence=data.get('confidence', 1.0),
                    created_at=datetime.now()
                )
                
                self.memory_layer.store_memory(memory_entry)
                
                return jsonify({
                    "entry_id": memory_entry.entry_id,
                    "status": "stored",
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Memory storage error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/v2/memory/retrieve/<memory_type>')
        def retrieve_memories(memory_type):
            """Retrieve memories by type."""
            try:
                context_filter = request.args.to_dict()
                
                memories = self.memory_layer.retrieve_memories(
                    MemoryType(memory_type), context_filter
                )
                
                response = {
                    "memory_type": memory_type,
                    "count": len(memories),
                    "memories": [],
                    "timestamp": datetime.now().isoformat()
                }
                
                for memory in memories:
                    response["memories"].append({
                        "entry_id": memory.entry_id,
                        "content": memory.content,
                        "context": memory.context,
                        "confidence": memory.confidence,
                        "created_at": memory.created_at.isoformat()
                    })
                
                return jsonify(response)
                
            except Exception as e:
                logger.error(f"Memory retrieval error: {e}")
                return jsonify({"error": str(e)}), 500
    
    def _setup_reasoning_api(self):
        """Setup reasoning engine API endpoints."""
        
        @self.app.route('/api/v2/reasoning/explain', methods=['POST'])
        def generate_reasoning():
            """Generate reasoning explanation for decision."""
            try:
                data = request.get_json()
                
                context = DecisionContext(
                    decision_type=data.get('decision_type'),
                    input_data=data.get('input_data', {}),
                    team_context=data.get('team_context', {}),
                    historical_data=data.get('historical_data', [])
                )
                
                level = ReasoningLevel(data.get('level', 'detailed'))
                reasoning = self.reasoning_engine.generate_reasoning(context, level)
                
                return jsonify({
                    "decision_type": context.decision_type,
                    "reasoning": {
                        "explanation": reasoning.explanation,
                        "confidence": reasoning.confidence,
                        "factors": reasoning.factors,
                        "data_sources": reasoning.data_sources
                    },
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Reasoning generation error: {e}")
                return jsonify({"error": str(e)}), 500
    
    def _setup_phase1_api(self):
        """Setup Phase 1 compatibility API endpoints."""
        
        @self.app.route('/api/v1/analytics/<team_id>')
        def get_team_analytics(team_id):
            """Phase 1 team analytics endpoint."""
            try:
                analytics_data = self.analytics_engine.get_team_analytics(team_id)
                return jsonify(analytics_data)
            except Exception as e:
                logger.error(f"Phase 1 analytics error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/v1/query', methods=['POST'])
        def process_nlp_query():
            """Phase 1 NLP query endpoint."""
            try:
                data = request.get_json()
                query = data.get('query')
                
                response = self.gpt_integration.process_query(query)
                return jsonify(response)
            except Exception as e:
                logger.error(f"Phase 1 query error: {e}")
                return jsonify({"error": str(e)}), 500
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application."""
        logger.info(f"Starting JUNO Phase 2 on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


# Application factory
def create_app():
    """Create and configure JUNO Phase 2 application."""
    return JUNOPhase2App()


if __name__ == '__main__':
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create and run application
    juno_app = create_app()
    
    # Run in development mode
    juno_app.run(debug=True)

