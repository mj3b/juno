import os
import logging
from typing import Dict, List, Optional, Any
from openai import OpenAI
import json
import time
from datetime import datetime, timedelta

class OpenAIIntegration:
    """
    OpenAI GPT integration for enhanced natural language processing
    in the JUNO.
    """
    
    def __init__(self):
        self.client = None
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o')
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
        self.temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.3'))
        
        # Usage tracking
        self.usage_stats = {
            'total_requests': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'last_reset': datetime.now()
        }
        
        # Cache for responses
        self.response_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        self.logger = logging.getLogger(__name__)
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.logger.info("OpenAI integration initialized successfully")
        else:
            self.logger.warning("OpenAI API key not found. GPT features will be disabled.")
    
    def is_available(self) -> bool:
        """Check if OpenAI integration is available."""
        return self.client is not None
    
    def enhance_query_understanding(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """
        Enhance query understanding using GPT for complex or ambiguous queries.
        
        Args:
            query: The natural language query
            context: Additional context including conversation history
            
        Returns:
            Enhanced query analysis with improved intent and entities
        """
        if not self.is_available():
            return {"error": "OpenAI integration not available"}
        
        # Check cache first
        cache_key = f"enhance_{hash(query + str(context))}"
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        try:
            system_prompt = self._get_query_enhancement_prompt()
            user_prompt = self._format_query_enhancement_request(query, context)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Track usage
            self._track_usage(response.usage)
            
            # Cache the response
            self._cache_response(cache_key, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in query enhancement: {str(e)}")
            return {"error": f"Query enhancement failed: {str(e)}"}
    
    def generate_intelligent_suggestions(self, current_query: str, jira_context: Dict) -> List[str]:
        """
        Generate intelligent query suggestions based on current context.
        
        Args:
            current_query: The current query being processed
            jira_context: Context about available Jira data
            
        Returns:
            List of suggested follow-up queries
        """
        if not self.is_available():
            return []
        
        try:
            system_prompt = self._get_suggestion_prompt()
            user_prompt = self._format_suggestion_request(current_query, jira_context)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            self._track_usage(response.usage)
            
            return result.get('suggestions', [])
            
        except Exception as e:
            self.logger.error(f"Error generating suggestions: {str(e)}")
            return []
    
    def explain_analytics_results(self, results: Dict, query: str) -> str:
        """
        Generate natural language explanations of analytics results.
        
        Args:
            results: The analytics results to explain
            query: The original query for context
            
        Returns:
            Natural language explanation of the results
        """
        if not self.is_available():
            return "Analytics results explanation not available (OpenAI integration disabled)."
        
        try:
            system_prompt = self._get_explanation_prompt()
            user_prompt = self._format_explanation_request(results, query)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=800,
                temperature=0.4
            )
            
            explanation = response.choices[0].message.content
            self._track_usage(response.usage)
            
            return explanation
            
        except Exception as e:
            self.logger.error(f"Error generating explanation: {str(e)}")
            return f"Unable to generate explanation: {str(e)}"
    
    def manage_conversation_context(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        """
        Manage conversation context and resolve references.
        
        Args:
            conversation_history: List of previous interactions
            
        Returns:
            Processed context with resolved references
        """
        if not self.is_available():
            return {"error": "OpenAI integration not available"}
        
        try:
            system_prompt = self._get_context_management_prompt()
            user_prompt = self._format_context_request(conversation_history)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=600,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            self._track_usage(response.usage)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in context management: {str(e)}")
            return {"error": f"Context management failed: {str(e)}"}
    
    def _get_query_enhancement_prompt(self) -> str:
        """Get the system prompt for query enhancement."""
        return """You are an expert at understanding Jira analytics queries. Your task is to analyze natural language queries about Jira data and provide enhanced understanding.

You should identify:
1. Intent: What type of analysis is being requested
2. Entities: Projects, users, time ranges, statuses, etc.
3. Filters: Any filtering criteria
4. Ambiguities: Parts that need clarification
5. Suggestions: How to improve the query

Available intents: assignee_count, status_distribution, issue_list, project_summary, defect_analysis, velocity_report, lead_time_analysis, trend_analysis

Return your analysis as JSON with these fields:
- intent: The primary intent
- confidence: Confidence score (0-1)
- entities: Dictionary of extracted entities
- filters: List of filter conditions
- ambiguities: List of unclear parts
- enhanced_query: Improved version of the query
- suggestions: List of clarifying questions"""
    
    def _get_suggestion_prompt(self) -> str:
        """Get the system prompt for generating suggestions."""
        return """You are an expert Jira analytics assistant. Based on the current query and available data, suggest relevant follow-up queries that would provide additional insights.

Focus on:
1. Related metrics that complement the current analysis
2. Different time periods or comparisons
3. Drill-down opportunities
4. Quality and performance insights
5. Actionable next steps

Return suggestions as JSON with a 'suggestions' array containing 3-5 relevant follow-up queries."""
    
    def _get_explanation_prompt(self) -> str:
        """Get the system prompt for explaining results."""
        return """You are an expert at explaining Jira analytics results in clear, business-friendly language. 

Your explanations should:
1. Summarize the key findings
2. Highlight important trends or patterns
3. Provide context about what the numbers mean
4. Suggest potential actions or next steps
5. Use clear, non-technical language

Be concise but comprehensive, focusing on actionable insights."""
    
    def _get_context_management_prompt(self) -> str:
        """Get the system prompt for context management."""
        return """You are managing conversation context for a Jira analytics system. Analyze the conversation history to:

1. Resolve pronoun references (it, that, them, etc.)
2. Identify implicit context from previous queries
3. Track the current focus (project, time period, etc.)
4. Detect topic changes or continuations

Return JSON with:
- resolved_references: Dictionary mapping pronouns to entities
- current_context: Current focus and scope
- topic_continuity: Whether this continues the previous topic
- implicit_filters: Filters implied by context"""
    
    def _format_query_enhancement_request(self, query: str, context: Dict = None) -> str:
        """Format the query enhancement request."""
        request = f"Query: {query}\n\n"
        
        if context:
            request += f"Context: {json.dumps(context, indent=2)}\n\n"
        
        request += "Please analyze this query and provide enhanced understanding."
        return request
    
    def _format_suggestion_request(self, query: str, jira_context: Dict) -> str:
        """Format the suggestion request."""
        return f"""Current Query: {query}

Available Jira Context:
{json.dumps(jira_context, indent=2)}

Please suggest relevant follow-up queries that would provide additional insights."""
    
    def _format_explanation_request(self, results: Dict, query: str) -> str:
        """Format the explanation request."""
        return f"""Original Query: {query}

Analytics Results:
{json.dumps(results, indent=2)}

Please provide a clear, business-friendly explanation of these results."""
    
    def _format_context_request(self, conversation_history: List[Dict]) -> str:
        """Format the context management request."""
        return f"""Conversation History:
{json.dumps(conversation_history, indent=2)}

Please analyze the context and resolve any references."""
    
    def _track_usage(self, usage):
        """Track API usage for monitoring and cost management."""
        self.usage_stats['total_requests'] += 1
        self.usage_stats['total_tokens'] += usage.total_tokens
        
        # Estimate cost (approximate pricing for GPT-4)
        input_cost = usage.prompt_tokens * 0.00003  # $0.03 per 1K tokens
        output_cost = usage.completion_tokens * 0.00006  # $0.06 per 1K tokens
        self.usage_stats['total_cost'] += input_cost + output_cost
        
        self.logger.info(f"OpenAI usage: {usage.total_tokens} tokens, estimated cost: ${input_cost + output_cost:.4f}")
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached response if available and not expired."""
        if cache_key in self.response_cache:
            cached_data = self.response_cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['response']
            else:
                del self.response_cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: Dict):
        """Cache response with timestamp."""
        self.response_cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        return self.usage_stats.copy()
    
    def reset_usage_stats(self):
        """Reset usage statistics."""
        self.usage_stats = {
            'total_requests': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'last_reset': datetime.now()
        }
        self.logger.info("Usage statistics reset")

