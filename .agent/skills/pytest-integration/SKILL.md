---
name: pytest-integration
description: Creates, organizes, and maintains Python integration tests using pytest, following best practices like test isolation and custom markers. Use this when instructed to write or update integration tests.
---
# SKILL: Python Integration Testing

## Description
You are an expert at writing and maintaining Python integration tests using pytest. Your purpose is to ensure that different components of an application work correctly together by leveraging real dependencies (like databases or APIs) in a controlled manner, while adhering to structural and performance best practices.

## Core Instructions

When activated to perform integration testing, execute this exact workflow:

### Step 1: Environment and Setup
- Ensure the project uses `pytest` as the testing framework (run `uv add --dev pytest` if required, preferring `uv`).
- Integration tests must be placed in a dedicated `tests/integration/` directory to distinguish them from unit tests.
- If they don't exist, create proper `conftest.py` files to manage shared fixtures for setup and teardown.

### Step 2: Test Marking and Execution
- Always tag integration tests with the `@pytest.mark.integration` marker so they can be run selectively.
- Provide instructions or commands to run these tests using `pytest -m integration`.
- When testing the pipeline locally or in CI, unit tests must run before the slower integration tests.

### Step 3: Managing Dependencies and State
- Use appropriate fixture scopes (e.g., `session` scope for a database connection, `function` scope for fresh data per test).
- Isolate each test: Clean up state and start with fresh data for every test run to prevent bleed-over.
- Avoid mocking external systems where possible. Instead, utilize Docker or local instances to test real interactions. Only use `monkeypatch` or mocking for highly specific edge cases or truly uncontrollable external services.

### Step 4: Test Design
- Write descriptive test file and function names (prefixed with `test_` and placed in `test_*.py` files).
- Keep tests focused: Verify a single integration behavior or specific interaction per test.
- Use `@pytest.mark.parametrize` to avoid duplication and efficiently test various input scenarios.
- Write clear assertions that make diagnosing failures easy. Avoid hardcoded values by using generated data or variables.

## Rules & Guardrails
- **DO NOT** mix unit tests and integration tests in the same file or directory.
- **DO NOT** run `pip` manually; always use `uv` for Python package operations.
- **DO NOT** invoke tests manually without `uv run pytest`.
- **DO NOT** mock the core components being integrated; the purpose is to test their real interactions.
- **DO NOT** leave dangling state (e.g., unclosed database connections or residual rows). Always clean up in fixtures.
