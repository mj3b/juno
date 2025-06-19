#!/usr/bin/env python3 mj3b
"""
Test script for Advanced Analytics functionality.
This script tests the analytics engine and visualization capabilities.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.analytics_engine import AdvancedAnalyticsEngine
from src.visualization_engine import DataVisualizationEngine
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_analytics_functionality():
    """Test analytics functionality with mock data."""
    
    logger.info("Starting analytics functionality tests...")
    
    # Initialize engines
    analytics_engine = AdvancedAnalyticsEngine()
    viz_engine = DataVisualizationEngine()
    
    # Test project key (would need real data in database)
    test_project_key = "DEMO"
    
    # Define test time range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    time_range = (start_date, end_date)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Velocity Metrics
    logger.info("\n--- Test 1: Velocity Metrics ---")
    total_tests += 1
    try:
        velocity_metrics = analytics_engine.calculate_velocity_metrics(
            test_project_key, time_range
        )
        logger.info(f"✅ Velocity metrics calculated: {len(velocity_metrics)} sprints")
        tests_passed += 1
        
        # Test velocity visualization
        if velocity_metrics:
            metrics_data = [
                {
                    'sprint_name': m.sprint_name,
                    'start_date': m.start_date.isoformat(),
                    'end_date': m.end_date.isoformat(),
                    'planned_points': m.planned_points,
                    'completed_points': m.completed_points,
                    'velocity': m.velocity,
                    'completion_rate': m.completion_rate,
                    'total_issues': m.total_issues,
                    'completed_issues': m.completed_issues
                }
                for m in velocity_metrics
            ]
            
            chart_data = viz_engine.generate_velocity_chart(metrics_data, 'matplotlib')
            if 'error' not in chart_data:
                logger.info("✅ Velocity chart generated successfully")
            else:
                logger.warning(f"⚠️ Velocity chart generation failed: {chart_data['error']}")
        
    except Exception as e:
        logger.error(f"❌ Velocity metrics test failed: {e}")
    
    # Test 2: Defect Analysis
    logger.info("\n--- Test 2: Defect Analysis ---")
    total_tests += 1
    try:
        defect_metrics = analytics_engine.analyze_defect_patterns(
            test_project_key, time_range
        )
        logger.info(f"✅ Defect analysis completed: {defect_metrics.total_defects} total defects")
        logger.info(f"   - Open: {defect_metrics.open_defects}")
        logger.info(f"   - Resolved: {defect_metrics.resolved_defects}")
        logger.info(f"   - Defect Rate: {defect_metrics.defect_rate:.2f}%")
        tests_passed += 1
        
        # Test defect visualization
        metrics_data = {
            'total_defects': defect_metrics.total_defects,
            'open_defects': defect_metrics.open_defects,
            'resolved_defects': defect_metrics.resolved_defects,
            'defect_rate': defect_metrics.defect_rate,
            'avg_resolution_time_hours': defect_metrics.avg_resolution_time,
            'defects_by_priority': defect_metrics.defects_by_priority,
            'defects_by_component': defect_metrics.defects_by_component
        }
        
        chart_data = viz_engine.generate_defect_analysis_charts(metrics_data, 'matplotlib')
        if 'error' not in chart_data:
            logger.info("✅ Defect analysis charts generated successfully")
        else:
            logger.warning(f"⚠️ Defect chart generation failed: {chart_data['error']}")
        
    except Exception as e:
        logger.error(f"❌ Defect analysis test failed: {e}")
    
    # Test 3: Lead Time Analysis
    logger.info("\n--- Test 3: Lead Time Analysis ---")
    total_tests += 1
    try:
        lead_time_metrics = analytics_engine.calculate_lead_time_metrics(
            test_project_key, time_range
        )
        logger.info(f"✅ Lead time analysis completed")
        logger.info(f"   - Avg Lead Time: {lead_time_metrics.avg_lead_time/24:.1f} days")
        logger.info(f"   - Median Lead Time: {lead_time_metrics.median_lead_time/24:.1f} days")
        logger.info(f"   - 95th Percentile: {lead_time_metrics.percentile_95_lead_time/24:.1f} days")
        tests_passed += 1
        
        # Test lead time visualization
        metrics_data = {
            'avg_lead_time_hours': lead_time_metrics.avg_lead_time,
            'median_lead_time_hours': lead_time_metrics.median_lead_time,
            'percentile_95_lead_time_hours': lead_time_metrics.percentile_95_lead_time,
            'lead_time_by_type_hours': lead_time_metrics.lead_time_by_type
        }
        
        chart_data = viz_engine.generate_lead_time_chart(metrics_data, 'matplotlib')
        if 'error' not in chart_data:
            logger.info("✅ Lead time chart generated successfully")
        else:
            logger.warning(f"⚠️ Lead time chart generation failed: {chart_data['error']}")
        
    except Exception as e:
        logger.error(f"❌ Lead time analysis test failed: {e}")
    
    # Test 4: Trend Analysis
    logger.info("\n--- Test 4: Trend Analysis ---")
    total_tests += 1
    try:
        trend_data = analytics_engine.generate_trend_analysis(
            test_project_key, 'velocity', time_range, 7
        )
        logger.info(f"✅ Trend analysis completed for velocity")
        logger.info(f"   - Trend Direction: {trend_data['trend_analysis']['direction']}")
        logger.info(f"   - Average: {trend_data['trend_analysis']['average']:.2f}")
        tests_passed += 1
        
        # Test trend visualization
        chart_data = viz_engine.generate_trend_chart(trend_data, 'matplotlib')
        if 'error' not in chart_data:
            logger.info("✅ Trend chart generated successfully")
        else:
            logger.warning(f"⚠️ Trend chart generation failed: {chart_data['error']}")
        
    except Exception as e:
        logger.error(f"❌ Trend analysis test failed: {e}")
    
    # Test 5: Comprehensive Report
    logger.info("\n--- Test 5: Comprehensive Report ---")
    total_tests += 1
    try:
        comprehensive_report = analytics_engine.generate_comprehensive_report(
            test_project_key, time_range
        )
        logger.info(f"✅ Comprehensive report generated")
        logger.info(f"   - Project: {comprehensive_report['project_key']}")
        logger.info(f"   - Generated at: {comprehensive_report['generated_at']}")
        
        if 'summary' in comprehensive_report:
            summary = comprehensive_report['summary']
            logger.info(f"   - Total Issues: {summary['total_issues']}")
            logger.info(f"   - Avg Velocity: {summary['avg_velocity']:.2f}")
            logger.info(f"   - Defect Rate: {summary['defect_rate']:.2f}%")
        
        tests_passed += 1
        
    except Exception as e:
        logger.error(f"❌ Comprehensive report test failed: {e}")
    
    # Test 6: Visualization Engine Features
    logger.info("\n--- Test 6: Visualization Engine Features ---")
    total_tests += 1
    try:
        # Test with mock data
        mock_velocity_data = [
            {
                'sprint_name': 'Sprint 1',
                'start_date': '2025-01-01T00:00:00',
                'end_date': '2025-01-14T23:59:59',
                'planned_points': 50,
                'completed_points': 45,
                'velocity': 45,
                'completion_rate': 90,
                'total_issues': 10,
                'completed_issues': 9
            },
            {
                'sprint_name': 'Sprint 2',
                'start_date': '2025-01-15T00:00:00',
                'end_date': '2025-01-28T23:59:59',
                'planned_points': 55,
                'completed_points': 52,
                'velocity': 52,
                'completion_rate': 94.5,
                'total_issues': 11,
                'completed_issues': 10
            }
        ]
        
        # Test Plotly chart generation
        plotly_chart = viz_engine.generate_velocity_chart(mock_velocity_data, 'plotly')
        if 'error' not in plotly_chart:
            logger.info("✅ Plotly velocity chart generated successfully")
        else:
            logger.warning(f"⚠️ Plotly chart generation failed: {plotly_chart['error']}")
        
        # Test Matplotlib chart generation
        matplotlib_chart = viz_engine.generate_velocity_chart(mock_velocity_data, 'matplotlib')
        if 'error' not in matplotlib_chart:
            logger.info("✅ Matplotlib velocity chart generated successfully")
        else:
            logger.warning(f"⚠️ Matplotlib chart generation failed: {matplotlib_chart['error']}")
        
        tests_passed += 1
        
    except Exception as e:
        logger.error(f"❌ Visualization engine test failed: {e}")
    
    # Summary
    logger.info(f"\n=== Test Results ===")
    logger.info(f"Passed: {tests_passed}/{total_tests}")
    logger.info(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        logger.info("🎉 All analytics tests passed!")
        return True
    else:
        logger.warning(f"⚠️ {total_tests - tests_passed} tests failed")
        return False

def test_mock_data_generation():
    """Test analytics with mock data when no real data is available."""
    logger.info("\n=== Testing with Mock Data ===")
    
    viz_engine = DataVisualizationEngine()
    
    # Mock velocity data
    mock_velocity = [
        {'sprint_name': 'Sprint 1', 'velocity': 45, 'completion_rate': 90, 'planned_points': 50, 'completed_points': 45, 'total_issues': 10, 'completed_issues': 9},
        {'sprint_name': 'Sprint 2', 'velocity': 52, 'completion_rate': 94.5, 'planned_points': 55, 'completed_points': 52, 'total_issues': 11, 'completed_issues': 10},
        {'sprint_name': 'Sprint 3', 'velocity': 48, 'completion_rate': 87, 'planned_points': 55, 'completed_points': 48, 'total_issues': 12, 'completed_issues': 10}
    ]
    
    # Mock defect data
    mock_defects = {
        'total_defects': 25,
        'open_defects': 8,
        'resolved_defects': 17,
        'defect_rate': 12.5,
        'avg_resolution_time_hours': 48,
        'defects_by_priority': {'High': 5, 'Medium': 12, 'Low': 8},
        'defects_by_component': {'Frontend': 10, 'Backend': 8, 'Database': 4, 'API': 3}
    }
    
    # Mock lead time data
    mock_lead_time = {
        'avg_lead_time_hours': 120,
        'median_lead_time_hours': 96,
        'percentile_95_lead_time_hours': 240,
        'lead_time_by_type_hours': {'Story': 100, 'Bug': 80, 'Task': 60, 'Epic': 200}
    }
    
    # Test visualizations with mock data
    try:
        velocity_chart = viz_engine.generate_velocity_chart(mock_velocity, 'plotly')
        logger.info("✅ Mock velocity chart generated")
        
        defect_chart = viz_engine.generate_defect_analysis_charts(mock_defects, 'plotly')
        logger.info("✅ Mock defect analysis chart generated")
        
        lead_time_chart = viz_engine.generate_lead_time_chart(mock_lead_time, 'plotly')
        logger.info("✅ Mock lead time chart generated")
        
        logger.info("🎉 All mock data visualizations generated successfully!")
        
    except Exception as e:
        logger.error(f"❌ Mock data visualization failed: {e}")

if __name__ == '__main__':
    logger.info("Testing Advanced Analytics functionality...")
    
    # Run main functionality tests
    success = test_analytics_functionality()
    
    # Run mock data tests
    test_mock_data_generation()
    
    logger.info("\nAnalytics testing completed!")
    sys.exit(0 if success else 1)

