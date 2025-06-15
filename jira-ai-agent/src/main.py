"""
JUNO - Jira AI Analytics Agent
Main Flask application entry point.

This module initializes the Flask application and configures all routes,
database connections, and middleware for the JUNO AI analytics system.
"""

import os
import sys

# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.jira_models import JiraIssue, JiraUser, JiraProject, JiraCustomField
from src.routes.user import user_bp
from src.routes.jira_routes import jira_bp
from src.routes.nlp_routes import nlp_bp
from src.routes.analytics_routes import analytics_bp
from src.routes.enhanced_nlp_routes import enhanced_nlp_bp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "a_very_secret_key_fallback_for_dev")

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(jira_bp, url_prefix='/api/jira')
app.register_blueprint(nlp_bp, url_prefix='/api/nlp')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(enhanced_nlp_bp, url_prefix='/api/enhanced-nlp')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/')
def api_info():
    return {
        'message': 'Jira AI Analytics Agent API',
        'version': '2.0.0',
        'features': [
            'Jira API Integration',
            'Natural Language Processing',
            'Advanced Analytics',
            'Data Visualization',
            'OpenAI GPT Enhancement'
        ],
        'endpoints': {
            'jira': '/api/jira/*',
            'nlp': '/api/nlp/*',
            'analytics': '/api/analytics/*',
            'enhanced_nlp': '/api/enhanced-nlp/*',
            'users': '/api/*'
        },
        'openai_integration': os.getenv('OPENAI_API_KEY') is not None
    }

@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'database': 'connected',
        'openai_integration': os.getenv('OPENAI_API_KEY') is not None
    }

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
