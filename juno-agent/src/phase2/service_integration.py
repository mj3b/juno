"""
JUNO Phase 2: Service Integration and Orchestration
Coordinates all Phase 2 components into a unified agentic AI system
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import time

# Import Phase 2 components
from juno.core.memory.memory_layer import MemoryLayer as JUNOMemoryLayer
from .reasoning_engine import JUNOReasoningEngine
from .sprint_risk_forecast import SprintRiskForecaster
from .velocity_analysis import VelocityAnalyzer
from .stale_triage_resolution import StaleTriageResolver
from .governance_framework import GovernanceFramework
from .database_setup import JUNODatabaseManager

class ServiceStatus(Enum):
    """Service status enumeration"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"
    STOPPING = "stopping"

@dataclass
class ServiceHealth:
    """Service health information"""
    status: ServiceStatus
    last_heartbeat: datetime
    error_count: int
    performance_metrics: Dict[str, float]
    uptime_seconds: float

class JUNOServiceOrchestrator:
    """
    Orchestrates all JUNO Phase 2 services and components
    Provides unified interface for agentic AI operations
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Service components
        self.db_manager = None
        self.memory_layer = None
        self.reasoning_engine = None
        self.risk_forecaster = None
        self.velocity_analyzer = None
        self.triage_resolver = None
        self.governance = None
        
        # Service management
        self.services = {}
        self.service_health = {}
        self.is_running = False
        self.start_time = None
        
        # Background tasks
        self.background_tasks = []
        self.task_scheduler = None
        
        # Event system
        self.event_handlers = {}
        self.event_queue = asyncio.Queue()
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for JUNO services"""
        return {
            "database": {
                "path": "juno_phase2.db",
                "backup_interval_hours": 24,
                "cleanup_interval_hours": 168  # 1 week
            },
            "memory": {
                "max_episodic_entries": 10000,
                "max_working_memory_mb": 100,
                "cleanup_interval_hours": 24
            },
            "reasoning": {
                "confidence_threshold": 0.8,
                "max_reasoning_depth": 5,
                "cache_size": 1000
            },
            "risk_forecast": {
                "update_interval_minutes": 60,
                "forecast_horizon_days": 14,
                "min_confidence": 0.7
            },
            "velocity_analysis": {
                "update_interval_minutes": 30,
                "trend_window_days": 30,
                "prediction_accuracy_threshold": 0.8
            },
            "triage": {
                "analysis_interval_minutes": 15,
                "staleness_threshold_hours": 48,
                "auto_execute_threshold": 0.9
            },
            "governance": {
                "approval_timeout_hours": 24,
                "escalation_enabled": True,
                "compliance_check_interval_hours": 6
            },
            "monitoring": {
                "health_check_interval_seconds": 30,
                "metrics_retention_days": 30,
                "alert_thresholds": {
                    "error_rate": 0.05,
                    "response_time_ms": 1000,
                    "memory_usage_mb": 500
                }
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize all JUNO services"""
        try:
            self.logger.info("Initializing JUNO Phase 2 Service Orchestrator...")
            
            # Initialize database
            self.db_manager = JUNODatabaseManager(self.config["database"]["path"])
            if not self.db_manager.connect():
                raise Exception("Failed to connect to database")
            
            # Initialize core components
            await self._initialize_components()
            
            # Setup event system
            self._setup_event_system()
            
            # Start background services
            await self._start_background_services()
            
            self.is_running = True
            self.start_time = datetime.now()
            
            self.logger.info("✅ JUNO Phase 2 services initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Service initialization failed: {e}")
            await self.shutdown()
            return False
    
    async def _initialize_components(self):
        """Initialize all Phase 2 components"""
        
        # Memory Layer
        self.memory_layer = JUNOMemoryLayer(
            db_manager=self.db_manager,
            config=self.config["memory"]
        )
        await self.memory_layer.initialize()
        self.services["memory"] = self.memory_layer
        
        # Reasoning Engine
        self.reasoning_engine = JUNOReasoningEngine(
            memory_layer=self.memory_layer,
            db_manager=self.db_manager,
            config=self.config["reasoning"]
        )
        await self.reasoning_engine.initialize()
        self.services["reasoning"] = self.reasoning_engine
        
        # Risk Forecaster
        self.risk_forecaster = SprintRiskForecaster(
            memory_layer=self.memory_layer,
            reasoning_engine=self.reasoning_engine,
            db_manager=self.db_manager,
            config=self.config["risk_forecast"]
        )
        await self.risk_forecaster.initialize()
        self.services["risk_forecast"] = self.risk_forecaster
        
        # Velocity Analyzer
        self.velocity_analyzer = VelocityAnalyzer(
            memory_layer=self.memory_layer,
            db_manager=self.db_manager,
            config=self.config["velocity_analysis"]
        )
        await self.velocity_analyzer.initialize()
        self.services["velocity"] = self.velocity_analyzer
        
        # Triage Resolver
        self.triage_resolver = StaleTriageResolver(
            memory_layer=self.memory_layer,
            reasoning_engine=self.reasoning_engine,
            db_manager=self.db_manager,
            config=self.config["triage"]
        )
        await self.triage_resolver.initialize()
        self.services["triage"] = self.triage_resolver
        
        # Governance Framework
        self.governance = GovernanceFramework(
            db_manager=self.db_manager,
            config=self.config["governance"]
        )
        await self.governance.initialize()
        self.services["governance"] = self.governance
        
        # Initialize service health tracking
        for service_name in self.services:
            self.service_health[service_name] = ServiceHealth(
                status=ServiceStatus.RUNNING,
                last_heartbeat=datetime.now(),
                error_count=0,
                performance_metrics={},
                uptime_seconds=0
            )
    
    def _setup_event_system(self):
        """Setup inter-service event communication"""
        
        # Risk forecast events
        self.register_event_handler("risk_level_changed", self._handle_risk_change)
        self.register_event_handler("sprint_completion_risk", self._handle_sprint_risk)
        
        # Triage events
        self.register_event_handler("stale_ticket_detected", self._handle_stale_ticket)
        self.register_event_handler("triage_action_required", self._handle_triage_action)
        
        # Governance events
        self.register_event_handler("approval_required", self._handle_approval_request)
        self.register_event_handler("escalation_triggered", self._handle_escalation)
        
        # Memory events
        self.register_event_handler("pattern_detected", self._handle_pattern_detection)
        self.register_event_handler("learning_insight", self._handle_learning_insight)
    
    async def _start_background_services(self):
        """Start background monitoring and maintenance tasks"""
        
        # Health monitoring
        self.background_tasks.append(
            asyncio.create_task(self._health_monitor_loop())
        )
        
        # Periodic risk forecasting
        self.background_tasks.append(
            asyncio.create_task(self._risk_forecast_loop())
        )
        
        # Velocity analysis updates
        self.background_tasks.append(
            asyncio.create_task(self._velocity_analysis_loop())
        )
        
        # Triage analysis
        self.background_tasks.append(
            asyncio.create_task(self._triage_analysis_loop())
        )
        
        # Governance monitoring
        self.background_tasks.append(
            asyncio.create_task(self._governance_monitor_loop())
        )
        
        # Database maintenance
        self.background_tasks.append(
            asyncio.create_task(self._database_maintenance_loop())
        )
        
        # Event processing
        self.background_tasks.append(
            asyncio.create_task(self._event_processor_loop())
        )
    
    async def _health_monitor_loop(self):
        """Monitor health of all services"""
        while self.is_running:
            try:
                for service_name, service in self.services.items():
                    health = await self._check_service_health(service_name, service)
                    self.service_health[service_name] = health
                    
                    if health.status == ServiceStatus.ERROR:
                        await self._handle_service_error(service_name, service)
                
                await asyncio.sleep(self.config["monitoring"]["health_check_interval_seconds"])
                
            except Exception as e:
                self.logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(30)
    
    async def _check_service_health(self, service_name: str, service) -> ServiceHealth:
        """Check health of individual service"""
        try:
            start_time = time.time()
            
            # Call service health check if available
            if hasattr(service, 'health_check'):
                health_result = await service.health_check()
                is_healthy = health_result.get('healthy', True)
                metrics = health_result.get('metrics', {})
            else:
                is_healthy = True
                metrics = {}
            
            response_time = (time.time() - start_time) * 1000  # ms
            metrics['response_time_ms'] = response_time
            
            current_health = self.service_health.get(service_name)
            if current_health:
                uptime = (datetime.now() - (datetime.now() - timedelta(seconds=current_health.uptime_seconds))).total_seconds()
                error_count = current_health.error_count if is_healthy else current_health.error_count + 1
            else:
                uptime = 0
                error_count = 0 if is_healthy else 1
            
            return ServiceHealth(
                status=ServiceStatus.RUNNING if is_healthy else ServiceStatus.ERROR,
                last_heartbeat=datetime.now(),
                error_count=error_count,
                performance_metrics=metrics,
                uptime_seconds=uptime
            )
            
        except Exception as e:
            self.logger.error(f"Health check failed for {service_name}: {e}")
            current_health = self.service_health.get(service_name)
            error_count = (current_health.error_count + 1) if current_health else 1
            
            return ServiceHealth(
                status=ServiceStatus.ERROR,
                last_heartbeat=datetime.now(),
                error_count=error_count,
                performance_metrics={},
                uptime_seconds=current_health.uptime_seconds if current_health else 0
            )
    
    async def _handle_service_error(self, service_name: str, service):
        """Handle service errors and attempt recovery"""
        self.logger.warning(f"Service error detected: {service_name}")
        
        # Attempt service restart if error count exceeds threshold
        health = self.service_health[service_name]
        if health.error_count > 3:
            self.logger.info(f"Attempting to restart service: {service_name}")
            try:
                if hasattr(service, 'restart'):
                    await service.restart()
                    health.error_count = 0
                    health.status = ServiceStatus.RUNNING
                    self.logger.info(f"Service restarted successfully: {service_name}")
            except Exception as e:
                self.logger.error(f"Service restart failed for {service_name}: {e}")
    
    async def _risk_forecast_loop(self):
        """Periodic risk forecasting"""
        while self.is_running:
            try:
                await self.risk_forecaster.run_forecast_analysis()
                await asyncio.sleep(self.config["risk_forecast"]["update_interval_minutes"] * 60)
            except Exception as e:
                self.logger.error(f"Risk forecast loop error: {e}")
                await asyncio.sleep(300)  # 5 minute retry
    
    async def _velocity_analysis_loop(self):
        """Periodic velocity analysis"""
        while self.is_running:
            try:
                await self.velocity_analyzer.analyze_current_velocity()
                await asyncio.sleep(self.config["velocity_analysis"]["update_interval_minutes"] * 60)
            except Exception as e:
                self.logger.error(f"Velocity analysis loop error: {e}")
                await asyncio.sleep(300)
    
    async def _triage_analysis_loop(self):
        """Periodic triage analysis"""
        while self.is_running:
            try:
                await self.triage_resolver.analyze_stale_tickets()
                await asyncio.sleep(self.config["triage"]["analysis_interval_minutes"] * 60)
            except Exception as e:
                self.logger.error(f"Triage analysis loop error: {e}")
                await asyncio.sleep(300)
    
    async def _governance_monitor_loop(self):
        """Monitor governance requests and escalations"""
        while self.is_running:
            try:
                await self.governance.process_pending_requests()
                await self.governance.check_escalations()
                await asyncio.sleep(self.config["governance"]["compliance_check_interval_hours"] * 3600)
            except Exception as e:
                self.logger.error(f"Governance monitor loop error: {e}")
                await asyncio.sleep(1800)  # 30 minute retry
    
    async def _database_maintenance_loop(self):
        """Database maintenance and cleanup"""
        while self.is_running:
            try:
                # Backup database
                backup_path = f"backup_juno_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                self.db_manager.backup_database(backup_path)
                
                # Cleanup old data
                await self._cleanup_old_data()
                
                await asyncio.sleep(self.config["database"]["backup_interval_hours"] * 3600)
            except Exception as e:
                self.logger.error(f"Database maintenance error: {e}")
                await asyncio.sleep(3600)  # 1 hour retry
    
    async def _cleanup_old_data(self):
        """Clean up old database entries"""
        try:
            cursor = self.db_manager.connection.cursor()
            
            # Clean old episodic memories
            retention_days = self.config["monitoring"]["metrics_retention_days"]
            cursor.execute("""
                DELETE FROM memory_episodic 
                WHERE timestamp < datetime('now', '-{} days')
            """.format(retention_days))
            
            # Clean old system metrics
            cursor.execute("""
                DELETE FROM system_metrics 
                WHERE recorded_at < datetime('now', '-{} days')
            """.format(retention_days))
            
            # Clean old working memory
            cursor.execute("""
                DELETE FROM memory_working 
                WHERE expires_at < datetime('now')
            """)
            
            self.db_manager.connection.commit()
            self.logger.info("Database cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Database cleanup error: {e}")
    
    async def _event_processor_loop(self):
        """Process events from the event queue"""
        while self.is_running:
            try:
                # Wait for events with timeout
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                await self._process_event(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Event processing error: {e}")
    
    async def _process_event(self, event: Dict[str, Any]):
        """Process individual event"""
        event_type = event.get("type")
        handlers = self.event_handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                self.logger.error(f"Event handler error for {event_type}: {e}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit event to the event queue"""
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        await self.event_queue.put(event)
    
    # Event handlers
    async def _handle_risk_change(self, event: Dict[str, Any]):
        """Handle risk level changes"""
        data = event["data"]
        risk_level = data.get("risk_level")
        team_id = data.get("team_id")
        
        if risk_level == "High":
            # Trigger governance request for intervention
            await self.governance.create_request(
                request_type="Risk Intervention",
                description=f"High risk detected for team {team_id}",
                priority="High",
                approval_level="pm"
            )
    
    async def _handle_sprint_risk(self, event: Dict[str, Any]):
        """Handle sprint completion risk"""
        data = event["data"]
        completion_probability = data.get("completion_probability", 0)
        
        if completion_probability < 0.6:
            # Trigger automatic triage analysis
            await self.triage_resolver.analyze_stale_tickets()
    
    async def _handle_stale_ticket(self, event: Dict[str, Any]):
        """Handle stale ticket detection"""
        data = event["data"]
        ticket_id = data.get("ticket_id")
        staleness_score = data.get("staleness_score", 0)
        
        if staleness_score > 0.8:
            # Store in memory for pattern recognition
            await self.memory_layer.store_episodic_memory(
                event_type="stale_ticket_detected",
                context=f"Ticket {ticket_id} became stale",
                outcome="pending_resolution",
                confidence=staleness_score
            )
    
    async def _handle_triage_action(self, event: Dict[str, Any]):
        """Handle triage action requirements"""
        data = event["data"]
        action_type = data.get("action_type")
        confidence = data.get("confidence", 0)
        
        if confidence > self.config["triage"]["auto_execute_threshold"]:
            # Auto-execute high confidence actions
            await self.triage_resolver.execute_action(data)
        else:
            # Request governance approval
            await self.governance.create_request(
                request_type="Triage Action",
                description=f"Approval required for {action_type}",
                priority="Medium",
                approval_level="team_lead"
            )
    
    async def _handle_approval_request(self, event: Dict[str, Any]):
        """Handle approval requests"""
        data = event["data"]
        # Log approval request for monitoring
        self.logger.info(f"Approval request: {data.get('description')}")
    
    async def _handle_escalation(self, event: Dict[str, Any]):
        """Handle escalation events"""
        data = event["data"]
        # Log escalation for monitoring
        self.logger.warning(f"Escalation triggered: {data.get('reason')}")
    
    async def _handle_pattern_detection(self, event: Dict[str, Any]):
        """Handle pattern detection from memory layer"""
        data = event["data"]
        pattern_type = data.get("pattern_type")
        confidence = data.get("confidence", 0)
        
        if confidence > 0.8:
            # Store high-confidence patterns as insights
            await self.memory_layer.store_semantic_memory(
                concept=f"pattern_{pattern_type}",
                definition=data.get("description", ""),
                category="behavioral_pattern",
                confidence=confidence
            )
    
    async def _handle_learning_insight(self, event: Dict[str, Any]):
        """Handle learning insights"""
        data = event["data"]
        # Log learning insights for dashboard display
        self.logger.info(f"Learning insight: {data.get('insight')}")
    
    # Public API methods
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "overall_status": "running" if self.is_running else "stopped",
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "services": {
                name: {
                    "status": health.status.value,
                    "last_heartbeat": health.last_heartbeat.isoformat(),
                    "error_count": health.error_count,
                    "performance_metrics": health.performance_metrics,
                    "uptime_seconds": health.uptime_seconds
                }
                for name, health in self.service_health.items()
            },
            "database_stats": self.db_manager.get_database_stats(),
            "active_background_tasks": len(self.background_tasks)
        }
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard display"""
        return {
            "status": await self.get_system_status(),
            "dashboard_status": self.db_manager.get_dashboard_status(),
            "recent_actions": self.db_manager.get_recent_actions(),
            "memory_insights": await self.memory_layer.get_insights() if self.memory_layer else {}
        }
    
    async def execute_agentic_action(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agentic AI action with full reasoning and governance"""
        try:
            # Generate reasoning for the action
            reasoning = await self.reasoning_engine.generate_reasoning(
                decision_type=action_type,
                input_data=parameters,
                context={"timestamp": datetime.now().isoformat()}
            )
            
            # Check if governance approval is required
            approval_required = reasoning.confidence < self.config["reasoning"]["confidence_threshold"]
            
            if approval_required:
                # Create governance request
                request_id = await self.governance.create_request(
                    request_type=action_type,
                    description=f"AI-recommended action: {action_type}",
                    priority="Medium",
                    approval_level="team_lead",
                    metadata={"reasoning": reasoning.to_dict(), "parameters": parameters}
                )
                
                return {
                    "status": "pending_approval",
                    "request_id": request_id,
                    "reasoning": reasoning.to_dict(),
                    "confidence": reasoning.confidence
                }
            else:
                # Execute action directly
                result = await self._execute_action(action_type, parameters, reasoning)
                
                # Store in audit trail
                await self.reasoning_engine.store_audit_trail(
                    decision_id=reasoning.id,
                    action_taken=action_type,
                    result=json.dumps(result),
                    feedback_score=None
                )
                
                return {
                    "status": "executed",
                    "result": result,
                    "reasoning": reasoning.to_dict(),
                    "confidence": reasoning.confidence
                }
                
        except Exception as e:
            self.logger.error(f"Agentic action execution failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _execute_action(self, action_type: str, parameters: Dict[str, Any], reasoning) -> Dict[str, Any]:
        """Execute the actual action based on type"""
        if action_type == "triage_analysis":
            return await self.triage_resolver.analyze_ticket(parameters.get("ticket_id"))
        elif action_type == "risk_forecast":
            return await self.risk_forecaster.forecast_sprint_risk(parameters.get("team_id"))
        elif action_type == "velocity_analysis":
            return await self.velocity_analyzer.analyze_team_velocity(parameters.get("team_id"))
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    async def shutdown(self):
        """Gracefully shutdown all services"""
        self.logger.info("Shutting down JUNO Phase 2 services...")
        
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Shutdown services
        for service_name, service in self.services.items():
            try:
                if hasattr(service, 'shutdown'):
                    await service.shutdown()
                self.logger.info(f"Service {service_name} shutdown complete")
            except Exception as e:
                self.logger.error(f"Error shutting down {service_name}: {e}")
        
        # Close database connection
        if self.db_manager:
            self.db_manager.disconnect()
        
        self.logger.info("✅ JUNO Phase 2 shutdown complete")

# Global orchestrator instance
_orchestrator_instance = None

async def get_orchestrator(config: Dict[str, Any] = None) -> JUNOServiceOrchestrator:
    """Get or create the global orchestrator instance"""
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        _orchestrator_instance = JUNOServiceOrchestrator(config)
        await _orchestrator_instance.initialize()
    
    return _orchestrator_instance

async def shutdown_orchestrator():
    """Shutdown the global orchestrator instance"""
    global _orchestrator_instance
    
    if _orchestrator_instance:
        await _orchestrator_instance.shutdown()
        _orchestrator_instance = None

if __name__ == "__main__":
    # Test orchestrator initialization
    async def test_orchestrator():
        logging.basicConfig(level=logging.INFO)
        
        orchestrator = JUNOServiceOrchestrator()
        
        if await orchestrator.initialize():
            print("✅ JUNO Phase 2 Orchestrator initialized successfully!")
            
            # Test system status
            status = await orchestrator.get_system_status()
            print(f"📊 System status: {status['overall_status']}")
            print(f"🔧 Active services: {len(status['services'])}")
            
            # Test dashboard data
            dashboard_data = await orchestrator.get_dashboard_data()
            print(f"📋 Dashboard data loaded: {len(dashboard_data)} sections")
            
            await orchestrator.shutdown()
        else:
            print("❌ Orchestrator initialization failed")
    
    asyncio.run(test_orchestrator())

