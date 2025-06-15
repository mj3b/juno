"""
JUNO Phase 2: Sprint Risk Forecast Algorithm
Predictive analytics engine for identifying sprint delivery risks before they impact outcomes.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import json
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level classifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(Enum):
    """Categories of sprint risks."""
    VELOCITY = "velocity"
    SCOPE = "scope"
    CAPACITY = "capacity"
    DEPENDENCIES = "dependencies"
    QUALITY = "quality"
    EXTERNAL = "external"


@dataclass
class SprintMetrics:
    """Current sprint metrics for risk analysis."""
    sprint_id: str
    team_id: str
    start_date: datetime
    end_date: datetime
    planned_points: int
    completed_points: int
    in_progress_points: int
    blocked_points: int
    team_capacity: float
    days_remaining: int
    velocity_trend: float
    defect_count: int
    code_review_backlog: int
    external_dependencies: int
    scope_changes: int


@dataclass
class RiskFactor:
    """Individual risk factor with impact assessment."""
    factor_id: str
    category: RiskCategory
    description: str
    impact_score: float  # 0.0 - 1.0
    probability: float   # 0.0 - 1.0
    risk_score: float    # impact * probability
    confidence: float    # 0.0 - 1.0
    data_sources: List[str]
    mitigation_suggestions: List[str]


@dataclass
class SprintRiskForecast:
    """Complete sprint risk forecast with recommendations."""
    forecast_id: str
    sprint_id: str
    team_id: str
    overall_risk_level: RiskLevel
    overall_risk_score: float
    completion_probability: float
    predicted_completion_date: datetime
    risk_factors: List[RiskFactor]
    recommendations: List[Dict[str, Any]]
    confidence: float
    forecast_timestamp: datetime
    data_freshness: datetime


class VelocityAnalyzer:
    """
    Analyzes team velocity patterns and predicts sprint completion probability.
    """
    
    def __init__(self):
        self.velocity_model = None
        self.scaler = StandardScaler()
        self.historical_data = []
    
    def add_historical_sprint(self, sprint_data: Dict[str, Any]) -> None:
        """Add historical sprint data for model training."""
        self.historical_data.append(sprint_data)
    
    def train_velocity_model(self) -> bool:
        """Train the velocity prediction model using historical data."""
        if len(self.historical_data) < 5:
            logger.warning("Insufficient historical data for velocity model training")
            return False
        
        try:
            # Prepare training data
            df = pd.DataFrame(self.historical_data)
            
            # Feature engineering
            features = [
                'planned_points', 'team_capacity', 'sprint_length_days',
                'initial_scope_changes', 'team_size', 'complexity_avg',
                'external_dependencies_count', 'previous_velocity'
            ]
            
            X = df[features].fillna(0)
            y = df['actual_velocity'].fillna(0)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.velocity_model = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
            self.velocity_model.fit(X_scaled, y)
            
            logger.info("Velocity prediction model trained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to train velocity model: {e}")
            return False
    
    def predict_sprint_velocity(self, sprint_metrics: SprintMetrics) -> Tuple[float, float]:
        """Predict sprint velocity and confidence."""
        if self.velocity_model is None:
            # Fallback to simple heuristic
            return self._heuristic_velocity_prediction(sprint_metrics)
        
        try:
            # Prepare features
            features = np.array([[
                sprint_metrics.planned_points,
                sprint_metrics.team_capacity,
                (sprint_metrics.end_date - sprint_metrics.start_date).days,
                sprint_metrics.scope_changes,
                5,  # Assumed team size
                0.7,  # Assumed complexity average
                sprint_metrics.external_dependencies,
                sprint_metrics.velocity_trend
            ]])
            
            # Scale and predict
            features_scaled = self.scaler.transform(features)
            predicted_velocity = self.velocity_model.predict(features_scaled)[0]
            
            # Calculate confidence based on model variance
            confidence = min(0.9, max(0.3, 1.0 - abs(predicted_velocity - sprint_metrics.velocity_trend) / 10))
            
            return predicted_velocity, confidence
            
        except Exception as e:
            logger.error(f"Velocity prediction failed: {e}")
            return self._heuristic_velocity_prediction(sprint_metrics)
    
    def _heuristic_velocity_prediction(self, sprint_metrics: SprintMetrics) -> Tuple[float, float]:
        """Fallback heuristic velocity prediction."""
        # Simple heuristic based on current progress and time remaining
        total_days = (sprint_metrics.end_date - sprint_metrics.start_date).days
        elapsed_days = total_days - sprint_metrics.days_remaining
        
        if elapsed_days <= 0:
            return sprint_metrics.velocity_trend, 0.5
        
        current_velocity = sprint_metrics.completed_points / elapsed_days
        predicted_velocity = current_velocity * total_days
        
        # Adjust for known factors
        if sprint_metrics.blocked_points > 0:
            predicted_velocity *= 0.9
        
        if sprint_metrics.scope_changes > 2:
            predicted_velocity *= 0.85
        
        confidence = 0.6 if sprint_metrics.days_remaining > 3 else 0.4
        
        return predicted_velocity, confidence


class RiskDetectionEngine:
    """
    Core engine for detecting and analyzing sprint risks.
    """
    
    def __init__(self, velocity_analyzer: VelocityAnalyzer):
        self.velocity_analyzer = velocity_analyzer
        self.risk_thresholds = {
            'velocity_variance': 0.2,
            'scope_change_limit': 3,
            'blocked_points_ratio': 0.15,
            'capacity_utilization': 0.9,
            'code_review_backlog': 5,
            'defect_density': 0.1
        }
    
    def analyze_sprint_risks(self, sprint_metrics: SprintMetrics) -> List[RiskFactor]:
        """Analyze all risk factors for a sprint."""
        risk_factors = []
        
        # Velocity risk analysis
        velocity_risks = self._analyze_velocity_risks(sprint_metrics)
        risk_factors.extend(velocity_risks)
        
        # Scope risk analysis
        scope_risks = self._analyze_scope_risks(sprint_metrics)
        risk_factors.extend(scope_risks)
        
        # Capacity risk analysis
        capacity_risks = self._analyze_capacity_risks(sprint_metrics)
        risk_factors.extend(capacity_risks)
        
        # Quality risk analysis
        quality_risks = self._analyze_quality_risks(sprint_metrics)
        risk_factors.extend(quality_risks)
        
        # Dependency risk analysis
        dependency_risks = self._analyze_dependency_risks(sprint_metrics)
        risk_factors.extend(dependency_risks)
        
        return risk_factors
    
    def _analyze_velocity_risks(self, metrics: SprintMetrics) -> List[RiskFactor]:
        """Analyze velocity-related risks."""
        risks = []
        
        # Predict velocity
        predicted_velocity, velocity_confidence = self.velocity_analyzer.predict_sprint_velocity(metrics)
        
        # Calculate completion probability
        completion_probability = predicted_velocity / metrics.planned_points if metrics.planned_points > 0 else 1.0
        
        if completion_probability < 0.8:
            impact = 1.0 - completion_probability
            probability = min(0.9, impact + 0.1)
            
            risks.append(RiskFactor(
                factor_id="velocity_shortfall",
                category=RiskCategory.VELOCITY,
                description=f"Predicted velocity ({predicted_velocity:.1f}) may not meet planned points ({metrics.planned_points})",
                impact_score=impact,
                probability=probability,
                risk_score=impact * probability,
                confidence=velocity_confidence,
                data_sources=["velocity_model", "historical_data"],
                mitigation_suggestions=[
                    "Consider reducing scope or extending sprint",
                    "Identify and remove blockers",
                    "Reallocate resources from lower priority items"
                ]
            ))
        
        # Velocity trend analysis
        if metrics.velocity_trend < 0.7:
            risks.append(RiskFactor(
                factor_id="velocity_decline",
                category=RiskCategory.VELOCITY,
                description=f"Velocity trending downward ({metrics.velocity_trend:.1%})",
                impact_score=0.7,
                probability=0.8,
                risk_score=0.56,
                confidence=0.8,
                data_sources=["sprint_metrics"],
                mitigation_suggestions=[
                    "Investigate root causes of velocity decline",
                    "Address team capacity or skill gaps",
                    "Review and optimize development processes"
                ]
            ))
        
        return risks
    
    def _analyze_scope_risks(self, metrics: SprintMetrics) -> List[RiskFactor]:
        """Analyze scope-related risks."""
        risks = []
        
        if metrics.scope_changes > self.risk_thresholds['scope_change_limit']:
            impact = min(1.0, metrics.scope_changes / 10)
            probability = 0.9
            
            risks.append(RiskFactor(
                factor_id="scope_creep",
                category=RiskCategory.SCOPE,
                description=f"High number of scope changes ({metrics.scope_changes})",
                impact_score=impact,
                probability=probability,
                risk_score=impact * probability,
                confidence=0.9,
                data_sources=["jira_changes"],
                mitigation_suggestions=[
                    "Implement stricter change control process",
                    "Defer non-critical changes to next sprint",
                    "Communicate scope impact to stakeholders"
                ]
            ))
        
        return risks
    
    def _analyze_capacity_risks(self, metrics: SprintMetrics) -> List[RiskFactor]:
        """Analyze capacity-related risks."""
        risks = []
        
        # Calculate current utilization
        total_active_points = metrics.completed_points + metrics.in_progress_points
        utilization = total_active_points / metrics.planned_points if metrics.planned_points > 0 else 0
        
        if utilization > self.risk_thresholds['capacity_utilization']:
            impact = min(1.0, (utilization - 0.8) * 2)
            probability = 0.8
            
            risks.append(RiskFactor(
                factor_id="capacity_overload",
                category=RiskCategory.CAPACITY,
                description=f"Team capacity utilization high ({utilization:.1%})",
                impact_score=impact,
                probability=probability,
                risk_score=impact * probability,
                confidence=0.8,
                data_sources=["team_metrics"],
                mitigation_suggestions=[
                    "Redistribute workload among team members",
                    "Consider bringing in additional resources",
                    "Defer lower priority items"
                ]
            ))
        
        # Blocked points analysis
        blocked_ratio = metrics.blocked_points / metrics.planned_points if metrics.planned_points > 0 else 0
        if blocked_ratio > self.risk_thresholds['blocked_points_ratio']:
            impact = min(1.0, blocked_ratio * 2)
            probability = 0.9
            
            risks.append(RiskFactor(
                factor_id="blocked_work",
                category=RiskCategory.CAPACITY,
                description=f"Significant work blocked ({metrics.blocked_points} points)",
                impact_score=impact,
                probability=probability,
                risk_score=impact * probability,
                confidence=0.9,
                data_sources=["jira_status"],
                mitigation_suggestions=[
                    "Escalate blocked items to appropriate stakeholders",
                    "Find alternative approaches for blocked work",
                    "Reassign team members to unblocked items"
                ]
            ))
        
        return risks
    
    def _analyze_quality_risks(self, metrics: SprintMetrics) -> List[RiskFactor]:
        """Analyze quality-related risks."""
        risks = []
        
        # Code review backlog
        if metrics.code_review_backlog > self.risk_thresholds['code_review_backlog']:
            impact = min(1.0, metrics.code_review_backlog / 20)
            probability = 0.7
            
            risks.append(RiskFactor(
                factor_id="code_review_backlog",
                category=RiskCategory.QUALITY,
                description=f"Code review backlog building up ({metrics.code_review_backlog} items)",
                impact_score=impact,
                probability=probability,
                risk_score=impact * probability,
                confidence=0.8,
                data_sources=["code_review_metrics"],
                mitigation_suggestions=[
                    "Allocate dedicated time for code reviews",
                    "Distribute review load among team members",
                    "Consider pair programming for complex items"
                ]
            ))
        
        # Defect density
        defect_density = metrics.defect_count / metrics.completed_points if metrics.completed_points > 0 else 0
        if defect_density > self.risk_thresholds['defect_density']:
            impact = min(1.0, defect_density * 5)
            probability = 0.8
            
            risks.append(RiskFactor(
                factor_id="quality_issues",
                category=RiskCategory.QUALITY,
                description=f"High defect density ({defect_density:.2f} defects per point)",
                impact_score=impact,
                probability=probability,
                risk_score=impact * probability,
                confidence=0.7,
                data_sources=["defect_tracking"],
                mitigation_suggestions=[
                    "Increase testing coverage and rigor",
                    "Review and improve development practices",
                    "Allocate time for technical debt reduction"
                ]
            ))
        
        return risks
    
    def _analyze_dependency_risks(self, metrics: SprintMetrics) -> List[RiskFactor]:
        """Analyze dependency-related risks."""
        risks = []
        
        if metrics.external_dependencies > 0:
            # Risk increases with number of dependencies and time pressure
            impact = min(1.0, metrics.external_dependencies / 5)
            probability = min(0.9, 0.3 + (metrics.external_dependencies * 0.2))
            
            risks.append(RiskFactor(
                factor_id="external_dependencies",
                category=RiskCategory.DEPENDENCIES,
                description=f"Sprint has {metrics.external_dependencies} external dependencies",
                impact_score=impact,
                probability=probability,
                risk_score=impact * probability,
                confidence=0.6,
                data_sources=["dependency_tracking"],
                mitigation_suggestions=[
                    "Proactively communicate with dependency owners",
                    "Develop contingency plans for critical dependencies",
                    "Consider parallel work streams where possible"
                ]
            ))
        
        return risks


class SprintRiskForecaster:
    """
    Main forecasting engine that combines all risk analysis components.
    """
    
    def __init__(self):
        self.velocity_analyzer = VelocityAnalyzer()
        self.risk_engine = RiskDetectionEngine(self.velocity_analyzer)
    
    def generate_forecast(self, sprint_metrics: SprintMetrics) -> SprintRiskForecast:
        """Generate comprehensive sprint risk forecast."""
        
        # Analyze all risk factors
        risk_factors = self.risk_engine.analyze_sprint_risks(sprint_metrics)
        
        # Calculate overall risk score
        overall_risk_score = self._calculate_overall_risk(risk_factors)
        overall_risk_level = self._determine_risk_level(overall_risk_score)
        
        # Predict completion probability
        predicted_velocity, velocity_confidence = self.velocity_analyzer.predict_sprint_velocity(sprint_metrics)
        completion_probability = min(1.0, predicted_velocity / sprint_metrics.planned_points) if sprint_metrics.planned_points > 0 else 1.0
        
        # Predict completion date
        predicted_completion_date = self._predict_completion_date(sprint_metrics, predicted_velocity)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_factors, sprint_metrics)
        
        # Calculate overall confidence
        confidence = self._calculate_forecast_confidence(risk_factors, velocity_confidence)
        
        forecast = SprintRiskForecast(
            forecast_id=f"forecast_{sprint_metrics.sprint_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            sprint_id=sprint_metrics.sprint_id,
            team_id=sprint_metrics.team_id,
            overall_risk_level=overall_risk_level,
            overall_risk_score=overall_risk_score,
            completion_probability=completion_probability,
            predicted_completion_date=predicted_completion_date,
            risk_factors=risk_factors,
            recommendations=recommendations,
            confidence=confidence,
            forecast_timestamp=datetime.now(),
            data_freshness=datetime.now()
        )
        
        return forecast
    
    def _calculate_overall_risk(self, risk_factors: List[RiskFactor]) -> float:
        """Calculate overall risk score from individual factors."""
        if not risk_factors:
            return 0.0
        
        # Weight risks by category
        category_weights = {
            RiskCategory.VELOCITY: 0.3,
            RiskCategory.SCOPE: 0.2,
            RiskCategory.CAPACITY: 0.25,
            RiskCategory.QUALITY: 0.15,
            RiskCategory.DEPENDENCIES: 0.1
        }
        
        weighted_risk = 0.0
        total_weight = 0.0
        
        for risk in risk_factors:
            weight = category_weights.get(risk.category, 0.1)
            weighted_risk += risk.risk_score * weight * risk.confidence
            total_weight += weight
        
        return min(1.0, weighted_risk / total_weight if total_weight > 0 else 0.0)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from numeric score."""
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _predict_completion_date(self, metrics: SprintMetrics, predicted_velocity: float) -> datetime:
        """Predict actual completion date based on velocity."""
        if predicted_velocity <= 0:
            return metrics.end_date + timedelta(days=7)  # Default extension
        
        remaining_points = metrics.planned_points - metrics.completed_points
        days_per_point = (metrics.end_date - metrics.start_date).days / predicted_velocity
        additional_days = remaining_points * days_per_point
        
        predicted_date = datetime.now() + timedelta(days=additional_days)
        
        # Don't predict completion before sprint end
        return max(predicted_date, metrics.end_date)
    
    def _generate_recommendations(self, risk_factors: List[RiskFactor], metrics: SprintMetrics) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on risks."""
        recommendations = []
        
        # Sort risks by severity
        high_risks = [r for r in risk_factors if r.risk_score >= 0.6]
        
        for risk in high_risks[:3]:  # Top 3 risks
            for suggestion in risk.mitigation_suggestions[:2]:  # Top 2 suggestions per risk
                recommendations.append({
                    "priority": "high" if risk.risk_score >= 0.8 else "medium",
                    "category": risk.category.value,
                    "action": suggestion,
                    "risk_factor": risk.factor_id,
                    "expected_impact": f"Reduce {risk.category.value} risk by {risk.risk_score * 0.3:.1%}",
                    "confidence": risk.confidence
                })
        
        # Add general recommendations based on sprint state
        if metrics.days_remaining <= 2:
            recommendations.append({
                "priority": "high",
                "category": "sprint_management",
                "action": "Focus on completing in-progress items rather than starting new work",
                "risk_factor": "time_pressure",
                "expected_impact": "Maximize sprint completion rate",
                "confidence": 0.9
            })
        
        return recommendations
    
    def _calculate_forecast_confidence(self, risk_factors: List[RiskFactor], velocity_confidence: float) -> float:
        """Calculate overall forecast confidence."""
        if not risk_factors:
            return velocity_confidence * 0.7  # Lower confidence with no risk data
        
        # Average confidence of risk factors
        avg_risk_confidence = sum(r.confidence for r in risk_factors) / len(risk_factors)
        
        # Combine with velocity confidence
        overall_confidence = (velocity_confidence * 0.4 + avg_risk_confidence * 0.6)
        
        # Reduce confidence for high-risk situations
        high_risk_count = len([r for r in risk_factors if r.risk_score >= 0.7])
        confidence_penalty = min(0.3, high_risk_count * 0.1)
        
        return max(0.3, overall_confidence - confidence_penalty)


# Example usage and testing
if __name__ == "__main__":
    # Initialize forecaster
    forecaster = SprintRiskForecaster()
    
    # Example sprint metrics
    sprint_metrics = SprintMetrics(
        sprint_id="SPRINT-24-3",
        team_id="team_alpha",
        start_date=datetime.now() - timedelta(days=10),
        end_date=datetime.now() + timedelta(days=4),
        planned_points=50,
        completed_points=35,
        in_progress_points=10,
        blocked_points=5,
        team_capacity=0.9,
        days_remaining=4,
        velocity_trend=0.8,
        defect_count=3,
        code_review_backlog=7,
        external_dependencies=2,
        scope_changes=4
    )
    
    # Generate forecast
    forecast = forecaster.generate_forecast(sprint_metrics)
    
    print("Sprint Risk Forecast Implementation Complete!")
    print(f"Overall Risk Level: {forecast.overall_risk_level.value}")
    print(f"Completion Probability: {forecast.completion_probability:.1%}")
    print(f"Risk Factors Identified: {len(forecast.risk_factors)}")
    print(f"Recommendations Generated: {len(forecast.recommendations)}")
    print(f"Forecast Confidence: {forecast.confidence:.1%}")

