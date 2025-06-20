from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from src.nlp_processor import ParsedQuery, QueryIntent, JiraNLUProcessor
from juno.core.models.jira_models import JiraIssue, JiraUser, JiraProject, JiraCustomField, db
import logging

logger = logging.getLogger(__name__)

class JQLGenerator:
    """
    Generates JQL (Jira Query Language) queries from parsed natural language queries.
    """
    
    def __init__(self):
        """Initialize the JQL generator."""
        self.field_mappings = {
            'project_key': 'project',
            'assignee': 'assignee',
            'status': 'status',
            'issue_type': 'issuetype',
            'priority': 'priority',
            'reporter': 'reporter',
            'created': 'created',
            'updated': 'updated',
            'resolved': 'resolved'
        }
    
    def generate_jql(self, parsed_query: ParsedQuery, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate JQL query from parsed natural language query.
        
        Args:
            parsed_query: Parsed query object
            context: Optional context information
            
        Returns:
            JQL query string
        """
        jql_parts = []
        
        # Add filter conditions
        for filter_key, filter_value in parsed_query.filters.items():
            if filter_key in self.field_mappings:
                jql_field = self.field_mappings[filter_key]
                
                if filter_key == 'assignee':
                    # Handle assignee by display name or account ID
                    jql_parts.append(f'assignee = "{filter_value}"')
                elif filter_key == 'project_key':
                    jql_parts.append(f'project = {filter_value}')
                else:
                    jql_parts.append(f'{jql_field} = "{filter_value}"')
        
        # Add time range conditions
        if parsed_query.time_range:
            start_date, end_date = parsed_query.time_range
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            jql_parts.append(f'created >= "{start_str}" AND created <= "{end_str}"')
        
        # Combine JQL parts
        jql = ' AND '.join(jql_parts) if jql_parts else 'project is not EMPTY'
        
        # Add ordering
        jql += ' ORDER BY created DESC'
        
        logger.info(f"Generated JQL: {jql}")
        return jql

class QueryExecutor:
    """
    Executes parsed queries against the Jira data and returns results.
    """
    
    def __init__(self, jql_generator: JQLGenerator):
        """Initialize the query executor."""
        self.jql_generator = jql_generator
    
    def execute_query(self, parsed_query: ParsedQuery, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a parsed query and return results.
        
        Args:
            parsed_query: Parsed query object
            context: Optional context information
            
        Returns:
            Query results as dictionary
        """
        logger.info(f"Executing query with intent: {parsed_query.intent}")
        
        try:
            if parsed_query.intent == QueryIntent.ASSIGNEE_COUNT:
                return self._execute_assignee_count(parsed_query, context)
            elif parsed_query.intent == QueryIntent.STATUS_DISTRIBUTION:
                return self._execute_status_distribution(parsed_query, context)
            elif parsed_query.intent == QueryIntent.ISSUE_LIST:
                return self._execute_issue_list(parsed_query, context)
            elif parsed_query.intent == QueryIntent.PROJECT_SUMMARY:
                return self._execute_project_summary(parsed_query, context)
            elif parsed_query.intent == QueryIntent.DEFECT_ANALYSIS:
                return self._execute_defect_analysis(parsed_query, context)
            else:
                return self._execute_generic_query(parsed_query, context)
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'data': None
            }
    
    def _execute_assignee_count(self, parsed_query: ParsedQuery, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute assignee count query."""
        query = db.session.query(
            JiraIssue.assignee_display_name,
            db.func.count(JiraIssue.id).label('count')
        ).filter(JiraIssue.assignee_display_name.isnot(None))
        
        # Apply filters
        query = self._apply_filters(query, parsed_query.filters)
        
        # Apply time range
        if parsed_query.time_range:
            start_date, end_date = parsed_query.time_range
            query = query.filter(JiraIssue.created >= start_date, JiraIssue.created <= end_date)
        
        results = query.group_by(JiraIssue.assignee_display_name).order_by(db.desc('count')).all()
        
        data = [
            {
                'assignee': result.assignee_display_name,
                'count': result.count
            }
            for result in results
        ]
        
        return {
            'status': 'success',
            'intent': parsed_query.intent.value,
            'data': data,
            'total_assignees': len(data),
            'total_issues': sum(item['count'] for item in data)
        }
    
    def _execute_status_distribution(self, parsed_query: ParsedQuery, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute status distribution query."""
        query = db.session.query(
            JiraIssue.status,
            db.func.count(JiraIssue.id).label('count')
        )
        
        # Apply filters
        query = self._apply_filters(query, parsed_query.filters)
        
        # Apply time range
        if parsed_query.time_range:
            start_date, end_date = parsed_query.time_range
            query = query.filter(JiraIssue.created >= start_date, JiraIssue.created <= end_date)
        
        results = query.group_by(JiraIssue.status).order_by(db.desc('count')).all()
        
        data = [
            {
                'status': result.status,
                'count': result.count
            }
            for result in results
        ]
        
        return {
            'status': 'success',
            'intent': parsed_query.intent.value,
            'data': data,
            'total_statuses': len(data),
            'total_issues': sum(item['count'] for item in data)
        }
    
    def _execute_issue_list(self, parsed_query: ParsedQuery, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute issue list query."""
        query = JiraIssue.query
        
        # Apply filters
        query = self._apply_filters(query, parsed_query.filters)
        
        # Apply time range
        if parsed_query.time_range:
            start_date, end_date = parsed_query.time_range
            query = query.filter(JiraIssue.created >= start_date, JiraIssue.created <= end_date)
        
        # Apply ordering
        query = query.order_by(JiraIssue.created.desc())
        
        # Limit results
        limit = context.get('limit', 50) if context else 50
        issues = query.limit(limit).all()
        
        data = [issue.to_dict() for issue in issues]
        
        return {
            'status': 'success',
            'intent': parsed_query.intent.value,
            'data': data,
            'count': len(data),
            'limited': len(data) == limit
        }
    
    def _execute_project_summary(self, parsed_query: ParsedQuery, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute project summary query."""
        project_key = parsed_query.filters.get('project_key')
        
        if not project_key:
            return {
                'status': 'error',
                'message': 'Project key is required for project summary',
                'data': None
            }
        
        # Get project info
        project = JiraProject.query.filter_by(project_key=project_key).first()
        if not project:
            return {
                'status': 'error',
                'message': f'Project {project_key} not found',
                'data': None
            }
        
        # Get issue statistics
        base_query = JiraIssue.query.filter_by(project_key=project_key)
        
        total_issues = base_query.count()
        
        # Status distribution
        status_dist = db.session.query(
            JiraIssue.status,
            db.func.count(JiraIssue.id).label('count')
        ).filter_by(project_key=project_key).group_by(JiraIssue.status).all()
        
        # Issue type distribution
        type_dist = db.session.query(
            JiraIssue.issue_type,
            db.func.count(JiraIssue.id).label('count')
        ).filter_by(project_key=project_key).group_by(JiraIssue.issue_type).all()
        
        # Assignee distribution
        assignee_dist = db.session.query(
            JiraIssue.assignee_display_name,
            db.func.count(JiraIssue.id).label('count')
        ).filter(
            JiraIssue.project_key == project_key,
            JiraIssue.assignee_display_name.isnot(None)
        ).group_by(JiraIssue.assignee_display_name).order_by(db.desc('count')).limit(10).all()
        
        data = {
            'project': project.to_dict(),
            'total_issues': total_issues,
            'status_distribution': [{'status': r.status, 'count': r.count} for r in status_dist],
            'type_distribution': [{'type': r.issue_type, 'count': r.count} for r in type_dist],
            'top_assignees': [{'assignee': r.assignee_display_name, 'count': r.count} for r in assignee_dist]
        }
        
        return {
            'status': 'success',
            'intent': parsed_query.intent.value,
            'data': data
        }
    
    def _execute_defect_analysis(self, parsed_query: ParsedQuery, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute defect analysis query."""
        # Filter for bug/defect issue types
        bug_types = ['Bug', 'Defect', 'Error', 'Issue']
        
        query = JiraIssue.query.filter(JiraIssue.issue_type.in_(bug_types))
        
        # Apply additional filters
        query = self._apply_filters(query, parsed_query.filters)
        
        # Apply time range
        if parsed_query.time_range:
            start_date, end_date = parsed_query.time_range
            query = query.filter(JiraIssue.created >= start_date, JiraIssue.created <= end_date)
        
        total_defects = query.count()
        
        # Defect status distribution
        status_dist = db.session.query(
            JiraIssue.status,
            db.func.count(JiraIssue.id).label('count')
        ).filter(JiraIssue.issue_type.in_(bug_types))
        
        if parsed_query.filters.get('project_key'):
            status_dist = status_dist.filter_by(project_key=parsed_query.filters['project_key'])
        
        if parsed_query.time_range:
            start_date, end_date = parsed_query.time_range
            status_dist = status_dist.filter(JiraIssue.created >= start_date, JiraIssue.created <= end_date)
        
        status_results = status_dist.group_by(JiraIssue.status).all()
        
        # Defect priority distribution
        priority_dist = db.session.query(
            JiraIssue.priority,
            db.func.count(JiraIssue.id).label('count')
        ).filter(
            JiraIssue.issue_type.in_(bug_types),
            JiraIssue.priority.isnot(None)
        )
        
        if parsed_query.filters.get('project_key'):
            priority_dist = priority_dist.filter_by(project_key=parsed_query.filters['project_key'])
        
        if parsed_query.time_range:
            start_date, end_date = parsed_query.time_range
            priority_dist = priority_dist.filter(JiraIssue.created >= start_date, JiraIssue.created <= end_date)
        
        priority_results = priority_dist.group_by(JiraIssue.priority).all()
        
        data = {
            'total_defects': total_defects,
            'status_distribution': [{'status': r.status, 'count': r.count} for r in status_results],
            'priority_distribution': [{'priority': r.priority, 'count': r.count} for r in priority_results]
        }
        
        return {
            'status': 'success',
            'intent': parsed_query.intent.value,
            'data': data
        }
    
    def _execute_generic_query(self, parsed_query: ParsedQuery, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a generic query when specific intent handler is not available."""
        # Generate JQL and return it for manual execution
        jql = self.jql_generator.generate_jql(parsed_query, context)
        
        return {
            'status': 'success',
            'intent': parsed_query.intent.value,
            'jql': jql,
            'message': 'Generated JQL query for manual execution',
            'data': None
        }
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to a SQLAlchemy query."""
        for filter_key, filter_value in filters.items():
            if filter_key == 'project_key':
                query = query.filter(JiraIssue.project_key == filter_value)
            elif filter_key == 'assignee':
                query = query.filter(JiraIssue.assignee_display_name.ilike(f'%{filter_value}%'))
            elif filter_key == 'status':
                query = query.filter(JiraIssue.status == filter_value)
            elif filter_key == 'issue_type':
                query = query.filter(JiraIssue.issue_type == filter_value)
            elif filter_key == 'priority':
                query = query.filter(JiraIssue.priority == filter_value)
        
        return query

class NaturalLanguageQueryProcessor:
    """
    Main processor that combines NLU, JQL generation, and query execution.
    """
    
    def __init__(self):
        """Initialize the natural language query processor."""
        self.nlu_processor = JiraNLUProcessor()
        self.jql_generator = JQLGenerator()
        self.query_executor = QueryExecutor(self.jql_generator)
    
    def process_natural_language_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a natural language query end-to-end.
        
        Args:
            query: Natural language query string
            context: Optional context information
            
        Returns:
            Query results as dictionary
        """
        try:
            # Parse the natural language query
            parsed_query = self.nlu_processor.process_query(query, context)
            
            # Check confidence threshold
            if parsed_query.confidence < 0.3:
                return {
                    'status': 'error',
                    'message': 'Query confidence too low. Please rephrase your question.',
                    'confidence': parsed_query.confidence,
                    'data': None
                }
            
            # Execute the query
            results = self.query_executor.execute_query(parsed_query, context)
            
            # Add metadata
            results['query_info'] = {
                'original_query': query,
                'intent': parsed_query.intent.value,
                'confidence': parsed_query.confidence,
                'entities': [
                    {
                        'type': entity.entity_type,
                        'value': entity.value,
                        'confidence': entity.confidence
                    }
                    for entity in parsed_query.entities
                ],
                'filters': parsed_query.filters,
                'time_range': {
                    'start': parsed_query.time_range[0].isoformat() if parsed_query.time_range else None,
                    'end': parsed_query.time_range[1].isoformat() if parsed_query.time_range else None
                } if parsed_query.time_range else None
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Natural language query processing failed: {e}")
            return {
                'status': 'error',
                'message': f'Failed to process query: {str(e)}',
                'data': None
            }

