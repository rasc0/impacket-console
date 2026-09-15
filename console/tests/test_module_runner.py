import os

from console.modules.base import ModuleRunner
from console.Options import Options


def make_options(**values):
    options = Options()
    for attr, value in values.items():
        setattr(options, attr, value)
    return options


def test_validate_reports_missing_required_option(sample_module_spec):
    runner = ModuleRunner(sample_module_spec)

    errors = runner.validate(make_options())

    assert errors == ["required option not set: target"]


def test_validate_passes_when_required_options_are_set(sample_module_spec):
    runner = ModuleRunner(sample_module_spec)

    errors = runner.validate(make_options(target="CORP/user:pass@dc01"))

    assert errors == []


def test_build_argv_includes_positional_and_value_flags(sample_module_spec):
    runner = ModuleRunner(sample_module_spec)
    options = make_options(target="CORP/user:pass@dc01", dc_ip="10.0.0.1")

    argv = runner.build_argv(options)

    assert argv == ["CORP/user:pass@dc01", "-dc-ip", "10.0.0.1"]


def test_build_argv_omits_unset_optional_flags(sample_module_spec):
    runner = ModuleRunner(sample_module_spec)
    options = make_options(target="CORP/user:pass@dc01")

    argv = runner.build_argv(options)

    assert argv == ["CORP/user:pass@dc01"]


def test_build_argv_emits_boolean_flag_only_when_truthy(sample_module_spec):
    runner = ModuleRunner(sample_module_spec)

    argvTrue = runner.build_argv(make_options(target="t", debug="true"))
    argvFalse = runner.build_argv(make_options(target="t", debug="false"))

    assert "-debug" in argvTrue
    assert "-debug" not in argvFalse


def test_script_path_joins_repo_root_and_module_path(sample_module_spec):
    runner = ModuleRunner(sample_module_spec)

    path = runner.script_path("/repo")

    assert path == os.path.join("/repo", "examples/SampleModule.py")
