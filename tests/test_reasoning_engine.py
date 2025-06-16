"""
JUNO Phase 2: Reasoning Engine Test Suite
Comprehensive testing for multi-factor decision making, confidence scoring, and audit trails
"""

import unittest
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

# Import JUNO Phase 2 components
import sys
sys.path.append('../juno-agent/src/phase2')

from reasoning_engine import ReasoningEngine, ReasoningLevel, DecisionContext, ConfidenceScore


class TestReasoningEngine(unittest.TestCase):
    """Comprehensive test suite for JUNO Reasoning Engine"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.reasoning_engine = ReasoningEngine()
        self.reasoning_engine.initialize()
        
        # Test data
        self.test_team_id = "team_reasoning_001"
        self.test_context = DecisionContext(
            team_id=self.test_team_id,
            decision_type="sprint_risk_assessment",
            factors={
                "velocity_trend": -0.15,
                "scope_change": 0.08,
                "team_capacity": 0.85,
                "dependency_risk": 0.3,
                "technical_debt": 0.25
            },
            historical_data={
                "previous_sprints": 12,
                "success_rate": 0.83,
                "avg_velocity": 42
            }
        )
        
    def tearDown(self):
        """Clean up after each test"""
        self.reasoning_engine.cleanup()
    
    def test_confidence_calculation(self):
        """Test confidence score calculation accuracy"""
        start_time = time.time()
        
        # Test high confidence scenario
        high_confidence_context = DecisionContext(
            team_id=self.test_team_id,
            decision_type="sprint_completion_prediction",
            factors={
                "velocity_consistency": 0.95,
                "scope_stability": 0.92,
                "team_availability": 0.98,
                "dependency_clarity": 0.89
            },
            historical_data={
                "previous_sprints": 24,
                "success_rate": 0.94,
                "pattern_strength": 0.91
            }
        )
        
        confidence = self.reasoning_engine.calculate_confidence(high_confidence_context)
        
        self.assertIsInstance(confidence, ConfidenceScore)
        self.assertGreaterEqual(confidence.overall_score, 0.85)
        self.assertLessEqual(confidence.overall_score, 1.0)
        self.assertGreater(confidence.data_quality, 0.8)
        self.assertGreater(confidence.pattern_strength, 0.8)
        
        # Test low confidence scenario
        low_confidence_context = DecisionContext(
            team_id=self.test_team_id,
            decision_type="new_team_prediction",
            factors={
                "velocity_consistency": 0.3,
                "scope_stability": 0.4,
                "team_availability": 0.6,
                "dependency_clarity": 0.2
            },
            historical_data={
                "previous_sprints": 2,
                "success_rate": 0.5,
                "pattern_strength": 0.1
            }
        )
        
        low_confidence = self.reasoning_engine.calculate_confidence(low_confidence_context)
        
        self.assertLessEqual(low_confidence.overall_score, 0.6)
        self.assertLess(low_confidence.data_quality, 0.7)
        
        calculation_time = (time.time() - start_time) * 1000
        self.assertLess(calculation_time, 80, "Confidence calculation should complete in < 80ms")
    
    def test_reasoning_explanation(self):
        """Test reasoning explanation generation and quality"""
        start_time = time.time()
        
        decision_result = self.reasoning_engine.make_decision(self.test_context)
        
        self.assertIsNotNone(decision_result)
        self.assertIsNotNone(decision_result.explanation)
        self.assertIsNotNone(decision_result.reasoning_chain)
        
        # Verify explanation quality
        explanation = decision_result.explanation
        self.assertGreater(len(explanation), 50, "Explanation should be detailed")
        self.assertIn("velocity", explanation.lower())
        self.assertIn("risk", explanation.lower())
        
        # Verify reasoning chain
        reasoning_chain = decision_result.reasoning_chain
        self.assertIsInstance(reasoning_chain, list)
        self.assertGreater(len(reasoning_chain), 2)
        
        for step in reasoning_chain:
            self.assertIn("factor", step)
            self.assertIn("weight", step)
            self.assertIn("impact", step)
            self.assertIsInstance(step["weight"], (int, float))
        
        explanation_time = (time.time() - start_time) * 1000
        self.assertLess(explanation_time, 150, "Explanation generation should complete in < 150ms")
    
    def test_audit_trail_generation(self):
        """Test comprehensive audit trail generation"""
        start_time = time.time()
        
        # Make multiple decisions to build audit trail
        decisions = []
        for i in range(5):
            context = DecisionContext(
                team_id=self.test_team_id,
                decision_type=f"test_decision_{i}",
                factors={
                    "factor_a": 0.5 + (i * 0.1),
                    "factor_b": 0.8 - (i * 0.05),
                    "factor_c": 0.6 + (i * 0.08)
                },
                timestamp=datetime.now() + timedelta(minutes=i)
            )
            
            decision = self.reasoning_engine.make_decision(context)
            decisions.append(decision)
        
        # Generate audit trail
        audit_trail = self.reasoning_engine.generate_audit_trail(
            self.test_team_id,
            start_date=datetime.now() - timedelta(hours=1),
            end_date=datetime.now() + timedelta(hours=1)
        )
        
        self.assertIsNotNone(audit_trail)
        self.assertGreaterEqual(len(audit_trail), 5)
        
        # Verify audit trail integrity
        for entry in audit_trail:
            self.assertIn("decision_id", entry)
            self.assertIn("timestamp", entry)
            self.assertIn("decision_type", entry)
            self.assertIn("confidence_score", entry)
            self.assertIn("factors_considered", entry)
            self.assertIn("reasoning_chain", entry)
            
            # Verify tamper-proof hash
            self.assertIn("integrity_hash", entry)
            self.assertIsInstance(entry["integrity_hash"], str)
            self.assertEqual(len(entry["integrity_hash"]), 64)  # SHA-256 hash
        
        audit_time = (time.time() - start_time) * 1000
        self.assertLess(audit_time, 120, "Audit trail generation should complete in < 120ms")
    
    def test_decision_transparency(self):
        """Test decision transparency and explainability"""
        start_time = time.time()
        
        # Complex decision scenario
        complex_context = DecisionContext(
            team_id=self.test_team_id,
            decision_type="sprint_risk_mitigation",
            factors={
                "velocity_decline": 0.22,
                "scope_creep": 0.15,
                "team_burnout_risk": 0.35,
                "technical_debt_impact": 0.18,
                "external_dependencies": 0.28,
                "quality_metrics": 0.75,
                "stakeholder_pressure": 0.45
            },
            constraints={
                "deadline_flexibility": 0.2,
                "resource_availability": 0.6,
                "quality_requirements": 0.9
            },
            historical_data={
                "similar_situations": 8,
                "success_rate": 0.625,
                "avg_recovery_time": 1.5
            }
        )
        
        decision = self.reasoning_engine.make_decision(complex_context)
        
        # Verify transparency components
        self.assertIsNotNone(decision.transparency_report)
        
        transparency = decision.transparency_report
        self.assertIn("factor_weights", transparency)
        self.assertIn("decision_logic", transparency)
        self.assertIn("alternative_options", transparency)
        self.assertIn("risk_assessment", transparency)
        self.assertIn("confidence_breakdown", transparency)
        
        # Verify factor weights sum to 1.0 (or close)
        factor_weights = transparency["factor_weights"]
        total_weight = sum(factor_weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=2)
        
        # Verify alternative options were considered
        alternatives = transparency["alternative_options"]
        self.assertIsInstance(alternatives, list)
        self.assertGreaterEqual(len(alternatives), 2)
        
        for alternative in alternatives:
            self.assertIn("option", alternative)
            self.assertIn("score", alternative)
            self.assertIn("pros", alternative)
            self.assertIn("cons", alternative)
        
        transparency_time = (time.time() - start_time) * 1000
        self.assertLess(transparency_time, 190, "Transparency analysis should complete in < 190ms")
    
    def test_multi_factor_analysis(self):
        """Test multi-factor analysis and weighting"""
        start_time = time.time()
        
        # Test with varying factor importance
        scenarios = [
            {
                "name": "velocity_critical",
                "factors": {
                    "velocity_trend": 0.9,
                    "team_capacity": 0.8,
                    "scope_stability": 0.6,
                    "quality_metrics": 0.7
                },
                "expected_primary_factor": "velocity_trend"
            },
            {
                "name": "quality_critical",
                "factors": {
                    "velocity_trend": 0.6,
                    "team_capacity": 0.7,
                    "scope_stability": 0.8,
                    "quality_metrics": 0.3
                },
                "expected_primary_factor": "quality_metrics"
            },
            {
                "name": "balanced_scenario",
                "factors": {
                    "velocity_trend": 0.75,
                    "team_capacity": 0.72,
                    "scope_stability": 0.78,
                    "quality_metrics": 0.74
                },
                "expected_balance": True
            }
        ]
        
        analysis_results = []
        
        for scenario in scenarios:
            context = DecisionContext(
                team_id=self.test_team_id,
                decision_type=f"multi_factor_{scenario['name']}",
                factors=scenario["factors"]
            )
            
            analysis = self.reasoning_engine.analyze_factors(context)
            analysis_results.append({
                "scenario": scenario["name"],
                "analysis": analysis,
                "context": context
            })
            
            # Verify analysis structure
            self.assertIn("factor_rankings", analysis)
            self.assertIn("correlation_matrix", analysis)
            self.assertIn("primary_drivers", analysis)
            self.assertIn("risk_factors", analysis)
            
            # Verify factor rankings
            rankings = analysis["factor_rankings"]
            self.assertEqual(len(rankings), len(scenario["factors"]))
            
            # Verify correlation matrix
            correlation_matrix = analysis["correlation_matrix"]
            self.assertIsInstance(correlation_matrix, dict)
        
        # Test cross-scenario consistency
        self.assertEqual(len(analysis_results), 3)
        
        multi_factor_time = (time.time() - start_time) * 1000
        self.assertLess(multi_factor_time, 260, "Multi-factor analysis should complete in < 260ms")
    
    def test_explanation_quality(self):
        """Test explanation quality and comprehensiveness"""
        start_time = time.time()
        
        # Generate decision with detailed explanation
        decision = self.reasoning_engine.make_decision(
            self.test_context,
            explanation_level=ReasoningLevel.DETAILED
        )
        
        explanation = decision.explanation
        reasoning_chain = decision.reasoning_chain
        
        # Test explanation completeness
        required_elements = [
            "decision rationale",
            "key factors",
            "confidence level",
            "risk assessment",
            "recommendations"
        ]
        
        explanation_lower = explanation.lower()
        for element in required_elements:
            self.assertTrue(
                any(keyword in explanation_lower for keyword in element.split()),
                f"Explanation should include {element}"
            )
        
        # Test reasoning chain quality
        self.assertGreaterEqual(len(reasoning_chain), 3)
        
        for i, step in enumerate(reasoning_chain):
            self.assertIn("step_number", step)
            self.assertEqual(step["step_number"], i + 1)
            self.assertIn("description", step)
            self.assertIn("factor_analysis", step)
            self.assertIn("intermediate_conclusion", step)
            
            # Verify step descriptions are meaningful
            self.assertGreater(len(step["description"]), 20)
        
        # Test explanation consistency
        final_decision = decision.decision
        final_confidence = decision.confidence.overall_score
        
        # Explanation should be consistent with decision
        if final_confidence > 0.8:
            self.assertIn("high confidence", explanation_lower)
        elif final_confidence < 0.5:
            self.assertIn("low confidence", explanation_lower)
        
        explanation_quality_time = (time.time() - start_time) * 1000
        self.assertLess(explanation_quality_time, 210, "Explanation quality test should complete in < 210ms")


class TestReasoningEngineIntegration(unittest.TestCase):
    """Integration tests for Reasoning Engine with other JUNO components"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.reasoning_engine = ReasoningEngine()
        self.reasoning_engine.initialize()
        
    def tearDown(self):
        """Clean up integration test environment"""
        self.reasoning_engine.cleanup()
    
    def test_memory_integration(self):
        """Test integration with Memory Layer for context enhancement"""
        # Simulate memory-enhanced decision making
        context_with_memory = DecisionContext(
            team_id="team_memory_integration",
            decision_type="sprint_planning_optimization",
            factors={
                "current_velocity": 0.85,
                "team_capacity": 0.9,
                "scope_complexity": 0.7
            },
            memory_context={
                "previous_similar_decisions": [
                    {"outcome": "success", "confidence": 0.89},
                    {"outcome": "partial_success", "confidence": 0.72},
                    {"outcome": "success", "confidence": 0.91}
                ],
                "team_preferences": {
                    "planning_style": "detailed",
                    "risk_tolerance": "medium"
                },
                "historical_patterns": {
                    "velocity_stability": 0.87,
                    "scope_change_frequency": 0.23
                }
            }
        )
        
        decision = self.reasoning_engine.make_decision(context_with_memory)
        
        # Verify memory integration enhances decision quality
        self.assertIsNotNone(decision)
        self.assertGreater(decision.confidence.overall_score, 0.7)
        self.assertIn("historical", decision.explanation.lower())
        
    def test_governance_integration(self):
        """Test integration with Governance Framework"""
        # Test decision requiring governance approval
        high_impact_context = DecisionContext(
            team_id="team_governance_test",
            decision_type="resource_reallocation",
            factors={
                "impact_scope": 0.95,
                "resource_cost": 0.85,
                "timeline_pressure": 0.8
            },
            governance_requirements={
                "approval_level": "senior_management",
                "stakeholder_notification": True,
                "risk_assessment_required": True
            }
        )
        
        decision = self.reasoning_engine.make_decision(high_impact_context)
        
        # Verify governance integration
        self.assertIsNotNone(decision.governance_metadata)
        self.assertIn("approval_required", decision.governance_metadata)
        self.assertTrue(decision.governance_metadata["approval_required"])
        self.assertIn("approval_level", decision.governance_metadata)


class TestReasoningEnginePerformance(unittest.TestCase):
    """Performance tests for Reasoning Engine"""
    
    def setUp(self):
        """Set up performance test environment"""
        self.reasoning_engine = ReasoningEngine()
        self.reasoning_engine.initialize()
        
    def tearDown(self):
        """Clean up performance test environment"""
        self.reasoning_engine.cleanup()
    
    def test_decision_latency(self):
        """Test decision-making latency under various loads"""
        latencies = []
        
        # Test 100 decisions for latency measurement
        for i in range(100):
            context = DecisionContext(
                team_id=f"team_perf_{i % 10}",
                decision_type="performance_test",
                factors={
                    "factor_1": 0.5 + (i % 10) * 0.05,
                    "factor_2": 0.8 - (i % 8) * 0.02,
                    "factor_3": 0.6 + (i % 12) * 0.03
                }
            )
            
            start_time = time.time()
            decision = self.reasoning_engine.make_decision(context)
            latency = (time.time() - start_time) * 1000  # Convert to ms
            
            latencies.append(latency)
            self.assertIsNotNone(decision)
        
        # Verify performance metrics
        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[94]  # 95th percentile
        p99_latency = sorted(latencies)[98]  # 99th percentile
        
        self.assertLess(avg_latency, 50, f"Average latency should be < 50ms, got {avg_latency:.2f}ms")
        self.assertLess(p95_latency, 100, f"95th percentile latency should be < 100ms, got {p95_latency:.2f}ms")
        self.assertLess(p99_latency, 150, f"99th percentile latency should be < 150ms, got {p99_latency:.2f}ms")


if __name__ == '__main__':
    # Configure logging for test execution
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test cases
    test_suite.addTest(unittest.makeSuite(TestReasoningEngine))
    test_suite.addTest(unittest.makeSuite(TestReasoningEngineIntegration))
    test_suite.addTest(unittest.makeSuite(TestReasoningEnginePerformance))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"JUNO Reasoning Engine Test Results")
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

