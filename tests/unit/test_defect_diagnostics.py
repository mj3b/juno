"""Unit tests for TestDefectDiagnostics."""
import unittest
import sys

sys.path.append('juno-agent/src/phase2')

from defect_diagnostics import TestDefectDiagnostics, TestCaseResult


class TestDiagnosticsModule(unittest.TestCase):
    def test_basic_analysis(self):
        diagnostics = TestDefectDiagnostics()
        sample = [
            TestCaseResult(name="a", status="PASS"),
            TestCaseResult(name="b", status="FAIL", error="AssertionError: boom"),
            TestCaseResult(name="c", status="FAIL", error="TimeoutError: slow"),
        ]
        report = diagnostics.analyze(sample)
        self.assertEqual(report.passed, 1)
        self.assertEqual(report.failed, 2)
        self.assertAlmostEqual(report.failure_rate, 66.67, places=1)
        self.assertIn("AssertionError", report.failure_categories)
        self.assertIn("TimeoutError", report.failure_categories)


if __name__ == "__main__":
    unittest.main()
