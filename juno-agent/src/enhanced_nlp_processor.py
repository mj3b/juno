import logging
from typing import Dict, List, Optional, Any, Tuple
from .nlp_processor import JiraNLUProcessor
from juno.infrastructure.openai_integration.openai_client import OpenAIIntegration
import time

class EnhancedNLPProcessor:
    """
    Enhanced NLP processor that combines local pattern matching
    with OpenAI GPT capabilities for superior query understanding.
    """
    
    def __init__(self):
        self.local_nlp = JiraNLUProcessor()
        self.openai_integration = OpenAIIntegration()
        self.logger = logging.getLogger(__name__)
        
        # Configuration for routing decisions
        self.confidence_threshold = 0.8
        self.use_gpt_for_complex = True
        self.use_gpt_for_conversation = True
        
        # Conversation context management
        self.conversation_history = []
        self.max_history_length = 10
    
    def process_query(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """
        Process a natural language query using the optimal processing strategy.
        
        Args:
            query: The natural language query
            context: Additional context including session info
            
        Returns:
            Processed query with intent, entities, and execution plan
        """
        start_time = time.time()
        
        # First, try local NLP processing
        local_result = self.local_nlp.process_query(query)
        
        # Convert ParsedQuery to dictionary if needed
        if hasattr(local_result, '__dict__'):
            local_result = {
                'intent': str(getattr(local_result, 'intent', 'unknown')),
                'entities': getattr(local_result, 'entities', {}),
                'confidence': getattr(local_result, 'confidence', 0.0),
                'jql': getattr(local_result, 'jql', ''),
                'filters': getattr(local_result, 'filters', [])
            }
        
        local_confidence = local_result.get('confidence', 0.0)
        
        # Determine processing strategy
        processing_strategy = self._determine_processing_strategy(
            query, local_result, local_confidence, context
        )
        
        self.logger.info(f"Processing strategy: {processing_strategy}")
        
        if processing_strategy == "local_only":
            result = local_result
            result['processing_method'] = 'local_nlp'
            
        elif processing_strategy == "openai_enhanced":
            result = self._process_with_openai_enhancement(query, local_result, context)
            
        elif processing_strategy == "hybrid":
            result = self._process_hybrid(query, local_result, context)
            
        else:  # fallback to local
            result = local_result
            result['processing_method'] = 'local_nlp_fallback'
        
        # Add conversation to history
        self._update_conversation_history(query, result)
        
        # Add processing metadata
        result['processing_time'] = time.time() - start_time
        result['openai_available'] = self.openai_integration.is_available()
        
        return result
    
    def _determine_processing_strategy(self, query: str, local_result: Dict, 
                                     local_confidence: float, context: Dict = None) -> str:
        """
        Determine the optimal processing strategy for the query.
        
        Returns:
            'local_only', 'openai_enhanced', 'hybrid', or 'fallback'
        """
        # If OpenAI is not available, use local only
        if not self.openai_integration.is_available():
            return "local_only"
        
        # High confidence local results
        if local_confidence >= self.confidence_threshold:
            return "local_only"
        
        # Check for conversational patterns
        if self._is_conversational_query(query):
            return "openai_enhanced"
        
        # Check for complex or ambiguous queries
        if self._is_complex_query(query, local_result):
            return "openai_enhanced"
        
        # Check if context suggests continuation
        if self._requires_context_resolution(query, context):
            return "openai_enhanced"
        
        # Medium confidence - use hybrid approach
        if local_confidence >= 0.5:
            return "hybrid"
        
        # Low confidence - enhance with OpenAI
        return "openai_enhanced"
    
    def _process_with_openai_enhancement(self, query: str, local_result: Dict, 
                                       context: Dict = None) -> Dict[str, Any]:
        """Process query with OpenAI enhancement."""
        try:
            # Prepare context for OpenAI
            openai_context = {
                'local_analysis': local_result,
                'conversation_history': self.conversation_history[-3:],  # Last 3 interactions
                'session_context': context or {}
            }
            
            # Get enhanced understanding from OpenAI
            enhanced_result = self.openai_integration.enhance_query_understanding(
                query, openai_context
            )
            
            if 'error' in enhanced_result:
                self.logger.warning(f"OpenAI enhancement failed: {enhanced_result['error']}")
                return self._fallback_to_local(local_result)
            
            # Merge local and enhanced results
            merged_result = self._merge_results(local_result, enhanced_result)
            merged_result['processing_method'] = 'openai_enhanced'
            
            # Generate intelligent suggestions
            suggestions = self.openai_integration.generate_intelligent_suggestions(
                query, self._get_jira_context()
            )
            merged_result['suggestions'] = suggestions
            
            return merged_result
            
        except Exception as e:
            self.logger.error(f"Error in OpenAI enhancement: {str(e)}")
            return self._fallback_to_local(local_result)
    
    def _process_hybrid(self, query: str, local_result: Dict, context: Dict = None) -> Dict[str, Any]:
        """Process using hybrid approach - local + selective OpenAI enhancement."""
        try:
            # Use local result as base
            result = local_result.copy()
            result['processing_method'] = 'hybrid'
            
            # Enhance specific aspects with OpenAI
            if self._needs_entity_enhancement(local_result):
                enhanced_entities = self._enhance_entities_with_openai(query, local_result)
                if enhanced_entities:
                    result['entities'].update(enhanced_entities)
            
            if self._needs_intent_clarification(local_result):
                clarified_intent = self._clarify_intent_with_openai(query, local_result)
                if clarified_intent:
                    result['intent'] = clarified_intent
                    result['confidence'] = min(result['confidence'] + 0.2, 1.0)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in hybrid processing: {str(e)}")
            return self._fallback_to_local(local_result)
    
    def _is_conversational_query(self, query: str) -> bool:
        """Check if query is conversational in nature."""
        conversational_patterns = [
            r'\b(what about|how about|and|also|too|as well)\b',
            r'\b(it|that|this|them|they)\b',
            r'\b(show me more|tell me about|what else)\b',
            r'\b(compared to|versus|vs)\b',
            r'^(yes|no|ok|sure|thanks)\b'
        ]
        
        import re
        for pattern in conversational_patterns:
            if re.search(pattern, query.lower()):
                return True
        return False
    
    def _is_complex_query(self, query: str, local_result: Dict) -> bool:
        """Check if query is complex and might benefit from GPT processing."""
        # Check for multiple clauses
        if len(query.split(' and ')) > 2 or len(query.split(' or ')) > 1:
            return True
        
        # Check for low confidence in local processing
        if local_result.get('confidence', 0) < 0.6:
            return True
        
        # Check for ambiguous entities
        entities = local_result.get('entities', {})
        if any(not v for v in entities.values()):  # Empty entity values
            return True
        
        # Check for complex time expressions
        time_patterns = [
            r'last.*before', r'between.*and', r'since.*until',
            r'excluding.*weekends', r'business.*days'
        ]
        import re
        for pattern in time_patterns:
            if re.search(pattern, query.lower()):
                return True
        
        return False
    
    def _requires_context_resolution(self, query: str, context: Dict = None) -> bool:
        """Check if query requires context resolution."""
        if not context:
            return False
        
        # Check for pronouns that need resolution
        pronouns = ['it', 'that', 'this', 'them', 'they', 'those', 'these']
        query_words = query.lower().split()
        
        return any(pronoun in query_words for pronoun in pronouns)
    
    def _merge_results(self, local_result: Dict, enhanced_result: Dict) -> Dict[str, Any]:
        """Merge local and enhanced results intelligently."""
        merged = local_result.copy()
        
        # Use enhanced intent if confidence is higher
        if enhanced_result.get('confidence', 0) > local_result.get('confidence', 0):
            merged['intent'] = enhanced_result.get('intent', local_result.get('intent'))
            merged['confidence'] = enhanced_result.get('confidence', local_result.get('confidence'))
        
        # Merge entities, preferring enhanced ones
        enhanced_entities = enhanced_result.get('entities', {})
        local_entities = local_result.get('entities', {})
        
        merged_entities = local_entities.copy()
        for key, value in enhanced_entities.items():
            if value and (not merged_entities.get(key) or len(str(value)) > len(str(merged_entities.get(key, '')))):
                merged_entities[key] = value
        
        merged['entities'] = merged_entities
        
        # Add enhanced information
        merged['enhanced_query'] = enhanced_result.get('enhanced_query', '')
        merged['ambiguities'] = enhanced_result.get('ambiguities', [])
        merged['openai_analysis'] = enhanced_result
        
        return merged
    
    def _fallback_to_local(self, local_result: Dict) -> Dict[str, Any]:
        """Fallback to local processing with appropriate marking."""
        result = local_result.copy()
        result['processing_method'] = 'local_fallback'
        result['openai_error'] = True
        return result
    
    def _needs_entity_enhancement(self, local_result: Dict) -> bool:
        """Check if entities need enhancement."""
        entities = local_result.get('entities', {})
        return any(not v for v in entities.values())
    
    def _needs_intent_clarification(self, local_result: Dict) -> bool:
        """Check if intent needs clarification."""
        return local_result.get('confidence', 0) < 0.7
    
    def _enhance_entities_with_openai(self, query: str, local_result: Dict) -> Optional[Dict]:
        """Enhance entities using OpenAI."""
        # Simplified entity enhancement - in practice, this would be more sophisticated
        try:
            enhanced_result = self.openai_integration.enhance_query_understanding(query, {'local_result': local_result})
            return enhanced_result.get('entities', {})
        except:
            return None
    
    def _clarify_intent_with_openai(self, query: str, local_result: Dict) -> Optional[str]:
        """Clarify intent using OpenAI."""
        try:
            enhanced_result = self.openai_integration.enhance_query_understanding(query, {'local_result': local_result})
            return enhanced_result.get('intent')
        except:
            return None
    
    def _update_conversation_history(self, query: str, result: Dict):
        """Update conversation history."""
        self.conversation_history.append({
            'timestamp': time.time(),
            'query': query,
            'intent': result.get('intent'),
            'entities': result.get('entities', {}),
            'processing_method': result.get('processing_method')
        })
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
    
    def _get_jira_context(self) -> Dict:
        """Get current Jira context for suggestions."""
        # This would be populated with actual Jira data in practice
        return {
            'available_projects': ['DEMO', 'TEST', 'PROD'],
            'common_users': ['john.doe', 'jane.smith', 'admin'],
            'recent_activity': 'High activity in DEMO project',
            'current_sprint': 'Sprint 23'
        }
    
    def explain_results(self, results: Dict, original_query: str) -> str:
        """Generate natural language explanation of results."""
        if self.openai_integration.is_available():
            return self.openai_integration.explain_analytics_results(results, original_query)
        else:
            return "Results explanation not available (OpenAI integration disabled)."
    
    def get_conversation_context(self) -> List[Dict]:
        """Get current conversation context."""
        return self.conversation_history.copy()
    
    def clear_conversation_context(self):
        """Clear conversation history."""
        self.conversation_history = []
        self.logger.info("Conversation context cleared")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        stats = {
            'conversation_length': len(self.conversation_history),
            'openai_available': self.openai_integration.is_available()
        }
        
        if self.openai_integration.is_available():
            stats['openai_usage'] = self.openai_integration.get_usage_stats()
        
        return stats

