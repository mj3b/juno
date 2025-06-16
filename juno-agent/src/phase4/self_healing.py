"""
JUNO Phase 4: Self-Healing Infrastructure
Production-grade self-healing and predictive scaling system
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import random
import numpy as np
from collections import deque

logger = logging.getLogger(__name__)

class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class HealingAction(Enum):
    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    FAILOVER = "failover"
    CLEAR_CACHE = "clear_cache"
    RESTART_DEPENDENCIES = "restart_dependencies"
    ROLLBACK_DEPLOYMENT = "rollback_deployment"
    ISOLATE_COMPONENT = "isolate_component"

@dataclass
class HealthMetrics:
    timestamp: datetime
    service_id: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_latency_ms: float
    error_rate: float
    response_time_ms: float
    throughput_rps: float
    active_connections: int
    queue_length: int

@dataclass
class Incident:
    incident_id: str
    service_id: str
    severity: IncidentSeverity
    description: str
    timestamp: datetime
    symptoms: List[str]
    root_cause: Optional[str]
    healing_actions: List[HealingAction]
    resolution_time: Optional[timedelta]
    auto_resolved: bool

@dataclass
class PredictionMetrics:
    timestamp: datetime
    predicted_cpu: float
    predicted_memory: float
    predicted_throughput: float
    confidence: float
    time_horizon_minutes: int

class SelfHealingManager:
    """
    Production-grade self-healing infrastructure management
    Provides automatic incident detection, diagnosis, and resolution
    """
    
    def __init__(self):
        # Health monitoring
        self.health_history: Dict[str, deque] = {}
        self.health_thresholds = {
            "cpu_usage": {"warning": 70.0, "critical": 90.0},
            "memory_usage": {"warning": 75.0, "critical": 95.0},
            "disk_usage": {"warning": 80.0, "critical": 95.0},
            "error_rate": {"warning": 0.05, "critical": 0.15},
            "response_time_ms": {"warning": 500.0, "critical": 2000.0},
            "network_latency_ms": {"warning": 100.0, "critical": 500.0}
        }
        
        # Incident management
        self.active_incidents: Dict[str, Incident] = {}
        self.incident_history: List[Incident] = []
        self.healing_strategies: Dict[str, List[HealingAction]] = {}
        
        # Predictive scaling
        self.prediction_models: Dict[str, Any] = {}
        self.scaling_policies: Dict[str, Dict[str, Any]] = {}
        self.prediction_history: Dict[str, deque] = {}
        
        # Configuration
        self.monitoring_interval = 30  # seconds
        self.healing_timeout = 300     # 5 minutes
        self.prediction_interval = 60  # 1 minute
        self.history_retention = 1440  # 24 hours of data points
        
        # Metrics
        self.metrics = {
            "incidents_detected": 0,
            "incidents_auto_resolved": 0,
            "avg_resolution_time_seconds": 0.0,
            "healing_success_rate": 0.0,
            "predictions_made": 0,
            "scaling_actions_taken": 0,
            "mttr_seconds": 0.0,  # Mean Time To Recovery
            "mtbf_hours": 0.0     # Mean Time Between Failures
        }
        
        self.running = False
        self.services = ["agent-1", "agent-2", "coordinator", "database", "api-gateway"]
        
        # Initialize healing strategies
        self._initialize_healing_strategies()
        self._initialize_scaling_policies()
    
    async def start(self):
        """Start the self-healing manager"""
        self.running = True
        logger.info("Starting self-healing infrastructure manager")
        
        # Start monitoring and healing loops
        asyncio.create_task(self._health_monitoring_loop())
        asyncio.create_task(self._incident_detection_loop())
        asyncio.create_task(self._healing_execution_loop())
        asyncio.create_task(self._predictive_scaling_loop())
        asyncio.create_task(self._metrics_update_loop())
    
    async def stop(self):
        """Stop the self-healing manager"""
        self.running = False
        logger.info("Self-healing infrastructure manager stopped")
    
    def _initialize_healing_strategies(self):
        """Initialize healing strategies for different types of issues"""
        self.healing_strategies = {
            "high_cpu": [HealingAction.SCALE_UP, HealingAction.RESTART_SERVICE],
            "high_memory": [HealingAction.CLEAR_CACHE, HealingAction.RESTART_SERVICE, HealingAction.SCALE_UP],
            "high_disk": [HealingAction.CLEAR_CACHE, HealingAction.SCALE_UP],
            "high_error_rate": [HealingAction.RESTART_SERVICE, HealingAction.ROLLBACK_DEPLOYMENT],
            "high_latency": [HealingAction.RESTART_DEPENDENCIES, HealingAction.SCALE_UP],
            "service_down": [HealingAction.RESTART_SERVICE, HealingAction.FAILOVER],
            "dependency_failure": [HealingAction.RESTART_DEPENDENCIES, HealingAction.ISOLATE_COMPONENT]
        }
    
    def _initialize_scaling_policies(self):
        """Initialize predictive scaling policies"""
        self.scaling_policies = {
            "cpu_based": {
                "scale_up_threshold": 70.0,
                "scale_down_threshold": 30.0,
                "min_instances": 2,
                "max_instances": 10,
                "cooldown_minutes": 5
            },
            "memory_based": {
                "scale_up_threshold": 75.0,
                "scale_down_threshold": 40.0,
                "min_instances": 2,
                "max_instances": 8,
                "cooldown_minutes": 5
            },
            "throughput_based": {
                "scale_up_threshold": 1000.0,  # RPS
                "scale_down_threshold": 200.0,
                "min_instances": 1,
                "max_instances": 15,
                "cooldown_minutes": 3
            }
        }
    
    async def _health_monitoring_loop(self):
        """Continuous health monitoring loop"""
        while self.running:
            try:
                for service_id in self.services:
                    metrics = await self._collect_health_metrics(service_id)
                    await self._store_health_metrics(service_id, metrics)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _incident_detection_loop(self):
        """Incident detection and classification loop"""
        while self.running:
            try:
                for service_id in self.services:
                    incidents = await self._detect_incidents(service_id)
                    
                    for incident in incidents:
                        if incident.incident_id not in self.active_incidents:
                            await self._register_incident(incident)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in incident detection loop: {e}")
                await asyncio.sleep(10)
    
    async def _healing_execution_loop(self):
        """Healing execution loop"""
        while self.running:
            try:
                for incident_id, incident in list(self.active_incidents.items()):
                    if not incident.auto_resolved:
                        success = await self._execute_healing(incident)
                        
                        if success:
                            await self._resolve_incident(incident_id)
                
                await asyncio.sleep(15)  # Check every 15 seconds
                
            except Exception as e:
                logger.error(f"Error in healing execution loop: {e}")
                await asyncio.sleep(10)
    
    async def _predictive_scaling_loop(self):
        """Predictive scaling loop"""
        while self.running:
            try:
                for service_id in self.services:
                    predictions = await self._generate_predictions(service_id)
                    
                    if predictions:
                        await self._evaluate_scaling_needs(service_id, predictions)
                
                await asyncio.sleep(self.prediction_interval)
                
            except Exception as e:
                logger.error(f"Error in predictive scaling loop: {e}")
                await asyncio.sleep(30)
    
    async def _collect_health_metrics(self, service_id: str) -> HealthMetrics:
        """Collect health metrics for a service"""
        try:
            # In production, this would collect real metrics from monitoring systems
            # For demo, we'll simulate realistic health metrics
            
            base_cpu = 45 + random.uniform(-20, 30)
            base_memory = 60 + random.uniform(-25, 25)
            base_disk = 40 + random.uniform(-15, 20)
            base_latency = 50 + random.uniform(-20, 40)
            base_error_rate = 0.02 + random.uniform(-0.015, 0.03)
            base_response_time = 150 + random.uniform(-50, 100)
            base_throughput = 500 + random.uniform(-100, 200)
            base_connections = 100 + random.randint(-30, 50)
            base_queue = 5 + random.randint(-3, 8)
            
            # Occasionally simulate issues
            if random.random() < 0.1:  # 10% chance of issues
                issue_type = random.choice(["cpu_spike", "memory_leak", "disk_full", "network_issue"])
                
                if issue_type == "cpu_spike":
                    base_cpu = 85 + random.uniform(0, 15)
                elif issue_type == "memory_leak":
                    base_memory = 90 + random.uniform(0, 10)
                elif issue_type == "disk_full":
                    base_disk = 95 + random.uniform(0, 5)
                elif issue_type == "network_issue":
                    base_latency = 300 + random.uniform(0, 200)
                    base_error_rate = 0.1 + random.uniform(0, 0.1)
            
            metrics = HealthMetrics(
                timestamp=datetime.now(),
                service_id=service_id,
                cpu_usage=max(0, min(100, base_cpu)),
                memory_usage=max(0, min(100, base_memory)),
                disk_usage=max(0, min(100, base_disk)),
                network_latency_ms=max(1, base_latency),
                error_rate=max(0, min(1, base_error_rate)),
                response_time_ms=max(10, base_response_time),
                throughput_rps=max(0, base_throughput),
                active_connections=max(0, base_connections),
                queue_length=max(0, base_queue)
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting health metrics for {service_id}: {e}")
            return HealthMetrics(
                timestamp=datetime.now(),
                service_id=service_id,
                cpu_usage=50.0,
                memory_usage=60.0,
                disk_usage=40.0,
                network_latency_ms=50.0,
                error_rate=0.02,
                response_time_ms=150.0,
                throughput_rps=500.0,
                active_connections=100,
                queue_length=5
            )
    
    async def _store_health_metrics(self, service_id: str, metrics: HealthMetrics):
        """Store health metrics for analysis"""
        try:
            if service_id not in self.health_history:
                self.health_history[service_id] = deque(maxlen=self.history_retention)
            
            self.health_history[service_id].append(metrics)
            
        except Exception as e:
            logger.error(f"Error storing health metrics for {service_id}: {e}")
    
    async def _detect_incidents(self, service_id: str) -> List[Incident]:
        """Detect incidents based on health metrics"""
        incidents = []
        
        try:
            if service_id not in self.health_history or len(self.health_history[service_id]) == 0:
                return incidents
            
            latest_metrics = self.health_history[service_id][-1]
            
            # Check for threshold violations
            symptoms = []
            severity = IncidentSeverity.LOW
            
            # CPU issues
            if latest_metrics.cpu_usage > self.health_thresholds["cpu_usage"]["critical"]:
                symptoms.append(f"Critical CPU usage: {latest_metrics.cpu_usage:.1f}%")
                severity = IncidentSeverity.CRITICAL
            elif latest_metrics.cpu_usage > self.health_thresholds["cpu_usage"]["warning"]:
                symptoms.append(f"High CPU usage: {latest_metrics.cpu_usage:.1f}%")
                severity = max(severity, IncidentSeverity.MEDIUM)
            
            # Memory issues
            if latest_metrics.memory_usage > self.health_thresholds["memory_usage"]["critical"]:
                symptoms.append(f"Critical memory usage: {latest_metrics.memory_usage:.1f}%")
                severity = IncidentSeverity.CRITICAL
            elif latest_metrics.memory_usage > self.health_thresholds["memory_usage"]["warning"]:
                symptoms.append(f"High memory usage: {latest_metrics.memory_usage:.1f}%")
                severity = max(severity, IncidentSeverity.MEDIUM)
            
            # Disk issues
            if latest_metrics.disk_usage > self.health_thresholds["disk_usage"]["critical"]:
                symptoms.append(f"Critical disk usage: {latest_metrics.disk_usage:.1f}%")
                severity = IncidentSeverity.CRITICAL
            elif latest_metrics.disk_usage > self.health_thresholds["disk_usage"]["warning"]:
                symptoms.append(f"High disk usage: {latest_metrics.disk_usage:.1f}%")
                severity = max(severity, IncidentSeverity.MEDIUM)
            
            # Error rate issues
            if latest_metrics.error_rate > self.health_thresholds["error_rate"]["critical"]:
                symptoms.append(f"Critical error rate: {latest_metrics.error_rate:.3f}")
                severity = IncidentSeverity.CRITICAL
            elif latest_metrics.error_rate > self.health_thresholds["error_rate"]["warning"]:
                symptoms.append(f"High error rate: {latest_metrics.error_rate:.3f}")
                severity = max(severity, IncidentSeverity.HIGH)
            
            # Response time issues
            if latest_metrics.response_time_ms > self.health_thresholds["response_time_ms"]["critical"]:
                symptoms.append(f"Critical response time: {latest_metrics.response_time_ms:.1f}ms")
                severity = IncidentSeverity.CRITICAL
            elif latest_metrics.response_time_ms > self.health_thresholds["response_time_ms"]["warning"]:
                symptoms.append(f"High response time: {latest_metrics.response_time_ms:.1f}ms")
                severity = max(severity, IncidentSeverity.MEDIUM)
            
            # Network latency issues
            if latest_metrics.network_latency_ms > self.health_thresholds["network_latency_ms"]["critical"]:
                symptoms.append(f"Critical network latency: {latest_metrics.network_latency_ms:.1f}ms")
                severity = IncidentSeverity.CRITICAL
            elif latest_metrics.network_latency_ms > self.health_thresholds["network_latency_ms"]["warning"]:
                symptoms.append(f"High network latency: {latest_metrics.network_latency_ms:.1f}ms")
                severity = max(severity, IncidentSeverity.MEDIUM)
            
            # Create incident if symptoms detected
            if symptoms:
                incident_id = f"incident-{service_id}-{int(latest_metrics.timestamp.timestamp())}"
                
                # Determine healing actions based on symptoms
                healing_actions = self._determine_healing_actions(symptoms)
                
                incident = Incident(
                    incident_id=incident_id,
                    service_id=service_id,
                    severity=severity,
                    description=f"Health issues detected in {service_id}",
                    timestamp=latest_metrics.timestamp,
                    symptoms=symptoms,
                    root_cause=None,
                    healing_actions=healing_actions,
                    resolution_time=None,
                    auto_resolved=False
                )
                
                incidents.append(incident)
            
            return incidents
            
        except Exception as e:
            logger.error(f"Error detecting incidents for {service_id}: {e}")
            return []
    
    def _determine_healing_actions(self, symptoms: List[str]) -> List[HealingAction]:
        """Determine appropriate healing actions based on symptoms"""
        actions = []
        
        try:
            for symptom in symptoms:
                if "CPU usage" in symptom:
                    actions.extend(self.healing_strategies["high_cpu"])
                elif "memory usage" in symptom:
                    actions.extend(self.healing_strategies["high_memory"])
                elif "disk usage" in symptom:
                    actions.extend(self.healing_strategies["high_disk"])
                elif "error rate" in symptom:
                    actions.extend(self.healing_strategies["high_error_rate"])
                elif "response time" in symptom or "latency" in symptom:
                    actions.extend(self.healing_strategies["high_latency"])
            
            # Remove duplicates while preserving order
            unique_actions = []
            for action in actions:
                if action not in unique_actions:
                    unique_actions.append(action)
            
            return unique_actions[:3]  # Limit to top 3 actions
            
        except Exception as e:
            logger.error(f"Error determining healing actions: {e}")
            return [HealingAction.RESTART_SERVICE]
    
    async def _register_incident(self, incident: Incident):
        """Register a new incident"""
        try:
            self.active_incidents[incident.incident_id] = incident
            self.incident_history.append(incident)
            self.metrics["incidents_detected"] += 1
            
            logger.warning(f"INCIDENT REGISTERED: {incident.incident_id} "
                          f"({incident.severity.value}) - {incident.description}")
            
            # Log symptoms
            for symptom in incident.symptoms:
                logger.warning(f"  Symptom: {symptom}")
            
        except Exception as e:
            logger.error(f"Error registering incident: {e}")
    
    async def _execute_healing(self, incident: Incident) -> bool:
        """Execute healing actions for an incident"""
        try:
            logger.info(f"Executing healing for incident: {incident.incident_id}")
            
            for action in incident.healing_actions:
                success = await self._execute_healing_action(action, incident.service_id)
                
                if success:
                    logger.info(f"Healing action successful: {action.value}")
                    
                    # Wait a bit for the action to take effect
                    await asyncio.sleep(30)
                    
                    # Check if the issue is resolved
                    if await self._verify_healing(incident):
                        logger.info(f"Incident resolved: {incident.incident_id}")
                        return True
                else:
                    logger.warning(f"Healing action failed: {action.value}")
                
                # Wait before trying next action
                await asyncio.sleep(10)
            
            logger.error(f"All healing actions failed for incident: {incident.incident_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error executing healing for {incident.incident_id}: {e}")
            return False
    
    async def _execute_healing_action(self, action: HealingAction, service_id: str) -> bool:
        """Execute a specific healing action"""
        try:
            logger.info(f"Executing healing action: {action.value} for {service_id}")
            
            # Simulate healing action execution
            await asyncio.sleep(2)
            
            # Simulate success/failure (85% success rate)
            success = random.random() > 0.15
            
            if success:
                logger.info(f"Healing action {action.value} completed successfully")
            else:
                logger.warning(f"Healing action {action.value} failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error executing healing action {action.value}: {e}")
            return False
    
    async def _verify_healing(self, incident: Incident) -> bool:
        """Verify if healing was successful"""
        try:
            # Collect fresh metrics
            metrics = await self._collect_health_metrics(incident.service_id)
            
            # Check if the issues that caused the incident are resolved
            for symptom in incident.symptoms:
                if "CPU usage" in symptom and metrics.cpu_usage > self.health_thresholds["cpu_usage"]["warning"]:
                    return False
                elif "memory usage" in symptom and metrics.memory_usage > self.health_thresholds["memory_usage"]["warning"]:
                    return False
                elif "disk usage" in symptom and metrics.disk_usage > self.health_thresholds["disk_usage"]["warning"]:
                    return False
                elif "error rate" in symptom and metrics.error_rate > self.health_thresholds["error_rate"]["warning"]:
                    return False
                elif "response time" in symptom and metrics.response_time_ms > self.health_thresholds["response_time_ms"]["warning"]:
                    return False
                elif "latency" in symptom and metrics.network_latency_ms > self.health_thresholds["network_latency_ms"]["warning"]:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying healing for {incident.incident_id}: {e}")
            return False
    
    async def _resolve_incident(self, incident_id: str):
        """Resolve an incident"""
        try:
            if incident_id in self.active_incidents:
                incident = self.active_incidents[incident_id]
                incident.auto_resolved = True
                incident.resolution_time = datetime.now() - incident.timestamp
                
                del self.active_incidents[incident_id]
                
                self.metrics["incidents_auto_resolved"] += 1
                
                logger.info(f"Incident resolved: {incident_id} "
                           f"(resolution time: {incident.resolution_time.total_seconds():.1f}s)")
            
        except Exception as e:
            logger.error(f"Error resolving incident {incident_id}: {e}")
    
    async def _generate_predictions(self, service_id: str) -> Optional[PredictionMetrics]:
        """Generate predictions for service metrics"""
        try:
            if (service_id not in self.health_history or 
                len(self.health_history[service_id]) < 10):
                return None
            
            # Simple prediction based on recent trends
            recent_metrics = list(self.health_history[service_id])[-10:]
            
            # Calculate trends
            cpu_values = [m.cpu_usage for m in recent_metrics]
            memory_values = [m.memory_usage for m in recent_metrics]
            throughput_values = [m.throughput_rps for m in recent_metrics]
            
            # Simple linear trend prediction
            cpu_trend = (cpu_values[-1] - cpu_values[0]) / len(cpu_values)
            memory_trend = (memory_values[-1] - memory_values[0]) / len(memory_values)
            throughput_trend = (throughput_values[-1] - throughput_values[0]) / len(throughput_values)
            
            # Predict 15 minutes ahead
            time_horizon = 15
            predicted_cpu = cpu_values[-1] + (cpu_trend * time_horizon)
            predicted_memory = memory_values[-1] + (memory_trend * time_horizon)
            predicted_throughput = throughput_values[-1] + (throughput_trend * time_horizon)
            
            # Calculate confidence based on trend consistency
            cpu_variance = np.var(cpu_values)
            confidence = max(0.1, min(0.9, 1.0 - (cpu_variance / 100)))
            
            predictions = PredictionMetrics(
                timestamp=datetime.now(),
                predicted_cpu=max(0, min(100, predicted_cpu)),
                predicted_memory=max(0, min(100, predicted_memory)),
                predicted_throughput=max(0, predicted_throughput),
                confidence=confidence,
                time_horizon_minutes=time_horizon
            )
            
            # Store prediction
            if service_id not in self.prediction_history:
                self.prediction_history[service_id] = deque(maxlen=100)
            self.prediction_history[service_id].append(predictions)
            
            self.metrics["predictions_made"] += 1
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating predictions for {service_id}: {e}")
            return None
    
    async def _evaluate_scaling_needs(self, service_id: str, predictions: PredictionMetrics):
        """Evaluate if scaling is needed based on predictions"""
        try:
            scaling_needed = False
            action = None
            
            # Check CPU-based scaling
            cpu_policy = self.scaling_policies["cpu_based"]
            if predictions.predicted_cpu > cpu_policy["scale_up_threshold"]:
                scaling_needed = True
                action = "scale_up"
            elif predictions.predicted_cpu < cpu_policy["scale_down_threshold"]:
                scaling_needed = True
                action = "scale_down"
            
            # Check memory-based scaling
            memory_policy = self.scaling_policies["memory_based"]
            if predictions.predicted_memory > memory_policy["scale_up_threshold"]:
                scaling_needed = True
                action = "scale_up"
            elif predictions.predicted_memory < memory_policy["scale_down_threshold"] and action != "scale_up":
                scaling_needed = True
                action = "scale_down"
            
            # Check throughput-based scaling
            throughput_policy = self.scaling_policies["throughput_based"]
            if predictions.predicted_throughput > throughput_policy["scale_up_threshold"]:
                scaling_needed = True
                action = "scale_up"
            elif predictions.predicted_throughput < throughput_policy["scale_down_threshold"] and action != "scale_up":
                scaling_needed = True
                action = "scale_down"
            
            if scaling_needed and predictions.confidence > 0.6:
                await self._execute_scaling_action(service_id, action, predictions)
            
        except Exception as e:
            logger.error(f"Error evaluating scaling needs for {service_id}: {e}")
    
    async def _execute_scaling_action(self, service_id: str, action: str, predictions: PredictionMetrics):
        """Execute predictive scaling action"""
        try:
            logger.info(f"Executing predictive scaling: {action} for {service_id} "
                       f"(confidence: {predictions.confidence:.2f})")
            
            # Simulate scaling action
            await asyncio.sleep(1)
            
            self.metrics["scaling_actions_taken"] += 1
            
            logger.info(f"Predictive scaling completed: {action} for {service_id}")
            
        except Exception as e:
            logger.error(f"Error executing scaling action for {service_id}: {e}")
    
    async def _metrics_update_loop(self):
        """Update metrics periodically"""
        while self.running:
            try:
                # Calculate MTTR (Mean Time To Recovery)
                resolved_incidents = [i for i in self.incident_history if i.auto_resolved and i.resolution_time]
                if resolved_incidents:
                    total_resolution_time = sum(i.resolution_time.total_seconds() for i in resolved_incidents)
                    self.metrics["mttr_seconds"] = total_resolution_time / len(resolved_incidents)
                    self.metrics["avg_resolution_time_seconds"] = self.metrics["mttr_seconds"]
                
                # Calculate healing success rate
                if self.metrics["incidents_detected"] > 0:
                    self.metrics["healing_success_rate"] = (
                        self.metrics["incidents_auto_resolved"] / self.metrics["incidents_detected"]
                    ) * 100
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
                await asyncio.sleep(30)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get self-healing metrics"""
        return {
            **self.metrics,
            "active_incidents": len(self.active_incidents),
            "mttr_seconds": round(self.metrics["mttr_seconds"], 2),
            "healing_success_rate": round(self.metrics["healing_success_rate"], 2)
        }
    
    def get_active_incidents(self) -> List[Incident]:
        """Get currently active incidents"""
        return list(self.active_incidents.values())
    
    def get_incident_history(self, hours: int = 24) -> List[Incident]:
        """Get incident history for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [i for i in self.incident_history if i.timestamp >= cutoff_time]
    
    def get_service_health(self, service_id: str) -> Optional[HealthMetrics]:
        """Get latest health metrics for a service"""
        if service_id in self.health_history and self.health_history[service_id]:
            return self.health_history[service_id][-1]
        return None
    
    def get_predictions(self, service_id: str) -> Optional[PredictionMetrics]:
        """Get latest predictions for a service"""
        if service_id in self.prediction_history and self.prediction_history[service_id]:
            return self.prediction_history[service_id][-1]
        return None

# Example usage
async def main():
    """Example usage of self-healing manager"""
    
    manager = SelfHealingManager()
    await manager.start()
    
    # Let it run for a while to detect and heal issues
    await asyncio.sleep(300)  # 5 minutes
    
    # Print metrics
    metrics = manager.get_metrics()
    print(f"Self-healing metrics: {json.dumps(metrics, indent=2)}")
    
    # Print active incidents
    active_incidents = manager.get_active_incidents()
    print(f"Active incidents: {len(active_incidents)}")
    for incident in active_incidents:
        print(f"  {incident.incident_id} ({incident.severity.value}) - {incident.description}")
    
    # Print recent incident history
    recent_incidents = manager.get_incident_history(1)  # Last hour
    print(f"Recent incidents: {len(recent_incidents)}")
    for incident in recent_incidents[-5:]:  # Last 5 incidents
        resolution_time = incident.resolution_time.total_seconds() if incident.resolution_time else "ongoing"
        print(f"  {incident.incident_id} - {incident.description} (resolved in {resolution_time}s)")
    
    await manager.stop()

if __name__ == "__main__":
    asyncio.run(main())

