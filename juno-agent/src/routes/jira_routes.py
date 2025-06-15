from flask import Blueprint, jsonify, request
from src.jira_connector import JiraAPIConnector
from src.data_extractor import JiraDataExtractor
from src.models.jira_models import JiraIssue, JiraUser, JiraProject, JiraCustomField, db
import logging
import os

logger = logging.getLogger(__name__)

jira_bp = Blueprint('jira', __name__)

def get_jira_connector():
    """Get configured Jira API connector from environment variables."""
    base_url = os.getenv('JIRA_BASE_URL')
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')
    
    if not all([base_url, email, api_token]):
        raise ValueError("Missing required Jira configuration. Please set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN environment variables.")
    
    return JiraAPIConnector(base_url, email, api_token)

@jira_bp.route('/test-connection', methods=['GET'])
def test_jira_connection():
    """Test connection to Jira API."""
    try:
        connector = get_jira_connector()
        success = connector.test_connection()
        
        if success:
            user_info = connector.get_myself()
            return jsonify({
                'status': 'success',
                'message': 'Successfully connected to Jira',
                'user': {
                    'displayName': user_info.get('displayName'),
                    'emailAddress': user_info.get('emailAddress'),
                    'accountId': user_info.get('accountId')
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to connect to Jira'
            }), 500
            
    except Exception as e:
        logger.error(f"Jira connection test failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@jira_bp.route('/sync-data', methods=['POST'])
def sync_jira_data():
    """Synchronize Jira data to local database."""
    try:
        data = request.get_json() or {}
        project_keys = data.get('project_keys')  # Optional list of project keys
        
        connector = get_jira_connector()
        extractor = JiraDataExtractor(connector)
        
        results = extractor.sync_all_data(project_keys)
        
        return jsonify({
            'status': 'success',
            'message': 'Data synchronization completed',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Data synchronization failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@jira_bp.route('/projects', methods=['GET'])
def get_projects():
    """Get all projects from local database."""
    try:
        projects = JiraProject.query.all()
        return jsonify({
            'status': 'success',
            'projects': [project.to_dict() for project in projects]
        })
    except Exception as e:
        logger.error(f"Failed to get projects: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@jira_bp.route('/projects/<project_key>', methods=['GET'])
def get_project(project_key):
    """Get a specific project by key."""
    try:
        project = JiraProject.query.filter_by(project_key=project_key).first()
        if not project:
            return jsonify({
                'status': 'error',
                'message': f'Project {project_key} not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'project': project.to_dict()
        })
    except Exception as e:
        logger.error(f"Failed to get project {project_key}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@jira_bp.route('/issues', methods=['GET'])
def get_issues():
    """Get issues with optional filtering."""
    try:
        # Get query parameters
        project_key = request.args.get('project_key')
        assignee = request.args.get('assignee')
        status = request.args.get('status')
        issue_type = request.args.get('issue_type')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = JiraIssue.query
        
        if project_key:
            query = query.filter(JiraIssue.project_key == project_key)
        if assignee:
            query = query.filter(JiraIssue.assignee_display_name.ilike(f'%{assignee}%'))
        if status:
            query = query.filter(JiraIssue.status == status)
        if issue_type:
            query = query.filter(JiraIssue.issue_type == issue_type)
        
        # Apply pagination
        total = query.count()
        issues = query.offset(offset).limit(limit).all()
        
        return jsonify({
            'status': 'success',
            'issues': [issue.to_dict() for issue in issues],
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get issues: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@jira_bp.route('/issues/<issue_key>', methods=['GET'])
def get_issue(issue_key):
    """Get a specific issue by key."""
    try:
        issue = JiraIssue.query.filter_by(issue_key=issue_key).first()
        if not issue:
            return jsonify({
                'status': 'error',
                'message': f'Issue {issue_key} not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'issue': issue.to_dict()
        })
    except Exception as e:
        logger.error(f"Failed to get issue {issue_key}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@jira_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users from local database."""
    try:
        users = JiraUser.query.all()
        return jsonify({
            'status': 'success',
            'users': [user.to_dict() for user in users]
        })
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@jira_bp.route('/custom-fields', methods=['GET'])
def get_custom_fields():
    """Get all custom fields from local database."""
    try:
        fields = JiraCustomField.query.all()
        return jsonify({
            'status': 'success',
            'custom_fields': [field.to_dict() for field in fields]
        })
    except Exception as e:
        logger.error(f"Failed to get custom fields: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@jira_bp.route('/search', methods=['POST'])
def search_issues():
    """Search issues using JQL query."""
    try:
        data = request.get_json()
        if not data or 'jql' not in data:
            return jsonify({
                'status': 'error',
                'message': 'JQL query is required'
            }), 400
        
        jql = data['jql']
        limit = data.get('limit', 50)
        
        connector = get_jira_connector()
        extractor = JiraDataExtractor(connector)
        
        # Extract issues using JQL
        issues = extractor.extract_issues(jql)
        
        # Limit results
        if len(issues) > limit:
            issues = issues[:limit]
        
        return jsonify({
            'status': 'success',
            'issues': [issue.to_dict() for issue in issues],
            'total': len(issues)
        })
        
    except Exception as e:
        logger.error(f"JQL search failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@jira_bp.route('/stats/assignee-counts', methods=['GET'])
def get_assignee_counts():
    """Get issue counts by assignee."""
    try:
        project_key = request.args.get('project_key')
        
        query = db.session.query(
            JiraIssue.assignee_display_name,
            db.func.count(JiraIssue.id).label('count')
        ).filter(JiraIssue.assignee_display_name.isnot(None))
        
        if project_key:
            query = query.filter(JiraIssue.project_key == project_key)
        
        results = query.group_by(JiraIssue.assignee_display_name).all()
        
        assignee_counts = [
            {
                'assignee': result.assignee_display_name,
                'count': result.count
            }
            for result in results
        ]
        
        return jsonify({
            'status': 'success',
            'assignee_counts': assignee_counts
        })
        
    except Exception as e:
        logger.error(f"Failed to get assignee counts: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@jira_bp.route('/stats/status-distribution', methods=['GET'])
def get_status_distribution():
    """Get issue distribution by status."""
    try:
        project_key = request.args.get('project_key')
        
        query = db.session.query(
            JiraIssue.status,
            db.func.count(JiraIssue.id).label('count')
        )
        
        if project_key:
            query = query.filter(JiraIssue.project_key == project_key)
        
        results = query.group_by(JiraIssue.status).all()
        
        status_distribution = [
            {
                'status': result.status,
                'count': result.count
            }
            for result in results
        ]
        
        return jsonify({
            'status': 'success',
            'status_distribution': status_distribution
        })
        
    except Exception as e:
        logger.error(f"Failed to get status distribution: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

