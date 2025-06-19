"""
JUNO Phase 2: Velocity Analysis Engine
Advanced velocity tracking and prediction for sprint planning and risk assessment.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import json
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class VelocityTrend(Enum):
    """Velocity trend classifications."""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"


@dataclass
class VelocityDataPoint:
    """Single velocity measurement."""
    sprint_id: str
    team_id: str
    sprint_start: datetime
    sprint_end: datetime
    planned_points: int
    completed_points: int
    velocity: float
    team_capacity: float
    scope_changes: int
    external_factors: List[str]


@dataclass
class VelocityAnalysis:
    """Comprehensive velocity analysis results."""
    team_id: str
    analysis_period: Tuple[datetime, datetime]
    current_velocity: float
    average_velocity: float
    velocity_trend: VelocityTrend
    trend_strength: float  # 0.0 - 1.0
    velocity_stability: float  # 0.0 - 1.0 (higher = more stable)
    prediction_confidence: float
    seasonal_patterns: Dict[str, float]
    capacity_correlation: float
    bottleneck_indicators: List[str]
    recommendations: List[str]


class VelocityPredictor:
    """
    Advanced velocity prediction using multiple algorithms and historical patterns.
    """
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.velocity_history = []
        self.seasonal_patterns = {}
        self.capacity_factors = {}
        
    def add_velocity_data(self, velocity_data: VelocityDataPoint) -> None:
        """Add velocity data point to historical dataset."""
        self.velocity_history.append(velocity_data)
        self._update_patterns()
    
    def _update_patterns(self) -> None:
        """Update seasonal and capacity patterns from historical data."""
        if len(self.velocity_history) < 3:
            return
        
        # Analyze seasonal patterns (by month, quarter)
        monthly_velocities = defaultdict(list)
        quarterly_velocities = defaultdict(list)
        
        for data in self.velocity_history:
            month = data.sprint_start.month
            quarter = (data.sprint_start.month - 1) // 3 + 1
            
            monthly_velocities[month].append(data.velocity)
            quarterly_velocities[quarter].append(data.velocity)
        
        # Calculate seasonal factors
        overall_avg = statistics.mean([d.velocity for d in self.velocity_history])
        
        self.seasonal_patterns = {
            'monthly': {
                month: statistics.mean(velocities) / overall_avg
                for month, velocities in monthly_velocities.items()
                if len(velocities) >= 2
            },
            'quarterly': {
                quarter: statistics.mean(velocities) / overall_avg
                for quarter, velocities in quarterly_velocities.items()
                if len(velocities) >= 2
            }
        }
        
        # Analyze capacity correlation
        if len(self.velocity_history) >= 5:
            capacities = [d.team_capacity for d in self.velocity_history]
            velocities = [d.velocity for d in self.velocity_history]
            
            # Simple correlation calculation
            capacity_corr = np.corrcoef(capacities, velocities)[0, 1]
            self.capacity_factors['correlation'] = capacity_corr if not np.isnan(capacity_corr) else 0.0
    
    def predict_velocity(
        self, 
        planned_points: int,
        team_capacity: float,
        sprint_start: datetime,
        external_factors: Optional[List[str]] = None
    ) -> Tuple[float, float]:
        """
        Predict velocity for upcoming sprint.
        Returns: (predicted_velocity, confidence)
        """
        if len(self.velocity_history) < 3:
            return self._simple_velocity_prediction(planned_points, team_capacity)
        
        # Multiple prediction methods
        trend_prediction = self._trend_based_prediction()
        seasonal_prediction = self._seasonal_adjusted_prediction(sprint_start)
        capacity_prediction = self._capacity_adjusted_prediction(team_capacity)
        
        # Weighted combination
        predictions = [
            (trend_prediction[0], 0.4, trend_prediction[1]),
            (seasonal_prediction[0], 0.3, seasonal_prediction[1]),
            (capacity_prediction[0], 0.3, capacity_prediction[1])
        ]
        
        # Calculate weighted average
        total_weight = 0.0
        weighted_velocity = 0.0
        weighted_confidence = 0.0
        
        for velocity, weight, confidence in predictions:
            adjusted_weight = weight * confidence
            total_weight += adjusted_weight
            weighted_velocity += velocity * adjusted_weight
            weighted_confidence += confidence * adjusted_weight
        
        if total_weight > 0:
            final_velocity = weighted_velocity / total_weight
            final_confidence = weighted_confidence / total_weight
        else:
            final_velocity, final_confidence = self._simple_velocity_prediction(planned_points, team_capacity)
        
        # Apply external factor adjustments
        if external_factors:
            adjustment_factor = self._calculate_external_factor_impact(external_factors)
            final_velocity *= adjustment_factor
            final_confidence *= 0.9  # Reduce confidence when external factors present
        
        return final_velocity, min(0.95, final_confidence)
    
    def _trend_based_prediction(self) -> Tuple[float, float]:
        """Predict based on velocity trend analysis."""
        recent_velocities = [d.velocity for d in self.velocity_history[-6:]]  # Last 6 sprints
        
        if len(recent_velocities) < 3:
            avg_velocity = statistics.mean(recent_velocities)
            return avg_velocity, 0.6
        
        # Linear trend calculation
        x = np.arange(len(recent_velocities))
        y = np.array(recent_velocities)
        
        # Simple linear regression
        slope, intercept = np.polyfit(x, y, 1)
        
        # Predict next point
        next_velocity = slope * len(recent_velocities) + intercept
        
        # Calculate confidence based on trend consistency
        trend_consistency = 1.0 - (np.std(recent_velocities) / np.mean(recent_velocities))
        confidence = max(0.3, min(0.9, trend_consistency))
        
        return max(0, next_velocity), confidence
    
    def _seasonal_adjusted_prediction(self, sprint_start: datetime) -> Tuple[float, float]:
        """Predict with seasonal adjustments."""
        base_velocity = statistics.mean([d.velocity for d in self.velocity_history[-4:]])
        
        month = sprint_start.month
        quarter = (sprint_start.month - 1) // 3 + 1
        
        # Apply seasonal factors
        seasonal_factor = 1.0
        confidence = 0.7
        
        if month in self.seasonal_patterns.get('monthly', {}):
            seasonal_factor = self.seasonal_patterns['monthly'][month]
            confidence = 0.8
        elif quarter in self.seasonal_patterns.get('quarterly', {}):
            seasonal_factor = self.seasonal_patterns['quarterly'][quarter]
            confidence = 0.75
        
        adjusted_velocity = base_velocity * seasonal_factor
        
        return adjusted_velocity, confidence
    
    def _capacity_adjusted_prediction(self, team_capacity: float) -> Tuple[float, float]:
        """Predict based on team capacity correlation."""
        base_velocity = statistics.mean([d.velocity for d in self.velocity_history[-4:]])
        
        if 'correlation' not in self.capacity_factors:
            return base_velocity, 0.6
        
        correlation = self.capacity_factors['correlation']
        
        # Calculate capacity adjustment
        avg_capacity = statistics.mean([d.team_capacity for d in self.velocity_history[-4:]])
        capacity_ratio = team_capacity / avg_capacity if avg_capacity > 0 else 1.0
        
        # Apply capacity adjustment based on correlation strength
        if abs(correlation) > 0.5:  # Strong correlation
            capacity_factor = 1.0 + (capacity_ratio - 1.0) * abs(correlation)
            confidence = 0.8
        else:  # Weak correlation
            capacity_factor = 1.0 + (capacity_ratio - 1.0) * 0.2
            confidence = 0.6
        
        adjusted_velocity = base_velocity * capacity_factor
        
        return adjusted_velocity, confidence
    
    def _simple_velocity_prediction(self, planned_points: int, team_capacity: float) -> Tuple[float, float]:
        """Fallback simple prediction for insufficient data."""
        if not self.velocity_history:
            # Very basic heuristic
            estimated_velocity = planned_points * team_capacity * 0.8
            return estimated_velocity, 0.4
        
        # Use recent average
        recent_avg = statistics.mean([d.velocity for d in self.velocity_history[-3:]])
        return recent_avg, 0.5
    
    def _calculate_external_factor_impact(self, external_factors: List[str]) -> float:
        """Calculate impact of external factors on velocity."""
        impact_factors = {
            'holidays': 0.8,
            'team_changes': 0.85,
            'major_release': 0.9,
            'infrastructure_changes': 0.9,
            'training': 0.85,
            'conferences': 0.9,
            'urgent_support': 0.8
        }
        
        total_impact = 1.0
        for factor in external_factors:
            if factor.lower() in impact_factors:
                total_impact *= impact_factors[factor.lower()]
        
        return max(0.5, total_impact)  # Don't reduce below 50%


class BottleneckDetector:
    """
    Identifies workflow bottlenecks that impact velocity.
    """
    
    def __init__(self):
        self.bottleneck_patterns = {
            'code_review': {
                'indicators': ['high_review_time', 'review_backlog'],
                'impact': 0.8,
                'solutions': ['Distribute review load', 'Set review time limits', 'Pair programming']
            },
            'testing': {
                'indicators': ['test_failures', 'long_test_cycles'],
                'impact': 0.7,
                'solutions': ['Improve test automation', 'Parallel testing', 'Test early and often']
            },
            'deployment': {
                'indicators': ['deployment_failures', 'long_deployment_time'],
                'impact': 0.6,
                'solutions': ['Automate deployment', 'Improve CI/CD pipeline', 'Feature flags']
            },
            'requirements': {
                'indicators': ['unclear_requirements', 'frequent_changes'],
                'impact': 0.9,
                'solutions': ['Better requirement gathering', 'Stakeholder alignment', 'Prototyping']
            }
        }
    
    def detect_bottlenecks(self, velocity_history: List[VelocityDataPoint]) -> List[str]:
        """Detect bottlenecks from velocity patterns and external factors."""
        bottlenecks = []
        
        if len(velocity_history) < 3:
            return bottlenecks
        
        # Analyze velocity variance
        velocities = [d.velocity for d in velocity_history[-6:]]
        velocity_std = np.std(velocities)
        velocity_mean = np.mean(velocities)
        
        if velocity_std / velocity_mean > 0.3:  # High variance
            bottlenecks.append("Inconsistent delivery patterns suggest workflow bottlenecks")
        
        # Analyze external factors
        all_factors = []
        for data in velocity_history[-6:]:
            all_factors.extend(data.external_factors)
        
        factor_counts = defaultdict(int)
        for factor in all_factors:
            factor_counts[factor] += 1
        
        # Identify recurring issues
        for factor, count in factor_counts.items():
            if count >= 3:  # Appears in 3+ sprints
                bottlenecks.append(f"Recurring issue: {factor}")
        
        return bottlenecks


class VelocityAnalysisEngine:
    """
    Main engine for comprehensive velocity analysis and insights.
    """
    
    def __init__(self):
        self.predictors = {}  # team_id -> VelocityPredictor
        self.bottleneck_detector = BottleneckDetector()
    
    def get_or_create_predictor(self, team_id: str) -> VelocityPredictor:
        """Get or create velocity predictor for team."""
        if team_id not in self.predictors:
            self.predictors[team_id] = VelocityPredictor(team_id)
        return self.predictors[team_id]
    
    def analyze_team_velocity(
        self, 
        team_id: str, 
        velocity_history: List[VelocityDataPoint]
    ) -> VelocityAnalysis:
        """Perform comprehensive velocity analysis for a team."""
        
        if not velocity_history:
            return self._empty_analysis(team_id)
        
        # Update predictor with historical data
        predictor = self.get_or_create_predictor(team_id)
        for data in velocity_history:
            predictor.add_velocity_data(data)
        
        # Calculate basic metrics
        velocities = [d.velocity for d in velocity_history]
        current_velocity = velocities[-1] if velocities else 0.0
        average_velocity = statistics.mean(velocities)
        
        # Determine trend
        velocity_trend, trend_strength = self._analyze_trend(velocities)
        
        # Calculate stability
        velocity_stability = self._calculate_stability(velocities)
        
        # Prediction confidence
        prediction_confidence = self._calculate_prediction_confidence(velocity_history)
        
        # Detect bottlenecks
        bottlenecks = self.bottleneck_detector.detect_bottlenecks(velocity_history)
        
        # Generate recommendations
        recommendations = self._generate_velocity_recommendations(
            velocity_trend, velocity_stability, bottlenecks
        )
        
        analysis = VelocityAnalysis(
            team_id=team_id,
            analysis_period=(velocity_history[0].sprint_start, velocity_history[-1].sprint_end),
            current_velocity=current_velocity,
            average_velocity=average_velocity,
            velocity_trend=velocity_trend,
            trend_strength=trend_strength,
            velocity_stability=velocity_stability,
            prediction_confidence=prediction_confidence,
            seasonal_patterns=predictor.seasonal_patterns,
            capacity_correlation=predictor.capacity_factors.get('correlation', 0.0),
            bottleneck_indicators=bottlenecks,
            recommendations=recommendations
        )
        
        return analysis
    
    def _analyze_trend(self, velocities: List[float]) -> Tuple[VelocityTrend, float]:
        """Analyze velocity trend and strength."""
        if len(velocities) < 3:
            return VelocityTrend.STABLE, 0.0
        
        # Calculate trend using linear regression
        x = np.arange(len(velocities))
        y = np.array(velocities)
        
        slope, _ = np.polyfit(x, y, 1)
        
        # Calculate trend strength (R-squared)
        y_pred = np.polyval([slope, np.mean(y)], x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Determine trend direction
        avg_velocity = np.mean(velocities)
        slope_threshold = avg_velocity * 0.05  # 5% of average
        
        if abs(slope) < slope_threshold:
            trend = VelocityTrend.STABLE
        elif slope > slope_threshold:
            trend = VelocityTrend.IMPROVING
        else:
            trend = VelocityTrend.DECLINING
        
        # Check for volatility
        cv = np.std(velocities) / np.mean(velocities) if np.mean(velocities) > 0 else 0
        if cv > 0.3:  # High coefficient of variation
            trend = VelocityTrend.VOLATILE
        
        return trend, max(0.0, r_squared)
    
    def _calculate_stability(self, velocities: List[float]) -> float:
        """Calculate velocity stability score."""
        if len(velocities) < 2:
            return 0.0
        
        # Coefficient of variation (lower = more stable)
        cv = np.std(velocities) / np.mean(velocities) if np.mean(velocities) > 0 else 1.0
        
        # Convert to stability score (0-1, higher = more stable)
        stability = max(0.0, 1.0 - min(1.0, cv))
        
        return stability
    
    def _calculate_prediction_confidence(self, velocity_history: List[VelocityDataPoint]) -> float:
        """Calculate confidence in velocity predictions."""
        if len(velocity_history) < 3:
            return 0.3
        
        # Factors affecting confidence
        data_points = len(velocity_history)
        data_recency = (datetime.now() - velocity_history[-1].sprint_end).days
        
        # Base confidence from data quantity
        quantity_confidence = min(0.9, data_points / 10)
        
        # Recency factor (data older than 90 days reduces confidence)
        recency_factor = max(0.5, 1.0 - (data_recency / 90))
        
        # Stability factor
        velocities = [d.velocity for d in velocity_history]
        stability = self._calculate_stability(velocities)
        
        # Combined confidence
        confidence = quantity_confidence * recency_factor * (0.5 + stability * 0.5)
        
        return min(0.95, confidence)
    
    def _generate_velocity_recommendations(
        self, 
        trend: VelocityTrend, 
        stability: float, 
        bottlenecks: List[str]
    ) -> List[str]:
        """Generate actionable velocity improvement recommendations."""
        recommendations = []
        
        # Trend-based recommendations
        if trend == VelocityTrend.DECLINING:
            recommendations.extend([
                "Investigate root causes of velocity decline",
                "Review team capacity and workload distribution",
                "Consider process improvements or training"
            ])
        elif trend == VelocityTrend.VOLATILE:
            recommendations.extend([
                "Focus on process standardization",
                "Improve sprint planning consistency",
                "Address recurring blockers and interruptions"
            ])
        elif trend == VelocityTrend.IMPROVING:
            recommendations.append("Identify and replicate successful practices")
        
        # Stability-based recommendations
        if stability < 0.5:
            recommendations.extend([
                "Implement more consistent development practices",
                "Improve estimation accuracy",
                "Reduce external interruptions and scope changes"
            ])
        
        # Bottleneck-based recommendations
        if bottlenecks:
            recommendations.append("Address identified workflow bottlenecks")
            for bottleneck in bottlenecks[:2]:  # Top 2 bottlenecks
                recommendations.append(f"Focus on: {bottleneck}")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _empty_analysis(self, team_id: str) -> VelocityAnalysis:
        """Return empty analysis for teams with no data."""
        return VelocityAnalysis(
            team_id=team_id,
            analysis_period=(datetime.now(), datetime.now()),
            current_velocity=0.0,
            average_velocity=0.0,
            velocity_trend=VelocityTrend.STABLE,
            trend_strength=0.0,
            velocity_stability=0.0,
            prediction_confidence=0.0,
            seasonal_patterns={},
            capacity_correlation=0.0,
            bottleneck_indicators=[],
            recommendations=["Collect velocity data over multiple sprints for analysis"]
        )


# Example usage and testing
if __name__ == "__main__":
    # Initialize velocity analysis engine
    velocity_engine = VelocityAnalysisEngine()
    
    # Example velocity history
    velocity_history = [
        VelocityDataPoint(
            sprint_id=f"SPRINT-24-{i}",
            team_id="team_alpha",
            sprint_start=datetime.now() - timedelta(days=14*i),
            sprint_end=datetime.now() - timedelta(days=14*i-14),
            planned_points=50,
            completed_points=45 + np.random.randint(-5, 5),
            velocity=45 + np.random.randint(-5, 5),
            team_capacity=0.9,
            scope_changes=np.random.randint(0, 3),
            external_factors=["holidays"] if i == 2 else []
        )
        for i in range(6, 0, -1)
    ]
    
    # Analyze velocity
    analysis = velocity_engine.analyze_team_velocity("team_alpha", velocity_history)
    
    print("Velocity Analysis Engine Implementation Complete!")
    print(f"Current Velocity: {analysis.current_velocity}")
    print(f"Velocity Trend: {analysis.velocity_trend.value}")
    print(f"Stability Score: {analysis.velocity_stability:.2f}")
    print(f"Prediction Confidence: {analysis.prediction_confidence:.1%}")
    print(f"Recommendations: {len(analysis.recommendations)}")

