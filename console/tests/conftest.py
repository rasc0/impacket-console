"""ADAConsole unit/functional testing"""
""" Put reusable fixtures here so that all tests can use them"""

import pytest



""" TABLE TEST FIXTURES"""

@pytest.fixture
def single_module():
    """A list containing exactly one row."""
    return [
        {"id": "1", "name": "One", "description": "A single row"},
    ]


@pytest.fixture
def multiple_modules():
    """A list of several rows"""
    return [
        {"id": "1", "name": "One", "description": "First Row"},
        {"id": "2", "name": "Two", "description": "Second Row"},
        {"id": "3", "name": "Three", "description": "Third Row"},
    ]


@pytest.fixture
def empty_modules():
    """An empty list of modules."""
    return []


@pytest.fixture
def module_missing_key():
    """A row missing the required 'description' key."""
    return [
        {"id": "1", "name": "First Row"},
    ]


@pytest.fixture
def module_with_non_string_values():
    """A row whose values are not strings (e.g. int id)."""
    return [
        {"id": 1, "name": "Row", "description": "Row with integer id"},
    ]


""" MODULE RUNNER / MODULES.JSON-SHAPED FIXTURES"""

@pytest.fixture
def sample_module_spec():
    """A minimal modules.json-shaped entry exercising every flag kind a
    ModuleRunner has to handle: a required positional, an optional
    value-taking flag, and an optional boolean (no-value) flag."""
    return {
        "id": "1",
        "name": "SampleModule.py",
        "description": "Sample module for tests",
        "path": "examples/SampleModule.py",
        "implemented": True,
        "required flags": [
            {"flag": "target", "help": "the target"},
        ],
        "optional flags": [
            {"flag": "-dc-ip", "help": "DC IP address"},
            {"flag": "-debug", "help": "debug output", "takes_value": False},
        ],
    }
