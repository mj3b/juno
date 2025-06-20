import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from juno.infrastructure.jira_integration.connector import JiraAPIConnector
from juno.core.models.jira_models import JiraIssue, JiraUser, JiraProject, JiraCustomField, db

logger = logging.getLogger(__name__)

class JiraDataExtractor:
    """
    Data extraction service for retrieving and processing Jira data.
    Handles the transformation of raw Jira API responses into structured data models.
    """
    
    def __init__(self, jira_connector: JiraAPIConnector):
        """
        Initialize the data extractor with a Jira API connector.
        
        Args:
            jira_connector: Configured JiraAPIConnector instance
        """
        self.jira_connector = jira_connector
    
    def _parse_datetime(self, date_string: Optional[str]) -> Optional[datetime]:
        """
        Parse Jira datetime string to Python datetime object.
        
        Args:
            date_string: ISO format datetime string from Jira
            
        Returns:
            Parsed datetime object or None
        """
        if not date_string:
            return None
        
        try:
            # Jira uses ISO format with timezone info
            # Remove timezone info for SQLite compatibility
            if date_string.endswith('Z'):
                date_string = date_string[:-1]
            elif '+' in date_string:
                date_string = date_string.split('+')[0]
            elif date_string.count('-') > 2:  # Has timezone offset
                date_string = date_string.rsplit('-', 1)[0]
            
            return datetime.fromisoformat(date_string.replace('T', ' '))
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse datetime '{date_string}': {e}")
            return None
    
    def _extract_user_info(self, user_data: Optional[Dict]) -> tuple:
        """
        Extract user account ID and display name from user object.
        
        Args:
            user_data: User object from Jira API response
            
        Returns:
            Tuple of (account_id, display_name)
        """
        if not user_data:
            return None, None
        
        return user_data.get('accountId'), user_data.get('displayName')
    
    def extract_issues(self, jql: str, project_key: Optional[str] = None) -> List[JiraIssue]:
        """
        Extract issues from Jira based on JQL query and convert to JiraIssue models.
        
        Args:
            jql: JQL query string
            project_key: Optional project key for filtering
            
        Returns:
            List of JiraIssue model instances
        """
        logger.info(f"Extracting issues with JQL: {jql}")
        
        # Define fields to retrieve
        fields = [
            'summary', 'description', 'issuetype', 'status', 'priority',
            'assignee', 'reporter', 'project', 'created', 'updated',
            'resolved', 'resolution', 'labels', 'components', 'fixVersions',
            'customfield_*'  # Get all custom fields
        ]
        
        # Get all issues matching the JQL
        raw_issues = self.jira_connector.get_all_issues(jql, fields=fields)
        
        jira_issues = []
        for raw_issue in raw_issues:
            try:
                issue = self._convert_raw_issue_to_model(raw_issue)
                if project_key and issue.project_key != project_key:
                    continue
                jira_issues.append(issue)
            except Exception as e:
                logger.error(f"Failed to convert issue {raw_issue.get('key', 'unknown')}: {e}")
                continue
        
        logger.info(f"Successfully extracted {len(jira_issues)} issues")
        return jira_issues
    
    def _convert_raw_issue_to_model(self, raw_issue: Dict[str, Any]) -> JiraIssue:
        """
        Convert raw Jira issue data to JiraIssue model.
        
        Args:
            raw_issue: Raw issue data from Jira API
            
        Returns:
            JiraIssue model instance
        """
        fields = raw_issue.get('fields', {})
        
        # Extract assignee and reporter info
        assignee_id, assignee_name = self._extract_user_info(fields.get('assignee'))
        reporter_id, reporter_name = self._extract_user_info(fields.get('reporter'))
        
        # Extract project info
        project = fields.get('project', {})
        project_key = project.get('key')
        project_name = project.get('name')
        
        # Extract custom fields
        custom_fields = {}
        for field_key, field_value in fields.items():
            if field_key.startswith('customfield_') and field_value is not None:
                custom_fields[field_key] = field_value
        
        # Extract story points (commonly stored in customfield_10016 or similar)
        story_points = None
        for cf_key, cf_value in custom_fields.items():
            if isinstance(cf_value, (int, float)):
                # This is a heuristic - in practice, you'd need to map the specific custom field
                story_points = cf_value
                break
        
        return JiraIssue(
            issue_key=raw_issue.get('key'),
            issue_id=raw_issue.get('id'),
            summary=fields.get('summary', ''),
            description=fields.get('description', ''),
            issue_type=fields.get('issuetype', {}).get('name', ''),
            status=fields.get('status', {}).get('name', ''),
            priority=fields.get('priority', {}).get('name') if fields.get('priority') else None,
            assignee_account_id=assignee_id,
            assignee_display_name=assignee_name,
            reporter_account_id=reporter_id,
            reporter_display_name=reporter_name,
            project_key=project_key,
            project_name=project_name,
            created=self._parse_datetime(fields.get('created')),
            updated=self._parse_datetime(fields.get('updated')),
            resolved=self._parse_datetime(fields.get('resolved')),
            resolution=fields.get('resolution', {}).get('name') if fields.get('resolution') else None,
            story_points=story_points,
            labels=json.dumps(fields.get('labels', [])),
            components=json.dumps([comp.get('name') for comp in fields.get('components', [])]),
            fix_versions=json.dumps([ver.get('name') for ver in fields.get('fixVersions', [])]),
            custom_fields=json.dumps(custom_fields),
            last_synced=datetime.utcnow()
        )
    
    def extract_users(self, query: str = '') -> List[JiraUser]:
        """
        Extract users from Jira and convert to JiraUser models.
        
        Args:
            query: Search query for users (empty string gets recent users)
            
        Returns:
            List of JiraUser model instances
        """
        logger.info(f"Extracting users with query: '{query}'")
        
        if query:
            raw_users = self.jira_connector.search_users(query, max_results=1000)
        else:
            # Get current user as a starting point
            current_user = self.jira_connector.get_myself()
            raw_users = [current_user]
        
        jira_users = []
        for raw_user in raw_users:
            try:
                user = self._convert_raw_user_to_model(raw_user)
                jira_users.append(user)
            except Exception as e:
                logger.error(f"Failed to convert user {raw_user.get('accountId', 'unknown')}: {e}")
                continue
        
        logger.info(f"Successfully extracted {len(jira_users)} users")
        return jira_users
    
    def _convert_raw_user_to_model(self, raw_user: Dict[str, Any]) -> JiraUser:
        """
        Convert raw Jira user data to JiraUser model.
        
        Args:
            raw_user: Raw user data from Jira API
            
        Returns:
            JiraUser model instance
        """
        return JiraUser(
            account_id=raw_user.get('accountId'),
            display_name=raw_user.get('displayName', ''),
            email_address=raw_user.get('emailAddress'),
            active=raw_user.get('active', True),
            time_zone=raw_user.get('timeZone'),
            account_type=raw_user.get('accountType'),
            last_synced=datetime.utcnow()
        )
    
    def extract_projects(self) -> List[JiraProject]:
        """
        Extract all projects from Jira and convert to JiraProject models.
        
        Returns:
            List of JiraProject model instances
        """
        logger.info("Extracting projects")
        
        expand = ['description', 'lead', 'url']
        raw_projects = self.jira_connector.get_projects(expand=expand)
        
        jira_projects = []
        for raw_project in raw_projects:
            try:
                project = self._convert_raw_project_to_model(raw_project)
                jira_projects.append(project)
            except Exception as e:
                logger.error(f"Failed to convert project {raw_project.get('key', 'unknown')}: {e}")
                continue
        
        logger.info(f"Successfully extracted {len(jira_projects)} projects")
        return jira_projects
    
    def _convert_raw_project_to_model(self, raw_project: Dict[str, Any]) -> JiraProject:
        """
        Convert raw Jira project data to JiraProject model.
        
        Args:
            raw_project: Raw project data from Jira API
            
        Returns:
            JiraProject model instance
        """
        lead = raw_project.get('lead', {})
        lead_id, lead_name = self._extract_user_info(lead)
        
        return JiraProject(
            project_id=raw_project.get('id'),
            project_key=raw_project.get('key'),
            name=raw_project.get('name', ''),
            description=raw_project.get('description', ''),
            project_type=raw_project.get('projectTypeKey'),
            lead_account_id=lead_id,
            lead_display_name=lead_name,
            url=raw_project.get('self'),
            last_synced=datetime.utcnow()
        )
    
    def extract_custom_fields(self) -> List[JiraCustomField]:
        """
        Extract custom field metadata from Jira and convert to JiraCustomField models.
        
        Returns:
            List of JiraCustomField model instances
        """
        logger.info("Extracting custom fields")
        
        raw_fields = self.jira_connector.get_fields()
        
        jira_custom_fields = []
        for raw_field in raw_fields:
            try:
                if raw_field.get('custom', False):  # Only process custom fields
                    custom_field = self._convert_raw_field_to_model(raw_field)
                    jira_custom_fields.append(custom_field)
            except Exception as e:
                logger.error(f"Failed to convert custom field {raw_field.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Successfully extracted {len(jira_custom_fields)} custom fields")
        return jira_custom_fields
    
    def _convert_raw_field_to_model(self, raw_field: Dict[str, Any]) -> JiraCustomField:
        """
        Convert raw Jira field data to JiraCustomField model.
        
        Args:
            raw_field: Raw field data from Jira API
            
        Returns:
            JiraCustomField model instance
        """
        schema = raw_field.get('schema', {})
        
        return JiraCustomField(
            field_id=raw_field.get('id'),
            name=raw_field.get('name', ''),
            description=raw_field.get('description', ''),
            field_type=raw_field.get('type'),
            custom=raw_field.get('custom', False),
            orderable=raw_field.get('orderable', False),
            navigable=raw_field.get('navigable', False),
            searchable=raw_field.get('searchable', False),
            clause_names=json.dumps(raw_field.get('clauseNames', [])),
            schema_type=schema.get('type'),
            schema_system=schema.get('system'),
            last_synced=datetime.utcnow()
        )
    
    def sync_all_data(self, project_keys: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Synchronize all Jira data (projects, users, custom fields, and issues).
        
        Args:
            project_keys: Optional list of project keys to sync (if None, sync all)
            
        Returns:
            Dictionary with counts of synced items
        """
        logger.info("Starting full data synchronization")
        
        results = {
            'projects': 0,
            'custom_fields': 0,
            'users': 0,
            'issues': 0
        }
        
        try:
            # Sync projects
            projects = self.extract_projects()
            for project in projects:
                existing = JiraProject.query.filter_by(project_key=project.project_key).first()
                if existing:
                    # Update existing project
                    for attr in ['name', 'description', 'project_type', 'lead_account_id', 
                               'lead_display_name', 'url', 'last_synced']:
                        setattr(existing, attr, getattr(project, attr))
                else:
                    db.session.add(project)
                results['projects'] += 1
            
            db.session.commit()
            logger.info(f"Synced {results['projects']} projects")
            
            # Sync custom fields
            custom_fields = self.extract_custom_fields()
            for field in custom_fields:
                existing = JiraCustomField.query.filter_by(field_id=field.field_id).first()
                if existing:
                    # Update existing field
                    for attr in ['name', 'description', 'field_type', 'custom', 'orderable',
                               'navigable', 'searchable', 'clause_names', 'schema_type',
                               'schema_system', 'last_synced']:
                        setattr(existing, attr, getattr(field, attr))
                else:
                    db.session.add(field)
                results['custom_fields'] += 1
            
            db.session.commit()
            logger.info(f"Synced {results['custom_fields']} custom fields")
            
            # Sync issues for each project
            target_projects = project_keys if project_keys else [p.project_key for p in projects]
            
            for project_key in target_projects:
                jql = f"project = {project_key}"
                issues = self.extract_issues(jql, project_key)
                
                for issue in issues:
                    existing = JiraIssue.query.filter_by(issue_key=issue.issue_key).first()
                    if existing:
                        # Update existing issue
                        for attr in ['summary', 'description', 'issue_type', 'status', 'priority',
                                   'assignee_account_id', 'assignee_display_name', 'reporter_account_id',
                                   'reporter_display_name', 'updated', 'resolved', 'resolution',
                                   'story_points', 'labels', 'components', 'fix_versions',
                                   'custom_fields', 'last_synced']:
                            setattr(existing, attr, getattr(issue, attr))
                    else:
                        db.session.add(issue)
                    results['issues'] += 1
                
                # Extract users from issues
                unique_user_ids = set()
                for issue in issues:
                    if issue.assignee_account_id:
                        unique_user_ids.add(issue.assignee_account_id)
                    if issue.reporter_account_id:
                        unique_user_ids.add(issue.reporter_account_id)
                
                # Fetch user details
                for user_id in unique_user_ids:
                    try:
                        raw_user = self.jira_connector.get_user(user_id)
                        user = self._convert_raw_user_to_model(raw_user)
                        
                        existing = JiraUser.query.filter_by(account_id=user.account_id).first()
                        if existing:
                            # Update existing user
                            for attr in ['display_name', 'email_address', 'active', 'time_zone',
                                       'account_type', 'last_synced']:
                                setattr(existing, attr, getattr(user, attr))
                        else:
                            db.session.add(user)
                        results['users'] += 1
                    except Exception as e:
                        logger.warning(f"Failed to fetch user {user_id}: {e}")
                
                db.session.commit()
                logger.info(f"Synced {len(issues)} issues for project {project_key}")
            
            logger.info(f"Data synchronization completed: {results}")
            return results
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Data synchronization failed: {e}")
            raise

