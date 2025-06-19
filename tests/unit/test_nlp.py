import os
import sys

base = os.path.join(os.path.dirname(__file__), '../../juno-agent')
sys.path.insert(0, os.path.join(base, 'src'))
sys.path.insert(0, base)

from nlp_processor import JiraNLUProcessor


def test_nlp_intent_detection():
    processor = JiraNLUProcessor()
    queries = [
        ('How many tickets are assigned to John Doe?', 'assignee_count'),
        ('Show velocity report for last 3 sprints', 'velocity_report'),
        ('Give me a project summary for DEMO', 'project_summary'),
    ]
    for q, expected in queries:
        parsed = processor.process_query(q)
        assert parsed.intent.value == expected
        assert parsed.confidence >= 0.3


def test_entity_extraction():
    processor = JiraNLUProcessor()
    parsed = processor.process_query(
        'Show tickets for project DEMO assigned to John Smith'
    )
    types = {e.entity_type for e in parsed.entities}
    assert {'project', 'user'} <= types


def test_time_range_extraction():
    processor = JiraNLUProcessor()
    parsed = processor.process_query('List issues created this month')
    assert parsed.time_range is not None
