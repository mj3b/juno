import tempfile
from datetime import datetime, timedelta

# Import JUNO Phase 2 components
from juno.core.memory.memory_layer import MemoryLayer, MemoryType, MemoryEntry


def create_memory_layer(tmp_path):
    return MemoryLayer(db_path=str(tmp_path / "memory.db"))


def test_store_and_retrieve_memory(tmp_path):
    layer = create_memory_layer(tmp_path)
    entry = MemoryEntry(
        id="entry1",
        memory_type=MemoryType.EPISODIC,
        content={"event": "unit_test"},
        context={"user": "tester"},
        confidence=0.9,
        timestamp=datetime.now(),
        tags=["test"],
    )
    assert layer.store_memory(entry)
    memories = layer.retrieve_memories(memory_type=MemoryType.EPISODIC)
    assert any(m.id == "entry1" for m in memories)


def test_update_confidence(tmp_path):
    layer = create_memory_layer(tmp_path)
    entry = MemoryEntry(
        id="conf",
        memory_type=MemoryType.EPISODIC,
        content={},
        context={},
        confidence=0.5,
        timestamp=datetime.now(),
    )
    layer.store_memory(entry)
    assert layer.update_confidence("conf", 0.8)
    memories = layer.retrieve_memories(memory_type=MemoryType.EPISODIC)
    assert memories[0].confidence == 0.8


def test_cleanup_expired(tmp_path):
    layer = create_memory_layer(tmp_path)
    expired = MemoryEntry(
        id="old",
        memory_type=MemoryType.EPISODIC,
        content={},
        context={},
        confidence=1.0,
        timestamp=datetime.now() - timedelta(days=2),
        expires_at=datetime.now() - timedelta(days=1),
    )
    valid = MemoryEntry(
        id="new",
        memory_type=MemoryType.EPISODIC,
        content={},
        context={},
        confidence=1.0,
        timestamp=datetime.now(),
        expires_at=datetime.now() + timedelta(days=1),
    )
    layer.store_memory(expired)
    layer.store_memory(valid)
    deleted = layer.cleanup_expired()
    assert deleted >= 1
    remaining = layer.retrieve_memories()
    assert any(m.id == "new" for m in remaining)
