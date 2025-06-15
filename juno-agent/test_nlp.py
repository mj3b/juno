#!/usr/bin/env python3
"""
Test script for Natural Language Processing functionality.
This script tests the NLP processor with various query types.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.query_processor import NaturalLanguageQueryProcessor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_nlp_functionality():
    """Test NLP functionality with various query types."""
    
    # Initialize the processor
    processor = NaturalLanguageQueryProcessor()
    
    # Test queries
    test_queries = [
        {
            'query': 'How many tickets are assigned to John Doe?',
            'expected_intent': 'assignee_count',
            'description': 'Assignee count query'
        },
        {
            'query': 'Show me the status distribution for project DEMO',
            'expected_intent': 'status_distribution',
            'description': 'Status distribution with project filter'
        },
        {
            'query': 'List all bugs in project DEMO from last month',
            'expected_intent': 'issue_list',
            'description': 'Issue list with type, project, and time filters'
        },
        {
            'query': 'Give me a project summary for DEMO',
            'expected_intent': 'project_summary',
            'description': 'Project summary query'
        },
        {
            'query': 'Show me defect analysis for this quarter',
            'expected_intent': 'defect_analysis',
            'description': 'Defect analysis with time filter'
        },
        {
            'query': 'How many open issues are there?',
            'expected_intent': 'status_distribution',
            'description': 'Status-based count query'
        },
        {
            'query': 'List high priority tickets assigned to me',
            'expected_intent': 'issue_list',
            'description': 'Issue list with priority and assignee filters'
        },
        {
            'query': 'What are the top 5 assignees by ticket count?',
            'expected_intent': 'assignee_count',
            'description': 'Top assignees ranking'
        },
        {
            'query': 'Show velocity report for last 3 sprints',
            'expected_intent': 'velocity_report',
            'description': 'Velocity analysis'
        },
        {
            'query': 'Generate burndown chart for current sprint',
            'expected_intent': 'burndown_chart',
            'description': 'Burndown chart request'
        }
    ]
    
    logger.info("Starting NLP functionality tests...")
    
    passed_tests = 0
    total_tests = len(test_queries)
    
    for i, test_case in enumerate(test_queries, 1):
        logger.info(f"\n--- Test {i}/{total_tests}: {test_case['description']} ---")
        logger.info(f"Query: '{test_case['query']}'")
        
        try:
            # Parse the query
            parsed_query = processor.nlu_processor.process_query(test_case['query'])
            
            logger.info(f"Detected Intent: {parsed_query.intent.value}")
            logger.info(f"Expected Intent: {test_case['expected_intent']}")
            logger.info(f"Confidence: {parsed_query.confidence:.2f}")
            
            # Check if intent matches
            intent_correct = parsed_query.intent.value == test_case['expected_intent']
            confidence_acceptable = parsed_query.confidence >= 0.3
            
            if intent_correct and confidence_acceptable:
                logger.info("✅ PASSED")
                passed_tests += 1
            else:
                logger.warning("❌ FAILED")
                if not intent_correct:
                    logger.warning(f"   Intent mismatch: got {parsed_query.intent.value}, expected {test_case['expected_intent']}")
                if not confidence_acceptable:
                    logger.warning(f"   Low confidence: {parsed_query.confidence:.2f} < 0.3")
            
            # Show extracted entities
            if parsed_query.entities:
                logger.info("Extracted Entities:")
                for entity in parsed_query.entities:
                    logger.info(f"  - {entity.entity_type}: '{entity.value}' (confidence: {entity.confidence:.2f})")
            
            # Show filters
            if parsed_query.filters:
                logger.info(f"Filters: {parsed_query.filters}")
            
            # Show time range
            if parsed_query.time_range:
                start, end = parsed_query.time_range
                logger.info(f"Time Range: {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
            
            # Generate JQL
            jql = processor.jql_generator.generate_jql(parsed_query)
            logger.info(f"Generated JQL: {jql}")
            
        except Exception as e:
            logger.error(f"❌ FAILED with exception: {e}")
    
    logger.info(f"\n=== Test Results ===")
    logger.info(f"Passed: {passed_tests}/{total_tests}")
    logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        logger.info("🎉 All tests passed!")
        return True
    else:
        logger.warning(f"⚠️  {total_tests - passed_tests} tests failed")
        return False

def test_entity_extraction():
    """Test entity extraction specifically."""
    logger.info("\n=== Testing Entity Extraction ===")
    
    processor = NaturalLanguageQueryProcessor()
    
    test_cases = [
        {
            'query': 'Show tickets for project DEMO assigned to John Smith',
            'expected_entities': ['project', 'user']
        },
        {
            'query': 'List high priority bugs from last week',
            'expected_entities': ['priority', 'issue_type', 'time_range']
        },
        {
            'query': 'How many open issues in project ABC?',
            'expected_entities': ['status', 'project']
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"\nQuery: '{test_case['query']}'")
        
        parsed_query = processor.nlu_processor.process_query(test_case['query'])
        
        extracted_types = [entity.entity_type for entity in parsed_query.entities]
        logger.info(f"Expected entities: {test_case['expected_entities']}")
        logger.info(f"Extracted entities: {extracted_types}")
        
        for entity in parsed_query.entities:
            logger.info(f"  - {entity.entity_type}: '{entity.value}'")

def test_time_range_extraction():
    """Test time range extraction specifically."""
    logger.info("\n=== Testing Time Range Extraction ===")
    
    processor = NaturalLanguageQueryProcessor()
    
    time_queries = [
        'Show tickets from last week',
        'List issues created this month',
        'Bugs reported in the last 30 days',
        'Issues from this quarter',
        'Show tickets from this year'
    ]
    
    for query in time_queries:
        logger.info(f"\nQuery: '{query}'")
        
        parsed_query = processor.nlu_processor.process_query(query)
        
        if parsed_query.time_range:
            start, end = parsed_query.time_range
            logger.info(f"Time Range: {start.strftime('%Y-%m-%d %H:%M')} to {end.strftime('%Y-%m-%d %H:%M')}")
        else:
            logger.info("No time range detected")

if __name__ == '__main__':
    logger.info("Testing NLP functionality...")
    
    # Run main functionality tests
    success = test_nlp_functionality()
    
    # Run specific entity extraction tests
    test_entity_extraction()
    
    # Run time range extraction tests
    test_time_range_extraction()
    
    logger.info("\nNLP testing completed!")
    sys.exit(0 if success else 1)

