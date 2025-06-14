from flask import Blueprint, jsonify, request
from src.query_processor import NaturalLanguageQueryProcessor
import logging

logger = logging.getLogger(__name__)

nlp_bp = Blueprint('nlp', __name__)

# Initialize the NLP processor
nlp_processor = NaturalLanguageQueryProcessor()

@nlp_bp.route('/query', methods=['POST'])
def process_natural_language_query():
    """Process a natural language query and return results."""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Query text is required'
            }), 400
        
        query = data['query']
        context = data.get('context', {})
        
        # Process the query
        results = nlp_processor.process_natural_language_query(query, context)
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Natural language query processing failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@nlp_bp.route('/test-queries', methods=['GET'])
def get_test_queries():
    """Get a list of sample queries for testing."""
    test_queries = [
        {
            'query': 'How many tickets are assigned to John Doe?',
            'description': 'Count issues by assignee',
            'expected_intent': 'assignee_count'
        },
        {
            'query': 'Show me the status distribution for project DEMO',
            'description': 'Status breakdown for a specific project',
            'expected_intent': 'status_distribution'
        },
        {
            'query': 'List all bugs in project DEMO from last month',
            'description': 'Filter issues by type, project, and time range',
            'expected_intent': 'issue_list'
        },
        {
            'query': 'Give me a project summary for DEMO',
            'description': 'Comprehensive project overview',
            'expected_intent': 'project_summary'
        },
        {
            'query': 'Show me defect analysis for this quarter',
            'description': 'Bug/defect analysis with time filter',
            'expected_intent': 'defect_analysis'
        },
        {
            'query': 'How many open issues are there?',
            'description': 'Count issues by status',
            'expected_intent': 'status_distribution'
        },
        {
            'query': 'List high priority tickets assigned to me',
            'description': 'Filter by priority and assignee',
            'expected_intent': 'issue_list'
        },
        {
            'query': 'What are the top 5 assignees by ticket count?',
            'description': 'Top assignees ranking',
            'expected_intent': 'assignee_count'
        }
    ]
    
    return jsonify({
        'status': 'success',
        'test_queries': test_queries
    })

@nlp_bp.route('/parse', methods=['POST'])
def parse_query_only():
    """Parse a natural language query without executing it."""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Query text is required'
            }), 400
        
        query = data['query']
        context = data.get('context', {})
        
        # Parse the query without executing
        parsed_query = nlp_processor.nlu_processor.process_query(query, context)
        
        result = {
            'status': 'success',
            'parsed_query': {
                'intent': parsed_query.intent.value,
                'confidence': parsed_query.confidence,
                'entities': [
                    {
                        'type': entity.entity_type,
                        'value': entity.value,
                        'confidence': entity.confidence,
                        'start_pos': entity.start_pos,
                        'end_pos': entity.end_pos
                    }
                    for entity in parsed_query.entities
                ],
                'filters': parsed_query.filters,
                'time_range': {
                    'start': parsed_query.time_range[0].isoformat() if parsed_query.time_range else None,
                    'end': parsed_query.time_range[1].isoformat() if parsed_query.time_range else None
                } if parsed_query.time_range else None,
                'aggregation_type': parsed_query.aggregation_type,
                'output_format': parsed_query.output_format,
                'original_query': parsed_query.original_query
            }
        }
        
        # Generate JQL for reference
        jql = nlp_processor.jql_generator.generate_jql(parsed_query, context)
        result['jql'] = jql
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Query parsing failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@nlp_bp.route('/intents', methods=['GET'])
def get_supported_intents():
    """Get list of supported query intents."""
    intents = [
        {
            'intent': 'assignee_count',
            'description': 'Count issues by assignee',
            'examples': [
                'How many tickets are assigned to John?',
                'Show assignee distribution',
                'Who has the most tickets?'
            ]
        },
        {
            'intent': 'status_distribution',
            'description': 'Show issue distribution by status',
            'examples': [
                'Status breakdown',
                'How many open issues?',
                'Show status distribution'
            ]
        },
        {
            'intent': 'issue_list',
            'description': 'List issues with optional filters',
            'examples': [
                'Show all bugs',
                'List tickets for project DEMO',
                'Find high priority issues'
            ]
        },
        {
            'intent': 'project_summary',
            'description': 'Comprehensive project overview',
            'examples': [
                'Project summary for DEMO',
                'Project overview',
                'Show project dashboard'
            ]
        },
        {
            'intent': 'defect_analysis',
            'description': 'Analysis of bugs and defects',
            'examples': [
                'Defect analysis',
                'Bug report',
                'Show defect patterns'
            ]
        },
        {
            'intent': 'velocity_report',
            'description': 'Team velocity and sprint metrics',
            'examples': [
                'Sprint velocity',
                'Team speed report',
                'Story points per sprint'
            ]
        },
        {
            'intent': 'lead_time_analysis',
            'description': 'Lead time and cycle time analysis',
            'examples': [
                'Lead time report',
                'How long to complete tickets?',
                'Average resolution time'
            ]
        },
        {
            'intent': 'burndown_chart',
            'description': 'Sprint progress and burndown charts',
            'examples': [
                'Burndown chart',
                'Sprint progress',
                'Remaining work chart'
            ]
        }
    ]
    
    return jsonify({
        'status': 'success',
        'supported_intents': intents
    })

