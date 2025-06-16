"""
JUNO Phase 3: Service Discovery and Health Monitoring
Production-grade service discovery for multi-agent coordination
"""

import asyncio
import json
import time
import aiohttp
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPING = "stopping"

@dataclass
class ServiceInstance:
    service_id: str
    agent_id: str
    host: str
    port: int
    status: ServiceStatus
    capabilities: List[str]
    metadata: Dict[str, str]
    last_heartbeat: datetime
    registration_time: datetime
    health_check_url: str
    load_metrics: Dict[str, float]

@dataclass
class HealthCheck:
    service_id: str
    status: ServiceStatus
    response_time_ms: float
    error_message: Optional[str]
    timestamp: datetime

class ServiceDiscovery:
    """
    Production-grade service discovery and health monitoring
    Handles agent registration, health checks, and load balancing
    """
    
    def __init__(self, discovery_port: int = 8500):
        self.discovery_port = discovery_port
        self.services: Dict[str, ServiceInstance] = {}
        self.health_checks: Dict[str, List[HealthCheck]] = {}
        
        # Configuration
        self.health_check_interval = 30  # seconds
        self.health_check_timeout = 5    # seconds
        self.unhealthy_threshold = 3     # failed checks
        self.cleanup_interval = 300      # 5 minutes
        
        # Metrics
        self.metrics = {
            "total_services": 0,
            "healthy_services": 0,
            "unhealthy_services": 0,
            "health_checks_performed": 0,
            "avg_response_time_ms": 0.0,
            "service_registrations": 0,
            "service_deregistrations": 0
        }
        
        self.running = False
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def start(self):
        """Start the service discovery system"""
        self.running = True
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.health_check_timeout)
        )
        
        logger.info(f"Starting service discovery on port {self.discovery_port}")
        
        # Start background tasks
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._cleanup_loop())
        asyncio.create_task(self._metrics_update_loop())
    
    async def stop(self):
        """Stop the service discovery system"""
        self.running = False
        if self._session:
            await self._session.close()
        logger.info("Service discovery stopped")
    
    async def register_service(self, service: ServiceInstance) -> bool:
        """Register a new service instance"""
        try:
            service.registration_time = datetime.now()
            service.last_heartbeat = datetime.now()
            service.status = ServiceStatus.STARTING
            
            self.services[service.service_id] = service
            self.health_checks[service.service_id] = []
            
            self.metrics["service_registrations"] += 1
            self.metrics["total_services"] = len(self.services)
            
            logger.info(f"Registered service: {service.service_id} ({service.agent_id})")
            
            # Perform initial health check
            await self._perform_health_check(service.service_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {service.service_id}: {e}")
            return False
    
    async def deregister_service(self, service_id: str) -> bool:
        """Deregister a service instance"""
        try:
            if service_id in self.services:
                service = self.services[service_id]
                service.status = ServiceStatus.STOPPING
                
                del self.services[service_id]
                del self.health_checks[service_id]
                
                self.metrics["service_deregistrations"] += 1
                self.metrics["total_services"] = len(self.services)
                
                logger.info(f"Deregistered service: {service_id}")
                return True
            else:
                logger.warning(f"Service not found for deregistration: {service_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to deregister service {service_id}: {e}")
            return False
    
    async def update_heartbeat(self, service_id: str, load_metrics: Dict[str, float] = None) -> bool:
        """Update service heartbeat and load metrics"""
        try:
            if service_id in self.services:
                service = self.services[service_id]
                service.last_heartbeat = datetime.now()
                
                if load_metrics:
                    service.load_metrics.update(load_metrics)
                
                logger.debug(f"Updated heartbeat for service: {service_id}")
                return True
            else:
                logger.warning(f"Service not found for heartbeat update: {service_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update heartbeat for {service_id}: {e}")
            return False
    
    async def discover_services(self, capability: str = None, status: ServiceStatus = None) -> List[ServiceInstance]:
        """Discover services by capability and status"""
        try:
            services = []
            
            for service in self.services.values():
                # Filter by capability
                if capability and capability not in service.capabilities:
                    continue
                
                # Filter by status
                if status and service.status != status:
                    continue
                
                services.append(service)
            
            # Sort by load (lowest first) for load balancing
            services.sort(key=lambda s: s.load_metrics.get("cpu_usage", 0.0))
            
            logger.debug(f"Discovered {len(services)} services (capability: {capability}, status: {status})")
            return services
            
        except Exception as e:
            logger.error(f"Failed to discover services: {e}")
            return []
    
    async def get_service(self, service_id: str) -> Optional[ServiceInstance]:
        """Get specific service instance"""
        return self.services.get(service_id)
    
    async def get_healthy_services(self, capability: str = None) -> List[ServiceInstance]:
        """Get all healthy services with optional capability filter"""
        return await self.discover_services(capability=capability, status=ServiceStatus.HEALTHY)
    
    async def select_service_for_load_balancing(self, capability: str) -> Optional[ServiceInstance]:
        """Select best service for load balancing based on current load"""
        healthy_services = await self.get_healthy_services(capability)
        
        if not healthy_services:
            return None
        
        # Select service with lowest combined load score
        def calculate_load_score(service: ServiceInstance) -> float:
            cpu = service.load_metrics.get("cpu_usage", 0.0)
            memory = service.load_metrics.get("memory_usage", 0.0)
            active_tasks = service.load_metrics.get("active_tasks", 0.0)
            
            # Weighted load score
            return (cpu * 0.4) + (memory * 0.3) + (active_tasks * 0.3)
        
        best_service = min(healthy_services, key=calculate_load_score)
        logger.debug(f"Selected service {best_service.service_id} for load balancing")
        
        return best_service
    
    async def _health_check_loop(self):
        """Background health check loop"""
        while self.running:
            try:
                # Perform health checks for all services
                for service_id in list(self.services.keys()):
                    await self._perform_health_check(service_id)
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(5)
    
    async def _perform_health_check(self, service_id: str):
        """Perform health check for a specific service"""
        try:
            service = self.services.get(service_id)
            if not service:
                return
            
            start_time = time.time()
            health_check = HealthCheck(
                service_id=service_id,
                status=ServiceStatus.UNKNOWN,
                response_time_ms=0.0,
                error_message=None,
                timestamp=datetime.now()
            )
            
            try:
                # Perform HTTP health check
                async with self._session.get(service.health_check_url) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        health_check.status = ServiceStatus.HEALTHY
                        service.status = ServiceStatus.HEALTHY
                    else:
                        health_check.status = ServiceStatus.UNHEALTHY
                        health_check.error_message = f"HTTP {response.status}"
                    
                    health_check.response_time_ms = response_time_ms
                    
            except Exception as e:
                health_check.status = ServiceStatus.UNHEALTHY
                health_check.error_message = str(e)
                health_check.response_time_ms = (time.time() - start_time) * 1000
            
            # Store health check result
            if service_id not in self.health_checks:
                self.health_checks[service_id] = []
            
            self.health_checks[service_id].append(health_check)
            
            # Keep only recent health checks (last 10)
            self.health_checks[service_id] = self.health_checks[service_id][-10:]
            
            # Update service status based on recent health checks
            await self._update_service_status(service_id)
            
            self.metrics["health_checks_performed"] += 1
            
            logger.debug(f"Health check for {service_id}: {health_check.status.value} "
                        f"({health_check.response_time_ms:.1f}ms)")
            
        except Exception as e:
            logger.error(f"Failed to perform health check for {service_id}: {e}")
    
    async def _update_service_status(self, service_id: str):
        """Update service status based on recent health checks"""
        try:
            service = self.services.get(service_id)
            health_checks = self.health_checks.get(service_id, [])
            
            if not service or not health_checks:
                return
            
            # Check recent health checks
            recent_checks = health_checks[-self.unhealthy_threshold:]
            unhealthy_count = sum(1 for check in recent_checks 
                                if check.status == ServiceStatus.UNHEALTHY)
            
            # Update status based on threshold
            if unhealthy_count >= self.unhealthy_threshold:
                if service.status != ServiceStatus.UNHEALTHY:
                    service.status = ServiceStatus.UNHEALTHY
                    logger.warning(f"Service {service_id} marked as unhealthy")
            else:
                if service.status == ServiceStatus.UNHEALTHY:
                    service.status = ServiceStatus.HEALTHY
                    logger.info(f"Service {service_id} recovered to healthy")
            
        except Exception as e:
            logger.error(f"Failed to update service status for {service_id}: {e}")
    
    async def _cleanup_loop(self):
        """Background cleanup loop for stale services"""
        while self.running:
            try:
                current_time = datetime.now()
                stale_services = []
                
                for service_id, service in self.services.items():
                    # Check if service hasn't sent heartbeat recently
                    time_since_heartbeat = current_time - service.last_heartbeat
                    if time_since_heartbeat > timedelta(seconds=self.cleanup_interval):
                        stale_services.append(service_id)
                
                # Remove stale services
                for service_id in stale_services:
                    logger.warning(f"Removing stale service: {service_id}")
                    await self.deregister_service(service_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(10)
    
    async def _metrics_update_loop(self):
        """Background metrics update loop"""
        while self.running:
            try:
                # Update service count metrics
                healthy_count = sum(1 for s in self.services.values() 
                                  if s.status == ServiceStatus.HEALTHY)
                unhealthy_count = sum(1 for s in self.services.values() 
                                    if s.status == ServiceStatus.UNHEALTHY)
                
                self.metrics["healthy_services"] = healthy_count
                self.metrics["unhealthy_services"] = unhealthy_count
                
                # Calculate average response time
                all_response_times = []
                for checks in self.health_checks.values():
                    all_response_times.extend([check.response_time_ms for check in checks[-5:]])
                
                if all_response_times:
                    self.metrics["avg_response_time_ms"] = sum(all_response_times) / len(all_response_times)
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in metrics update loop: {e}")
                await asyncio.sleep(10)
    
    def get_metrics(self) -> Dict[str, any]:
        """Get current service discovery metrics"""
        return {
            **self.metrics,
            "services_by_status": {
                status.value: sum(1 for s in self.services.values() if s.status == status)
                for status in ServiceStatus
            },
            "services_by_capability": self._get_capability_distribution(),
            "avg_response_time_ms": round(self.metrics["avg_response_time_ms"], 2)
        }
    
    def _get_capability_distribution(self) -> Dict[str, int]:
        """Get distribution of services by capability"""
        capability_count = {}
        for service in self.services.values():
            for capability in service.capabilities:
                capability_count[capability] = capability_count.get(capability, 0) + 1
        return capability_count
    
    def get_service_status(self) -> Dict[str, Dict[str, any]]:
        """Get detailed status of all services"""
        return {
            service_id: {
                "service": asdict(service),
                "recent_health_checks": [
                    asdict(check) for check in self.health_checks.get(service_id, [])[-3:]
                ]
            }
            for service_id, service in self.services.items()
        }

# Example usage
async def main():
    """Example usage of service discovery"""
    
    discovery = ServiceDiscovery()
    await discovery.start()
    
    # Register some test services
    services = [
        ServiceInstance(
            service_id="agent-1-risk-analyzer",
            agent_id="agent-1",
            host="localhost",
            port=8001,
            status=ServiceStatus.STARTING,
            capabilities=["risk_analysis", "sprint_forecasting"],
            metadata={"version": "2.0", "region": "us-east-1"},
            last_heartbeat=datetime.now(),
            registration_time=datetime.now(),
            health_check_url="http://localhost:8001/health",
            load_metrics={"cpu_usage": 25.0, "memory_usage": 40.0, "active_tasks": 3.0}
        ),
        ServiceInstance(
            service_id="agent-2-task-coordinator",
            agent_id="agent-2",
            host="localhost",
            port=8002,
            status=ServiceStatus.STARTING,
            capabilities=["task_coordination", "workflow_management"],
            metadata={"version": "2.0", "region": "us-east-1"},
            last_heartbeat=datetime.now(),
            registration_time=datetime.now(),
            health_check_url="http://localhost:8002/health",
            load_metrics={"cpu_usage": 15.0, "memory_usage": 30.0, "active_tasks": 1.0}
        )
    ]
    
    for service in services:
        await discovery.register_service(service)
    
    # Wait a bit for health checks
    await asyncio.sleep(2)
    
    # Discover services
    risk_analyzers = await discovery.discover_services(capability="risk_analysis")
    print(f"Found {len(risk_analyzers)} risk analysis services")
    
    # Load balancing
    best_coordinator = await discovery.select_service_for_load_balancing("task_coordination")
    if best_coordinator:
        print(f"Selected coordinator: {best_coordinator.service_id}")
    
    # Print metrics
    metrics = discovery.get_metrics()
    print(f"Service discovery metrics: {json.dumps(metrics, indent=2)}")
    
    await discovery.stop()

if __name__ == "__main__":
    asyncio.run(main())

