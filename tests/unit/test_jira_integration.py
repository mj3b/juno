import os
import sys
from types import SimpleNamespace
import pytest

base = os.path.join(os.path.dirname(__file__), '../../juno-agent')
sys.path.insert(0, os.path.join(base, 'src'))
sys.path.insert(0, base)

jira_module = pytest.importorskip('jira_connector')
extractor_module = pytest.importorskip('data_extractor')
JiraAPIConnector = jira_module.JiraAPIConnector
JiraDataExtractor = extractor_module.JiraDataExtractor


def test_jira_integration(monkeypatch):
    connector = JiraAPIConnector('https://example.atlassian.net', 'user', 'token')
    monkeypatch.setattr(connector, 'test_connection', lambda: True)

    extractor = JiraDataExtractor(connector)
    monkeypatch.setattr(extractor, 'extract_projects', lambda: [SimpleNamespace(project_key='DEMO')])
    monkeypatch.setattr(extractor, 'extract_issues', lambda jql: [SimpleNamespace(issue_key='DEMO-1')])
    monkeypatch.setattr(extractor, 'extract_custom_fields', lambda: [])
    monkeypatch.setattr(extractor, 'extract_users', lambda: [])

    assert connector.test_connection()
    projects = extractor.extract_projects()
    assert len(projects) == 1
    assert projects[0].project_key == 'DEMO'

    issues = extractor.extract_issues('project = DEMO')
    assert len(issues) == 1
    assert issues[0].issue_key == 'DEMO-1'

    assert extractor.extract_custom_fields() == []
    assert extractor.extract_users() == []
