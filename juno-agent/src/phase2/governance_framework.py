"""
JUNO Phase 2: Governance Framework and Lead/PM Workflows
Enterprise-grade governance system for agentic AI operations with human oversight.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Approval status for governance actions."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    EXPIRED = "expired"


class GovernanceRole(Enum):
    """Governance roles in the system."""
    TEAM_LEAD = "team_lead"
    PROJECT_MANAGER = "project_manager"
    ENGINEERING_MANAGER = "engineering_manager"
    DIRECTOR = "director"
    ADMIN = "admin"


class ActionCategory(Enum):
    """Categories of actions requiring governance."""
    TICKET_MANAGEMENT = "ticket_management"
    SPRINT_PLANNING = "sprint_planning"
    RESOURCE_ALLOCATION = "resource_allocation"
    PROCESS_CHANGE = "process_change"
    ESCALATION = "escalation"


@dataclass
class GovernanceAction:
    """Represents an action requiring governance approval."""
    action_id: str
    action_type: str
    category: ActionCategory
    description: str
    proposed_by: str  # AI agent or user
    team_id: str
    impact_level: str  # low, medium, high, critical
    confidence_score: float
    reasoning: str
    data_sources: List[str]
    affected_tickets: List[str]
    estimated_impact: Dict[str, Any]
    requires_approval: bool
    approval_threshold: float
    created_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any]


@dataclass
class ApprovalRequest:
    """Approval request for governance actions."""
    request_id: str
    action_id: str
    requested_by: str
    approver_role: GovernanceRole
    approver_id: Optional[str]
    status: ApprovalStatus
    priority: str
    deadline: datetime
    approval_reason: Optional[str]
    rejection_reason: Optional[str]
    escalation_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    notification_sent: bool


@dataclass
class EscalationRule:
    """Rules for escalating governance decisions."""
    rule_id: str
    trigger_conditions: Dict[str, Any]
    escalation_path: List[GovernanceRole]
    timeout_hours: int
    auto_escalate: bool
    notification_template: str


class GovernanceRoleManager:
    """
    Manages governance roles and permissions.
    """
    
    def __init__(self):
        self.role_hierarchy = {
            GovernanceRole.ADMIN: 100,
            GovernanceRole.DIRECTOR: 80,
            GovernanceRole.ENGINEERING_MANAGER: 60,
            GovernanceRole.PROJECT_MANAGER: 40,
            GovernanceRole.TEAM_LEAD: 20
        }
        
        self.role_permissions = {
            GovernanceRole.TEAM_LEAD: {
                "approve_ticket_management": True,
                "approve_sprint_planning": True,
                "approve_resource_allocation": False,
                "approve_process_change": False,
                "escalate_decisions": True,
                "max_impact_level": "medium"
            },
            GovernanceRole.PROJECT_MANAGER: {
                "approve_ticket_management": True,
                "approve_sprint_planning": True,
                "approve_resource_allocation": True,
                "approve_process_change": False,
                "escalate_decisions": True,
                "max_impact_level": "high"
            },
            GovernanceRole.ENGINEERING_MANAGER: {
                "approve_ticket_management": True,
                "approve_sprint_planning": True,
                "approve_resource_allocation": True,
                "approve_process_change": True,
                "escalate_decisions": True,
                "max_impact_level": "critical"
            },
            GovernanceRole.DIRECTOR: {
                "approve_ticket_management": True,
                "approve_sprint_planning": True,
                "approve_resource_allocation": True,
                "approve_process_change": True,
                "escalate_decisions": False,
                "max_impact_level": "critical"
            },
            GovernanceRole.ADMIN: {
                "approve_ticket_management": True,
                "approve_sprint_planning": True,
                "approve_resource_allocation": True,
                "approve_process_change": True,
                "escalate_decisions": False,
                "max_impact_level": "critical"
            }
        }
        
        self.user_roles = {}  # user_id -> GovernanceRole
        self.team_assignments = {}  # user_id -> List[team_id]
    
    def assign_role(self, user_id: str, role: GovernanceRole, teams: List[str]) -> bool:
        """Assign governance role to user for specific teams."""
        self.user_roles[user_id] = role
        self.team_assignments[user_id] = teams
        logger.info(f"Assigned role {role.value} to user {user_id} for teams {teams}")
        return True
    
    def can_approve(self, user_id: str, action: GovernanceAction) -> bool:
        """Check if user can approve the given action."""
        if user_id not in self.user_roles:
            return False
        
        user_role = self.user_roles[user_id]
        user_teams = self.team_assignments.get(user_id, [])
        
        # Check team assignment
        if action.team_id not in user_teams and user_role not in [GovernanceRole.DIRECTOR, GovernanceRole.ADMIN]:
            return False
        
        # Check permissions
        permissions = self.role_permissions[user_role]
        category_permission = f"approve_{action.category.value}"
        
        if not permissions.get(category_permission, False):
            return False
        
        # Check impact level
        impact_levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        max_impact = permissions.get("max_impact_level", "low")
        
        if impact_levels.get(action.impact_level, 0) > impact_levels.get(max_impact, 0):
            return False
        
        return True
    
    def get_approver_for_action(self, action: GovernanceAction) -> Optional[GovernanceRole]:
        """Determine appropriate approver role for action."""
        impact_levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        impact_score = impact_levels.get(action.impact_level, 1)
        
        if impact_score <= 2:
            return GovernanceRole.TEAM_LEAD
        elif impact_score == 3:
            return GovernanceRole.PROJECT_MANAGER
        else:
            return GovernanceRole.ENGINEERING_MANAGER


class ApprovalWorkflowEngine:
    """
    Manages approval workflows for governance actions.
    """
    
    def __init__(self, role_manager: GovernanceRoleManager):
        self.role_manager = role_manager
        self.pending_requests = {}  # request_id -> ApprovalRequest
        self.approval_history = []
        self.escalation_rules = []
        self.notification_callbacks = []  # List of notification functions
    
    def submit_for_approval(self, action: GovernanceAction) -> str:
        """Submit action for approval workflow."""
        
        # Determine required approver
        required_role = self.role_manager.get_approver_for_action(action)
        
        # Create approval request
        request = ApprovalRequest(
            request_id=str(uuid.uuid4()),
            action_id=action.action_id,
            requested_by=action.proposed_by,
            approver_role=required_role,
            approver_id=None,
            status=ApprovalStatus.PENDING,
            priority=self._determine_priority(action),
            deadline=datetime.now() + timedelta(hours=self._get_approval_timeout(action)),
            approval_reason=None,
            rejection_reason=None,
            escalation_reason=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            notification_sent=False
        )
        
        self.pending_requests[request.request_id] = request
        
        # Send notification
        self._send_approval_notification(request, action)
        
        logger.info(f"Submitted action {action.action_id} for approval by {required_role.value}")
        return request.request_id
    
    def process_approval(
        self, 
        request_id: str, 
        approver_id: str, 
        approved: bool, 
        reason: str
    ) -> bool:
        """Process approval decision."""
        
        if request_id not in self.pending_requests:
            logger.error(f"Approval request {request_id} not found")
            return False
        
        request = self.pending_requests[request_id]
        
        # Verify approver permissions
        # This would integrate with actual user authentication
        # For now, assume approver_id is valid
        
        # Update request
        request.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        request.approver_id = approver_id
        request.updated_at = datetime.now()
        
        if approved:
            request.approval_reason = reason
        else:
            request.rejection_reason = reason
        
        # Move to history
        self.approval_history.append(request)
        del self.pending_requests[request_id]
        
        # Send notification
        self._send_decision_notification(request, approved)
        
        logger.info(f"Approval request {request_id} {'approved' if approved else 'rejected'} by {approver_id}")
        return True
    
    def escalate_request(self, request_id: str, escalation_reason: str) -> bool:
        """Escalate approval request to higher authority."""
        
        if request_id not in self.pending_requests:
            return False
        
        request = self.pending_requests[request_id]
        
        # Determine next escalation level
        next_role = self._get_escalation_role(request.approver_role)
        
        if not next_role:
            logger.warning(f"No escalation path available for request {request_id}")
            return False
        
        # Update request
        request.approver_role = next_role
        request.status = ApprovalStatus.ESCALATED
        request.escalation_reason = escalation_reason
        request.updated_at = datetime.now()
        request.deadline = datetime.now() + timedelta(hours=24)  # Reset deadline
        
        # Send escalation notification
        self._send_escalation_notification(request)
        
        logger.info(f"Escalated request {request_id} to {next_role.value}")
        return True
    
    def check_expired_requests(self) -> List[str]:
        """Check for expired approval requests and handle them."""
        expired_requests = []
        current_time = datetime.now()
        
        for request_id, request in list(self.pending_requests.items()):
            if current_time > request.deadline:
                # Auto-escalate or mark as expired
                if self._should_auto_escalate(request):
                    self.escalate_request(request_id, "Automatic escalation due to timeout")
                else:
                    request.status = ApprovalStatus.EXPIRED
                    self.approval_history.append(request)
                    del self.pending_requests[request_id]
                    expired_requests.append(request_id)
        
        return expired_requests
    
    def get_pending_approvals(self, approver_role: GovernanceRole, team_id: Optional[str] = None) -> List[ApprovalRequest]:
        """Get pending approval requests for a specific role/team."""
        pending = []
        
        for request in self.pending_requests.values():
            if request.approver_role == approver_role and request.status == ApprovalStatus.PENDING:
                # Add team filtering logic here if needed
                pending.append(request)
        
        return sorted(pending, key=lambda r: r.created_at)
    
    def _determine_priority(self, action: GovernanceAction) -> str:
        """Determine priority level for approval request."""
        if action.impact_level == "critical":
            return "urgent"
        elif action.impact_level == "high":
            return "high"
        elif action.confidence_score < 0.7:
            return "high"  # Low confidence requires urgent review
        else:
            return "normal"
    
    def _get_approval_timeout(self, action: GovernanceAction) -> int:
        """Get approval timeout in hours based on action characteristics."""
        if action.impact_level == "critical":
            return 4  # 4 hours for critical
        elif action.impact_level == "high":
            return 12  # 12 hours for high
        else:
            return 24  # 24 hours for medium/low
    
    def _get_escalation_role(self, current_role: GovernanceRole) -> Optional[GovernanceRole]:
        """Get next role in escalation hierarchy."""
        escalation_map = {
            GovernanceRole.TEAM_LEAD: GovernanceRole.PROJECT_MANAGER,
            GovernanceRole.PROJECT_MANAGER: GovernanceRole.ENGINEERING_MANAGER,
            GovernanceRole.ENGINEERING_MANAGER: GovernanceRole.DIRECTOR,
            GovernanceRole.DIRECTOR: None,  # No further escalation
            GovernanceRole.ADMIN: None
        }
        return escalation_map.get(current_role)
    
    def _should_auto_escalate(self, request: ApprovalRequest) -> bool:
        """Determine if request should auto-escalate on timeout."""
        return request.priority in ["urgent", "high"]
    
    def _send_approval_notification(self, request: ApprovalRequest, action: GovernanceAction):
        """Send notification for new approval request."""
        notification_data = {
            "type": "approval_request",
            "request_id": request.request_id,
            "action_description": action.description,
            "impact_level": action.impact_level,
            "confidence": action.confidence_score,
            "deadline": request.deadline.isoformat(),
            "approver_role": request.approver_role.value
        }
        
        for callback in self.notification_callbacks:
            try:
                callback(notification_data)
            except Exception as e:
                logger.error(f"Notification callback failed: {e}")
    
    def _send_decision_notification(self, request: ApprovalRequest, approved: bool):
        """Send notification for approval decision."""
        notification_data = {
            "type": "approval_decision",
            "request_id": request.request_id,
            "approved": approved,
            "approver_id": request.approver_id,
            "reason": request.approval_reason if approved else request.rejection_reason
        }
        
        for callback in self.notification_callbacks:
            try:
                callback(notification_data)
            except Exception as e:
                logger.error(f"Notification callback failed: {e}")
    
    def _send_escalation_notification(self, request: ApprovalRequest):
        """Send notification for escalated request."""
        notification_data = {
            "type": "escalation",
            "request_id": request.request_id,
            "escalated_to": request.approver_role.value,
            "reason": request.escalation_reason
        }
        
        for callback in self.notification_callbacks:
            try:
                callback(notification_data)
            except Exception as e:
                logger.error(f"Notification callback failed: {e}")


class ComplianceMonitor:
    """
    Monitors compliance with governance policies and regulations.
    """
    
    def __init__(self):
        self.compliance_rules = {}
        self.audit_log = []
        self.compliance_violations = []
        self.reporting_callbacks = []
    
    def add_compliance_rule(self, rule_id: str, rule_definition: Dict[str, Any]):
        """Add compliance rule to monitor."""
        self.compliance_rules[rule_id] = {
            "definition": rule_definition,
            "created_at": datetime.now(),
            "violations": 0,
            "last_check": None
        }
    
    def check_compliance(self, action: GovernanceAction, approval_request: ApprovalRequest) -> Dict[str, Any]:
        """Check action compliance against all rules."""
        compliance_result = {
            "compliant": True,
            "violations": [],
            "warnings": [],
            "recommendations": []
        }
        
        for rule_id, rule_data in self.compliance_rules.items():
            rule_result = self._evaluate_rule(rule_id, rule_data["definition"], action, approval_request)
            
            if not rule_result["compliant"]:
                compliance_result["compliant"] = False
                compliance_result["violations"].extend(rule_result["violations"])
            
            compliance_result["warnings"].extend(rule_result.get("warnings", []))
            compliance_result["recommendations"].extend(rule_result.get("recommendations", []))
        
        # Log compliance check
        self.audit_log.append({
            "timestamp": datetime.now(),
            "action_id": action.action_id,
            "request_id": approval_request.request_id,
            "compliance_result": compliance_result
        })
        
        return compliance_result
    
    def _evaluate_rule(self, rule_id: str, rule_definition: Dict[str, Any], action: GovernanceAction, request: ApprovalRequest) -> Dict[str, Any]:
        """Evaluate specific compliance rule."""
        # This would contain actual compliance rule evaluation logic
        # For now, implement basic examples
        
        result = {"compliant": True, "violations": [], "warnings": [], "recommendations": []}
        
        # Example: Approval timeout compliance
        if rule_definition.get("type") == "approval_timeout":
            max_timeout = rule_definition.get("max_hours", 24)
            actual_timeout = (request.deadline - request.created_at).total_seconds() / 3600
            
            if actual_timeout > max_timeout:
                result["compliant"] = False
                result["violations"].append(f"Approval timeout ({actual_timeout:.1f}h) exceeds maximum ({max_timeout}h)")
        
        # Example: Impact level vs approver role compliance
        elif rule_definition.get("type") == "approver_authority":
            required_levels = rule_definition.get("impact_approver_mapping", {})
            required_role = required_levels.get(action.impact_level)
            
            if required_role and request.approver_role.value != required_role:
                result["warnings"].append(f"Impact level {action.impact_level} typically requires {required_role} approval")
        
        return result
    
    def generate_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report for specified period."""
        relevant_logs = [
            log for log in self.audit_log
            if start_date <= log["timestamp"] <= end_date
        ]
        
        total_actions = len(relevant_logs)
        compliant_actions = len([log for log in relevant_logs if log["compliance_result"]["compliant"]])
        
        violation_summary = defaultdict(int)
        for log in relevant_logs:
            for violation in log["compliance_result"]["violations"]:
                violation_summary[violation] += 1
        
        report = {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "summary": {
                "total_actions": total_actions,
                "compliant_actions": compliant_actions,
                "compliance_rate": compliant_actions / total_actions if total_actions > 0 else 1.0,
                "total_violations": total_actions - compliant_actions
            },
            "violation_breakdown": dict(violation_summary),
            "recommendations": self._generate_compliance_recommendations(violation_summary)
        }
        
        return report
    
    def _generate_compliance_recommendations(self, violation_summary: Dict[str, int]) -> List[str]:
        """Generate recommendations based on compliance violations."""
        recommendations = []
        
        if violation_summary:
            most_common = max(violation_summary.items(), key=lambda x: x[1])
            recommendations.append(f"Address most common violation: {most_common[0]} ({most_common[1]} occurrences)")
        
        return recommendations


class GovernanceDashboard:
    """
    Provides dashboard interface for governance monitoring and management.
    """
    
    def __init__(self, workflow_engine: ApprovalWorkflowEngine, compliance_monitor: ComplianceMonitor):
        self.workflow_engine = workflow_engine
        self.compliance_monitor = compliance_monitor
    
    def get_dashboard_data(self, user_id: str, role: GovernanceRole) -> Dict[str, Any]:
        """Get dashboard data for specific user/role."""
        
        # Pending approvals
        pending_approvals = self.workflow_engine.get_pending_approvals(role)
        
        # Recent decisions
        recent_decisions = [
            req for req in self.workflow_engine.approval_history[-10:]
            if req.approver_id == user_id
        ]
        
        # Compliance summary
        compliance_summary = self._get_compliance_summary()
        
        # Performance metrics
        performance_metrics = self._get_performance_metrics()
        
        dashboard_data = {
            "user_info": {"user_id": user_id, "role": role.value},
            "pending_approvals": {
                "count": len(pending_approvals),
                "urgent_count": len([req for req in pending_approvals if req.priority == "urgent"]),
                "requests": [self._format_approval_request(req) for req in pending_approvals[:5]]
            },
            "recent_decisions": {
                "count": len(recent_decisions),
                "decisions": [self._format_decision(req) for req in recent_decisions]
            },
            "compliance": compliance_summary,
            "performance": performance_metrics,
            "alerts": self._get_governance_alerts()
        }
        
        return dashboard_data
    
    def _format_approval_request(self, request: ApprovalRequest) -> Dict[str, Any]:
        """Format approval request for dashboard display."""
        return {
            "request_id": request.request_id,
            "description": f"Action requiring {request.approver_role.value} approval",
            "priority": request.priority,
            "deadline": request.deadline.isoformat(),
            "age_hours": (datetime.now() - request.created_at).total_seconds() / 3600,
            "status": request.status.value
        }
    
    def _format_decision(self, request: ApprovalRequest) -> Dict[str, Any]:
        """Format decision for dashboard display."""
        return {
            "request_id": request.request_id,
            "decision": request.status.value,
            "timestamp": request.updated_at.isoformat(),
            "reason": request.approval_reason or request.rejection_reason
        }
    
    def _get_compliance_summary(self) -> Dict[str, Any]:
        """Get compliance summary for dashboard."""
        # Last 30 days compliance
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        report = self.compliance_monitor.generate_compliance_report(start_date, end_date)
        
        return {
            "compliance_rate": f"{report['summary']['compliance_rate']:.1%}",
            "total_violations": report['summary']['total_violations'],
            "trend": "improving"  # This would be calculated from historical data
        }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for dashboard."""
        # Calculate from approval history
        recent_approvals = self.workflow_engine.approval_history[-50:]
        
        if not recent_approvals:
            return {"avg_approval_time": "N/A", "approval_rate": "N/A"}
        
        approval_times = []
        approved_count = 0
        
        for req in recent_approvals:
            if req.status == ApprovalStatus.APPROVED:
                approved_count += 1
                approval_time = (req.updated_at - req.created_at).total_seconds() / 3600
                approval_times.append(approval_time)
        
        avg_approval_time = sum(approval_times) / len(approval_times) if approval_times else 0
        approval_rate = approved_count / len(recent_approvals)
        
        return {
            "avg_approval_time": f"{avg_approval_time:.1f} hours",
            "approval_rate": f"{approval_rate:.1%}",
            "total_requests": len(recent_approvals)
        }
    
    def _get_governance_alerts(self) -> List[Dict[str, Any]]:
        """Get governance alerts for dashboard."""
        alerts = []
        
        # Check for overdue approvals
        overdue_count = len([
            req for req in self.workflow_engine.pending_requests.values()
            if datetime.now() > req.deadline
        ])
        
        if overdue_count > 0:
            alerts.append({
                "type": "warning",
                "message": f"{overdue_count} approval request(s) overdue",
                "action": "Review pending approvals"
            })
        
        # Check compliance rate
        compliance_summary = self._get_compliance_summary()
        compliance_rate = float(compliance_summary["compliance_rate"].rstrip('%')) / 100
        
        if compliance_rate < 0.9:
            alerts.append({
                "type": "error",
                "message": f"Compliance rate below 90% ({compliance_summary['compliance_rate']})",
                "action": "Review compliance violations"
            })
        
        return alerts


# Example usage and testing
if __name__ == "__main__":
    # Initialize governance system
    role_manager = GovernanceRoleManager()
    workflow_engine = ApprovalWorkflowEngine(role_manager)
    compliance_monitor = ComplianceMonitor()
    dashboard = GovernanceDashboard(workflow_engine, compliance_monitor)
    
    # Set up roles
    role_manager.assign_role("john_lead", GovernanceRole.TEAM_LEAD, ["team_alpha"])
    role_manager.assign_role("jane_pm", GovernanceRole.PROJECT_MANAGER, ["team_alpha", "team_beta"])
    
    # Add compliance rules
    compliance_monitor.add_compliance_rule("approval_timeout", {
        "type": "approval_timeout",
        "max_hours": 24
    })
    
    # Example governance action
    action = GovernanceAction(
        action_id="action_123",
        action_type="reassign_ticket",
        category=ActionCategory.TICKET_MANAGEMENT,
        description="Reassign stale ticket JIRA-456 to available developer",
        proposed_by="juno_ai",
        team_id="team_alpha",
        impact_level="medium",
        confidence_score=0.85,
        reasoning="Ticket has been stale for 5 days, original assignee unavailable",
        data_sources=["jira_api", "team_capacity"],
        affected_tickets=["JIRA-456"],
        estimated_impact={"resolution_time_reduction": "2 days"},
        requires_approval=True,
        approval_threshold=0.8,
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(hours=24),
        metadata={"original_assignee": "dev1", "suggested_assignee": "dev2"}
    )
    
    # Submit for approval
    request_id = workflow_engine.submit_for_approval(action)
    
    # Check compliance
    pending_request = workflow_engine.pending_requests[request_id]
    compliance_result = compliance_monitor.check_compliance(action, pending_request)
    
    # Get dashboard data
    dashboard_data = dashboard.get_dashboard_data("john_lead", GovernanceRole.TEAM_LEAD)
    
    print("Governance Framework Implementation Complete!")
    print(f"Approval request created: {request_id}")
    print(f"Compliance check: {'PASS' if compliance_result['compliant'] else 'FAIL'}")
    print(f"Pending approvals: {dashboard_data['pending_approvals']['count']}")
    print(f"Compliance rate: {dashboard_data['compliance']['compliance_rate']}")

