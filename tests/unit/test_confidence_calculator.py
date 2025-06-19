import os
import sys
import pytest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from juno.core.reasoning.reasoning_engine import (
    ConfidenceCalculator,
    DataSource,
    ReasoningStep,
    ConfidenceLevel,
)


def make_ds(quality=1.0, reliability=1.0, age_hours=0):
    return DataSource(
        source_type="test",
        source_id=str(age_hours),
        data_quality=quality,
        last_updated=datetime.now() - timedelta(hours=age_hours),
        reliability_score=reliability,
    )


def make_step(conf=0.9):
    return ReasoningStep(
        step_id="s",
        description="test",
        input_data={},
        process="none",
        output_data={},
        confidence=conf,
        timestamp=datetime.now(),
    )


def test_calculate_overall_confidence_high():
    data_sources = [make_ds(0.95, 0.9, 1), make_ds(0.9, 0.85, 5)]
    steps = [make_step(0.9) for _ in range(4)]

    score, level = ConfidenceCalculator.calculate_overall_confidence(
        data_sources, steps, alternatives_count=2
    )

    assert score > 0.7
    assert level in (ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH)


def test_calculate_overall_confidence_no_data():
    score, level = ConfidenceCalculator.calculate_overall_confidence([], [])

    assert score == 0.0
    assert level == ConfidenceLevel.VERY_LOW
