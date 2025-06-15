import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

class JiraAPIConnector:
    """
    Jira API Connector module for handling all interactions with Jira Cloud REST API.
    Provides secure authentication, rate limiting, and data extraction capabilities.
    """
    
    def __init__(self, base_url: str, email: str, api_token: str):
        """
        Initialize the Jira API Connector.
        
        Args:
            base_url: Jira instance base URL (e.g., 'https://your-domain.atlassian.net')
            email: User email for authentication
            api_token: API token for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.session = requests.Session()
        self.session.auth = (email, api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Rate limiting configuration
        self.rate_limit_delay = 0.1  # Minimum delay between requests (seconds)
        self.last_request_time = 0
        self.max_retries = 3
        self.retry_delay = 1  # Initial retry delay (seconds)
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a rate-limited HTTP request to the Jira API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., '/rest/api/3/search')
            params: Query parameters
            data: Request body data
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.exceptions.RequestException: For HTTP errors
        """
        # Rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_request)
        
        url = urljoin(self.base_url, endpoint)
        
        for attempt in range(self.max_retries):
            try:
                self.last_request_time = time.time()
                
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params)
                elif method.upper() == 'POST':
                    response = self.session.post(url, params=params, json=data)
                elif method.upper() == 'PUT':
                    response = self.session.put(url, params=params, json=data)
                elif method.upper() == 'DELETE':
                    response = self.session.delete(url, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Handle rate limiting (429 status code)
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', self.retry_delay))
                    logger.warning(f"Rate limited. Waiting {retry_after} seconds before retry.")
                    time.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                return response.json() if response.content else {}
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Request failed after {self.max_retries} attempts: {e}")
                    raise
                
                wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time} seconds: {e}")
                time.sleep(wait_time)
    
    def test_connection(self) -> bool:
        """
        Test the connection to Jira API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = self._make_request('GET', '/rest/api/3/myself')
            logger.info(f"Successfully connected to Jira as: {response.get('displayName')}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Jira: {e}")
            return False
    
    def search_issues(self, jql: str, fields: Optional[List[str]] = None, 
                     expand: Optional[List[str]] = None, max_results: int = 50, 
                     start_at: int = 0) -> Dict[str, Any]:
        """
        Search for issues using JQL.
        
        Args:
            jql: JQL query string
            fields: List of fields to include in response
            expand: List of fields to expand
            max_results: Maximum number of results per page
            start_at: Starting index for pagination
            
        Returns:
            Search results as dictionary
        """
        params = {
            'jql': jql,
            'maxResults': max_results,
            'startAt': start_at
        }
        
        if fields:
            params['fields'] = ','.join(fields)
        
        if expand:
            params['expand'] = ','.join(expand)
        
        return self._make_request('GET', '/rest/api/3/search', params=params)
    
    def get_all_issues(self, jql: str, fields: Optional[List[str]] = None, 
                      expand: Optional[List[str]] = None, batch_size: int = 100) -> List[Dict[str, Any]]:
        """
        Get all issues matching a JQL query using pagination.
        
        Args:
            jql: JQL query string
            fields: List of fields to include in response
            expand: List of fields to expand
            batch_size: Number of issues to fetch per request
            
        Returns:
            List of all matching issues
        """
        all_issues = []
        start_at = 0
        
        while True:
            response = self.search_issues(jql, fields, expand, batch_size, start_at)
            issues = response.get('issues', [])
            all_issues.extend(issues)
            
            # Check if we've retrieved all issues
            total = response.get('total', 0)
            if start_at + len(issues) >= total:
                break
            
            start_at += batch_size
            logger.info(f"Retrieved {len(all_issues)}/{total} issues")
        
        logger.info(f"Retrieved all {len(all_issues)} issues")
        return all_issues
    
    def get_issue(self, issue_key: str, fields: Optional[List[str]] = None, 
                 expand: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get a specific issue by key or ID.
        
        Args:
            issue_key: Issue key (e.g., 'PROJ-123') or ID
            fields: List of fields to include in response
            expand: List of fields to expand
            
        Returns:
            Issue data as dictionary
        """
        params = {}
        
        if fields:
            params['fields'] = ','.join(fields)
        
        if expand:
            params['expand'] = ','.join(expand)
        
        return self._make_request('GET', f'/rest/api/3/issue/{issue_key}', params=params)
    
    def get_user(self, account_id: str) -> Dict[str, Any]:
        """
        Get user information by account ID.
        
        Args:
            account_id: User account ID
            
        Returns:
            User data as dictionary
        """
        params = {'accountId': account_id}
        return self._make_request('GET', '/rest/api/3/user', params=params)
    
    def search_users(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search for users.
        
        Args:
            query: Search query (username, display name, or email)
            max_results: Maximum number of results
            
        Returns:
            List of matching users
        """
        params = {
            'query': query,
            'maxResults': max_results
        }
        response = self._make_request('GET', '/rest/api/3/user/search', params=params)
        return response if isinstance(response, list) else []
    
    def get_projects(self, expand: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get all projects accessible to the user.
        
        Args:
            expand: List of fields to expand
            
        Returns:
            List of projects
        """
        params = {}
        
        if expand:
            params['expand'] = ','.join(expand)
        
        response = self._make_request('GET', '/rest/api/3/project', params=params)
        return response if isinstance(response, list) else []
    
    def get_project(self, project_key: str, expand: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get a specific project by key or ID.
        
        Args:
            project_key: Project key (e.g., 'PROJ') or ID
            expand: List of fields to expand
            
        Returns:
            Project data as dictionary
        """
        params = {}
        
        if expand:
            params['expand'] = ','.join(expand)
        
        return self._make_request('GET', f'/rest/api/3/project/{project_key}', params=params)
    
    def get_fields(self) -> List[Dict[str, Any]]:
        """
        Get all fields (including custom fields) available in the Jira instance.
        
        Returns:
            List of field definitions
        """
        response = self._make_request('GET', '/rest/api/3/field')
        return response if isinstance(response, list) else []
    
    def get_issue_types(self) -> List[Dict[str, Any]]:
        """
        Get all issue types.
        
        Returns:
            List of issue types
        """
        response = self._make_request('GET', '/rest/api/3/issuetype')
        return response if isinstance(response, list) else []
    
    def get_statuses(self) -> List[Dict[str, Any]]:
        """
        Get all statuses.
        
        Returns:
            List of statuses
        """
        response = self._make_request('GET', '/rest/api/3/status')
        return response if isinstance(response, list) else []
    
    def get_priorities(self) -> List[Dict[str, Any]]:
        """
        Get all priorities.
        
        Returns:
            List of priorities
        """
        response = self._make_request('GET', '/rest/api/3/priority')
        return response if isinstance(response, list) else []
    
    def get_myself(self) -> Dict[str, Any]:
        """
        Get information about the currently authenticated user.
        
        Returns:
            Current user data as dictionary
        """
        return self._make_request('GET', '/rest/api/3/myself')

