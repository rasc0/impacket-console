#!/usr/bin/env python3
"""
Regenerates console/modules.json and the generated attribute block in
console/Options.py by statically scanning impacket's examples/*.py scripts
for their argparse definitions.

Run this after pulling upstream impacket changes (new scripts, renamed or
added flags, new modules) to keep the console's module catalog in sync:

    python console/generate_modules.py

It never imports or executes the example scripts - many have import-time
side effects or extra dependencies - it parses their source with `ast`
instead, so it is safe to run against any checkout.

This file was generated with AI
"""
import ast
import json
import os
import re
import sys

from FlagUtils import flag_to_attr

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
EXAMPLES_DIR = os.path.join(REPO_ROOT, "examples")
MODULES_JSON = os.path.join(SCRIPT_DIR, "modules.json")
OPTIONS_PY = os.path.join(SCRIPT_DIR, "Options.py")

# Calls made on an already-known parser-like variable that themselves
# produce another parser-like object (subparsers, groups, etc).
PARSER_FACTORY_ATTRS = {"add_subparsers", "add_parser", "add_argument_group", "add_mutually_exclusive_group"}

# argparse `action` values that don't consume a value token (flag is either
# present or absent) - everything else ("store", "append", "extend", or no
# action kwarg at all) is treated as taking a value.
NON_VALUE_ACTIONS = {"store_true", "store_false", "store_const", "count", "help", "version"}

# Keys on an existing modules.json entry that are hand-curated and must
# survive regeneration rather than being reset to a default every run.
CURATED_KEYS = ("implemented",)

GENERATED_START = "        # === GENERATED OPTIONS START ==="
GENERATED_END = "        # === GENERATED OPTIONS END ==="


def _const_str(node):
    """Return the string value of a Constant node, or None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _call_target(call):
    """For a Call node, return (owner_name_or_None, attr_or_func_name)."""
    func = call.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return func.value.id, func.attr
    if isinstance(func, ast.Name):
        return None, func.id
    return None, None


def extract_module_info(source, filename):
    """Statically parse one example script's source.

    Returns (description, required_flags, optional_flags) or None if the
    script doesn't appear to define an argparse parser at all.
    """
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError:
        return None

    parser_vars = set()
    description = None

    assigns = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
        and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
    ]

    # Several passes: a parser-factory call (e.g. subparsers.add_parser(...))
    # can only be recognised once its owner variable is already known.
    for _ in range(4):
        changed = False
        for node in assigns:
            target_name = node.targets[0].id
            owner, attr = _call_target(node.value)

            is_argparser_call = attr == "ArgumentParser"
            is_parser_factory = attr in PARSER_FACTORY_ATTRS and owner in parser_vars

            if is_argparser_call:
                if target_name not in parser_vars:
                    parser_vars.add(target_name)
                    changed = True
                if description is None:
                    for kw in node.value.keywords:
                        if kw.arg == "description":
                            description = _const_str(kw.value)
            elif is_parser_factory and target_name not in parser_vars:
                parser_vars.add(target_name)
                changed = True
        if not changed:
            break

    if not parser_vars:
        return None

    required = {}
    optional = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        owner, attr = _call_target(node)
        if attr != "add_argument" or owner not in parser_vars:
            continue

        flag = next((s for arg in node.args if (s := _const_str(arg))), None)
        if not flag:
            continue

        help_text = None
        explicit_required = False
        action = None
        for kw in node.keywords:
            if kw.arg == "help":
                help_text = _const_str(kw.value)
            elif kw.arg == "required" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                explicit_required = True
            elif kw.arg == "action":
                action = _const_str(kw.value)

        is_positional = not flag.startswith("-")
        is_required = explicit_required or is_positional
        # Positional args are always a bare value; only a "-flag" can be a
        # value-less boolean switch (action=store_true/store_false/etc).
        takes_value = is_positional or action not in NON_VALUE_ACTIONS

        entry = {"flag": flag}
        if help_text:
            entry["help"] = help_text
        if not takes_value:
            entry["takes_value"] = False

        bucket = required if is_required else optional
        bucket.setdefault(flag, entry)  # first definition wins

    if description is None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr):
                s = _const_str(node.value)
                if s:
                    description = s.strip().splitlines()[0].strip()
                    break

    return description or "", list(required.values()), list(optional.values())


def load_existing_modules():
    """Return {name: entry} for the modules.json already on disk, so
    hand-curated fields (see CURATED_KEYS) survive regeneration."""
    if not os.path.exists(MODULES_JSON):
        return {}
    with open(MODULES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {m["name"]: m for m in data.get("modules", [])}


def build_modules():
    modules = []
    filenames = sorted(f for f in os.listdir(EXAMPLES_DIR) if f.endswith(".py"))
    existing = load_existing_modules()

    for i, filename in enumerate(filenames, start=1):
        path = os.path.join(EXAMPLES_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        info = extract_module_info(source, filename)
        if info is None:
            print(f"skip (no argparse found): {filename}", file=sys.stderr)
            continue

        description, required, optional = info
        old = existing.get(filename, {})
        module = {
            "id": str(i),
            "name": filename,
            "description": description,
            "path": os.path.relpath(path, REPO_ROOT),
        }
        for key in CURATED_KEYS:
            module[key] = old.get(key, False)
        module["required flags"] = required
        module["optional flags"] = optional
        modules.append(module)

    return modules


def write_modules_json(modules):
    with open(MODULES_JSON, "w", encoding="utf-8") as f:
        json.dump({"modules": modules}, f, indent=2)
        f.write("\n")


def collect_attr_names(modules):
    names = set()
    for module in modules:
        for entry in module["required flags"] + module["optional flags"]:
            names.add(flag_to_attr(entry["flag"]))
    return sorted(names)


def write_options_py(attr_names):
    with open(OPTIONS_PY, "r", encoding="utf-8") as f:
        content = f.read()

    if GENERATED_START not in content or GENERATED_END not in content:
        raise RuntimeError(
            f"{OPTIONS_PY} is missing the GENERATED OPTIONS markers; "
            "cannot regenerate without clobbering hand-written code."
        )

    body = "\n".join(f"        self.{name} = None" for name in attr_names) or "        pass"
    new_block = f"{GENERATED_START}\n{body}\n{GENERATED_END}"
    pattern = re.compile(re.escape(GENERATED_START) + r".*?" + re.escape(GENERATED_END), re.DOTALL)
    content, count = pattern.subn(new_block, content, count=1)
    if count != 1:
        raise RuntimeError(f"Failed to substitute generated block in {OPTIONS_PY}")

    with open(OPTIONS_PY, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    modules = build_modules()
    write_modules_json(modules)
    attr_names = collect_attr_names(modules)
    write_options_py(attr_names)
    print(f"Wrote {len(modules)} modules to {os.path.relpath(MODULES_JSON, REPO_ROOT)}")
    print(f"Wrote {len(attr_names)} option attributes to {os.path.relpath(OPTIONS_PY, REPO_ROOT)}")


if __name__ == "__main__":
    main()
