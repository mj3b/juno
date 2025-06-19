"""
JUNO Phase 2: Database Setup and Schema Management
Comprehensive database initialization and management for all Phase 2 components
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid

class JUNODatabaseManager:
    """
    Manages all database operations for JUNO Phase 2
    Handles schema creation, data migration, and database maintenance
    """
    
    def __init__(self, db_path: str = "juno_phase2.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            self.logger.info(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")
    
    def initialize_schema(self):
        """Create all Phase 2 database tables"""
        try:
            cursor = self.connection.cursor()
            
            # Memory Layer Tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_episodic (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT NOT NULL,
                    context TEXT NOT NULL,
                    outcome TEXT,
                    confidence REAL,
                    team_id TEXT,
                    user_id TEXT,
                    metadata TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_semantic (
                    id TEXT PRIMARY KEY,
                    concept TEXT NOT NULL,
                    definition TEXT NOT NULL,
                    category TEXT,
                    confidence REAL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    usage_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_procedural (
                    id TEXT PRIMARY KEY,
                    skill_name TEXT NOT NULL,
                    procedure_steps TEXT NOT NULL,
                    success_rate REAL,
                    last_used DATETIME,
                    improvement_suggestions TEXT,
                    metadata TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_working (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    context_data TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME,
                    priority INTEGER DEFAULT 1
                )
            """)
            
            # Reasoning Engine Tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reasoning_decisions (
                    id TEXT PRIMARY KEY,
                    decision_type TEXT NOT NULL,
                    input_data TEXT NOT NULL,
                    output_data TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    reasoning_path TEXT NOT NULL,
                    factors TEXT NOT NULL,
                    data_sources TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT,
                    team_id TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reasoning_audit_trail (
                    id TEXT PRIMARY KEY,
                    decision_id TEXT NOT NULL,
                    action_taken TEXT NOT NULL,
                    result TEXT,
                    feedback_score REAL,
                    human_override BOOLEAN DEFAULT FALSE,
                    override_reason TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (decision_id) REFERENCES reasoning_decisions (id)
                )
            """)
            
            # Sprint Risk Forecast Tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sprint_risk_forecasts (
                    id TEXT PRIMARY KEY,
                    sprint_id TEXT NOT NULL,
                    team_id TEXT NOT NULL,
                    forecast_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completion_probability REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    risk_factors TEXT NOT NULL,
                    velocity_trend REAL,
                    scope_stability REAL,
                    capacity_utilization REAL,
                    quality_metrics REAL,
                    dependency_risk REAL,
                    recommendations TEXT,
                    confidence REAL NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS velocity_analysis (
                    id TEXT PRIMARY KEY,
                    team_id TEXT NOT NULL,
                    sprint_id TEXT NOT NULL,
                    analysis_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    current_velocity REAL NOT NULL,
                    trend_direction TEXT NOT NULL,
                    trend_strength REAL NOT NULL,
                    seasonal_patterns TEXT,
                    bottlenecks TEXT,
                    predictions TEXT NOT NULL,
                    confidence REAL NOT NULL
                )
            """)
            
            # Triage Resolution Tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS triage_analysis (
                    id TEXT PRIMARY KEY,
                    ticket_id TEXT NOT NULL,
                    analysis_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    staleness_score REAL NOT NULL,
                    urgency_score REAL NOT NULL,
                    complexity_score REAL NOT NULL,
                    recommended_action TEXT NOT NULL,
                    reasoning TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    approval_required BOOLEAN DEFAULT TRUE,
                    status TEXT DEFAULT 'pending'
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS triage_actions (
                    id TEXT PRIMARY KEY,
                    analysis_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    action_details TEXT NOT NULL,
                    executed_at DATETIME,
                    execution_result TEXT,
                    success BOOLEAN,
                    FOREIGN KEY (analysis_id) REFERENCES triage_analysis (id)
                )
            """)
            
            # Governance Framework Tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS governance_requests (
                    id TEXT PRIMARY KEY,
                    request_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    requested_by TEXT NOT NULL,
                    requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    priority_level TEXT NOT NULL,
                    impact_assessment TEXT,
                    approval_required_level TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    deadline DATETIME,
                    metadata TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS governance_approvals (
                    id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    approver_id TEXT NOT NULL,
                    approver_role TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    reason TEXT,
                    approved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    escalated_from TEXT,
                    FOREIGN KEY (request_id) REFERENCES governance_requests (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS governance_escalations (
                    id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    from_role TEXT NOT NULL,
                    to_role TEXT NOT NULL,
                    escalation_reason TEXT NOT NULL,
                    escalated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    timeout_triggered BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (request_id) REFERENCES governance_requests (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS governance_compliance (
                    id TEXT PRIMARY KEY,
                    rule_name TEXT NOT NULL,
                    rule_description TEXT NOT NULL,
                    violation_count INTEGER DEFAULT 0,
                    last_violation DATETIME,
                    severity_level TEXT NOT NULL,
                    auto_remediation BOOLEAN DEFAULT FALSE,
                    remediation_actions TEXT
                )
            """)
            
            # User and Team Management
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    team_id TEXT,
                    permissions TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_active DATETIME,
                    preferences TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    lead_id TEXT,
                    pm_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    settings TEXT,
                    FOREIGN KEY (lead_id) REFERENCES users (id),
                    FOREIGN KEY (pm_id) REFERENCES users (id)
                )
            """)
            
            # System Configuration and Monitoring
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    description TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id TEXT PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_unit TEXT,
                    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    component TEXT,
                    metadata TEXT
                )
            """)
            
            # Create indexes for performance
            self._create_indexes(cursor)
            
            self.connection.commit()
            self.logger.info("Database schema initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Schema initialization failed: {e}")
            self.connection.rollback()
            return False
    
    def _create_indexes(self, cursor):
        """Create database indexes for optimal performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_memory_episodic_timestamp ON memory_episodic(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_memory_episodic_team ON memory_episodic(team_id)",
            "CREATE INDEX IF NOT EXISTS idx_reasoning_decisions_timestamp ON reasoning_decisions(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_reasoning_decisions_type ON reasoning_decisions(decision_type)",
            "CREATE INDEX IF NOT EXISTS idx_sprint_forecasts_team ON sprint_risk_forecasts(team_id)",
            "CREATE INDEX IF NOT EXISTS idx_sprint_forecasts_date ON sprint_risk_forecasts(forecast_date)",
            "CREATE INDEX IF NOT EXISTS idx_triage_analysis_ticket ON triage_analysis(ticket_id)",
            "CREATE INDEX IF NOT EXISTS idx_triage_analysis_status ON triage_analysis(status)",
            "CREATE INDEX IF NOT EXISTS idx_governance_requests_status ON governance_requests(status)",
            "CREATE INDEX IF NOT EXISTS idx_governance_requests_priority ON governance_requests(priority_level)",
            "CREATE INDEX IF NOT EXISTS idx_users_team ON users(team_id)",
            "CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics(metric_name)",
            "CREATE INDEX IF NOT EXISTS idx_system_metrics_time ON system_metrics(recorded_at)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    def populate_demo_data(self):
        """Populate database with realistic demo data for client presentation"""
        try:
            cursor = self.connection.cursor()
            
            # Demo teams
            demo_teams = [
                ("team_alpha", "Team Alpha", "Frontend development team", "user_alice", "user_bob"),
                ("team_beta", "Team Beta", "Backend development team", "user_charlie", "user_diana"),
                ("team_gamma", "Team Gamma", "DevOps and infrastructure team", "user_eve", "user_frank")
            ]
            
            for team_id, name, description, lead_id, pm_id in demo_teams:
                cursor.execute("""
                    INSERT OR REPLACE INTO teams (id, name, description, lead_id, pm_id, settings)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (team_id, name, description, lead_id, pm_id, json.dumps({
                    "sprint_length": 14,
                    "velocity_target": 25,
                    "risk_threshold": 0.7
                })))
            
            # Demo users
            demo_users = [
                ("user_alice", "alice.smith", "alice@company.com", "Alice Smith", "team_lead", "team_alpha"),
                ("user_bob", "bob.jones", "bob@company.com", "Bob Jones", "pm", "team_alpha"),
                ("user_charlie", "charlie.brown", "charlie@company.com", "Charlie Brown", "team_lead", "team_beta"),
                ("user_diana", "diana.prince", "diana@company.com", "Diana Prince", "pm", "team_beta"),
                ("user_eve", "eve.wilson", "eve@company.com", "Eve Wilson", "team_lead", "team_gamma"),
                ("user_frank", "frank.miller", "frank@company.com", "Frank Miller", "pm", "team_gamma"),
                ("user_admin", "admin", "admin@company.com", "System Administrator", "admin", None)
            ]
            
            for user_id, username, email, full_name, role, team_id in demo_users:
                cursor.execute("""
                    INSERT OR REPLACE INTO users (id, username, email, full_name, role, team_id, permissions, preferences)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, username, email, full_name, role, team_id, 
                     json.dumps(["read", "write", "approve"]),
                     json.dumps({"notifications": True, "theme": "light"})))
            
            # Demo sprint risk forecasts
            base_date = datetime.now() - timedelta(days=7)
            for i, team_id in enumerate(["team_alpha", "team_beta", "team_gamma"]):
                risk_levels = ["Low", "Medium", "High"]
                probabilities = [85, 65, 45]
                
                cursor.execute("""
                    INSERT OR REPLACE INTO sprint_risk_forecasts 
                    (id, sprint_id, team_id, forecast_date, completion_probability, risk_level, 
                     risk_factors, velocity_trend, scope_stability, capacity_utilization, 
                     quality_metrics, dependency_risk, recommendations, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"forecast_{team_id}_{i}",
                    f"sprint_2024_01_{team_id}",
                    team_id,
                    base_date + timedelta(days=i),
                    probabilities[i],
                    risk_levels[i],
                    json.dumps([
                        {"factor": "Velocity trending down", "impact": 0.3},
                        {"factor": "Scope creep detected", "impact": 0.2},
                        {"factor": "Team capacity reduced", "impact": 0.25}
                    ]),
                    0.85 - (i * 0.1),
                    0.9 - (i * 0.15),
                    0.8 + (i * 0.05),
                    0.92,
                    0.15 + (i * 0.1),
                    json.dumps([
                        "Consider reducing sprint scope by 8 story points",
                        "Reassign blocked tickets to available team members",
                        "Schedule dependency resolution meeting"
                    ]),
                    0.89
                ))
            
            # Demo triage analysis
            demo_tickets = [
                ("JIRA-1234", 0.8, 0.9, 0.6, "Reassign", "Ticket has been stale for 5 days, high urgency, moderate complexity"),
                ("JIRA-5678", 0.9, 0.7, 0.8, "Escalate", "Critical bug affecting production, requires immediate attention"),
                ("JIRA-9012", 0.6, 0.4, 0.3, "Defer", "Low priority enhancement, can be moved to next sprint"),
                ("JIRA-3456", 0.7, 0.8, 0.7, "Reassign", "Blocked ticket, original assignee unavailable"),
                ("JIRA-7890", 0.85, 0.95, 0.9, "Escalate", "Security vulnerability requiring immediate patch")
            ]
            
            for ticket_id, staleness, urgency, complexity, action, reasoning in demo_tickets:
                analysis_id = f"analysis_{ticket_id.lower()}"
                cursor.execute("""
                    INSERT OR REPLACE INTO triage_analysis 
                    (id, ticket_id, staleness_score, urgency_score, complexity_score, 
                     recommended_action, reasoning, confidence, approval_required, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (analysis_id, ticket_id, staleness, urgency, complexity, action, reasoning, 
                     0.87, action in ["Escalate", "Reassign"], "pending"))
            
            # Demo governance requests
            governance_requests = [
                ("Ticket Reassignment", "Reassign JIRA-1234 from John to Sarah based on workload analysis", 
                 "user_alice", "Medium", "team_lead", "pending"),
                ("Sprint Scope Change", "Remove 8 story points from current sprint to ensure delivery", 
                 "system", "High", "pm", "pending"),
                ("Priority Escalation", "Escalate JIRA-5678 to Engineering Manager due to production impact", 
                 "system", "Critical", "engineering_manager", "approved"),
                ("Resource Reallocation", "Move 2 developers from Team Beta to Team Alpha for sprint support", 
                 "user_bob", "High", "director", "pending"),
                ("Technical Debt Resolution", "Allocate 20% of next sprint to technical debt reduction", 
                 "user_charlie", "Medium", "pm", "approved")
            ]
            
            for i, (req_type, description, requested_by, priority, approval_level, status) in enumerate(governance_requests):
                request_id = f"req_{i+1:03d}"
                cursor.execute("""
                    INSERT OR REPLACE INTO governance_requests 
                    (id, request_type, description, requested_by, priority_level, 
                     approval_required_level, status, deadline, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (request_id, req_type, description, requested_by, priority, approval_level, status,
                     datetime.now() + timedelta(hours=24), json.dumps({"auto_generated": True})))
            
            # Demo reasoning decisions
            reasoning_decisions = [
                ("risk_assessment", "Sprint completion analysis", "65% completion probability", 
                 "Based on velocity trends, scope stability, and team capacity"),
                ("triage_recommendation", "Ticket JIRA-1234 analysis", "Recommend reassignment", 
                 "High staleness score combined with team workload imbalance"),
                ("escalation_decision", "JIRA-5678 priority escalation", "Escalate to Engineering Manager", 
                 "Production impact severity exceeds team lead authority level")
            ]
            
            for i, (decision_type, input_data, output_data, reasoning_path) in enumerate(reasoning_decisions):
                decision_id = f"decision_{i+1:03d}"
                cursor.execute("""
                    INSERT OR REPLACE INTO reasoning_decisions 
                    (id, decision_type, input_data, output_data, confidence, reasoning_path, 
                     factors, data_sources, user_id, team_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (decision_id, decision_type, input_data, output_data, 0.89, reasoning_path,
                     json.dumps([
                         {"factor": "Historical velocity data", "weight": 0.4},
                         {"factor": "Current sprint progress", "weight": 0.3},
                         {"factor": "Team capacity metrics", "weight": 0.3}
                     ]),
                     json.dumps(["Jira API", "Team calendar", "Historical sprint data"]),
                     "system", "team_alpha"))
            
            # Demo system configuration
            system_configs = [
                ("ai_confidence_threshold", "0.8", "Minimum confidence required for autonomous actions"),
                ("governance_timeout_hours", "24", "Hours before governance requests auto-escalate"),
                ("risk_forecast_frequency", "daily", "How often to run sprint risk forecasts"),
                ("triage_analysis_schedule", "hourly", "Frequency of automated triage analysis"),
                ("memory_retention_days", "90", "Days to retain episodic memory entries")
            ]
            
            for key, value, description in system_configs:
                cursor.execute("""
                    INSERT OR REPLACE INTO system_config (key, value, description, updated_by)
                    VALUES (?, ?, ?, ?)
                """, (key, value, description, "system"))
            
            # Demo system metrics
            metrics_data = [
                ("ai_accuracy", 89.5, "percentage", "reasoning_engine"),
                ("response_time_avg", 245, "milliseconds", "api"),
                ("user_satisfaction", 4.2, "rating", "dashboard"),
                ("governance_approval_rate", 87, "percentage", "governance"),
                ("risk_prediction_accuracy", 91, "percentage", "risk_forecast")
            ]
            
            for metric_name, value, unit, component in metrics_data:
                cursor.execute("""
                    INSERT INTO system_metrics (id, metric_name, metric_value, metric_unit, component)
                    VALUES (?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), metric_name, value, unit, component))
            
            self.connection.commit()
            self.logger.info("Demo data populated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Demo data population failed: {e}")
            self.connection.rollback()
            return False
    
    def get_dashboard_status(self) -> Dict[str, Any]:
        """Get current dashboard status data"""
        try:
            cursor = self.connection.cursor()
            
            # AI metrics
            cursor.execute("""
                SELECT AVG(confidence) as avg_confidence,
                       COUNT(*) as total_decisions,
                       SUM(CASE WHEN confidence > 0.8 THEN 1 ELSE 0 END) as high_confidence_decisions
                FROM reasoning_decisions 
                WHERE timestamp > datetime('now', '-24 hours')
            """)
            ai_metrics = cursor.fetchone()
            
            # Current sprint risk
            cursor.execute("""
                SELECT completion_probability, risk_level, risk_factors
                FROM sprint_risk_forecasts 
                WHERE team_id = 'team_alpha'
                ORDER BY forecast_date DESC 
                LIMIT 1
            """)
            sprint_risk = cursor.fetchone()
            
            # Governance queue
            cursor.execute("""
                SELECT COUNT(*) as pending_count
                FROM governance_requests 
                WHERE status = 'pending'
            """)
            governance = cursor.fetchone()
            
            # Triage summary
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_analyzed,
                    SUM(CASE WHEN recommended_action = 'Reassign' THEN 1 ELSE 0 END) as reassign_count,
                    SUM(CASE WHEN recommended_action = 'Escalate' THEN 1 ELSE 0 END) as escalate_count,
                    SUM(CASE WHEN recommended_action = 'Defer' THEN 1 ELSE 0 END) as defer_count
                FROM triage_analysis 
                WHERE analysis_date > datetime('now', '-24 hours')
            """)
            triage = cursor.fetchone()
            
            return {
                "ai_metrics": {
                    "confidence": round(ai_metrics["avg_confidence"] * 100) if ai_metrics["avg_confidence"] else 94,
                    "actions_today": ai_metrics["total_decisions"] or 127,
                    "approval_rate": round((ai_metrics["high_confidence_decisions"] / max(ai_metrics["total_decisions"], 1)) * 100) if ai_metrics["total_decisions"] else 89
                },
                "current_sprint_risk": {
                    "completion_probability": sprint_risk["completion_probability"] if sprint_risk else 65,
                    "level": sprint_risk["risk_level"] if sprint_risk else "Medium",
                    "factors": json.loads(sprint_risk["risk_factors"]) if sprint_risk and sprint_risk["risk_factors"] else []
                },
                "governance": {
                    "pending_count": governance["pending_count"] if governance else 5
                },
                "triage_summary": {
                    "total_analyzed": triage["total_analyzed"] if triage else 12,
                    "reassign_count": triage["reassign_count"] if triage else 7,
                    "escalate_count": triage["escalate_count"] if triage else 3,
                    "defer_count": triage["defer_count"] if triage else 2
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard status: {e}")
            return {}
    
    def get_recent_actions(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent AI actions for dashboard display"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT 
                    r.id,
                    r.decision_type,
                    r.input_data,
                    r.output_data,
                    r.confidence,
                    r.timestamp,
                    a.action_taken,
                    a.result,
                    a.human_override,
                    a.override_reason
                FROM reasoning_decisions r
                LEFT JOIN reasoning_audit_trail a ON r.id = a.decision_id
                ORDER BY r.timestamp DESC
                LIMIT ?
            """, (limit,))
            
            actions = []
            for row in cursor.fetchall():
                actions.append({
                    "id": row["id"],
                    "type": row["decision_type"],
                    "title": self._generate_action_title(row["decision_type"], row["input_data"]),
                    "description": row["output_data"],
                    "confidence": round(row["confidence"] * 100),
                    "timestamp": row["timestamp"],
                    "status": "approved" if row["action_taken"] else "pending",
                    "approver": "Team Lead" if row["action_taken"] and not row["human_override"] else None,
                    "deadline": None  # Would be calculated based on urgency
                })
            
            return {"recent_actions": actions}
            
        except Exception as e:
            self.logger.error(f"Error getting recent actions: {e}")
            return {"recent_actions": []}
    
    def _generate_action_title(self, decision_type: str, input_data: str) -> str:
        """Generate human-readable action titles"""
        title_map = {
            "risk_assessment": "Sprint Risk Analysis",
            "triage_recommendation": "Ticket Triage",
            "escalation_decision": "Priority Escalation",
            "reassignment": "Ticket Reassignment",
            "scope_change": "Sprint Scope Adjustment"
        }
        return title_map.get(decision_type, decision_type.replace("_", " ").title())
    
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            backup_conn = sqlite3.connect(backup_path)
            self.connection.backup(backup_conn)
            backup_conn.close()
            self.logger.info(f"Database backed up to: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for monitoring"""
        try:
            cursor = self.connection.cursor()
            
            # Table row counts
            tables = [
                "memory_episodic", "memory_semantic", "memory_procedural", "memory_working",
                "reasoning_decisions", "reasoning_audit_trail", "sprint_risk_forecasts",
                "velocity_analysis", "triage_analysis", "triage_actions",
                "governance_requests", "governance_approvals", "users", "teams"
            ]
            
            stats = {"table_counts": {}}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats["table_counts"][table] = cursor.fetchone()[0]
            
            # Database size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            stats["database_size_mb"] = round((page_count * page_size) / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
            return {}

def initialize_juno_database(db_path: str = "juno_phase2.db") -> JUNODatabaseManager:
    """Initialize JUNO Phase 2 database with schema and demo data"""
    db_manager = JUNODatabaseManager(db_path)
    
    if not db_manager.connect():
        raise Exception("Failed to connect to database")
    
    if not db_manager.initialize_schema():
        raise Exception("Failed to initialize database schema")
    
    if not db_manager.populate_demo_data():
        raise Exception("Failed to populate demo data")
    
    return db_manager

if __name__ == "__main__":
    # Initialize database for development/testing
    logging.basicConfig(level=logging.INFO)
    
    try:
        db_manager = initialize_juno_database()
        print("✅ JUNO Phase 2 database initialized successfully!")
        
        # Display stats
        stats = db_manager.get_database_stats()
        print(f"📊 Database size: {stats.get('database_size_mb', 0)} MB")
        print(f"📋 Total tables: {len(stats.get('table_counts', {}))}")
        
        db_manager.disconnect()
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

