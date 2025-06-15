"""
JUNO Phase 2: Transparent Reasoning Framework
Provides explainable AI capabilities with confidence scoring and audit trails.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ReasoningType(Enum):
    """Types of reasoning processes."""
    ANALYTICAL = "analytical"      # Data-driven analysis
    PREDICTIVE = "predictive"      # Future state predictions
    DIAGNOSTIC = "diagnostic"      # Problem identification
    PRESCRIPTIVE = "prescriptive"  # Action recommendations
    COMPARATIVE = "comparative"    # Comparison analysis


class ConfidenceLevel(Enum):
    """Confidence level categories."""
    VERY_LOW = "very_low"      # 0.0 - 0.3
    LOW = "low"                # 0.3 - 0.5
    MEDIUM = "medium"          # 0.5 - 0.7
    HIGH = "high"              # 0.7 - 0.9
    VERY_HIGH = "very_high"    # 0.9 - 1.0


@dataclass
class DataSource:
    """Represents a data source used in reasoning."""
    source_type: str
    source_id: str
    data_quality: float
    last_updated: datetime
    reliability_score: float


@dataclass
class ReasoningStep:
    """Represents a single step in the reasoning process."""
    step_id: str
    description: str
    input_data: Dict[str, Any]
    process: str
    output_data: Dict[str, Any]
    confidence: float
    timestamp: datetime


@dataclass
class ReasoningResult:
    """Complete reasoning result with explanation and confidence."""
    reasoning_id: str
    reasoning_type: ReasoningType
    question: str
    conclusion: str
    confidence: float
    confidence_level: ConfidenceLevel
    data_sources: List[DataSource]
    reasoning_steps: List[ReasoningStep]
    alternatives_considered: List[Dict[str, Any]]
    assumptions: List[str]
    limitations: List[str]
    timestamp: datetime
    processing_time_ms: int


class ConfidenceCalculator:
    """
    Calculates confidence scores based on multiple factors.
    """
    
    @staticmethod
    def calculate_data_confidence(data_sources: List[DataSource]) -> float:
        """Calculate confidence based on data quality and reliability."""
        if not data_sources:
            return 0.0
        
        total_weight = 0.0
        weighted_confidence = 0.0
        
        for source in data_sources:
            # Weight based on data quality and reliability
            weight = (source.data_quality * source.reliability_score)
            total_weight += weight
            weighted_confidence += weight * source.reliability_score
        
        return min(weighted_confidence / total_weight if total_weight > 0 else 0.0, 1.0)
    
    @staticmethod
    def calculate_temporal_confidence(data_sources: List[DataSource]) -> float:
        """Calculate confidence based on data freshness."""
        if not data_sources:
            return 0.0
        
        now = datetime.now()
        total_freshness = 0.0
        
        for source in data_sources:
            # Calculate age in hours
            age_hours = (now - source.last_updated).total_seconds() / 3600
            
            # Freshness score decreases with age
            if age_hours <= 1:
                freshness = 1.0
            elif age_hours <= 24:
                freshness = 0.9
            elif age_hours <= 168:  # 1 week
                freshness = 0.7
            elif age_hours <= 720:  # 1 month
                freshness = 0.5
            else:
                freshness = 0.3
            
            total_freshness += freshness
        
        return total_freshness / len(data_sources)
    
    @staticmethod
    def calculate_complexity_confidence(reasoning_steps: List[ReasoningStep]) -> float:
        """Calculate confidence based on reasoning complexity."""
        if not reasoning_steps:
            return 0.0
        
        # More steps can mean more thorough analysis but also more uncertainty
        step_count = len(reasoning_steps)
        
        if step_count <= 3:
            complexity_factor = 1.0
        elif step_count <= 6:
            complexity_factor = 0.9
        elif step_count <= 10:
            complexity_factor = 0.8
        else:
            complexity_factor = 0.7
        
        # Average confidence of individual steps
        avg_step_confidence = sum(step.confidence for step in reasoning_steps) / step_count
        
        return avg_step_confidence * complexity_factor
    
    @classmethod
    def calculate_overall_confidence(
        cls,
        data_sources: List[DataSource],
        reasoning_steps: List[ReasoningStep],
        alternatives_count: int = 0
    ) -> Tuple[float, ConfidenceLevel]:
        """Calculate overall confidence score."""
        data_conf = cls.calculate_data_confidence(data_sources)
        temporal_conf = cls.calculate_temporal_confidence(data_sources)
        complexity_conf = cls.calculate_complexity_confidence(reasoning_steps)
        
        # Weight the different confidence factors
        overall_confidence = (
            data_conf * 0.4 +
            temporal_conf * 0.3 +
            complexity_conf * 0.3
        )
        
        # Bonus for considering alternatives
        if alternatives_count > 0:
            alternative_bonus = min(alternatives_count * 0.05, 0.15)
            overall_confidence = min(overall_confidence + alternative_bonus, 1.0)
        
        # Determine confidence level
        if overall_confidence >= 0.9:
            level = ConfidenceLevel.VERY_HIGH
        elif overall_confidence >= 0.7:
            level = ConfidenceLevel.HIGH
        elif overall_confidence >= 0.5:
            level = ConfidenceLevel.MEDIUM
        elif overall_confidence >= 0.3:
            level = ConfidenceLevel.LOW
        else:
            level = ConfidenceLevel.VERY_LOW
        
        return overall_confidence, level


class ReasoningEngine:
    """
    Core reasoning engine that provides transparent, explainable AI decisions.
    """
    
    def __init__(self):
        self.reasoning_history = []
    
    def create_reasoning_result(
        self,
        reasoning_type: ReasoningType,
        question: str,
        conclusion: str,
        data_sources: List[DataSource],
        reasoning_steps: List[ReasoningStep],
        alternatives_considered: Optional[List[Dict[str, Any]]] = None,
        assumptions: Optional[List[str]] = None,
        limitations: Optional[List[str]] = None,
        processing_time_ms: int = 0
    ) -> ReasoningResult:
        """Create a complete reasoning result with confidence calculation."""
        
        if alternatives_considered is None:
            alternatives_considered = []
        if assumptions is None:
            assumptions = []
        if limitations is None:
            limitations = []
        
        # Calculate confidence
        confidence, confidence_level = ConfidenceCalculator.calculate_overall_confidence(
            data_sources=data_sources,
            reasoning_steps=reasoning_steps,
            alternatives_count=len(alternatives_considered)
        )
        
        result = ReasoningResult(
            reasoning_id=str(uuid.uuid4()),
            reasoning_type=reasoning_type,
            question=question,
            conclusion=conclusion,
            confidence=confidence,
            confidence_level=confidence_level,
            data_sources=data_sources,
            reasoning_steps=reasoning_steps,
            alternatives_considered=alternatives_considered,
            assumptions=assumptions,
            limitations=limitations,
            timestamp=datetime.now(),
            processing_time_ms=processing_time_ms
        )
        
        self.reasoning_history.append(result)
        return result
    
    def explain_reasoning(self, reasoning_result: ReasoningResult, detail_level: str = "detailed") -> Dict[str, Any]:
        """Generate human-readable explanation of reasoning."""
        
        if detail_level == "basic":
            return self._basic_explanation(reasoning_result)
        elif detail_level == "detailed":
            return self._detailed_explanation(reasoning_result)
        elif detail_level == "verbose":
            return self._verbose_explanation(reasoning_result)
        else:
            return self._detailed_explanation(reasoning_result)
    
    def _basic_explanation(self, result: ReasoningResult) -> Dict[str, Any]:
        """Generate basic explanation."""
        return {
            "conclusion": result.conclusion,
            "confidence": f"{result.confidence:.0%}",
            "confidence_level": result.confidence_level.value.replace("_", " ").title(),
            "data_sources_count": len(result.data_sources),
            "reasoning_type": result.reasoning_type.value.title()
        }
    
    def _detailed_explanation(self, result: ReasoningResult) -> Dict[str, Any]:
        """Generate detailed explanation."""
        return {
            "reasoning_id": result.reasoning_id,
            "question": result.question,
            "conclusion": result.conclusion,
            "confidence": {
                "score": f"{result.confidence:.1%}",
                "level": result.confidence_level.value.replace("_", " ").title(),
                "numeric": round(result.confidence, 3)
            },
            "reasoning_process": {
                "type": result.reasoning_type.value.title(),
                "steps_count": len(result.reasoning_steps),
                "key_steps": [
                    {
                        "step": i + 1,
                        "description": step.description,
                        "confidence": f"{step.confidence:.1%}"
                    }
                    for i, step in enumerate(result.reasoning_steps[:3])  # Show first 3 steps
                ]
            },
            "data_foundation": {
                "sources_analyzed": len(result.data_sources),
                "data_quality": f"{sum(ds.data_quality for ds in result.data_sources) / len(result.data_sources):.1%}" if result.data_sources else "N/A",
                "most_recent_data": max(ds.last_updated for ds in result.data_sources).strftime("%Y-%m-%d %H:%M") if result.data_sources else "N/A"
            },
            "alternatives_considered": len(result.alternatives_considered),
            "assumptions": result.assumptions[:3] if result.assumptions else [],  # Show first 3
            "limitations": result.limitations[:3] if result.limitations else [],  # Show first 3
            "timestamp": result.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "processing_time": f"{result.processing_time_ms}ms"
        }
    
    def _verbose_explanation(self, result: ReasoningResult) -> Dict[str, Any]:
        """Generate verbose explanation with full details."""
        detailed = self._detailed_explanation(result)
        
        # Add complete reasoning steps
        detailed["complete_reasoning_steps"] = [
            {
                "step_id": step.step_id,
                "description": step.description,
                "process": step.process,
                "confidence": step.confidence,
                "timestamp": step.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for step in result.reasoning_steps
        ]
        
        # Add complete data sources
        detailed["complete_data_sources"] = [
            {
                "type": ds.source_type,
                "id": ds.source_id,
                "quality": f"{ds.data_quality:.1%}",
                "reliability": f"{ds.reliability_score:.1%}",
                "last_updated": ds.last_updated.strftime("%Y-%m-%d %H:%M:%S")
            }
            for ds in result.data_sources
        ]
        
        # Add all alternatives and assumptions
        detailed["all_alternatives"] = result.alternatives_considered
        detailed["all_assumptions"] = result.assumptions
        detailed["all_limitations"] = result.limitations
        
        return detailed


class AuditTrail:
    """
    Maintains comprehensive audit trails for all reasoning and decisions.
    """
    
    def __init__(self):
        self.audit_entries = []
    
    def log_reasoning(
        self,
        reasoning_result: ReasoningResult,
        user_id: str,
        session_id: str,
        action_taken: Optional[str] = None
    ) -> str:
        """Log a reasoning event to the audit trail."""
        
        audit_entry = {
            "audit_id": str(uuid.uuid4()),
            "event_type": "reasoning",
            "reasoning_id": reasoning_result.reasoning_id,
            "user_id": user_id,
            "session_id": session_id,
            "question": reasoning_result.question,
            "conclusion": reasoning_result.conclusion,
            "confidence": reasoning_result.confidence,
            "reasoning_type": reasoning_result.reasoning_type.value,
            "action_taken": action_taken,
            "timestamp": datetime.now(),
            "data_sources_count": len(reasoning_result.data_sources),
            "reasoning_steps_count": len(reasoning_result.reasoning_steps)
        }
        
        self.audit_entries.append(audit_entry)
        logger.info(f"Audit trail entry created: {audit_entry['audit_id']}")
        
        return audit_entry["audit_id"]
    
    def log_decision(
        self,
        decision_id: str,
        decision_type: str,
        decision_data: Dict[str, Any],
        reasoning_id: str,
        user_id: str,
        approved_by: Optional[str] = None,
        approval_required: bool = False
    ) -> str:
        """Log a decision event to the audit trail."""
        
        audit_entry = {
            "audit_id": str(uuid.uuid4()),
            "event_type": "decision",
            "decision_id": decision_id,
            "decision_type": decision_type,
            "decision_data": decision_data,
            "reasoning_id": reasoning_id,
            "user_id": user_id,
            "approved_by": approved_by,
            "approval_required": approval_required,
            "approval_status": "approved" if approved_by else ("pending" if approval_required else "auto_approved"),
            "timestamp": datetime.now()
        }
        
        self.audit_entries.append(audit_entry)
        logger.info(f"Decision audit entry created: {audit_entry['audit_id']}")
        
        return audit_entry["audit_id"]
    
    def get_audit_trail(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve audit trail entries based on criteria."""
        
        filtered_entries = self.audit_entries
        
        if user_id:
            filtered_entries = [e for e in filtered_entries if e.get("user_id") == user_id]
        
        if session_id:
            filtered_entries = [e for e in filtered_entries if e.get("session_id") == session_id]
        
        if event_type:
            filtered_entries = [e for e in filtered_entries if e.get("event_type") == event_type]
        
        # Sort by timestamp (most recent first) and limit
        filtered_entries.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return filtered_entries[:limit]


# Example usage and testing
if __name__ == "__main__":
    # Initialize reasoning engine
    reasoning_engine = ReasoningEngine()
    audit_trail = AuditTrail()
    
    # Example: Create data sources
    data_sources = [
        DataSource(
            source_type="jira_api",
            source_id="sprint_data_24_3",
            data_quality=0.95,
            last_updated=datetime.now(),
            reliability_score=0.9
        ),
        DataSource(
            source_type="team_metrics",
            source_id="velocity_history",
            data_quality=0.85,
            last_updated=datetime.now(),
            reliability_score=0.8
        )
    ]
    
    # Example: Create reasoning steps
    reasoning_steps = [
        ReasoningStep(
            step_id="step_1",
            description="Analyze current sprint velocity",
            input_data={"sprint_points": 50, "completed_points": 42},
            process="velocity_calculation",
            output_data={"velocity_percentage": 0.84},
            confidence=0.9,
            timestamp=datetime.now()
        ),
        ReasoningStep(
            step_id="step_2",
            description="Compare with historical performance",
            input_data={"current_velocity": 0.84, "historical_avg": 0.78},
            process="trend_analysis",
            output_data={"trend": "improving", "variance": 0.06},
            confidence=0.85,
            timestamp=datetime.now()
        )
    ]
    
    # Create reasoning result
    result = reasoning_engine.create_reasoning_result(
        reasoning_type=ReasoningType.ANALYTICAL,
        question="How is our current sprint performing?",
        conclusion="Sprint is performing above average with 84% velocity vs 78% historical average",
        data_sources=data_sources,
        reasoning_steps=reasoning_steps,
        alternatives_considered=[
            {"alternative": "Sprint is on track", "confidence": 0.7},
            {"alternative": "Sprint is behind schedule", "confidence": 0.2}
        ],
        assumptions=["Team capacity remains constant", "No major blockers emerge"],
        limitations=["Based on current data only", "External dependencies not considered"],
        processing_time_ms=150
    )
    
    # Generate explanation
    explanation = reasoning_engine.explain_reasoning(result, detail_level="detailed")
    
    # Log to audit trail
    audit_id = audit_trail.log_reasoning(
        reasoning_result=result,
        user_id="john_doe",
        session_id="sess_123"
    )
    
    print("Transparent reasoning framework implementation complete!")
    print(f"Reasoning confidence: {result.confidence:.1%}")
    print(f"Audit trail entry: {audit_id}")

