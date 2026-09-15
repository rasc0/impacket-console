import pytest

from console import SearchModules


@pytest.fixture
def named_modules():
    """Modules with realistic ".py"-suffixed names, as in modules.json. Created with the help of AI"""
    return [
        {"id": "1", "name": "One.py", "description": "First Row"},
        {"id": "2", "name": "Two.py", "description": "Second Row"},
        {"id": "3", "name": "Three.py", "description": "Third Row"},
    ]


def test_search_module_matches_name_or_description(multiple_modules):
    results, count = SearchModules.searchModule(multiple_modules, "second")

    assert count == 1
    assert results[0]["name"] == "Two"


def test_search_module_id_finds_module_past_the_first(multiple_modules):
    # Regression: searchModuleId used to return None as soon as the first
    # module in the list didn't match, instead of continuing the search.
    assert SearchModules.searchModuleId(multiple_modules, "3")["name"] == "Three"


def test_search_module_id_accepts_int_or_str(multiple_modules):
    # Regression: comparing an int id against the JSON's string ids never matched.
    assert SearchModules.searchModuleId(multiple_modules, 2)["name"] == "Two"
    assert SearchModules.searchModuleId(multiple_modules, "2")["name"] == "Two"


def test_search_module_id_returns_none_when_not_found(multiple_modules):
    assert SearchModules.searchModuleId(multiple_modules, "99") is None


def test_search_module_name_matches_case_insensitively_with_or_without_py(named_modules):
    assert SearchModules.searchModuleName(named_modules, "one")["id"] == "1"
    assert SearchModules.searchModuleName(named_modules, "One.py")["id"] == "1"


def test_search_module_name_returns_none_when_not_found(named_modules):
    assert SearchModules.searchModuleName(named_modules, "nonexistent") is None
