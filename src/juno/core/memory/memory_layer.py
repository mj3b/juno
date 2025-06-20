"""
JUNO Phase 2: Memory Layer Architecture
Provides persistent memory and learning capabilities for agentic AI operations.
"""

import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of memory stored in the system."""
    EPISODIC = "episodic"      # Specific events and interactions
    SEMANTIC = "semantic"      # Learned patterns and relationships
    PROCEDURAL = "procedural"  # Workflow processes and decision trees
    WORKING = "working"        # Active context and ongoing tasks


@dataclass
class MemoryEntry:
    """Represents a single memory entry in the system."""
    id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    context: Dict[str, Any]
    confidence: float
    timestamp: datetime
    expires_at: Optional[datetime] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class MemoryLayer:
    """
    Core memory layer for JUNO Phase 2 agentic capabilities.
    Provides persistent storage and retrieval of contextual information.
    """
    
    def __init__(self, db_path: str = "juno_memory.db"):
        self.db_path = db_path
        self._init_database()

    def initialize(self) -> None:
        """Backward compatible initialization hook."""
        self._init_database()

    def close(self) -> None:
        """Backward compatible cleanup hook."""
        # Database connections are opened and closed per operation so this is
        # effectively a no-op. It exists for API compatibility with older tests.
        return None

    @staticmethod
    def _json_serializer(obj: Any) -> Any:
        """Serialize objects that are not JSON serializable by default."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)
        
    def _init_database(self):
        """Initialize the memory database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_entries (
                id TEXT PRIMARY KEY,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                context TEXT NOT NULL,
                confidence REAL NOT NULL,
                timestamp TEXT NOT NULL,
                expires_at TEXT,
                tags TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_entries(memory_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_entries(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tags ON memory_entries(tags)
        """)
        
        conn.commit()
        conn.close()
        
    def store_memory(self, memory: MemoryEntry) -> bool:
        """Store a memory entry in the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO memory_entries 
                (id, memory_type, content, context, confidence, timestamp, expires_at, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id,
                memory.memory_type.value,
                json.dumps(memory.content, default=self._json_serializer),
                json.dumps(memory.context, default=self._json_serializer),
                memory.confidence,
                memory.timestamp.isoformat(),
                memory.expires_at.isoformat() if memory.expires_at else None,
                json.dumps(memory.tags, default=self._json_serializer)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Stored memory entry: {memory.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return False
    
    def retrieve_memories(
        self, 
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        min_confidence: float = 0.0
    ) -> List[MemoryEntry]:
        """Retrieve memory entries based on criteria."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT id, memory_type, content, context, confidence, timestamp, expires_at, tags
                FROM memory_entries
                WHERE confidence >= ?
                AND (expires_at IS NULL OR expires_at > ?)
            """
            params = [min_confidence, datetime.now().isoformat()]
            
            if memory_type:
                query += " AND memory_type = ?"
                params.append(memory_type.value)
                
            if tags:
                # Simple tag matching - can be enhanced for more complex queries
                tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])
                query += f" AND ({tag_conditions})"
                params.extend([f"%{tag}%" for tag in tags])
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            memories = []
            for row in rows:
                memory = MemoryEntry(
                    id=row[0],
                    memory_type=MemoryType(row[1]),
                    content=json.loads(row[2]),
                    context=json.loads(row[3]),
                    confidence=row[4],
                    timestamp=datetime.fromisoformat(row[5]),
                    expires_at=datetime.fromisoformat(row[6]) if row[6] else None,
                    tags=json.loads(row[7]) if row[7] else []
                )
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return []
    
    def update_confidence(self, memory_id: str, new_confidence: float) -> bool:
        """Update the confidence score of a memory entry."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE memory_entries 
                SET confidence = ?
                WHERE id = ?
            """, (new_confidence, memory_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated confidence for memory {memory_id}: {new_confidence}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update confidence: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """Remove expired memory entries."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM memory_entries
                WHERE expires_at IS NOT NULL AND expires_at <= ?
            """, (datetime.now().isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} expired memory entries")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired memories: {e}")
            return 0


class TeamMemoryManager:
    """
    Manages team-specific memory and learning patterns.
    Tracks team preferences, patterns, and workflow optimizations.
    """
    
    def __init__(self, memory_layer: MemoryLayer):
        self.memory_layer = memory_layer
    
    def store_team_preference(
        self, 
        team_id: str, 
        preference_type: str, 
        preference_data: Dict[str, Any],
        confidence: float = 0.8
    ) -> str:
        """Store a team preference or pattern."""
        memory_id = self._generate_memory_id(f"team_{team_id}_{preference_type}")
        
        memory = MemoryEntry(
            id=memory_id,
            memory_type=MemoryType.SEMANTIC,
            content={
                "preference_type": preference_type,
                "data": preference_data,
                "team_id": team_id
            },
            context={
                "team_id": team_id,
                "source": "team_preference"
            },
            confidence=confidence,
            timestamp=datetime.now(),
            tags=["team", team_id, preference_type]
        )
        
        self.memory_layer.store_memory(memory)
        return memory_id
    
    def get_team_preferences(self, team_id: str) -> List[Dict[str, Any]]:
        """Retrieve all preferences for a specific team."""
        memories = self.memory_layer.retrieve_memories(
            memory_type=MemoryType.SEMANTIC,
            tags=[team_id, "team"]
        )
        
        preferences = []
        for memory in memories:
            if memory.context.get("team_id") == team_id:
                preferences.append({
                    "type": memory.content.get("preference_type"),
                    "data": memory.content.get("data"),
                    "confidence": memory.confidence,
                    "timestamp": memory.timestamp
                })
        
        return preferences
    
    def store_workflow_pattern(
        self,
        team_id: str,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        success_rate: float
    ) -> str:
        """Store a successful workflow pattern."""
        memory_id = self._generate_memory_id(f"workflow_{team_id}_{pattern_type}")
        
        memory = MemoryEntry(
            id=memory_id,
            memory_type=MemoryType.PROCEDURAL,
            content={
                "pattern_type": pattern_type,
                "pattern_data": pattern_data,
                "success_rate": success_rate,
                "team_id": team_id
            },
            context={
                "team_id": team_id,
                "source": "workflow_pattern"
            },
            confidence=success_rate,
            timestamp=datetime.now(),
            tags=["workflow", team_id, pattern_type]
        )
        
        self.memory_layer.store_memory(memory)
        return memory_id
    
    def get_workflow_patterns(self, team_id: str, pattern_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve workflow patterns for a team."""
        tags = ["workflow", team_id]
        if pattern_type:
            tags.append(pattern_type)
            
        memories = self.memory_layer.retrieve_memories(
            memory_type=MemoryType.PROCEDURAL,
            tags=tags
        )
        
        patterns = []
        for memory in memories:
            if memory.context.get("team_id") == team_id:
                patterns.append({
                    "type": memory.content.get("pattern_type"),
                    "data": memory.content.get("pattern_data"),
                    "success_rate": memory.content.get("success_rate"),
                    "confidence": memory.confidence,
                    "timestamp": memory.timestamp
                })
        
        return patterns
    
    def _generate_memory_id(self, base_string: str) -> str:
        """Generate a unique memory ID."""
        timestamp = datetime.now().isoformat()
        combined = f"{base_string}_{timestamp}"
        return hashlib.md5(combined.encode()).hexdigest()


class SessionMemoryManager:
    """
    Manages session-specific memory and context.
    Handles working memory for active conversations and tasks.
    """
    
    def __init__(self, memory_layer: MemoryLayer):
        self.memory_layer = memory_layer
        self.active_sessions = {}
    
    def start_session(self, session_id: str, user_id: str, team_id: str) -> Dict[str, Any]:
        """Start a new session and initialize working memory."""
        session_context = {
            "session_id": session_id,
            "user_id": user_id,
            "team_id": team_id,
            "started_at": datetime.now(),
            "conversation_history": [],
            "active_tasks": [],
            "context_variables": {}
        }
        
        self.active_sessions[session_id] = session_context
        
        # Store session start in memory
        memory_id = self._generate_memory_id(f"session_start_{session_id}")
        memory = MemoryEntry(
            id=memory_id,
            memory_type=MemoryType.EPISODIC,
            content={
                "event": "session_start",
                "session_id": session_id,
                "user_id": user_id,
                "team_id": team_id
            },
            context=session_context,
            confidence=1.0,
            timestamp=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
            tags=["session", session_id, user_id, team_id]
        )
        
        self.memory_layer.store_memory(memory)
        return session_context
    
    def add_conversation_turn(
        self, 
        session_id: str, 
        user_input: str, 
        ai_response: str,
        reasoning: Dict[str, Any]
    ) -> bool:
        """Add a conversation turn to session memory."""
        if session_id not in self.active_sessions:
            return False
        
        turn = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response": ai_response,
            "reasoning": reasoning
        }
        
        self.active_sessions[session_id]["conversation_history"].append(turn)
        
        # Store conversation turn in persistent memory
        memory_id = self._generate_memory_id(f"conversation_{session_id}_{len(self.active_sessions[session_id]['conversation_history'])}")
        memory = MemoryEntry(
            id=memory_id,
            memory_type=MemoryType.EPISODIC,
            content={
                "event": "conversation_turn",
                "turn": turn,
                "session_id": session_id
            },
            context=self.active_sessions[session_id],
            confidence=0.9,
            timestamp=datetime.now(),
            expires_at=datetime.now() + timedelta(days=30),
            tags=["conversation", session_id]
        )
        
        self.memory_layer.store_memory(memory)
        return True
    
    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the current session context."""
        return self.active_sessions.get(session_id)
    
    def end_session(self, session_id: str) -> bool:
        """End a session and store final context."""
        if session_id not in self.active_sessions:
            return False
        
        session_context = self.active_sessions[session_id]
        session_context["ended_at"] = datetime.now()
        
        # Store session end in memory
        memory_id = self._generate_memory_id(f"session_end_{session_id}")
        memory = MemoryEntry(
            id=memory_id,
            memory_type=MemoryType.EPISODIC,
            content={
                "event": "session_end",
                "session_id": session_id,
                "duration": (session_context["ended_at"] - session_context["started_at"]).total_seconds(),
                "conversation_turns": len(session_context["conversation_history"])
            },
            context=session_context,
            confidence=1.0,
            timestamp=datetime.now(),
            expires_at=datetime.now() + timedelta(days=90),
            tags=["session", session_id]
        )
        
        self.memory_layer.store_memory(memory)
        del self.active_sessions[session_id]
        return True
    
    def _generate_memory_id(self, base_string: str) -> str:
        """Generate a unique memory ID."""
        timestamp = datetime.now().isoformat()
        combined = f"{base_string}_{timestamp}"
        return hashlib.md5(combined.encode()).hexdigest()


# Example usage and testing
if __name__ == "__main__":
    # Initialize memory layer
    memory_layer = MemoryLayer()
    team_memory = TeamMemoryManager(memory_layer)
    session_memory = SessionMemoryManager(memory_layer)
    
    # Example: Store team preference
    team_memory.store_team_preference(
        team_id="team_alpha",
        preference_type="sprint_length",
        preference_data={"days": 14, "preferred_start_day": "monday"},
        confidence=0.9
    )
    
    # Example: Start session and add conversation
    session_context = session_memory.start_session(
        session_id="sess_123",
        user_id="john_doe",
        team_id="team_alpha"
    )
    
    session_memory.add_conversation_turn(
        session_id="sess_123",
        user_input="How's our sprint velocity?",
        ai_response="Your team's velocity is trending upward...",
        reasoning={"confidence": 0.85, "data_sources": ["jira_api"]}
    )
    
    print("Memory layer implementation complete!")

