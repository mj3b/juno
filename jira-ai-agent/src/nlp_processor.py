import re
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class QueryIntent(Enum):
    """Enumeration of supported query intents."""
    ASSIGNEE_COUNT = "assignee_count"
    STATUS_DISTRIBUTION = "status_distribution"
    ISSUE_LIST = "issue_list"
    PROJECT_SUMMARY = "project_summary"
    VELOCITY_REPORT = "velocity_report"
    DEFECT_ANALYSIS = "defect_analysis"
    LEAD_TIME_ANALYSIS = "lead_time_analysis"
    BURNDOWN_CHART = "burndown_chart"
    CUSTOM_REPORT = "custom_report"
    UNKNOWN = "unknown"

@dataclass
class ExtractedEntity:
    """Represents an extracted entity from natural language query."""
    entity_type: str
    value: str
    confidence: float
    start_pos: int
    end_pos: int

@dataclass
class ParsedQuery:
    """Represents a parsed natural language query."""
    intent: QueryIntent
    entities: List[ExtractedEntity]
    filters: Dict[str, Any]
    time_range: Optional[Tuple[datetime, datetime]]
    aggregation_type: Optional[str]
    output_format: str
    confidence: float
    original_query: str

class JiraNLUProcessor:
    """
    Natural Language Understanding processor for Jira queries.
    Handles intent recognition, entity extraction, and query normalization.
    """
    
    def __init__(self):
        """Initialize the NLU processor with patterns and vocabularies."""
        self._init_intent_patterns()
        self._init_entity_patterns()
        self._init_jira_vocabulary()
    
    def _init_intent_patterns(self):
        """Initialize intent recognition patterns."""
        self.intent_patterns = {
            QueryIntent.ASSIGNEE_COUNT: [
                r"(?:how many|count|number of).*(?:tickets?|issues?).*(?:assigned to|for|by)\s+(\w+)",
                r"(?:show|get|list).*(?:assignee|assignment).*(?:count|distribution)",
                r"(?:tickets?|issues?).*(?:per|by)\s+assignee",
                r"(?:who has|assignee).*(?:most|how many).*(?:tickets?|issues?)"
            ],
            QueryIntent.STATUS_DISTRIBUTION: [
                r"(?:status|state).*(?:distribution|breakdown|summary)",
                r"(?:how many|count).*(?:tickets?|issues?).*(?:in|by|per)\s+(?:status|state)",
                r"(?:show|get|list).*(?:status|state).*(?:count|summary)",
                r"(?:breakdown|distribution).*(?:status|state)"
            ],
            QueryIntent.ISSUE_LIST: [
                r"(?:show|list|get|find).*(?:tickets?|issues?)",
                r"(?:tickets?|issues?).*(?:in|for|from)\s+(\w+)",
                r"(?:all|recent).*(?:tickets?|issues?)",
                r"(?:search|find).*(?:tickets?|issues?).*(?:where|with|that)"
            ],
            QueryIntent.PROJECT_SUMMARY: [
                r"(?:project|summary).*(?:overview|summary|report)",
                r"(?:show|get).*project.*(?:status|summary|overview)",
                r"(?:overview|summary).*(?:of|for)\s+project",
                r"project.*(?:dashboard|summary|overview)"
            ],
            QueryIntent.VELOCITY_REPORT: [
                r"(?:velocity|speed).*(?:report|chart|analysis)",
                r"(?:sprint|team).*velocity",
                r"(?:how fast|speed).*(?:team|sprint)",
                r"(?:story points?|points?).*(?:per|by)\s+sprint"
            ],
            QueryIntent.DEFECT_ANALYSIS: [
                r"(?:defect|bug|error).*(?:analysis|report|pattern|trend)",
                r"(?:bug|defect).*(?:count|distribution|summary)",
                r"(?:quality|defect).*(?:metrics|analysis)",
                r"(?:how many|count).*(?:bugs?|defects?)"
            ],
            QueryIntent.LEAD_TIME_ANALYSIS: [
                r"(?:lead time|cycle time).*(?:analysis|report)",
                r"(?:how long|time).*(?:to complete|to resolve|to finish)",
                r"(?:average|mean).*(?:time|duration).*(?:to|for)",
                r"(?:time|duration).*(?:analysis|metrics)"
            ],
            QueryIntent.BURNDOWN_CHART: [
                r"(?:burndown|burnup).*(?:chart|graph)",
                r"(?:sprint|release).*(?:progress|burndown)",
                r"(?:remaining|completed).*(?:work|effort).*(?:chart|graph)",
                r"(?:progress|completion).*(?:chart|graph|report)"
            ]
        }
    
    def _init_entity_patterns(self):
        """Initialize entity extraction patterns."""
        self.entity_patterns = {
            'project': [
                r"(?:project|proj)\s+([A-Z]{2,10})",
                r"(?:in|for|from)\s+([A-Z]{2,10})",
                r"([A-Z]{2,10})\s+project"
            ],
            'user': [
                r"(?:assigned to|assignee|for|by)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)",
                r"(?:user|person)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)",
                r"([a-zA-Z]+(?:\s+[a-zA-Z]+)?)'s\s+(?:tickets?|issues?)"
            ],
            'status': [
                r"(?:status|state)\s+([a-zA-Z\s]+)",
                r"(?:in|with)\s+(open|closed|resolved|in progress|done|to do)",
                r"(open|closed|resolved|in progress|done|to do)\s+(?:tickets?|issues?)"
            ],
            'issue_type': [
                r"(?:type|kind)\s+([a-zA-Z\s]+)",
                r"(bug|defect|story|task|epic|feature)s?",
                r"(?:issues?\s+of\s+type|tickets?\s+of\s+type)\s+([a-zA-Z\s]+)"
            ],
            'priority': [
                r"(?:priority)\s+([a-zA-Z\s]+)",
                r"(high|medium|low|critical|blocker)\s+priority",
                r"(high|medium|low|critical|blocker)\s+(?:tickets?|issues?)"
            ],
            'time_range': [
                r"(?:last|past|previous)\s+(\d+)\s+(day|week|month|quarter|year)s?",
                r"(?:this|current)\s+(week|month|quarter|year|sprint)",
                r"(?:in|during)\s+(Q[1-4]|january|february|march|april|may|june|july|august|september|october|november|december)",
                r"(?:from|since)\s+(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})",
                r"(?:between)\s+(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})\s+(?:and)\s+(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})"
            ]
        }
    
    def _init_jira_vocabulary(self):
        """Initialize Jira-specific vocabulary and synonyms."""
        self.jira_vocabulary = {
            'issue_synonyms': ['ticket', 'issue', 'item', 'task', 'story', 'bug', 'defect'],
            'status_synonyms': {
                'open': ['open', 'new', 'created', 'to do', 'todo'],
                'in_progress': ['in progress', 'in-progress', 'active', 'working', 'development'],
                'resolved': ['resolved', 'fixed', 'completed', 'done', 'closed'],
                'closed': ['closed', 'finished', 'archived']
            },
            'priority_synonyms': {
                'critical': ['critical', 'blocker', 'urgent', 'highest'],
                'high': ['high', 'important', 'major'],
                'medium': ['medium', 'normal', 'moderate'],
                'low': ['low', 'minor', 'trivial', 'lowest']
            },
            'type_synonyms': {
                'bug': ['bug', 'defect', 'error', 'issue', 'problem'],
                'story': ['story', 'user story', 'feature', 'requirement'],
                'task': ['task', 'work item', 'todo'],
                'epic': ['epic', 'initiative', 'theme']
            }
        }
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> ParsedQuery:
        """
        Process a natural language query and extract structured information.
        
        Args:
            query: Natural language query string
            context: Optional context information (current project, user, etc.)
            
        Returns:
            ParsedQuery object with extracted information
        """
        logger.info(f"Processing query: {query}")
        
        # Normalize query
        normalized_query = self._normalize_query(query)
        
        # Extract intent
        intent, intent_confidence = self._extract_intent(normalized_query)
        
        # Extract entities
        entities = self._extract_entities(normalized_query, context)
        
        # Extract filters
        filters = self._extract_filters(entities, context)
        
        # Extract time range
        time_range = self._extract_time_range(normalized_query)
        
        # Determine aggregation type
        aggregation_type = self._determine_aggregation(normalized_query, intent)
        
        # Determine output format
        output_format = self._determine_output_format(normalized_query, intent)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_confidence(intent_confidence, entities)
        
        parsed_query = ParsedQuery(
            intent=intent,
            entities=entities,
            filters=filters,
            time_range=time_range,
            aggregation_type=aggregation_type,
            output_format=output_format,
            confidence=overall_confidence,
            original_query=query
        )
        
        logger.info(f"Parsed query - Intent: {intent}, Confidence: {overall_confidence:.2f}")
        return parsed_query
    
    def _normalize_query(self, query: str) -> str:
        """Normalize the query string."""
        # Convert to lowercase
        normalized = query.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Expand contractions
        contractions = {
            "don't": "do not",
            "won't": "will not",
            "can't": "cannot",
            "n't": " not",
            "'re": " are",
            "'ve": " have",
            "'ll": " will",
            "'d": " would"
        }
        
        for contraction, expansion in contractions.items():
            normalized = normalized.replace(contraction, expansion)
        
        return normalized
    
    def _extract_intent(self, query: str) -> Tuple[QueryIntent, float]:
        """Extract the intent from the query."""
        best_intent = QueryIntent.UNKNOWN
        best_confidence = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    # Calculate confidence based on pattern specificity and match quality
                    confidence = len(match.group(0)) / len(query)
                    confidence = min(confidence * 2, 1.0)  # Boost confidence but cap at 1.0
                    
                    if confidence > best_confidence:
                        best_intent = intent
                        best_confidence = confidence
        
        # If no specific intent found, try to infer from keywords
        if best_intent == QueryIntent.UNKNOWN:
            if any(word in query for word in ['show', 'list', 'get', 'find']):
                best_intent = QueryIntent.ISSUE_LIST
                best_confidence = 0.3
        
        return best_intent, best_confidence
    
    def _extract_entities(self, query: str, context: Optional[Dict[str, Any]] = None) -> List[ExtractedEntity]:
        """Extract entities from the query."""
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, query, re.IGNORECASE)
                for match in matches:
                    value = match.group(1) if match.groups() else match.group(0)
                    
                    # Normalize entity value
                    normalized_value = self._normalize_entity_value(entity_type, value)
                    
                    if normalized_value:
                        entity = ExtractedEntity(
                            entity_type=entity_type,
                            value=normalized_value,
                            confidence=0.8,  # Base confidence for pattern matches
                            start_pos=match.start(),
                            end_pos=match.end()
                        )
                        entities.append(entity)
        
        # Remove duplicate entities (keep highest confidence)
        entities = self._deduplicate_entities(entities)
        
        return entities
    
    def _normalize_entity_value(self, entity_type: str, value: str) -> Optional[str]:
        """Normalize entity values using Jira vocabulary."""
        value = value.strip().lower()
        
        if entity_type == 'status':
            for canonical, synonyms in self.jira_vocabulary['status_synonyms'].items():
                if value in synonyms:
                    return canonical
        elif entity_type == 'priority':
            for canonical, synonyms in self.jira_vocabulary['priority_synonyms'].items():
                if value in synonyms:
                    return canonical
        elif entity_type == 'issue_type':
            for canonical, synonyms in self.jira_vocabulary['type_synonyms'].items():
                if value in synonyms:
                    return canonical
        elif entity_type == 'project':
            # Project keys are typically uppercase
            return value.upper()
        elif entity_type == 'user':
            # Normalize user names (title case)
            return value.title()
        
        return value
    
    def _deduplicate_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """Remove duplicate entities, keeping the one with highest confidence."""
        unique_entities = {}
        
        for entity in entities:
            key = (entity.entity_type, entity.value)
            if key not in unique_entities or entity.confidence > unique_entities[key].confidence:
                unique_entities[key] = entity
        
        return list(unique_entities.values())
    
    def _extract_filters(self, entities: List[ExtractedEntity], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert extracted entities into filter conditions."""
        filters = {}
        
        for entity in entities:
            if entity.entity_type == 'project':
                filters['project_key'] = entity.value
            elif entity.entity_type == 'user':
                filters['assignee'] = entity.value
            elif entity.entity_type == 'status':
                filters['status'] = entity.value
            elif entity.entity_type == 'issue_type':
                filters['issue_type'] = entity.value
            elif entity.entity_type == 'priority':
                filters['priority'] = entity.value
        
        # Add context-based filters
        if context:
            if 'default_project' in context and 'project_key' not in filters:
                filters['project_key'] = context['default_project']
        
        return filters
    
    def _extract_time_range(self, query: str) -> Optional[Tuple[datetime, datetime]]:
        """Extract time range from the query."""
        now = datetime.now()
        
        # Look for relative time expressions
        relative_patterns = [
            (r"last\s+(\d+)\s+days?", lambda m: (now - timedelta(days=int(m.group(1))), now)),
            (r"last\s+(\d+)\s+weeks?", lambda m: (now - timedelta(weeks=int(m.group(1))), now)),
            (r"last\s+(\d+)\s+months?", lambda m: (now - timedelta(days=int(m.group(1)) * 30), now)),
            (r"this\s+week", lambda m: self._get_week_range(now)),
            (r"this\s+month", lambda m: self._get_month_range(now)),
            (r"this\s+quarter", lambda m: self._get_quarter_range(now)),
            (r"this\s+year", lambda m: self._get_year_range(now))
        ]
        
        for pattern, range_func in relative_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                try:
                    return range_func(match)
                except Exception as e:
                    logger.warning(f"Failed to parse time range: {e}")
                    continue
        
        return None
    
    def _get_week_range(self, date: datetime) -> Tuple[datetime, datetime]:
        """Get the start and end of the current week."""
        start = date - timedelta(days=date.weekday())
        end = start + timedelta(days=6)
        return start.replace(hour=0, minute=0, second=0, microsecond=0), end.replace(hour=23, minute=59, second=59)
    
    def _get_month_range(self, date: datetime) -> Tuple[datetime, datetime]:
        """Get the start and end of the current month."""
        start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if date.month == 12:
            end = start.replace(year=date.year + 1, month=1) - timedelta(days=1)
        else:
            end = start.replace(month=date.month + 1) - timedelta(days=1)
        return start, end.replace(hour=23, minute=59, second=59)
    
    def _get_quarter_range(self, date: datetime) -> Tuple[datetime, datetime]:
        """Get the start and end of the current quarter."""
        quarter = (date.month - 1) // 3 + 1
        start_month = (quarter - 1) * 3 + 1
        start = date.replace(month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if quarter == 4:
            end = start.replace(year=date.year + 1, month=1) - timedelta(days=1)
        else:
            end = start.replace(month=start_month + 3) - timedelta(days=1)
        
        return start, end.replace(hour=23, minute=59, second=59)
    
    def _get_year_range(self, date: datetime) -> Tuple[datetime, datetime]:
        """Get the start and end of the current year."""
        start = date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = date.replace(month=12, day=31, hour=23, minute=59, second=59)
        return start, end
    
    def _determine_aggregation(self, query: str, intent: QueryIntent) -> Optional[str]:
        """Determine the type of aggregation needed."""
        if intent in [QueryIntent.ASSIGNEE_COUNT, QueryIntent.STATUS_DISTRIBUTION]:
            return 'count'
        elif 'average' in query or 'mean' in query:
            return 'average'
        elif 'sum' in query or 'total' in query:
            return 'sum'
        elif 'max' in query or 'maximum' in query:
            return 'max'
        elif 'min' in query or 'minimum' in query:
            return 'min'
        
        return None
    
    def _determine_output_format(self, query: str, intent: QueryIntent) -> str:
        """Determine the desired output format."""
        if 'chart' in query or 'graph' in query:
            return 'chart'
        elif 'table' in query or 'list' in query:
            return 'table'
        elif intent in [QueryIntent.BURNDOWN_CHART, QueryIntent.VELOCITY_REPORT]:
            return 'chart'
        elif intent in [QueryIntent.ASSIGNEE_COUNT, QueryIntent.STATUS_DISTRIBUTION]:
            return 'table'
        
        return 'table'  # Default format
    
    def _calculate_confidence(self, intent_confidence: float, entities: List[ExtractedEntity]) -> float:
        """Calculate overall confidence score for the parsed query."""
        if not entities:
            return intent_confidence * 0.5  # Lower confidence if no entities found
        
        entity_confidence = sum(entity.confidence for entity in entities) / len(entities)
        return (intent_confidence + entity_confidence) / 2

