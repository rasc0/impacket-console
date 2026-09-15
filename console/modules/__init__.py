"""
Registry mapping a modules.json "name" to the ModuleRunner subclass that
knows how to run it.

To add a module:
  1. Confirm/fix its entry in ../modules.json (rerun generate_modules.py if
     the flags look stale - the "implemented" field survives that).
  2. Add a <module>.py here with a class subclassing base.ModuleRunner,
     overriding validate()/build_argv() only if the generic behaviour in
     base.py isn't enough for this module.
  3. Register the class in MODULE_RUNNERS below, keyed by the exact "name"
     used in modules.json (e.g. "GetUserSPNs.py").
  4. Flip "implemented": true for that module in modules.json - that's what
     makes it show up in `list`/`search` and lets `run` execute it.

See base.py for the full contract, and get_user_spns.py for the minimal
(no-override) example.
"""
from .base import ModuleRunner
from .get_user_spns import GetUserSPNsModule

MODULE_RUNNERS = {
    "GetUserSPNs.py": GetUserSPNsModule,
}


def get_runner(moduleSpec):
    """Return a ModuleRunner instance for the given modules.json entry.

    Falls back to the generic ModuleRunner for any implemented module that
    doesn't need a bespoke subclass - a module only needs an entry in
    MODULE_RUNNERS once base.py's generic argv-building genuinely isn't
    enough for it.
    """
    runnerClass = MODULE_RUNNERS.get(moduleSpec["name"], ModuleRunner)
    return runnerClass(moduleSpec)
