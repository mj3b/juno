#!/usr/bin/env python3 mj3b
"""
Test script for Jira API integration.
This script tests the Jira API connector and data extraction functionality.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.jira_connector import JiraAPIConnector
from src.data_extractor import JiraDataExtractor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_jira_integration():
    """Test Jira API integration with sample data."""
    
    # These would normally come from environment variables
    # For testing, you can set them here or use environment variables
    base_url = os.getenv('JIRA_BASE_URL', 'https://your-domain.atlassian.net')
    email = os.getenv('JIRA_EMAIL', 'your-email@example.com')
    api_token = os.getenv('JIRA_API_TOKEN', 'your-api-token')
    
    if not all([base_url, email, api_token]) or 'your-' in base_url:
        logger.error("Please set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN environment variables")
        logger.info("Example:")
        logger.info("export JIRA_BASE_URL='https://your-domain.atlassian.net'")
        logger.info("export JIRA_EMAIL='your-email@example.com'")
        logger.info("export JIRA_API_TOKEN='your-api-token'")
        return False
    
    try:
        # Test connection
        logger.info("Testing Jira API connection...")
        connector = JiraAPIConnector(base_url, email, api_token)
        
        if not connector.test_connection():
            logger.error("Failed to connect to Jira")
            return False
        
        # Test data extraction
        logger.info("Testing data extraction...")
        extractor = JiraDataExtractor(connector)
        
        # Test getting projects
        logger.info("Extracting projects...")
        projects = extractor.extract_projects()
        logger.info(f"Found {len(projects)} projects")
        
        if projects:
            # Test getting issues from first project
            first_project = projects[0]
            logger.info(f"Extracting issues from project: {first_project.project_key}")
            
            jql = f"project = {first_project.project_key} ORDER BY created DESC"
            issues = extractor.extract_issues(jql)
            logger.info(f"Found {len(issues)} issues in project {first_project.project_key}")
            
            if issues:
                # Show sample issue
                sample_issue = issues[0]
                logger.info(f"Sample issue: {sample_issue.issue_key} - {sample_issue.summary}")
        
        # Test getting custom fields
        logger.info("Extracting custom fields...")
        custom_fields = extractor.extract_custom_fields()
        logger.info(f"Found {len(custom_fields)} custom fields")
        
        # Test getting users
        logger.info("Extracting current user...")
        users = extractor.extract_users()
        logger.info(f"Found {len(users)} users")
        
        logger.info("All tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

if __name__ == '__main__':
    success = test_jira_integration()
    sys.exit(0 if success else 1)

