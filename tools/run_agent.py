#!/usr/bin/env python3
"""
JUNO Agent Main Entry Point

Runs the JUNO agentic AI platform with the new modular architecture.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from flask import Flask, send_from_directory
from flask_cors import CORS
from juno.core.agent.analytics_engine import AnalyticsEngine
from juno.core.agent.query_processor import QueryProcessor
from juno.applications.dashboard_service.visualization import VisualizationEngine
from config import config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "a_very_secret_key_fallback_for_dev")
    
    # Enable CORS for all routes
    CORS(app)
    
    # Initialize JUNO components
    analytics = AnalyticsEngine()
    query_processor = QueryProcessor()
    visualization = VisualizationEngine()
    
    @app.route('/')
    def api_info():
        return {
            'message': 'JUNO Agentic AI Platform',
            'version': '3.0.0',
            'architecture': 'Agent Project Structure',
            'features': [
                'Agentic AI Workflow Management',
                'Multi-Phase Evolution (Phase 1-4)',
                'Memory Layer Intelligence',
                'Autonomous Reasoning Engine',
                'Enterprise Jira Integration',
                'OpenAI Enterprise GPT'
            ],
            'phases': {
                'phase1': 'Analytics Foundation',
                'phase2': 'Agentic Workflow Manager',
                'phase3': 'Multi-Agent Orchestration',
                'phase4': 'AI-Native Operations'
            }
        }
    
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'architecture': 'agent_project_structure',
            'components': {
                'core_agent': 'operational',
                'memory_layer': 'operational',
                'reasoning_engine': 'operational',
                'infrastructure': 'operational'
            }
        }
    
    return app

def main():
    """Main entry point for JUNO agent."""
    print("🚀 Starting JUNO Agentic AI Platform...")
    print("📁 Using new Agent Project Structure")
    
    app = create_app()
    
    print("✅ JUNO components initialized successfully!")
    print(f"🌐 Running on port {config.load_config()['app']['port']}")
    
    # Start the Flask application
    app.run(host='0.0.0.0', port=config.load_config()['app']['port'], debug=config.load_config()['app']['debug'])

if __name__ == "__main__":
    main()

