from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class JiraIssue(db.Model):
    """Model for storing Jira issue data"""
    __tablename__ = 'jira_issues'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_key = db.Column(db.String(50), unique=True, nullable=False)
    issue_id = db.Column(db.String(50), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    issue_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(50))
    assignee_account_id = db.Column(db.String(100))
    assignee_display_name = db.Column(db.String(100))
    reporter_account_id = db.Column(db.String(100))
    reporter_display_name = db.Column(db.String(100))
    project_key = db.Column(db.String(50), nullable=False)
    project_name = db.Column(db.String(200))
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime, nullable=False)
    resolved = db.Column(db.DateTime)
    resolution = db.Column(db.String(50))
    story_points = db.Column(db.Float)
    labels = db.Column(db.Text)  # JSON string of labels
    components = db.Column(db.Text)  # JSON string of components
    fix_versions = db.Column(db.Text)  # JSON string of fix versions
    custom_fields = db.Column(db.Text)  # JSON string of custom field values
    last_synced = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<JiraIssue {self.issue_key}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'issue_key': self.issue_key,
            'issue_id': self.issue_id,
            'summary': self.summary,
            'description': self.description,
            'issue_type': self.issue_type,
            'status': self.status,
            'priority': self.priority,
            'assignee_account_id': self.assignee_account_id,
            'assignee_display_name': self.assignee_display_name,
            'reporter_account_id': self.reporter_account_id,
            'reporter_display_name': self.reporter_display_name,
            'project_key': self.project_key,
            'project_name': self.project_name,
            'created': self.created.isoformat() if self.created else None,
            'updated': self.updated.isoformat() if self.updated else None,
            'resolved': self.resolved.isoformat() if self.resolved else None,
            'resolution': self.resolution,
            'story_points': self.story_points,
            'labels': self.labels,
            'components': self.components,
            'fix_versions': self.fix_versions,
            'custom_fields': self.custom_fields,
            'last_synced': self.last_synced.isoformat() if self.last_synced else None
        }

class JiraUser(db.Model):
    """Model for storing Jira user data"""
    __tablename__ = 'jira_users'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
    time_zone = db.Column(db.String(50))
    account_type = db.Column(db.String(50))
    last_synced = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<JiraUser {self.display_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'display_name': self.display_name,
            'email_address': self.email_address,
            'active': self.active,
            'time_zone': self.time_zone,
            'account_type': self.account_type,
            'last_synced': self.last_synced.isoformat() if self.last_synced else None
        }

class JiraProject(db.Model):
    """Model for storing Jira project data"""
    __tablename__ = 'jira_projects'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(50), unique=True, nullable=False)
    project_key = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    project_type = db.Column(db.String(50))
    lead_account_id = db.Column(db.String(100))
    lead_display_name = db.Column(db.String(100))
    url = db.Column(db.String(500))
    last_synced = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<JiraProject {self.project_key}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_key': self.project_key,
            'name': self.name,
            'description': self.description,
            'project_type': self.project_type,
            'lead_account_id': self.lead_account_id,
            'lead_display_name': self.lead_display_name,
            'url': self.url,
            'last_synced': self.last_synced.isoformat() if self.last_synced else None
        }

class JiraCustomField(db.Model):
    """Model for storing Jira custom field metadata"""
    __tablename__ = 'jira_custom_fields'
    
    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    field_type = db.Column(db.String(100))
    custom = db.Column(db.Boolean, default=True)
    orderable = db.Column(db.Boolean, default=False)
    navigable = db.Column(db.Boolean, default=False)
    searchable = db.Column(db.Boolean, default=False)
    clause_names = db.Column(db.Text)  # JSON string of clause names
    schema_type = db.Column(db.String(100))
    schema_system = db.Column(db.String(100))
    last_synced = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<JiraCustomField {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'field_id': self.field_id,
            'name': self.name,
            'description': self.description,
            'field_type': self.field_type,
            'custom': self.custom,
            'orderable': self.orderable,
            'navigable': self.navigable,
            'searchable': self.searchable,
            'clause_names': self.clause_names,
            'schema_type': self.schema_type,
            'schema_system': self.schema_system,
            'last_synced': self.last_synced.isoformat() if self.last_synced else None
        }

