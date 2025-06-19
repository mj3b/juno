import logging
from typing import Dict, List, Optional, Any, Tuple
from .nlp_processor import JiraNLUProcessor
from .enterprise_gpt_integration import EnterpriseGPTIntegration
import time

class EnhancedNLPProcessor:
    """
    Enhanced NLP processor that combines local pattern matching
    with Enterprise GPT capabilities (OpenAI, Enterprise, Azure, Custom) 
    for superior query understanding.
    """
    
    def __init__(self):
        self.local_nlp = JiraNLUProcessor()
        self.enterprise_gpt = EnterpriseGPTIntegration()
        self.logger = logging.getLogger(__name__)
        
        # Configuration for routing decisions
        self.confidence_threshold = 0.8
        self.use_gpt_for_complex = True
        self.use_gpt_for_conversation = True
        
        # Conversation context management
        self.conversation_history = []
        self.max_history_length = 10
        
        # Provider-specific configurations
        self.provider_preferences = {
            'enterprise': {
                'use_for_intent_analysis': True,
                'use_for_real_time_context': True,
                'confidence_boost': 0.1
            },
            'openai': {
                'use_for_complex_queries': True,
                'use_for_explanations': True,
                'confidence_boost': 0.05
            },
            'azure': {
                'use_for_enterprise_queries': True,
                'use_for_compliance': True,
                'confidence_boost': 0.05
            }
        }
    
    def process_query(self, query: str, context: Dict = None, preferred_provider: str = None) -> Dict[str, Any]:
        """
        Process a natural language query using the optimal processing strategy.
        
        Args:
            query: The natural language query
            context: Additional context including session info
            preferred_provider: Specific GPT provider to use
            
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
        
        # Determine processing strategy and provider
        processing_strategy, selected_provider = self._determine_processing_strategy(
            query, local_result, local_confidence, context, preferred_provider
        )
        
        self.logger.info(f"Processing strategy: {processing_strategy}, Provider: {selected_provider}")
        
        if processing_strategy == "local_only":
            result = local_result
            result['processing_method'] = 'local_nlp'
            result['provider_used'] = 'local'
            
        elif processing_strategy == "gpt_enhanced":
            result = self._process_with_gpt_enhancement(query, local_result, context, selected_provider)
            
        elif processing_strategy == "hybrid":
            result = self._process_hybrid(query, local_result, context, selected_provider)
            
        else:  # fallback to local
            result = local_result
            result['processing_method'] = 'local_nlp_fallback'
            result['provider_used'] = 'local'
        
        # Add conversation to history
        self._update_conversation_history(query, result)
        
        # Add processing metadata
        result['processing_time'] = time.time() - start_time
        result['gpt_available'] = self.enterprise_gpt.is_available()
        result['available_providers'] = self.enterprise_gpt.get_available_providers()
        
        return result
    
    def _determine_processing_strategy(self, query: str, local_result: Dict, 
                                     local_confidence: float, context: Dict = None,
                                     preferred_provider: str = None) -> Tuple[str, Optional[str]]:
        """
        Determine the optimal processing strategy and provider for the query.
        
        Returns:
            Tuple of (strategy, provider) where strategy is one of:
            'local_only', 'gpt_enhanced', 'hybrid', or 'fallback'
        """
        # If no GPT providers are available, use local only
        if not self.enterprise_gpt.is_available():
            return "local_only", None
        
        # Select provider based on preference and availability
        selected_provider = self._select_optimal_provider(query, context, preferred_provider)
        
        # High confidence local results
        if local_confidence >= self.confidence_threshold:
            return "local_only", None
        
        # Check for conversational patterns
        if self._is_conversational_query(query):
            return "gpt_enhanced", selected_provider
        
        # Check for complex or ambiguous queries
        if self._is_complex_query(query, local_result):
            return "gpt_enhanced", selected_provider
        
        # Check if context suggests continuation
        if self._requires_context_resolution(query, context):
            return "gpt_enhanced", selected_provider
        
        # Enterprise GPT specific: Use for intent analysis
        if selected_provider == "enterprise" and self._benefits_from_intent_analysis(query):
            return "gpt_enhanced", selected_provider
        
        # Medium confidence - use hybrid approach
        if local_confidence >= 0.5:
            return "hybrid", selected_provider
        
        # Low confidence - enhance with GPT
        return "gpt_enhanced", selected_provider
    
    def _select_optimal_provider(self, query: str, context: Dict = None, 
                               preferred_provider: str = None) -> Optional[str]:
        """Select the optimal GPT provider for the query."""
        available_providers = self.enterprise_gpt.get_available_providers()
        
        if not available_providers:
            return None
        
        # Use preferred provider if specified and available
        if preferred_provider and preferred_provider in available_providers:
            return preferred_provider
        
        # Enterprise GPT Enterprise Intent Engine for intent-heavy queries
        if "enterprise" in available_providers:
            if self._benefits_from_intent_analysis(query):
                return "enterprise"
            if self._is_real_time_query(query):
                return "enterprise"
        
        # OpenAI for complex analytical queries
        if "openai" in available_providers:
            if self._is_complex_analytical_query(query):
                return "openai"
        
        # Azure for enterprise/compliance queries
        if "azure" in available_providers:
            if self._is_enterprise_query(query, context):
                return "azure"
        
        # Default to first available provider
        return available_providers[0]
    
    def _benefits_from_intent_analysis(self, query: str) -> bool:
        """Check if query would benefit from Enterprise GPT's intent analysis."""
        intent_keywords = [
            'want', 'need', 'should', 'could', 'would like',
            'help', 'show', 'find', 'get', 'tell me'
        ]
        return any(keyword in query.lower() for keyword in intent_keywords)
    
    def _is_real_time_query(self, query: str) -> bool:
        """Check if query requires real-time data analysis."""
        real_time_keywords = [
            'current', 'now', 'today', 'this moment', 'right now',
            'latest', 'recent', 'active', 'ongoing'
        ]
        return any(keyword in query.lower() for keyword in real_time_keywords)
    
    def _is_complex_analytical_query(self, query: str) -> bool:
        """Check if query is complex analytical that benefits from OpenAI."""
        analytical_keywords = [
            'analyze', 'compare', 'trend', 'pattern', 'correlation',
            'predict', 'forecast', 'insight', 'relationship'
        ]
        return any(keyword in query.lower() for keyword in analytical_keywords)
    
    def _is_enterprise_query(self, query: str, context: Dict = None) -> bool:
        """Check if query is enterprise-focused for Azure."""
        enterprise_keywords = [
            'compliance', 'audit', 'security', 'governance',
            'policy', 'regulation', 'enterprise', 'corporate'
        ]
        return any(keyword in query.lower() for keyword in enterprise_keywords)
    
    def _process_with_gpt_enhancement(self, query: str, local_result: Dict, 
                                    context: Dict = None, provider: str = None) -> Dict[str, Any]:
        """Process query with Enterprise GPT enhancement."""
        try:
            # Prepare context for GPT
            gpt_context = {
                'local_analysis': local_result,
                'conversation_history': self.conversation_history[-3:],  # Last 3 interactions
                'session_context': context or {}
            }
            
            # Get enhanced understanding from Enterprise GPT
            enhanced_result = self.enterprise_gpt.enhance_query_understanding(
                query, gpt_context, provider
            )
            
            if 'error' in enhanced_result:
                self.logger.warning(f"GPT enhancement failed: {enhanced_result['error']}")
                return self._fallback_to_local(local_result)
            
            # Merge local and enhanced results
            merged_result = self._merge_results(local_result, enhanced_result)
            merged_result['processing_method'] = 'gpt_enhanced'
            merged_result['provider_used'] = provider or 'unknown'
            
            # Handle Enterprise GPT specific features
            if provider == "enterprise":
                merged_result = self._handle_enterprise_features(merged_result, enhanced_result)
            
            # Generate intelligent suggestions
            suggestions = self.enterprise_gpt.generate_intelligent_suggestions(
                query, self._get_jira_context(), provider
            )
            merged_result['suggestions'] = suggestions
            
            return merged_result
            
        except Exception as e:
            self.logger.error(f"Error in GPT enhancement: {str(e)}")
            return self._fallback_to_local(local_result)
    
    def _handle_enterprise_features(self, merged_result: Dict, enhanced_result: Dict) -> Dict[str, Any]:
        """Handle Enterprise GPT Enterprise Intent Engine specific features."""
        # Extract Enterprise GPT specific fields
        if 'intent' in enhanced_result:
            merged_result['enterprise_intent'] = enhanced_result['intent']
        
        if 'confidence' in enhanced_result:
            # Apply Enterprise GPT confidence boost
            boost = self.provider_preferences.get('enterprise', {}).get('confidence_boost', 0.1)
            merged_result['confidence'] = min(enhanced_result['confidence'] + boost, 1.0)
        
        if 'suggested_actions' in enhanced_result:
            merged_result['suggested_actions'] = enhanced_result['suggested_actions']
        
        # Mark as Enterprise GPT enhanced
        merged_result['enterprise_enhanced'] = True
        
        return merged_result
    
    def _process_hybrid(self, query: str, local_result: Dict, context: Dict = None, 
                       provider: str = None) -> Dict[str, Any]:
        """Process using hybrid approach - local + selective GPT enhancement."""
        try:
            # Use local result as base
            result = local_result.copy()
            result['processing_method'] = 'hybrid'
            result['provider_used'] = provider or 'local'
            
            # Enhance specific aspects with GPT
            if self._needs_entity_enhancement(local_result):
                enhanced_entities = self._enhance_entities_with_gpt(query, local_result, provider)
                if enhanced_entities:
                    result['entities'].update(enhanced_entities)
            
            if self._needs_intent_clarification(local_result):
                clarified_intent = self._clarify_intent_with_gpt(query, local_result, provider)
                if clarified_intent:
                    result['intent'] = clarified_intent
                    result['confidence'] = min(result['confidence'] + 0.2, 1.0)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in hybrid processing: {str(e)}")
            return self._fallback_to_local(local_result)
    
    def _enhance_entities_with_gpt(self, query: str, local_result: Dict, provider: str = None) -> Optional[Dict]:
        """Enhance entities using Enterprise GPT."""
        try:
            enhanced_result = self.enterprise_gpt.enhance_query_understanding(
                query, {'local_result': local_result}, provider
            )
            return enhanced_result.get('entities', {})
        except:
            return None
    
    def _clarify_intent_with_gpt(self, query: str, local_result: Dict, provider: str = None) -> Optional[str]:
        """Clarify intent using Enterprise GPT."""
        try:
            enhanced_result = self.enterprise_gpt.enhance_query_understanding(
                query, {'local_result': local_result}, provider
            )
            return enhanced_result.get('intent')
        except:
            return None
    
    def explain_results(self, results: Dict, original_query: str, provider: str = None) -> str:
        """Generate natural language explanation of results."""
        if self.enterprise_gpt.is_available():
            return self.enterprise_gpt.explain_analytics_results(results, original_query, provider)
        else:
            return "Results explanation not available (No GPT providers configured)."
    
    def manage_conversation_context(self, provider: str = None) -> Dict[str, Any]:
        """Manage conversation context using Enterprise GPT."""
        if self.enterprise_gpt.is_available() and self.conversation_history:
            return self.enterprise_gpt.manage_conversation_context(
                self.conversation_history, provider
            )
        return {"error": "No conversation context or GPT providers available"}
    
    def switch_provider(self, provider: str) -> bool:
        """Switch to a different GPT provider."""
        return self.enterprise_gpt.switch_provider(provider)
    
    def get_provider_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of available providers."""
        capabilities = {}
        
        for provider in self.enterprise_gpt.get_available_providers():
            if provider == "enterprise":
                capabilities[provider] = {
                    "intent_analysis": True,
                    "real_time_context": True,
                    "suggested_actions": True,
                    "multi_language": True,
                    "confidence_scoring": True
                }
            elif provider == "openai":
                capabilities[provider] = {
                    "complex_reasoning": True,
                    "function_calling": True,
                    "advanced_models": True,
                    "fine_tuning": True
                }
            elif provider == "azure":
                capabilities[provider] = {
                    "enterprise_security": True,
                    "compliance": True,
                    "private_endpoints": True,
                    "content_filtering": True
                }
            else:
                capabilities[provider] = {
                    "basic_completion": True,
                    "custom_configuration": True
                }
        
        return capabilities
    
    # Keep existing methods from the original class
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
        merged['gpt_analysis'] = enhanced_result
        
        return merged
    
    def _fallback_to_local(self, local_result: Dict) -> Dict[str, Any]:
        """Fallback to local processing with appropriate marking."""
        result = local_result.copy()
        result['processing_method'] = 'local_fallback'
        result['gpt_error'] = True
        result['provider_used'] = 'local'
        return result
    
    def _needs_entity_enhancement(self, local_result: Dict) -> bool:
        """Check if entities need enhancement."""
        entities = local_result.get('entities', {})
        return any(not v for v in entities.values())
    
    def _needs_intent_clarification(self, local_result: Dict) -> bool:
        """Check if intent needs clarification."""
        return local_result.get('confidence', 0) < 0.7
    
    def _update_conversation_history(self, query: str, result: Dict):
        """Update conversation history."""
        self.conversation_history.append({
            'timestamp': time.time(),
            'query': query,
            'intent': result.get('intent'),
            'entities': result.get('entities', {}),
            'processing_method': result.get('processing_method'),
            'provider_used': result.get('provider_used')
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
            'gpt_available': self.enterprise_gpt.is_available(),
            'available_providers': self.enterprise_gpt.get_available_providers()
        }
        
        if self.enterprise_gpt.is_available():
            stats['gpt_usage'] = self.enterprise_gpt.get_usage_stats()
        
        return stats

