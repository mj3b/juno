"""
JUNO Phase 4: ML-Based Threat Detection
Production-grade machine learning threat detection system
"""

import asyncio
import numpy as np
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import random
from collections import deque
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    RESOURCE_ABUSE = "resource_abuse"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    DENIAL_OF_SERVICE = "denial_of_service"
    MALICIOUS_PAYLOAD = "malicious_payload"

@dataclass
class ThreatEvent:
    threat_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    confidence_score: float
    timestamp: datetime
    source_ip: str
    affected_service: str
    description: str
    indicators: Dict[str, Any]
    raw_data: Dict[str, Any]

@dataclass
class SecurityMetrics:
    timestamp: datetime
    request_rate: float
    error_rate: float
    response_time_ms: float
    cpu_usage: float
    memory_usage: float
    network_io: float
    failed_auth_attempts: int
    unique_ips: int
    payload_size_bytes: int

class MLThreatDetector:
    """
    Production-grade ML-based threat detection system
    Uses multiple ML models to detect various types of security threats
    """
    
    def __init__(self):
        # ML Models
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        
        # Model state
        self.is_trained = False
        self.training_data = deque(maxlen=10000)
        self.feature_names = [
            "request_rate", "error_rate", "response_time_ms",
            "cpu_usage", "memory_usage", "network_io",
            "failed_auth_attempts", "unique_ips", "payload_size_bytes"
        ]
        
        # Threat detection configuration
        self.detection_interval = 30  # seconds
        self.training_interval = 3600  # 1 hour
        self.min_training_samples = 100
        self.threat_threshold = -0.5  # Anomaly score threshold
        
        # Threat patterns (rule-based detection)
        self.threat_patterns = {
            ThreatType.RESOURCE_ABUSE: {
                "cpu_threshold": 90.0,
                "memory_threshold": 95.0,
                "request_rate_threshold": 1000.0
            },
            ThreatType.UNAUTHORIZED_ACCESS: {
                "failed_auth_threshold": 10,
                "unique_ip_threshold": 100
            },
            ThreatType.DENIAL_OF_SERVICE: {
                "request_rate_spike": 5.0,  # 5x normal rate
                "error_rate_threshold": 0.5
            },
            ThreatType.DATA_EXFILTRATION: {
                "payload_size_threshold": 10485760,  # 10MB
                "network_io_threshold": 1073741824   # 1GB
            }
        }
        
        # Metrics and state
        self.detected_threats = []
        self.metrics = {
            "threats_detected": 0,
            "false_positives": 0,
            "true_positives": 0,
            "detection_accuracy": 0.0,
            "avg_detection_time_ms": 0.0,
            "model_training_count": 0,
            "last_training_time": None
        }
        
        self.running = False
        self.baseline_metrics = None
    
    async def start(self):
        """Start the threat detection system"""
        self.running = True
        logger.info("Starting ML threat detection system")
        
        # Start detection loops
        asyncio.create_task(self._detection_loop())
        asyncio.create_task(self._training_loop())
        asyncio.create_task(self._baseline_update_loop())
    
    async def stop(self):
        """Stop the threat detection system"""
        self.running = False
        logger.info("ML threat detection system stopped")
    
    async def _detection_loop(self):
        """Main threat detection loop"""
        while self.running:
            try:
                # Collect current metrics
                current_metrics = await self._collect_security_metrics()
                
                # Store for training
                self.training_data.append(current_metrics)
                
                # Perform threat detection
                threats = await self._detect_threats(current_metrics)
                
                # Process detected threats
                for threat in threats:
                    await self._process_threat(threat)
                
                await asyncio.sleep(self.detection_interval)
                
            except Exception as e:
                logger.error(f"Error in detection loop: {e}")
                await asyncio.sleep(10)
    
    async def _training_loop(self):
        """Background model training loop"""
        while self.running:
            try:
                if (len(self.training_data) >= self.min_training_samples and
                    (not self.is_trained or 
                     (self.metrics["last_training_time"] and
                      (datetime.now() - self.metrics["last_training_time"]).total_seconds() > self.training_interval))):
                    
                    await self._train_models()
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in training loop: {e}")
                await asyncio.sleep(60)
    
    async def _baseline_update_loop(self):
        """Update baseline metrics for comparison"""
        while self.running:
            try:
                if len(self.training_data) >= 50:
                    await self._update_baseline_metrics()
                
                await asyncio.sleep(600)  # Update every 10 minutes
                
            except Exception as e:
                logger.error(f"Error in baseline update loop: {e}")
                await asyncio.sleep(60)
    
    async def _collect_security_metrics(self) -> SecurityMetrics:
        """Collect current security metrics"""
        try:
            # In production, this would collect real metrics from monitoring systems
            # For demo, we'll simulate realistic security metrics
            
            base_request_rate = 100 + random.uniform(-20, 30)
            base_error_rate = 0.02 + random.uniform(-0.01, 0.03)
            base_response_time = 150 + random.uniform(-30, 50)
            base_cpu = 45 + random.uniform(-15, 25)
            base_memory = 60 + random.uniform(-20, 20)
            base_network_io = 1048576 + random.uniform(-200000, 500000)  # ~1MB
            base_failed_auth = random.randint(0, 5)
            base_unique_ips = 50 + random.randint(-10, 20)
            base_payload_size = 1024 + random.randint(-500, 2000)
            
            # Occasionally simulate suspicious activity
            if random.random() < 0.05:  # 5% chance of suspicious activity
                threat_type = random.choice(list(ThreatType))
                if threat_type == ThreatType.DENIAL_OF_SERVICE:
                    base_request_rate *= 10
                    base_error_rate *= 5
                elif threat_type == ThreatType.RESOURCE_ABUSE:
                    base_cpu = 95 + random.uniform(0, 5)
                    base_memory = 98 + random.uniform(0, 2)
                elif threat_type == ThreatType.UNAUTHORIZED_ACCESS:
                    base_failed_auth = 15 + random.randint(0, 10)
                elif threat_type == ThreatType.DATA_EXFILTRATION:
                    base_payload_size = 10485760 + random.randint(0, 5242880)  # 10-15MB
                    base_network_io = 1073741824 + random.randint(0, 536870912)  # 1-1.5GB
            
            metrics = SecurityMetrics(
                timestamp=datetime.now(),
                request_rate=max(0, base_request_rate),
                error_rate=max(0, min(1, base_error_rate)),
                response_time_ms=max(50, base_response_time),
                cpu_usage=max(0, min(100, base_cpu)),
                memory_usage=max(0, min(100, base_memory)),
                network_io=max(0, base_network_io),
                failed_auth_attempts=max(0, base_failed_auth),
                unique_ips=max(1, base_unique_ips),
                payload_size_bytes=max(0, base_payload_size)
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting security metrics: {e}")
            return SecurityMetrics(
                timestamp=datetime.now(),
                request_rate=100.0,
                error_rate=0.02,
                response_time_ms=150.0,
                cpu_usage=45.0,
                memory_usage=60.0,
                network_io=1048576.0,
                failed_auth_attempts=0,
                unique_ips=50,
                payload_size_bytes=1024
            )
    
    async def _detect_threats(self, metrics: SecurityMetrics) -> List[ThreatEvent]:
        """Detect threats using ML and rule-based approaches"""
        threats = []
        
        try:
            # ML-based anomaly detection
            if self.is_trained:
                ml_threats = await self._ml_anomaly_detection(metrics)
                threats.extend(ml_threats)
            
            # Rule-based threat detection
            rule_threats = await self._rule_based_detection(metrics)
            threats.extend(rule_threats)
            
            # Behavioral analysis
            behavioral_threats = await self._behavioral_analysis(metrics)
            threats.extend(behavioral_threats)
            
            return threats
            
        except Exception as e:
            logger.error(f"Error in threat detection: {e}")
            return []
    
    async def _ml_anomaly_detection(self, metrics: SecurityMetrics) -> List[ThreatEvent]:
        """ML-based anomaly detection"""
        try:
            # Prepare feature vector
            features = np.array([[
                metrics.request_rate,
                metrics.error_rate,
                metrics.response_time_ms,
                metrics.cpu_usage,
                metrics.memory_usage,
                metrics.network_io,
                metrics.failed_auth_attempts,
                metrics.unique_ips,
                metrics.payload_size_bytes
            ]])
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Get anomaly score
            anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
            is_anomaly = self.anomaly_detector.predict(features_scaled)[0] == -1
            
            threats = []
            
            if is_anomaly and anomaly_score < self.threat_threshold:
                # Determine threat type based on which metrics are most anomalous
                threat_type = self._classify_anomaly_type(metrics)
                threat_level = self._determine_threat_level(anomaly_score)
                
                threat = ThreatEvent(
                    threat_id=f"ml-{int(metrics.timestamp.timestamp())}",
                    threat_type=threat_type,
                    threat_level=threat_level,
                    confidence_score=abs(anomaly_score),
                    timestamp=metrics.timestamp,
                    source_ip="unknown",
                    affected_service="system",
                    description=f"ML anomaly detected: {threat_type.value}",
                    indicators={
                        "anomaly_score": anomaly_score,
                        "detection_method": "ml_isolation_forest"
                    },
                    raw_data=asdict(metrics)
                )
                
                threats.append(threat)
                logger.warning(f"ML anomaly detected: {threat_type.value} "
                             f"(score: {anomaly_score:.3f})")
            
            return threats
            
        except Exception as e:
            logger.error(f"Error in ML anomaly detection: {e}")
            return []
    
    async def _rule_based_detection(self, metrics: SecurityMetrics) -> List[ThreatEvent]:
        """Rule-based threat detection"""
        threats = []
        
        try:
            # Check for resource abuse
            if (metrics.cpu_usage > self.threat_patterns[ThreatType.RESOURCE_ABUSE]["cpu_threshold"] or
                metrics.memory_usage > self.threat_patterns[ThreatType.RESOURCE_ABUSE]["memory_threshold"]):
                
                threat = ThreatEvent(
                    threat_id=f"rule-resource-{int(metrics.timestamp.timestamp())}",
                    threat_type=ThreatType.RESOURCE_ABUSE,
                    threat_level=ThreatLevel.HIGH,
                    confidence_score=0.9,
                    timestamp=metrics.timestamp,
                    source_ip="internal",
                    affected_service="system",
                    description="Resource abuse detected: High CPU/Memory usage",
                    indicators={
                        "cpu_usage": metrics.cpu_usage,
                        "memory_usage": metrics.memory_usage,
                        "detection_method": "rule_based"
                    },
                    raw_data=asdict(metrics)
                )
                threats.append(threat)
            
            # Check for unauthorized access attempts
            if metrics.failed_auth_attempts > self.threat_patterns[ThreatType.UNAUTHORIZED_ACCESS]["failed_auth_threshold"]:
                threat = ThreatEvent(
                    threat_id=f"rule-auth-{int(metrics.timestamp.timestamp())}",
                    threat_type=ThreatType.UNAUTHORIZED_ACCESS,
                    threat_level=ThreatLevel.MEDIUM,
                    confidence_score=0.85,
                    timestamp=metrics.timestamp,
                    source_ip="multiple",
                    affected_service="authentication",
                    description="Multiple failed authentication attempts detected",
                    indicators={
                        "failed_attempts": metrics.failed_auth_attempts,
                        "detection_method": "rule_based"
                    },
                    raw_data=asdict(metrics)
                )
                threats.append(threat)
            
            # Check for potential DoS
            if (self.baseline_metrics and 
                metrics.request_rate > self.baseline_metrics["request_rate"] * 
                self.threat_patterns[ThreatType.DENIAL_OF_SERVICE]["request_rate_spike"]):
                
                threat = ThreatEvent(
                    threat_id=f"rule-dos-{int(metrics.timestamp.timestamp())}",
                    threat_type=ThreatType.DENIAL_OF_SERVICE,
                    threat_level=ThreatLevel.CRITICAL,
                    confidence_score=0.95,
                    timestamp=metrics.timestamp,
                    source_ip="multiple",
                    affected_service="api",
                    description="Potential DoS attack: Request rate spike detected",
                    indicators={
                        "current_rate": metrics.request_rate,
                        "baseline_rate": self.baseline_metrics["request_rate"],
                        "spike_factor": metrics.request_rate / self.baseline_metrics["request_rate"],
                        "detection_method": "rule_based"
                    },
                    raw_data=asdict(metrics)
                )
                threats.append(threat)
            
            # Check for data exfiltration
            if (metrics.payload_size_bytes > self.threat_patterns[ThreatType.DATA_EXFILTRATION]["payload_size_threshold"] or
                metrics.network_io > self.threat_patterns[ThreatType.DATA_EXFILTRATION]["network_io_threshold"]):
                
                threat = ThreatEvent(
                    threat_id=f"rule-exfil-{int(metrics.timestamp.timestamp())}",
                    threat_type=ThreatType.DATA_EXFILTRATION,
                    threat_level=ThreatLevel.HIGH,
                    confidence_score=0.8,
                    timestamp=metrics.timestamp,
                    source_ip="unknown",
                    affected_service="data",
                    description="Potential data exfiltration: Large payload/network transfer",
                    indicators={
                        "payload_size": metrics.payload_size_bytes,
                        "network_io": metrics.network_io,
                        "detection_method": "rule_based"
                    },
                    raw_data=asdict(metrics)
                )
                threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Error in rule-based detection: {e}")
            return []
    
    async def _behavioral_analysis(self, metrics: SecurityMetrics) -> List[ThreatEvent]:
        """Behavioral analysis for threat detection"""
        threats = []
        
        try:
            # Analyze patterns in recent data
            if len(self.training_data) >= 10:
                recent_data = list(self.training_data)[-10:]
                
                # Check for unusual patterns
                current_hour = metrics.timestamp.hour
                same_hour_data = [m for m in recent_data if m.timestamp.hour == current_hour]
                
                if len(same_hour_data) >= 3:
                    avg_request_rate = sum(m.request_rate for m in same_hour_data) / len(same_hour_data)
                    
                    # Detect sudden behavioral changes
                    if metrics.request_rate > avg_request_rate * 3:
                        threat = ThreatEvent(
                            threat_id=f"behavioral-{int(metrics.timestamp.timestamp())}",
                            threat_type=ThreatType.ANOMALOUS_BEHAVIOR,
                            threat_level=ThreatLevel.MEDIUM,
                            confidence_score=0.7,
                            timestamp=metrics.timestamp,
                            source_ip="unknown",
                            affected_service="system",
                            description="Behavioral anomaly: Unusual request pattern",
                            indicators={
                                "current_rate": metrics.request_rate,
                                "historical_avg": avg_request_rate,
                                "deviation_factor": metrics.request_rate / avg_request_rate,
                                "detection_method": "behavioral_analysis"
                            },
                            raw_data=asdict(metrics)
                        )
                        threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Error in behavioral analysis: {e}")
            return []
    
    def _classify_anomaly_type(self, metrics: SecurityMetrics) -> ThreatType:
        """Classify the type of anomaly based on metrics"""
        # Simple heuristic classification
        if metrics.cpu_usage > 80 or metrics.memory_usage > 80:
            return ThreatType.RESOURCE_ABUSE
        elif metrics.failed_auth_attempts > 5:
            return ThreatType.UNAUTHORIZED_ACCESS
        elif metrics.request_rate > 500:
            return ThreatType.DENIAL_OF_SERVICE
        elif metrics.payload_size_bytes > 5242880:  # 5MB
            return ThreatType.DATA_EXFILTRATION
        else:
            return ThreatType.ANOMALOUS_BEHAVIOR
    
    def _determine_threat_level(self, anomaly_score: float) -> ThreatLevel:
        """Determine threat level based on anomaly score"""
        if anomaly_score < -0.8:
            return ThreatLevel.CRITICAL
        elif anomaly_score < -0.6:
            return ThreatLevel.HIGH
        elif anomaly_score < -0.4:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    async def _process_threat(self, threat: ThreatEvent):
        """Process a detected threat"""
        try:
            self.detected_threats.append(threat)
            self.metrics["threats_detected"] += 1
            
            logger.warning(f"THREAT DETECTED: {threat.threat_type.value} "
                          f"({threat.threat_level.value}) - {threat.description}")
            
            # Trigger response based on threat level
            if threat.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                await self._trigger_immediate_response(threat)
            
            # Store threat for analysis
            await self._store_threat_event(threat)
            
        except Exception as e:
            logger.error(f"Error processing threat: {e}")
    
    async def _trigger_immediate_response(self, threat: ThreatEvent):
        """Trigger immediate response for high-priority threats"""
        try:
            logger.critical(f"IMMEDIATE RESPONSE TRIGGERED: {threat.threat_id}")
            
            # In production, this would trigger:
            # - Automated blocking/quarantine
            # - Alert notifications
            # - Incident response workflows
            # - Security team notifications
            
            # For demo, we'll simulate response actions
            if threat.threat_type == ThreatType.DENIAL_OF_SERVICE:
                logger.info("Activating rate limiting and DDoS protection")
            elif threat.threat_type == ThreatType.UNAUTHORIZED_ACCESS:
                logger.info("Temporarily blocking suspicious IPs")
            elif threat.threat_type == ThreatType.DATA_EXFILTRATION:
                logger.info("Activating data loss prevention measures")
            elif threat.threat_type == ThreatType.RESOURCE_ABUSE:
                logger.info("Implementing resource quotas and limits")
            
        except Exception as e:
            logger.error(f"Error triggering immediate response: {e}")
    
    async def _store_threat_event(self, threat: ThreatEvent):
        """Store threat event for analysis and reporting"""
        try:
            # In production, this would store to a security database
            # For demo, we'll just log it
            logger.info(f"Storing threat event: {threat.threat_id}")
            
        except Exception as e:
            logger.error(f"Error storing threat event: {e}")
    
    async def _train_models(self):
        """Train ML models with collected data"""
        try:
            logger.info("Training ML models...")
            
            # Prepare training data
            training_features = []
            for metrics in self.training_data:
                features = [
                    metrics.request_rate,
                    metrics.error_rate,
                    metrics.response_time_ms,
                    metrics.cpu_usage,
                    metrics.memory_usage,
                    metrics.network_io,
                    metrics.failed_auth_attempts,
                    metrics.unique_ips,
                    metrics.payload_size_bytes
                ]
                training_features.append(features)
            
            training_features = np.array(training_features)
            
            # Fit scaler
            self.scaler.fit(training_features)
            
            # Scale features
            training_features_scaled = self.scaler.transform(training_features)
            
            # Train anomaly detector
            self.anomaly_detector.fit(training_features_scaled)
            
            self.is_trained = True
            self.metrics["model_training_count"] += 1
            self.metrics["last_training_time"] = datetime.now()
            
            logger.info(f"Model training completed with {len(training_features)} samples")
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
    
    async def _update_baseline_metrics(self):
        """Update baseline metrics for comparison"""
        try:
            if len(self.training_data) < 10:
                return
            
            recent_data = list(self.training_data)[-50:]  # Last 50 samples
            
            self.baseline_metrics = {
                "request_rate": sum(m.request_rate for m in recent_data) / len(recent_data),
                "error_rate": sum(m.error_rate for m in recent_data) / len(recent_data),
                "response_time_ms": sum(m.response_time_ms for m in recent_data) / len(recent_data),
                "cpu_usage": sum(m.cpu_usage for m in recent_data) / len(recent_data),
                "memory_usage": sum(m.memory_usage for m in recent_data) / len(recent_data),
                "network_io": sum(m.network_io for m in recent_data) / len(recent_data),
                "failed_auth_attempts": sum(m.failed_auth_attempts for m in recent_data) / len(recent_data),
                "unique_ips": sum(m.unique_ips for m in recent_data) / len(recent_data),
                "payload_size_bytes": sum(m.payload_size_bytes for m in recent_data) / len(recent_data)
            }
            
            logger.debug("Baseline metrics updated")
            
        except Exception as e:
            logger.error(f"Error updating baseline metrics: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get threat detection metrics"""
        accuracy = 0.0
        if self.metrics["threats_detected"] > 0:
            accuracy = (self.metrics["true_positives"] / 
                       (self.metrics["true_positives"] + self.metrics["false_positives"])) * 100
        
        return {
            **self.metrics,
            "detection_accuracy": round(accuracy, 2),
            "is_trained": self.is_trained,
            "training_data_size": len(self.training_data),
            "recent_threats": len([t for t in self.detected_threats 
                                 if (datetime.now() - t.timestamp).total_seconds() < 3600])
        }
    
    def get_recent_threats(self, hours: int = 24) -> List[ThreatEvent]:
        """Get recent threat events"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [t for t in self.detected_threats if t.timestamp >= cutoff_time]
    
    def get_threat_summary(self) -> Dict[str, Any]:
        """Get threat detection summary"""
        recent_threats = self.get_recent_threats()
        
        threat_by_type = {}
        threat_by_level = {}
        
        for threat in recent_threats:
            threat_by_type[threat.threat_type.value] = threat_by_type.get(threat.threat_type.value, 0) + 1
            threat_by_level[threat.threat_level.value] = threat_by_level.get(threat.threat_level.value, 0) + 1
        
        return {
            "total_threats_24h": len(recent_threats),
            "threats_by_type": threat_by_type,
            "threats_by_level": threat_by_level,
            "avg_confidence": sum(t.confidence_score for t in recent_threats) / max(len(recent_threats), 1)
        }
    
    async def save_model(self, filepath: str):
        """Save trained models"""
        try:
            model_data = {
                "anomaly_detector": self.anomaly_detector,
                "scaler": self.scaler,
                "is_trained": self.is_trained,
                "baseline_metrics": self.baseline_metrics,
                "metrics": self.metrics
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"Models saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    async def load_model(self, filepath: str):
        """Load trained models"""
        try:
            model_data = joblib.load(filepath)
            
            self.anomaly_detector = model_data["anomaly_detector"]
            self.scaler = model_data["scaler"]
            self.is_trained = model_data["is_trained"]
            self.baseline_metrics = model_data.get("baseline_metrics")
            
            logger.info(f"Models loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")

# Example usage
async def main():
    """Example usage of ML threat detector"""
    
    detector = MLThreatDetector()
    await detector.start()
    
    # Let it run for a while to collect data and detect threats
    await asyncio.sleep(300)  # 5 minutes
    
    # Print metrics
    metrics = detector.get_metrics()
    print(f"Threat detection metrics: {json.dumps(metrics, indent=2)}")
    
    # Print threat summary
    summary = detector.get_threat_summary()
    print(f"Threat summary: {json.dumps(summary, indent=2)}")
    
    # Print recent threats
    recent_threats = detector.get_recent_threats(1)  # Last hour
    print(f"Recent threats: {len(recent_threats)}")
    for threat in recent_threats[-5:]:  # Last 5 threats
        print(f"  {threat.threat_type.value} ({threat.threat_level.value}) - {threat.description}")
    
    # Save model
    await detector.save_model("threat_detection_model.pkl")
    
    await detector.stop()

if __name__ == "__main__":
    asyncio.run(main())

