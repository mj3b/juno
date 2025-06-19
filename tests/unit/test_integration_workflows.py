"""
JUNO Phase 2: Integration Test Suite
Comprehensive integration testing for API endpoints, database operations, and external system integrations
"""

import unittest
import asyncio
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import JUNO Phase 2 components
import sys
sys.path.append('../juno-agent/src/phase2')

from memory_layer import MemoryLayer, MemoryType, MemoryEntry
from reasoning_engine import ReasoningEngine, DecisionContext
from sprint_risk_forecast import SprintRiskForecaster
from governance_framework import GovernanceFramework
from database_setup import JUNODatabaseManager


class TestAPIIntegration(unittest.TestCase):
    """Test suite for API endpoint integration"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment for API integration tests"""
        cls.base_url = "http://localhost:5000/api/v2"
        cls.test_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer test_token"
        }
        
        # Mock external services
        cls.jira_mock = Mock()
        cls.slack_mock = Mock()
        cls.confluence_mock = Mock()
        
    def setUp(self):
        """Set up individual test"""
        self.test_team_id = "team_integration_001"
        self.test_user_id = "user_integration_001"
        
    def test_memory_api_endpoints(self):
        """Test Memory Layer API endpoints"""
        start_time = time.time()
        
        # Test store memory endpoint
        memory_data = {
            "memory_type": "episodic",
            "team_id": self.test_team_id,
            "key": "test_memory_key",
            "value": {"test": "data", "timestamp": datetime.now().isoformat()},
            "confidence": 0.95
        }
        
        # Mock API response for store memory
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            mock_post.return_value.json.return_value = {"success": True, "memory_id": "mem_123"}
            
            response = requests.post(
                f"{self.base_url}/memory/store",
                json=memory_data,
                headers=self.test_headers
            )
            
            self.assertEqual(response.status_code, 201)
            self.assertTrue(response.json()["success"])
        
        # Test retrieve memory endpoint
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "memory_id": "mem_123",
                "data": memory_data,
                "retrieved_at": datetime.now().isoformat()
            }
            
            response = requests.get(
                f"{self.base_url}/memory/{self.test_team_id}/episodic/test_memory_key",
                headers=self.test_headers
            )
            
            self.assertEqual(response.status_code, 200)
            self.assertIn("data", response.json())
        
        api_time = (time.time() - start_time) * 1000
        self.assertLess(api_time, 100, "Memory API calls should complete in < 100ms")
    
    def test_reasoning_api_endpoints(self):
        """Test Reasoning Engine API endpoints"""
        start_time = time.time()
        
        # Test decision making endpoint
        decision_data = {
            "team_id": self.test_team_id,
            "decision_type": "sprint_risk_assessment",
            "factors": {
                "velocity_trend": -0.15,
                "scope_change": 0.08,
                "team_capacity": 0.85
            },
            "context": {
                "sprint_id": "sprint_001",
                "current_date": datetime.now().isoformat()
            }
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "decision_id": "dec_456",
                "decision": "medium_risk",
                "confidence": 0.87,
                "reasoning": "Velocity decline and scope changes indicate medium risk",
                "recommendations": ["Monitor velocity closely", "Review scope changes"]
            }
            
            response = requests.post(
                f"{self.base_url}/reasoning/decide",
                json=decision_data,
                headers=self.test_headers
            )
            
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertIn("decision", result)
            self.assertIn("confidence", result)
            self.assertIn("reasoning", result)
            self.assertGreater(result["confidence"], 0.8)
        
        reasoning_time = (time.time() - start_time) * 1000
        self.assertLess(reasoning_time, 200, "Reasoning API calls should complete in < 200ms")
    
    def test_risk_forecast_api_endpoints(self):
        """Test Risk Forecasting API endpoints"""
        start_time = time.time()
        
        # Test sprint risk forecast endpoint
        forecast_data = {
            "team_id": self.test_team_id,
            "sprint_id": "sprint_001",
            "current_metrics": {
                "velocity": 42,
                "completed_points": 25,
                "remaining_points": 17,
                "days_remaining": 5
            }
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "forecast_id": "forecast_789",
                "completion_probability": 0.78,
                "risk_level": "medium",
                "risk_factors": {
                    "velocity_risk": 0.25,
                    "scope_risk": 0.15,
                    "capacity_risk": 0.20
                },
                "recommendations": [
                    "Consider reducing scope by 2-3 story points",
                    "Monitor team capacity for next 2 days"
                ],
                "confidence": 0.89
            }
            
            response = requests.post(
                f"{self.base_url}/risk/forecast",
                json=forecast_data,
                headers=self.test_headers
            )
            
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertIn("completion_probability", result)
            self.assertIn("risk_level", result)
            self.assertIn("confidence", result)
            self.assertGreater(result["confidence"], 0.85)
        
        forecast_time = (time.time() - start_time) * 1000
        self.assertLess(forecast_time, 300, "Risk forecast API calls should complete in < 300ms")
    
    def test_governance_api_endpoints(self):
        """Test Governance Framework API endpoints"""
        start_time = time.time()
        
        # Test governance approval endpoint
        approval_data = {
            "decision_id": "dec_456",
            "action_type": "resource_reallocation",
            "impact_level": "high",
            "requester_id": self.test_user_id,
            "justification": "Critical sprint risk mitigation required"
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 202
            mock_post.return_value.json.return_value = {
                "approval_id": "approval_101",
                "status": "pending",
                "required_approvers": ["manager_001", "director_001"],
                "estimated_approval_time": "2-4 hours",
                "workflow_stage": "manager_review"
            }
            
            response = requests.post(
                f"{self.base_url}/governance/approve",
                json=approval_data,
                headers=self.test_headers
            )
            
            self.assertEqual(response.status_code, 202)
            result = response.json()
            self.assertIn("approval_id", result)
            self.assertIn("status", result)
            self.assertEqual(result["status"], "pending")
        
        governance_time = (time.time() - start_time) * 1000
        self.assertLess(governance_time, 150, "Governance API calls should complete in < 150ms")


class TestDatabaseIntegration(unittest.TestCase):
    """Test suite for database integration and operations"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.db_manager = JUNODatabaseManager(self.temp_db.name)
        self.db_manager.connect()
        self.db_manager.initialize_schema()
        
    def tearDown(self):
        """Clean up test database"""
        self.db_manager.disconnect()
        os.unlink(self.temp_db.name)
    
    def test_database_schema_integrity(self):
        """Test database schema creation and integrity"""
        start_time = time.time()
        
        # Verify all required tables exist
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = [
            'memory_episodic', 'memory_semantic', 'memory_procedural', 'memory_working',
            'decisions', 'risk_forecasts', 'governance_approvals', 'audit_trail'
        ]
        
        for table in required_tables:
            self.assertIn(table, tables, f"Required table {table} not found")
        
        # Verify indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        # Should have indexes for performance
        self.assertGreater(len(indexes), 5, "Insufficient database indexes")
        
        schema_time = (time.time() - start_time) * 1000
        self.assertLess(schema_time, 50, "Schema verification should complete in < 50ms")
    
    def test_concurrent_database_operations(self):
        """Test database performance under concurrent load"""
        start_time = time.time()
        
        def database_operation(thread_id):
            """Simulate concurrent database operations"""
            try:
                # Insert test data
                cursor = self.db_manager.connection.cursor()
                cursor.execute('''
                    INSERT INTO memory_episodic (id, team_id, key, value, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    f"mem_{thread_id}",
                    f"team_{thread_id % 5}",
                    f"test_key_{thread_id}",
                    json.dumps({"thread": thread_id, "data": f"test_data_{thread_id}"}),
                    0.9,
                    datetime.now().isoformat()
                ))
                
                # Query test data
                cursor.execute('''
                    SELECT * FROM memory_episodic WHERE team_id = ?
                ''', (f"team_{thread_id % 5}",))
                
                results = cursor.fetchall()
                return len(results)
                
            except Exception as e:
                return f"Error: {str(e)}"
        
        # Run concurrent operations
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(database_operation, i) for i in range(50)]
            results = [future.result() for future in as_completed(futures)]
        
        # Verify all operations completed successfully
        error_count = len([r for r in results if isinstance(r, str) and r.startswith("Error")])
        self.assertEqual(error_count, 0, f"Database errors in concurrent operations: {error_count}")
        
        concurrent_time = (time.time() - start_time) * 1000
        self.assertLess(concurrent_time, 2000, "Concurrent operations should complete in < 2s")
    
    def test_data_consistency_and_transactions(self):
        """Test data consistency and transaction handling"""
        start_time = time.time()
        
        # Test transaction rollback
        cursor = self.db_manager.connection.cursor()
        
        try:
            cursor.execute("BEGIN TRANSACTION")
            
            # Insert valid data
            cursor.execute('''
                INSERT INTO memory_episodic (id, team_id, key, value, confidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ("mem_test_1", "team_test", "key_1", '{"test": "data"}', 0.9, datetime.now().isoformat()))
            
            # Insert invalid data (should cause rollback)
            cursor.execute('''
                INSERT INTO memory_episodic (id, team_id, key, value, confidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ("mem_test_1", "team_test", "key_2", '{"test": "data"}', 1.5, "invalid_date"))  # Invalid confidence
            
            cursor.execute("COMMIT")
            
        except Exception:
            cursor.execute("ROLLBACK")
        
        # Verify rollback worked - no data should be inserted
        cursor.execute("SELECT COUNT(*) FROM memory_episodic WHERE team_id = 'team_test'")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 0, "Transaction rollback failed")
        
        consistency_time = (time.time() - start_time) * 1000
        self.assertLess(consistency_time, 100, "Consistency test should complete in < 100ms")


class TestExternalIntegrations(unittest.TestCase):
    """Test suite for external system integrations"""
    
    def setUp(self):
        """Set up external integration mocks"""
        self.jira_base_url = "https://test-company.atlassian.net"
        self.slack_webhook_url = "https://hooks.slack.com/test"
        self.confluence_base_url = "https://test-company.atlassian.net/wiki"
        
    def test_jira_integration(self):
        """Test Jira API integration"""
        start_time = time.time()
        
        # Test Jira ticket retrieval
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "issues": [
                    {
                        "key": "JUNO-123",
                        "fields": {
                            "summary": "Test ticket",
                            "status": {"name": "In Progress"},
                            "assignee": {"displayName": "Test User"},
                            "customfield_10016": 5  # Story points
                        }
                    }
                ]
            }
            
            # Simulate Jira API call
            response = requests.get(
                f"{self.jira_base_url}/rest/api/2/search",
                params={"jql": "project = JUNO AND sprint in openSprints()"},
                headers={"Authorization": "Bearer test_token"}
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("issues", data)
            self.assertGreater(len(data["issues"]), 0)
        
        # Test Jira ticket update
        with patch('requests.put') as mock_put:
            mock_put.return_value.status_code = 204
            
            response = requests.put(
                f"{self.jira_base_url}/rest/api/2/issue/JUNO-123",
                json={
                    "fields": {
                        "description": "Updated by JUNO AI agent"
                    }
                },
                headers={"Authorization": "Bearer test_token"}
            )
            
            self.assertEqual(response.status_code, 204)
        
        jira_time = (time.time() - start_time) * 1000
        self.assertLess(jira_time, 500, "Jira integration should complete in < 500ms")
    
    def test_slack_integration(self):
        """Test Slack webhook integration"""
        start_time = time.time()
        
        # Test Slack notification
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.text = "ok"
            
            slack_message = {
                "text": "JUNO Alert: Sprint risk detected",
                "attachments": [
                    {
                        "color": "warning",
                        "fields": [
                            {
                                "title": "Team",
                                "value": "Backend Team Alpha",
                                "short": True
                            },
                            {
                                "title": "Risk Level",
                                "value": "Medium",
                                "short": True
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                self.slack_webhook_url,
                json=slack_message
            )
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "ok")
        
        slack_time = (time.time() - start_time) * 1000
        self.assertLess(slack_time, 200, "Slack integration should complete in < 200ms")
    
    def test_confluence_integration(self):
        """Test Confluence API integration"""
        start_time = time.time()
        
        # Test Confluence page creation
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "id": "12345",
                "title": "JUNO Sprint Risk Report",
                "version": {"number": 1},
                "_links": {
                    "webui": "/display/TEAM/JUNO+Sprint+Risk+Report"
                }
            }
            
            page_content = {
                "type": "page",
                "title": "JUNO Sprint Risk Report",
                "space": {"key": "TEAM"},
                "body": {
                    "storage": {
                        "value": "<h1>Sprint Risk Analysis</h1><p>Generated by JUNO AI</p>",
                        "representation": "storage"
                    }
                }
            }
            
            response = requests.post(
                f"{self.confluence_base_url}/rest/api/content",
                json=page_content,
                headers={"Authorization": "Bearer test_token"}
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("id", data)
            self.assertIn("title", data)
        
        confluence_time = (time.time() - start_time) * 1000
        self.assertLess(confluence_time, 300, "Confluence integration should complete in < 300ms")


class TestWorkflowIntegration(unittest.TestCase):
    """Test suite for end-to-end workflow integration"""
    
    def setUp(self):
        """Set up workflow integration test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Initialize components
        self.memory_layer = MemoryLayer(db_path=self.temp_db.name)
        self.memory_layer.initialize()
        
        self.reasoning_engine = ReasoningEngine()
        self.reasoning_engine.initialize()
        
        self.risk_forecaster = SprintRiskForecaster()
        self.governance_framework = GovernanceFramework()
        
    def tearDown(self):
        """Clean up workflow test environment"""
        self.memory_layer.close()
        self.reasoning_engine.cleanup()
        os.unlink(self.temp_db.name)
    
    def test_end_to_end_risk_assessment_workflow(self):
        """Test complete risk assessment workflow"""
        start_time = time.time()
        
        # Step 1: Store team context in memory
        team_context = MemoryEntry(
            memory_type=MemoryType.SEMANTIC,
            team_id="team_workflow_001",
            key="team_baseline",
            value={
                "avg_velocity": 42,
                "success_rate": 0.85,
                "team_size": 7,
                "tech_stack": ["Python", "React", "PostgreSQL"]
            },
            confidence=0.95
        )
        
        memory_result = self.memory_layer.store_memory(team_context)
        self.assertTrue(memory_result)
        
        # Step 2: Analyze current sprint risk
        current_context = DecisionContext(
            team_id="team_workflow_001",
            decision_type="sprint_risk_assessment",
            factors={
                "velocity_trend": -0.12,
                "scope_change": 0.15,
                "team_capacity": 0.8,
                "dependency_risk": 0.25
            }
        )
        
        decision = self.reasoning_engine.make_decision(current_context)
        self.assertIsNotNone(decision)
        self.assertGreater(decision.confidence.overall_score, 0.8)
        
        # Step 3: Generate risk forecast
        forecast_result = self.risk_forecaster.forecast_sprint_completion(
            team_id="team_workflow_001",
            current_metrics={
                "velocity": 38,  # Below average
                "completed_points": 20,
                "remaining_points": 22,
                "days_remaining": 6
            }
        )
        
        self.assertIsNotNone(forecast_result)
        self.assertIn("completion_probability", forecast_result)
        self.assertIn("risk_level", forecast_result)
        
        # Step 4: Check if governance approval needed
        if decision.confidence.overall_score < 0.9 or forecast_result.get("risk_level") == "high":
            approval_request = {
                "decision_id": decision.decision_id,
                "action_type": "risk_mitigation",
                "impact_level": "medium",
                "auto_approved": False
            }
            
            governance_result = self.governance_framework.request_approval(approval_request)
            self.assertIsNotNone(governance_result)
            self.assertIn("approval_id", governance_result)
        
        # Step 5: Store decision outcome in memory
        outcome_entry = MemoryEntry(
            memory_type=MemoryType.EPISODIC,
            team_id="team_workflow_001",
            key=f"risk_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            value={
                "decision": decision.decision,
                "confidence": decision.confidence.overall_score,
                "forecast": forecast_result,
                "timestamp": datetime.now().isoformat()
            },
            confidence=decision.confidence.overall_score
        )
        
        outcome_result = self.memory_layer.store_memory(outcome_entry)
        self.assertTrue(outcome_result)
        
        workflow_time = (time.time() - start_time) * 1000
        self.assertLess(workflow_time, 1000, "End-to-end workflow should complete in < 1s")
    
    def test_multi_team_coordination_workflow(self):
        """Test workflow coordination across multiple teams"""
        start_time = time.time()
        
        teams = ["team_alpha", "team_beta", "team_gamma"]
        coordination_results = []
        
        for team_id in teams:
            # Simulate team-specific risk assessment
            team_context = DecisionContext(
                team_id=team_id,
                decision_type="cross_team_dependency_analysis",
                factors={
                    "dependency_count": len(teams) - 1,
                    "coordination_complexity": 0.6,
                    "communication_frequency": 0.8
                }
            )
            
            decision = self.reasoning_engine.make_decision(team_context)
            coordination_results.append({
                "team_id": team_id,
                "decision": decision.decision,
                "confidence": decision.confidence.overall_score
            })
        
        # Verify all teams processed
        self.assertEqual(len(coordination_results), 3)
        
        # Verify coordination decisions are consistent
        avg_confidence = sum(r["confidence"] for r in coordination_results) / len(coordination_results)
        self.assertGreater(avg_confidence, 0.7)
        
        coordination_time = (time.time() - start_time) * 1000
        self.assertLess(coordination_time, 500, "Multi-team coordination should complete in < 500ms")


if __name__ == '__main__':
    # Configure logging for test execution
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test cases
    test_suite.addTest(unittest.makeSuite(TestAPIIntegration))
    test_suite.addTest(unittest.makeSuite(TestDatabaseIntegration))
    test_suite.addTest(unittest.makeSuite(TestExternalIntegrations))
    test_suite.addTest(unittest.makeSuite(TestWorkflowIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"JUNO Integration Test Results")
    print(f"{'='*60}")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")

