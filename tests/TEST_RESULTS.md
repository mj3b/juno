# JUNO Test Results

## Test Execution Summary

* **Date:** June 19, 2025
* **Environment:** Local development container
* **Total Tests Collected:** 5
* **Tests Executed:** 0 (collection error)
* **Tests Skipped:** 9
* **Import Errors:** 1
* **Success Rate:** 0%

Tests could not run because required packages like `requests` are not installed.
Most test modules are skipped when dependencies are missing. See below for the
pytest output.

```
$ pytest -q
ERROR tests/unit/test_jira_integration.py
9 skipped, 1 error in 0.19s
```
