import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from juno.core.models.jira_models import JiraIssue, JiraUser, JiraProject, db
import logging

logger = logging.getLogger(__name__)

@dataclass
class SprintMetrics:
    """Sprint-level metrics for velocity analysis."""
    sprint_name: str
    start_date: datetime
    end_date: datetime
    planned_points: float
    completed_points: float
    total_issues: int
    completed_issues: int
    velocity: float
    completion_rate: float

@dataclass
class DefectMetrics:
    """Defect analysis metrics."""
    total_defects: int
    open_defects: int
    resolved_defects: int
    defect_rate: float
    avg_resolution_time: float
    defects_by_priority: Dict[str, int]
    defects_by_component: Dict[str, int]
    reopened_defects: int
    escape_rate: float

@dataclass
class LeadTimeMetrics:
    """Lead time and cycle time metrics."""
    avg_lead_time: float
    avg_cycle_time: float
    median_lead_time: float
    median_cycle_time: float
    percentile_95_lead_time: float
    percentile_95_cycle_time: float
    lead_time_by_type: Dict[str, float]
    cycle_time_by_type: Dict[str, float]

class AdvancedAnalyticsEngine:
    """
    Advanced analytics engine for Jira data analysis.
    Provides sophisticated metrics and insights for enterprise reporting.
    """
    
    def __init__(self):
        """Initialize the analytics engine."""
        self.logger = logging.getLogger(__name__)
    
    def calculate_velocity_metrics(self, project_key: str, 
                                 time_range: Optional[Tuple[datetime, datetime]] = None,
                                 sprint_duration_days: int = 14) -> List[SprintMetrics]:
        """
        Calculate velocity metrics for sprints.
        
        Args:
            project_key: Project key to analyze
            time_range: Optional time range for analysis
            sprint_duration_days: Duration of sprints in days
            
        Returns:
            List of SprintMetrics for each sprint period
        """
        logger.info(f"Calculating velocity metrics for project {project_key}")
        
        # Get issues for the project
        query = JiraIssue.query.filter_by(project_key=project_key)
        
        if time_range:
            start_date, end_date = time_range
            query = query.filter(JiraIssue.created >= start_date, JiraIssue.created <= end_date)
        
        issues = query.all()
        
        if not issues:
            logger.warning(f"No issues found for project {project_key}")
            return []
        
        # Group issues by sprint periods
        sprint_metrics = []
        
        # Determine sprint periods based on issue creation dates
        earliest_date = min(issue.created for issue in issues if issue.created)
        latest_date = max(issue.updated for issue in issues if issue.updated)
        
        current_date = earliest_date
        sprint_number = 1
        
        while current_date < latest_date:
            sprint_end = current_date + timedelta(days=sprint_duration_days)
            
            # Get issues for this sprint period
            sprint_issues = [
                issue for issue in issues
                if issue.created and current_date <= issue.created < sprint_end
            ]
            
            if sprint_issues:
                metrics = self._calculate_sprint_metrics(
                    f"Sprint {sprint_number}",
                    current_date,
                    sprint_end,
                    sprint_issues
                )
                sprint_metrics.append(metrics)
            
            current_date = sprint_end
            sprint_number += 1
        
        logger.info(f"Calculated metrics for {len(sprint_metrics)} sprints")
        return sprint_metrics
    
    def _calculate_sprint_metrics(self, sprint_name: str, start_date: datetime, 
                                end_date: datetime, issues: List[JiraIssue]) -> SprintMetrics:
        """Calculate metrics for a single sprint."""
        total_issues = len(issues)
        
        # Calculate story points (assuming they're stored in story_points field)
        planned_points = sum(issue.story_points or 0 for issue in issues)
        
        # Count completed issues (resolved within sprint period)
        completed_issues = [
            issue for issue in issues
            if issue.resolved and start_date <= issue.resolved < end_date
        ]
        
        completed_count = len(completed_issues)
        completed_points = sum(issue.story_points or 0 for issue in completed_issues)
        
        # Calculate metrics
        velocity = completed_points
        completion_rate = (completed_count / total_issues) * 100 if total_issues > 0 else 0
        
        return SprintMetrics(
            sprint_name=sprint_name,
            start_date=start_date,
            end_date=end_date,
            planned_points=planned_points,
            completed_points=completed_points,
            total_issues=total_issues,
            completed_issues=completed_count,
            velocity=velocity,
            completion_rate=completion_rate
        )
    
    def analyze_defect_patterns(self, project_key: Optional[str] = None,
                              time_range: Optional[Tuple[datetime, datetime]] = None) -> DefectMetrics:
        """
        Analyze defect patterns and quality metrics.
        
        Args:
            project_key: Optional project key to filter by
            time_range: Optional time range for analysis
            
        Returns:
            DefectMetrics with comprehensive defect analysis
        """
        logger.info(f"Analyzing defect patterns for project {project_key or 'all projects'}")
        
        # Define defect issue types
        defect_types = ['Bug', 'Defect', 'Error', 'Issue']
        
        # Build query for defects
        query = JiraIssue.query.filter(JiraIssue.issue_type.in_(defect_types))
        
        if project_key:
            query = query.filter_by(project_key=project_key)
        
        if time_range:
            start_date, end_date = time_range
            query = query.filter(JiraIssue.created >= start_date, JiraIssue.created <= end_date)
        
        defects = query.all()
        
        if not defects:
            logger.warning("No defects found for analysis")
            return DefectMetrics(
                total_defects=0, open_defects=0, resolved_defects=0,
                defect_rate=0, avg_resolution_time=0, defects_by_priority={},
                defects_by_component={}, reopened_defects=0, escape_rate=0
            )
        
        # Calculate basic metrics
        total_defects = len(defects)
        open_defects = len([d for d in defects if d.status in ['Open', 'New', 'To Do', 'In Progress']])
        resolved_defects = len([d for d in defects if d.status in ['Resolved', 'Closed', 'Done']])
        
        # Calculate resolution time for resolved defects
        resolution_times = []
        for defect in defects:
            if defect.resolved and defect.created:
                resolution_time = (defect.resolved - defect.created).total_seconds() / 3600  # hours
                resolution_times.append(resolution_time)
        
        avg_resolution_time = np.mean(resolution_times) if resolution_times else 0
        
        # Defects by priority
        defects_by_priority = {}
        for defect in defects:
            priority = defect.priority or 'Unknown'
            defects_by_priority[priority] = defects_by_priority.get(priority, 0) + 1
        
        # Defects by component (from components JSON field)
        defects_by_component = {}
        for defect in defects:
            if defect.components:
                try:
                    components = json.loads(defect.components)
                    for component in components:
                        defects_by_component[component] = defects_by_component.get(component, 0) + 1
                except json.JSONDecodeError:
                    continue
        
        # Calculate defect rate (defects per total issues)
        total_issues_query = JiraIssue.query
        if project_key:
            total_issues_query = total_issues_query.filter_by(project_key=project_key)
        if time_range:
            start_date, end_date = time_range
            total_issues_query = total_issues_query.filter(
                JiraIssue.created >= start_date, JiraIssue.created <= end_date
            )
        
        total_issues = total_issues_query.count()
        defect_rate = (total_defects / total_issues) * 100 if total_issues > 0 else 0
        
        # Estimate reopened defects (simplified - would need issue history for accuracy)
        reopened_defects = 0  # Would require transition history analysis
        
        # Calculate escape rate (simplified)
        escape_rate = 0  # Would require production vs pre-production defect classification
        
        return DefectMetrics(
            total_defects=total_defects,
            open_defects=open_defects,
            resolved_defects=resolved_defects,
            defect_rate=defect_rate,
            avg_resolution_time=avg_resolution_time,
            defects_by_priority=defects_by_priority,
            defects_by_component=defects_by_component,
            reopened_defects=reopened_defects,
            escape_rate=escape_rate
        )
    
    def calculate_lead_time_metrics(self, project_key: Optional[str] = None,
                                  time_range: Optional[Tuple[datetime, datetime]] = None) -> LeadTimeMetrics:
        """
        Calculate lead time and cycle time metrics.
        
        Args:
            project_key: Optional project key to filter by
            time_range: Optional time range for analysis
            
        Returns:
            LeadTimeMetrics with comprehensive timing analysis
        """
        logger.info(f"Calculating lead time metrics for project {project_key or 'all projects'}")
        
        # Build query
        query = JiraIssue.query.filter(JiraIssue.resolved.isnot(None))
        
        if project_key:
            query = query.filter_by(project_key=project_key)
        
        if time_range:
            start_date, end_date = time_range
            query = query.filter(JiraIssue.created >= start_date, JiraIssue.created <= end_date)
        
        issues = query.all()
        
        if not issues:
            logger.warning("No resolved issues found for lead time analysis")
            return LeadTimeMetrics(
                avg_lead_time=0, avg_cycle_time=0, median_lead_time=0,
                median_cycle_time=0, percentile_95_lead_time=0,
                percentile_95_cycle_time=0, lead_time_by_type={},
                cycle_time_by_type={}
            )
        
        # Calculate lead times (created to resolved)
        lead_times = []
        cycle_times = []  # For now, same as lead time (would need workflow transition data)
        lead_times_by_type = {}
        cycle_times_by_type = {}
        
        for issue in issues:
            if issue.created and issue.resolved:
                lead_time_hours = (issue.resolved - issue.created).total_seconds() / 3600
                lead_times.append(lead_time_hours)
                cycle_times.append(lead_time_hours)  # Simplified
                
                # Group by issue type
                issue_type = issue.issue_type
                if issue_type not in lead_times_by_type:
                    lead_times_by_type[issue_type] = []
                    cycle_times_by_type[issue_type] = []
                
                lead_times_by_type[issue_type].append(lead_time_hours)
                cycle_times_by_type[issue_type].append(lead_time_hours)
        
        # Calculate statistics
        avg_lead_time = np.mean(lead_times) if lead_times else 0
        avg_cycle_time = np.mean(cycle_times) if cycle_times else 0
        median_lead_time = np.median(lead_times) if lead_times else 0
        median_cycle_time = np.median(cycle_times) if cycle_times else 0
        percentile_95_lead_time = np.percentile(lead_times, 95) if lead_times else 0
        percentile_95_cycle_time = np.percentile(cycle_times, 95) if cycle_times else 0
        
        # Calculate averages by type
        avg_lead_time_by_type = {
            issue_type: np.mean(times)
            for issue_type, times in lead_times_by_type.items()
        }
        avg_cycle_time_by_type = {
            issue_type: np.mean(times)
            for issue_type, times in cycle_times_by_type.items()
        }
        
        return LeadTimeMetrics(
            avg_lead_time=avg_lead_time,
            avg_cycle_time=avg_cycle_time,
            median_lead_time=median_lead_time,
            median_cycle_time=median_cycle_time,
            percentile_95_lead_time=percentile_95_lead_time,
            percentile_95_cycle_time=percentile_95_cycle_time,
            lead_time_by_type=avg_lead_time_by_type,
            cycle_time_by_type=avg_cycle_time_by_type
        )
    
    def generate_trend_analysis(self, project_key: str, metric_type: str,
                              time_range: Tuple[datetime, datetime],
                              interval_days: int = 7) -> Dict[str, Any]:
        """
        Generate trend analysis for various metrics over time.
        
        Args:
            project_key: Project key to analyze
            metric_type: Type of metric ('velocity', 'defects', 'lead_time', 'throughput')
            time_range: Time range for analysis
            interval_days: Interval for trend buckets in days
            
        Returns:
            Dictionary with trend data and analysis
        """
        logger.info(f"Generating {metric_type} trend analysis for project {project_key}")
        
        start_date, end_date = time_range
        
        # Create time buckets
        buckets = []
        current_date = start_date
        
        while current_date < end_date:
            bucket_end = min(current_date + timedelta(days=interval_days), end_date)
            buckets.append((current_date, bucket_end))
            current_date = bucket_end
        
        trend_data = []
        
        for bucket_start, bucket_end in buckets:
            bucket_data = self._calculate_bucket_metrics(
                project_key, metric_type, bucket_start, bucket_end
            )
            bucket_data['period_start'] = bucket_start.isoformat()
            bucket_data['period_end'] = bucket_end.isoformat()
            trend_data.append(bucket_data)
        
        # Calculate trend statistics
        values = [data['value'] for data in trend_data if data['value'] is not None]
        
        if len(values) >= 2:
            # Simple linear trend calculation
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values, 1)
            trend_direction = 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
        else:
            slope = 0
            trend_direction = 'insufficient_data'
        
        return {
            'metric_type': metric_type,
            'project_key': project_key,
            'time_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'interval_days': interval_days,
            'trend_data': trend_data,
            'trend_analysis': {
                'direction': trend_direction,
                'slope': slope,
                'average': np.mean(values) if values else 0,
                'min': min(values) if values else 0,
                'max': max(values) if values else 0,
                'std_dev': np.std(values) if values else 0
            }
        }
    
    def _calculate_bucket_metrics(self, project_key: str, metric_type: str,
                                start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate metrics for a specific time bucket."""
        query = JiraIssue.query.filter_by(project_key=project_key)
        query = query.filter(JiraIssue.created >= start_date, JiraIssue.created < end_date)
        
        issues = query.all()
        
        if metric_type == 'velocity':
            # Calculate story points completed in this period
            completed_issues = [
                issue for issue in issues
                if issue.resolved and start_date <= issue.resolved < end_date
            ]
            value = sum(issue.story_points or 0 for issue in completed_issues)
            
        elif metric_type == 'defects':
            # Count defects created in this period
            defect_types = ['Bug', 'Defect', 'Error', 'Issue']
            defects = [issue for issue in issues if issue.issue_type in defect_types]
            value = len(defects)
            
        elif metric_type == 'lead_time':
            # Average lead time for issues resolved in this period
            resolved_issues = [
                issue for issue in issues
                if issue.resolved and start_date <= issue.resolved < end_date and issue.created
            ]
            if resolved_issues:
                lead_times = [
                    (issue.resolved - issue.created).total_seconds() / 3600
                    for issue in resolved_issues
                ]
                value = np.mean(lead_times)
            else:
                value = None
                
        elif metric_type == 'throughput':
            # Number of issues completed in this period
            completed_issues = [
                issue for issue in issues
                if issue.resolved and start_date <= issue.resolved < end_date
            ]
            value = len(completed_issues)
            
        else:
            value = None
        
        return {
            'value': value,
            'issue_count': len(issues)
        }
    
    def generate_comprehensive_report(self, project_key: str,
                                    time_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive analytics report for a project.
        
        Args:
            project_key: Project key to analyze
            time_range: Optional time range for analysis
            
        Returns:
            Comprehensive report with all analytics
        """
        logger.info(f"Generating comprehensive report for project {project_key}")
        
        report = {
            'project_key': project_key,
            'generated_at': datetime.utcnow().isoformat(),
            'time_range': {
                'start': time_range[0].isoformat() if time_range else None,
                'end': time_range[1].isoformat() if time_range else None
            } if time_range else None
        }
        
        try:
            # Velocity metrics
            velocity_metrics = self.calculate_velocity_metrics(project_key, time_range)
            report['velocity_analysis'] = [
                {
                    'sprint_name': m.sprint_name,
                    'start_date': m.start_date.isoformat(),
                    'end_date': m.end_date.isoformat(),
                    'planned_points': m.planned_points,
                    'completed_points': m.completed_points,
                    'velocity': m.velocity,
                    'completion_rate': m.completion_rate,
                    'total_issues': m.total_issues,
                    'completed_issues': m.completed_issues
                }
                for m in velocity_metrics
            ]
            
            # Defect analysis
            defect_metrics = self.analyze_defect_patterns(project_key, time_range)
            report['defect_analysis'] = {
                'total_defects': defect_metrics.total_defects,
                'open_defects': defect_metrics.open_defects,
                'resolved_defects': defect_metrics.resolved_defects,
                'defect_rate': defect_metrics.defect_rate,
                'avg_resolution_time_hours': defect_metrics.avg_resolution_time,
                'defects_by_priority': defect_metrics.defects_by_priority,
                'defects_by_component': defect_metrics.defects_by_component
            }
            
            # Lead time analysis
            lead_time_metrics = self.calculate_lead_time_metrics(project_key, time_range)
            report['lead_time_analysis'] = {
                'avg_lead_time_hours': lead_time_metrics.avg_lead_time,
                'median_lead_time_hours': lead_time_metrics.median_lead_time,
                'percentile_95_lead_time_hours': lead_time_metrics.percentile_95_lead_time,
                'lead_time_by_type_hours': lead_time_metrics.lead_time_by_type
            }
            
            # Summary statistics
            total_issues_query = JiraIssue.query.filter_by(project_key=project_key)
            if time_range:
                start_date, end_date = time_range
                total_issues_query = total_issues_query.filter(
                    JiraIssue.created >= start_date, JiraIssue.created <= end_date
                )
            
            total_issues = total_issues_query.count()
            
            report['summary'] = {
                'total_issues': total_issues,
                'avg_velocity': np.mean([m.velocity for m in velocity_metrics]) if velocity_metrics else 0,
                'avg_completion_rate': np.mean([m.completion_rate for m in velocity_metrics]) if velocity_metrics else 0,
                'defect_rate': defect_metrics.defect_rate,
                'avg_lead_time_days': lead_time_metrics.avg_lead_time / 24 if lead_time_metrics.avg_lead_time else 0
            }
            
            logger.info(f"Successfully generated comprehensive report for project {project_key}")
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            report['error'] = str(e)
        
        return report

