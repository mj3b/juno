from flask import Blueprint, jsonify, request
from ..enhanced_nlp_processor import EnhancedNLPProcessor
from ..openai_integration import OpenAIIntegration
import logging

# Create blueprint for enhanced NLP routes
enhanced_nlp_bp = Blueprint('enhanced_nlp', __name__)

# Initialize enhanced NLP processor
enhanced_nlp_processor = EnhancedNLPProcessor()
openai_integration = OpenAIIntegration()

logger = logging.getLogger(__name__)

@enhanced_nlp_bp.route('/enhanced-query', methods=['POST'])
def process_enhanced_query():
    """
    Process natural language query with OpenAI enhancement.
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        context = data.get('context', {})
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Query is required'
            }), 400
        
        # Process query with enhanced NLP
        result = enhanced_nlp_processor.process_query(query, context)
        
        return jsonify({
            'status': 'success',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error in enhanced query processing: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Enhanced query processing failed: {str(e)}'
        }), 500

@enhanced_nlp_bp.route('/explain-results', methods=['POST'])
def explain_results():
    """
    Generate natural language explanation of analytics results.
    """
    try:
        data = request.get_json()
        results = data.get('results', {})
        original_query = data.get('original_query', '')
        
        if not results:
            return jsonify({
                'status': 'error',
                'message': 'Results are required'
            }), 400
        
        explanation = enhanced_nlp_processor.explain_results(results, original_query)
        
        return jsonify({
            'status': 'success',
            'explanation': explanation
        })
        
    except Exception as e:
        logger.error(f"Error in results explanation: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Results explanation failed: {str(e)}'
        }), 500

@enhanced_nlp_bp.route('/suggestions', methods=['POST'])
def get_intelligent_suggestions():
    """
    Get intelligent query suggestions based on context.
    """
    try:
        data = request.get_json()
        current_query = data.get('current_query', '')
        jira_context = data.get('jira_context', {})
        
        if not openai_integration.is_available():
            return jsonify({
                'status': 'error',
                'message': 'OpenAI integration not available'
            }), 503
        
        suggestions = openai_integration.generate_intelligent_suggestions(
            current_query, jira_context
        )
        
        return jsonify({
            'status': 'success',
            'suggestions': suggestions
        })
        
    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Suggestion generation failed: {str(e)}'
        }), 500

@enhanced_nlp_bp.route('/conversation-context', methods=['GET'])
def get_conversation_context():
    """
    Get current conversation context.
    """
    try:
        context = enhanced_nlp_processor.get_conversation_context()
        
        return jsonify({
            'status': 'success',
            'conversation_context': context
        })
        
    except Exception as e:
        logger.error(f"Error getting conversation context: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get conversation context: {str(e)}'
        }), 500

@enhanced_nlp_bp.route('/conversation-context', methods=['DELETE'])
def clear_conversation_context():
    """
    Clear conversation context.
    """
    try:
        enhanced_nlp_processor.clear_conversation_context()
        
        return jsonify({
            'status': 'success',
            'message': 'Conversation context cleared'
        })
        
    except Exception as e:
        logger.error(f"Error clearing conversation context: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to clear conversation context: {str(e)}'
        }), 500

@enhanced_nlp_bp.route('/processing-stats', methods=['GET'])
def get_processing_stats():
    """
    Get processing statistics including OpenAI usage.
    """
    try:
        stats = enhanced_nlp_processor.get_processing_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting processing stats: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get processing stats: {str(e)}'
        }), 500

@enhanced_nlp_bp.route('/openai-status', methods=['GET'])
def get_openai_status():
    """
    Get OpenAI integration status and configuration.
    """
    try:
        status = {
            'available': openai_integration.is_available(),
            'model': openai_integration.model if openai_integration.is_available() else None,
            'usage_stats': openai_integration.get_usage_stats() if openai_integration.is_available() else None
        }
        
        return jsonify({
            'status': 'success',
            'openai_status': status
        })
        
    except Exception as e:
        logger.error(f"Error getting OpenAI status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get OpenAI status: {str(e)}'
        }), 500

@enhanced_nlp_bp.route('/test-enhanced-queries', methods=['GET'])
def test_enhanced_queries():
    """
    Test enhanced NLP with sample queries.
    """
    try:
        test_queries = [
            {
                'query': 'How many tickets did John work on last month compared to this month?',
                'description': 'Complex comparative query with time ranges'
            },
            {
                'query': 'Show me the velocity trend and explain what it means for our next sprint',
                'description': 'Query requiring analysis and explanation'
            },
            {
                'query': 'What about the defect rate? Is it getting better?',
                'description': 'Conversational follow-up query'
            },
            {
                'query': 'Give me insights on project DEMO including quality metrics and team performance',
                'description': 'Multi-faceted analysis request'
            }
        ]
        
        results = []
        for test_case in test_queries:
            try:
                result = enhanced_nlp_processor.process_query(test_case['query'])
                results.append({
                    'query': test_case['query'],
                    'description': test_case['description'],
                    'result': result,
                    'success': True
                })
            except Exception as e:
                results.append({
                    'query': test_case['query'],
                    'description': test_case['description'],
                    'error': str(e),
                    'success': False
                })
        
        return jsonify({
            'status': 'success',
            'test_results': results,
            'openai_available': openai_integration.is_available()
        })
        
    except Exception as e:
        logger.error(f"Error in enhanced query testing: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Enhanced query testing failed: {str(e)}'
        }), 500

