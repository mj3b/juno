"""Test Defect Diagnostics Module for JUNO Phase 2.

This module analyzes test results and categorizes failures to assist
with root cause identification.
"""

from dataclasses import dataclass, field
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


@dataclass
class TestCaseResult:
    """Represents a single test case result."""
    name: str
    status: str
    error: str | None = None


@dataclass
class DiagnosticsReport:
    """Aggregated diagnostics for a set of test results."""
    total_tests: int
    passed: int
    failed: int
    failure_rate: float
    failure_categories: Dict[str, int] = field(default_factory=dict)
    example_failures: List[Dict[str, str]] = field(default_factory=list)


class TestDefectDiagnostics:
    """Analyze test results and produce defect diagnostics."""

    def analyze(self, results: List[TestCaseResult]) -> DiagnosticsReport:
        total = len(results)
        passed = len([r for r in results if r.status.upper() == "PASS"])
        failed_cases = [r for r in results if r.status.upper() == "FAIL"]
        failed = len(failed_cases)
        failure_rate = failed / total * 100 if total else 0.0

        categories: Dict[str, int] = {}
        examples: List[Dict[str, str]] = []

        for case in failed_cases:
            if case.error:
                category = case.error.split(":", 1)[0]
            else:
                category = "UnknownError"
            categories[category] = categories.get(category, 0) + 1
            if len(examples) < 5:
                examples.append({"test": case.name, "error": case.error or ""})

        report = DiagnosticsReport(
            total_tests=total,
            passed=passed,
            failed=failed,
            failure_rate=round(failure_rate, 2),
            failure_categories=categories,
            example_failures=examples,
        )

        logger.info(
            "Generated test defect diagnostics: %s failed/%s total",
            failed,
            total,
        )
        return report


if __name__ == "__main__":
    sample = [
        TestCaseResult(name="test_example", status="FAIL", error="AssertionError: expected 1"),
        TestCaseResult(name="test_ok", status="PASS"),
    ]
    diag = TestDefectDiagnostics().analyze(sample)
    print(diag)
