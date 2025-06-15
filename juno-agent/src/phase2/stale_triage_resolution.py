"""
JUNO Phase 2: Stale Triage Resolution Engine
Autonomous system for identifying and resolving stale tickets with Lead/PM oversight.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TriageAction(Enum):
    """Available triage actions."""
    REASSIGN = "reassign"
    ESCALATE = "escalate"
    DEFER = "defer"
    CLOSE = "close"
    UPDATE_PRIORITY = "update_priority"
    REQUEST_INFO = "request_info"


class TicketStatus(Enum):
    """Ticket status classifications."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    WAITING = "waiting"
    RESOLVED = "resolved"
    CLOSED = "closed"


class StalenessLevel(Enum):
    """Staleness level classifications."""
    FRESH = "fresh"
    AGING = "aging"
    STALE = "stale"
    CRITICAL = "critical"


@dataclass
class TicketInfo:
    """Comprehensive ticket information for triage analysis."""
    ticket_id: str
    title: str
    description: str
    status: TicketStatus
    priority: str
    assignee: Optional[str]
    reporter: str
    created_date: datetime
    last_updated: datetime
    last_comment_date: Optional[datetime]
    story_points: Optional[int]
    labels: List[str]
    components: List[str]
    sprint_id: Optional[str]
    team_id: str
    dependencies: List[str]
    watchers: List[str]
    time_in_status: timedelta
    comment_count: int
    activity_score: float


@dataclass
class TriageRecommendation:
    """Triage action recommendation with reasoning."""
    ticket_id: str
    recommended_action: TriageAction
    confidence: float
    reasoning: str
    urgency_score: float
    staleness_level: StalenessLevel
    suggested_assignee: Optional[str]
    escalation_target: Optional[str]
    estimated_effort: Optional[str]
    business_impact: str
    technical_impact: str
    dependencies_affected: List[str]
    approval_required: bool
    auto_executable: bool


class StalenessAnalyzer:
    """
    Analyzes ticket staleness and determines appropriate actions.
    """
    
    def __init__(self):
        self.staleness_thresholds = {
            'aging_days': 3,
            'stale_days': 7,
            'critical_days': 14
        }
        
        self.priority_weights = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4,
            'trivial': 0.2
        }
    
    def analyze_staleness(self, ticket: TicketInfo) -> Tuple[StalenessLevel, float]:
        """Analyze ticket staleness level and urgency score."""
        
        # Calculate days since last activity
        last_activity = max(
            ticket.last_updated,
            ticket.last_comment_date or datetime.min
        )
        days_stale = (datetime.now() - last_activity).days
        
        # Determine staleness level
        if days_stale >= self.staleness_thresholds['critical_days']:
            staleness_level = StalenessLevel.CRITICAL
        elif days_stale >= self.staleness_thresholds['stale_days']:
            staleness_level = StalenessLevel.STALE
        elif days_stale >= self.staleness_thresholds['aging_days']:
            staleness_level = StalenessLevel.AGING
        else:
            staleness_level = StalenessLevel.FRESH
        
        # Calculate urgency score
        urgency_score = self._calculate_urgency_score(ticket, days_stale)
        
        return staleness_level, urgency_score
    
    def _calculate_urgency_score(self, ticket: TicketInfo, days_stale: int) -> float:
        """Calculate urgency score based on multiple factors."""
        
        # Base urgency from staleness
        staleness_urgency = min(1.0, days_stale / 14)  # Max at 14 days
        
        # Priority weight
        priority_weight = self.priority_weights.get(ticket.priority.lower(), 0.5)
        
        # Sprint assignment weight
        sprint_weight = 1.2 if ticket.sprint_id else 0.8
        
        # Dependency weight
        dependency_weight = 1.0 + (len(ticket.dependencies) * 0.1)
        
        # Activity weight (inverse of activity score)
        activity_weight = max(0.5, 1.0 - ticket.activity_score)
        
        # Watcher weight (more watchers = higher urgency)
        watcher_weight = 1.0 + (len(ticket.watchers) * 0.05)
        
        # Combined urgency score
        urgency_score = (
            staleness_urgency * 0.4 +
            priority_weight * 0.3 +
            activity_weight * 0.2 +
            dependency_weight * 0.1
        ) * sprint_weight * watcher_weight
        
        return min(1.0, urgency_score)


class ActionRecommendationEngine:
    """
    Recommends appropriate triage actions based on ticket analysis.
    """
    
    def __init__(self):
        self.action_rules = self._initialize_action_rules()
        self.team_patterns = {}  # team_id -> patterns
    
    def _initialize_action_rules(self) -> Dict[str, Any]:
        """Initialize action recommendation rules."""
        return {
            'reassign_conditions': {
                'assignee_inactive': 7,  # days
                'workload_threshold': 0.9,
                'skill_mismatch_indicators': ['needs_expertise', 'complex_technical']
            },
            'escalate_conditions': {
                'high_priority_stale_days': 5,
                'critical_priority_stale_days': 3,
                'dependency_blocker': True,
                'external_dependency': True
            },
            'defer_conditions': {
                'low_priority_threshold': 0.3,
                'no_sprint_assignment': True,
                'future_release_labels': ['future', 'backlog', 'nice-to-have']
            },
            'close_conditions': {
                'duplicate_indicators': ['duplicate', 'wont-fix'],
                'obsolete_indicators': ['obsolete', 'outdated'],
                'no_activity_days': 30
            }
        }
    
    def recommend_action(self, ticket: TicketInfo, staleness_level: StalenessLevel, urgency_score: float) -> TriageRecommendation:
        """Generate triage action recommendation."""
        
        # Analyze different action options
        reassign_score = self._evaluate_reassign_action(ticket, staleness_level, urgency_score)
        escalate_score = self._evaluate_escalate_action(ticket, staleness_level, urgency_score)
        defer_score = self._evaluate_defer_action(ticket, staleness_level, urgency_score)
        close_score = self._evaluate_close_action(ticket, staleness_level, urgency_score)
        
        # Select best action
        action_scores = [
            (TriageAction.REASSIGN, reassign_score),
            (TriageAction.ESCALATE, escalate_score),
            (TriageAction.DEFER, defer_score),
            (TriageAction.CLOSE, close_score)
        ]
        
        best_action, confidence = max(action_scores, key=lambda x: x[1])
        
        # Generate detailed recommendation
        recommendation = self._create_recommendation(
            ticket, best_action, confidence, staleness_level, urgency_score
        )
        
        return recommendation
    
    def _evaluate_reassign_action(self, ticket: TicketInfo, staleness_level: StalenessLevel, urgency_score: float) -> float:
        """Evaluate reassignment action score."""
        score = 0.0
        
        # No assignee
        if not ticket.assignee:
            score += 0.8
        
        # Assignee inactive (heuristic based on last update)
        elif (datetime.now() - ticket.last_updated).days > self.action_rules['reassign_conditions']['assignee_inactive']:
            score += 0.7
        
        # High priority with staleness
        if ticket.priority.lower() in ['high', 'critical'] and staleness_level in [StalenessLevel.STALE, StalenessLevel.CRITICAL]:
            score += 0.6
        
        # Sprint assignment without progress
        if ticket.sprint_id and ticket.status == TicketStatus.OPEN:
            score += 0.5
        
        return min(1.0, score)
    
    def _evaluate_escalate_action(self, ticket: TicketInfo, staleness_level: StalenessLevel, urgency_score: float) -> float:
        """Evaluate escalation action score."""
        score = 0.0
        
        # High priority stale tickets
        if ticket.priority.lower() == 'critical' and staleness_level in [StalenessLevel.STALE, StalenessLevel.CRITICAL]:
            score += 0.9
        elif ticket.priority.lower() == 'high' and staleness_level == StalenessLevel.CRITICAL:
            score += 0.8
        
        # Blocked status
        if ticket.status == TicketStatus.BLOCKED:
            score += 0.7
        
        # Dependencies
        if ticket.dependencies:
            score += 0.6
        
        # Sprint assignment with no progress
        if ticket.sprint_id and staleness_level in [StalenessLevel.STALE, StalenessLevel.CRITICAL]:
            score += 0.5
        
        return min(1.0, score)
    
    def _evaluate_defer_action(self, ticket: TicketInfo, staleness_level: StalenessLevel, urgency_score: float) -> float:
        """Evaluate defer action score."""
        score = 0.0
        
        # Low priority
        if ticket.priority.lower() in ['low', 'trivial']:
            score += 0.7
        
        # No sprint assignment
        if not ticket.sprint_id:
            score += 0.6
        
        # Future release labels
        future_labels = self.action_rules['defer_conditions']['future_release_labels']
        if any(label.lower() in future_labels for label in ticket.labels):
            score += 0.8
        
        # Low urgency score
        if urgency_score < 0.3:
            score += 0.5
        
        return min(1.0, score)
    
    def _evaluate_close_action(self, ticket: TicketInfo, staleness_level: StalenessLevel, urgency_score: float) -> float:
        """Evaluate close action score."""
        score = 0.0
        
        # Duplicate or obsolete indicators
        close_indicators = (
            self.action_rules['close_conditions']['duplicate_indicators'] +
            self.action_rules['close_conditions']['obsolete_indicators']
        )
        
        if any(indicator in ticket.labels or indicator in ticket.title.lower() for indicator in close_indicators):
            score += 0.9
        
        # Very old with no activity
        if staleness_level == StalenessLevel.CRITICAL and urgency_score < 0.2:
            score += 0.6
        
        # No comments and low priority
        if ticket.comment_count == 0 and ticket.priority.lower() in ['low', 'trivial']:
            score += 0.5
        
        return min(1.0, score)
    
    def _create_recommendation(
        self, 
        ticket: TicketInfo, 
        action: TriageAction, 
        confidence: float,
        staleness_level: StalenessLevel, 
        urgency_score: float
    ) -> TriageRecommendation:
        """Create detailed triage recommendation."""
        
        # Generate reasoning
        reasoning = self._generate_reasoning(ticket, action, staleness_level, urgency_score)
        
        # Determine approval requirements
        approval_required = self._requires_approval(ticket, action, urgency_score)
        auto_executable = confidence > 0.8 and not approval_required
        
        # Generate additional details
        suggested_assignee = self._suggest_assignee(ticket, action)
        escalation_target = self._suggest_escalation_target(ticket, action)
        business_impact = self._assess_business_impact(ticket, urgency_score)
        technical_impact = self._assess_technical_impact(ticket)
        
        return TriageRecommendation(
            ticket_id=ticket.ticket_id,
            recommended_action=action,
            confidence=confidence,
            reasoning=reasoning,
            urgency_score=urgency_score,
            staleness_level=staleness_level,
            suggested_assignee=suggested_assignee,
            escalation_target=escalation_target,
            estimated_effort=self._estimate_effort(ticket),
            business_impact=business_impact,
            technical_impact=technical_impact,
            dependencies_affected=ticket.dependencies,
            approval_required=approval_required,
            auto_executable=auto_executable
        )
    
    def _generate_reasoning(self, ticket: TicketInfo, action: TriageAction, staleness_level: StalenessLevel, urgency_score: float) -> str:
        """Generate human-readable reasoning for the recommendation."""
        
        staleness_days = (datetime.now() - max(ticket.last_updated, ticket.last_comment_date or datetime.min)).days
        
        base_reasoning = f"Ticket has been {staleness_level.value} for {staleness_days} days with urgency score {urgency_score:.2f}."
        
        action_reasoning = {
            TriageAction.REASSIGN: f"Reassignment recommended due to {'no assignee' if not ticket.assignee else 'assignee inactivity'} and {ticket.priority} priority.",
            TriageAction.ESCALATE: f"Escalation needed for {ticket.priority} priority ticket with {staleness_level.value} status and potential blockers.",
            TriageAction.DEFER: f"Deferral appropriate for {ticket.priority} priority ticket with low urgency and no immediate sprint assignment.",
            TriageAction.CLOSE: f"Closure recommended based on staleness, low activity, and indicators suggesting ticket may be obsolete or duplicate."
        }
        
        return f"{base_reasoning} {action_reasoning.get(action, 'Action recommended based on analysis.')}"
    
    def _requires_approval(self, ticket: TicketInfo, action: TriageAction, urgency_score: float) -> bool:
        """Determine if action requires Lead/PM approval."""
        
        # High-impact actions always require approval
        if action in [TriageAction.CLOSE, TriageAction.ESCALATE]:
            return True
        
        # High priority tickets require approval
        if ticket.priority.lower() in ['critical', 'high']:
            return True
        
        # Sprint-assigned tickets require approval
        if ticket.sprint_id:
            return True
        
        # High urgency requires approval
        if urgency_score > 0.7:
            return True
        
        return False
    
    def _suggest_assignee(self, ticket: TicketInfo, action: TriageAction) -> Optional[str]:
        """Suggest new assignee for reassignment actions."""
        if action != TriageAction.REASSIGN:
            return None
        
        # This would integrate with team capacity and skill matching
        # For now, return placeholder logic
        if 'frontend' in ticket.components:
            return "frontend_lead"
        elif 'backend' in ticket.components:
            return "backend_lead"
        else:
            return "team_lead"
    
    def _suggest_escalation_target(self, ticket: TicketInfo, action: TriageAction) -> Optional[str]:
        """Suggest escalation target."""
        if action != TriageAction.ESCALATE:
            return None
        
        if ticket.priority.lower() == 'critical':
            return "engineering_manager"
        else:
            return "team_lead"
    
    def _assess_business_impact(self, ticket: TicketInfo, urgency_score: float) -> str:
        """Assess business impact of the ticket."""
        if urgency_score > 0.8:
            return "High - Critical business functionality affected"
        elif urgency_score > 0.6:
            return "Medium - Important feature or workflow impacted"
        elif urgency_score > 0.3:
            return "Low - Minor impact on user experience"
        else:
            return "Minimal - Limited or no immediate business impact"
    
    def _assess_technical_impact(self, ticket: TicketInfo) -> str:
        """Assess technical impact of the ticket."""
        if len(ticket.dependencies) > 2:
            return "High - Blocks multiple other tickets or features"
        elif ticket.dependencies:
            return "Medium - Has dependencies that may be affected"
        else:
            return "Low - Isolated change with minimal dependencies"
    
    def _estimate_effort(self, ticket: TicketInfo) -> Optional[str]:
        """Estimate effort required for ticket resolution."""
        if ticket.story_points:
            if ticket.story_points <= 2:
                return "Small (1-2 days)"
            elif ticket.story_points <= 5:
                return "Medium (3-5 days)"
            elif ticket.story_points <= 8:
                return "Large (1-2 weeks)"
            else:
                return "Extra Large (2+ weeks)"
        
        # Fallback estimation based on description length and complexity indicators
        description_length = len(ticket.description) if ticket.description else 0
        if description_length > 1000 or any(word in ticket.title.lower() for word in ['complex', 'refactor', 'architecture']):
            return "Large (1-2 weeks)"
        elif description_length > 500:
            return "Medium (3-5 days)"
        else:
            return "Small (1-2 days)"


class StaleTriageEngine:
    """
    Main engine for stale triage resolution with autonomous capabilities.
    """
    
    def __init__(self):
        self.staleness_analyzer = StalenessAnalyzer()
        self.recommendation_engine = ActionRecommendationEngine()
        self.processed_tickets = {}  # ticket_id -> last_processed_time
    
    def analyze_stale_tickets(self, tickets: List[TicketInfo]) -> List[TriageRecommendation]:
        """Analyze tickets and generate triage recommendations."""
        recommendations = []
        
        for ticket in tickets:
            # Skip recently processed tickets
            if self._recently_processed(ticket.ticket_id):
                continue
            
            # Analyze staleness
            staleness_level, urgency_score = self.staleness_analyzer.analyze_staleness(ticket)
            
            # Skip fresh tickets unless they have other issues
            if staleness_level == StalenessLevel.FRESH and urgency_score < 0.5:
                continue
            
            # Generate recommendation
            recommendation = self.recommendation_engine.recommend_action(
                ticket, staleness_level, urgency_score
            )
            
            recommendations.append(recommendation)
            
            # Mark as processed
            self.processed_tickets[ticket.ticket_id] = datetime.now()
        
        # Sort by urgency and confidence
        recommendations.sort(key=lambda r: (r.urgency_score * r.confidence), reverse=True)
        
        return recommendations
    
    def _recently_processed(self, ticket_id: str, hours: int = 24) -> bool:
        """Check if ticket was recently processed."""
        if ticket_id not in self.processed_tickets:
            return False
        
        last_processed = self.processed_tickets[ticket_id]
        return (datetime.now() - last_processed) < timedelta(hours=hours)
    
    def execute_autonomous_actions(self, recommendations: List[TriageRecommendation]) -> List[Dict[str, Any]]:
        """Execute autonomous actions for recommendations that don't require approval."""
        executed_actions = []
        
        for recommendation in recommendations:
            if recommendation.auto_executable and recommendation.confidence > 0.8:
                # Execute the action (this would integrate with Jira API)
                action_result = self._execute_action(recommendation)
                executed_actions.append(action_result)
        
        return executed_actions
    
    def _execute_action(self, recommendation: TriageRecommendation) -> Dict[str, Any]:
        """Execute a specific triage action."""
        # This would integrate with actual Jira API
        # For now, return simulation of action execution
        
        action_result = {
            "ticket_id": recommendation.ticket_id,
            "action": recommendation.recommended_action.value,
            "executed_at": datetime.now().isoformat(),
            "confidence": recommendation.confidence,
            "reasoning": recommendation.reasoning,
            "success": True,
            "details": {}
        }
        
        if recommendation.recommended_action == TriageAction.REASSIGN:
            action_result["details"] = {
                "new_assignee": recommendation.suggested_assignee,
                "comment": f"Auto-reassigned due to staleness. Reasoning: {recommendation.reasoning}"
            }
        elif recommendation.recommended_action == TriageAction.DEFER:
            action_result["details"] = {
                "moved_to": "backlog",
                "comment": f"Deferred due to low priority and staleness. Reasoning: {recommendation.reasoning}"
            }
        
        logger.info(f"Executed {recommendation.recommended_action.value} for ticket {recommendation.ticket_id}")
        
        return action_result


# Example usage and testing
if __name__ == "__main__":
    # Initialize stale triage engine
    triage_engine = StaleTriageEngine()
    
    # Example stale tickets
    stale_tickets = [
        TicketInfo(
            ticket_id="JIRA-123",
            title="Fix login bug",
            description="Users cannot login with special characters",
            status=TicketStatus.OPEN,
            priority="high",
            assignee=None,
            reporter="user@example.com",
            created_date=datetime.now() - timedelta(days=10),
            last_updated=datetime.now() - timedelta(days=8),
            last_comment_date=datetime.now() - timedelta(days=8),
            story_points=3,
            labels=["bug", "login"],
            components=["frontend"],
            sprint_id="SPRINT-24-3",
            team_id="team_alpha",
            dependencies=[],
            watchers=["pm@example.com"],
            time_in_status=timedelta(days=8),
            comment_count=2,
            activity_score=0.2
        )
    ]
    
    # Analyze and generate recommendations
    recommendations = triage_engine.analyze_stale_tickets(stale_tickets)
    
    # Execute autonomous actions
    executed_actions = triage_engine.execute_autonomous_actions(recommendations)
    
    print("Stale Triage Resolution Engine Implementation Complete!")
    print(f"Recommendations Generated: {len(recommendations)}")
    print(f"Autonomous Actions Executed: {len(executed_actions)}")
    
    if recommendations:
        rec = recommendations[0]
        print(f"Top Recommendation: {rec.recommended_action.value} for {rec.ticket_id}")
        print(f"Confidence: {rec.confidence:.1%}")
        print(f"Reasoning: {rec.reasoning}")

