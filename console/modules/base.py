"""
Base class for a module "runner" - the piece of code that knows how to turn
a selected module's Options into an actual `python examples/<Module>.py ...`
invocation.

The default implementation here is entirely generic: it builds argv purely
from the module's entry in modules.json (required/optional flags, whether
each flag takes a value) plus whatever the user has `set`. That's enough to
run most impacket example scripts unmodified - see get_user_spns.py for the
minimal case, which doesn't need to override anything.

Override validate()/build_argv() (or pre_run()/post_run()) in a subclass
only when a module needs something the generic path can't do, e.g.:
  - cross-checking option combinations (see modules.json's original
    dpapi.py flags for an example where required-ness is action-dependent)
  - prompting for/transforming a value before launch
  - post-processing the subprocess output
  - anything that isn't "build a flat argv list and exec the script"
"""
import os

try:
    from FlagUtils import flag_to_attr
except ImportError:  # imported as console.modules.base (e.g. under pytest from repo root)
    from console.FlagUtils import flag_to_attr


class ModuleRunner:
    def __init__(self, moduleSpec):
        self.moduleSpec = moduleSpec

    def validate(self, options):
        """Return a list of human-readable error strings; empty = OK to run."""
        errors = []
        for entry in self.moduleSpec["required flags"]:
            attr = flag_to_attr(entry["flag"])
            value = getattr(options, attr, None)
            if value is None or value == "":
                errors.append("required option not set: {}".format(entry["flag"]))
        return errors

    def build_argv(self, options):
        """Build the argv list to pass to the script (after its path)."""
        argv = []
        for entry in self.moduleSpec["required flags"]:
            argv.extend(self._entry_argv(entry, options))
        for entry in self.moduleSpec["optional flags"]:
            argv.extend(self._entry_argv(entry, options))
        return argv

    def _entry_argv(self, entry, options):
        flag = entry["flag"]
        attr = flag_to_attr(flag)
        value = getattr(options, attr, None)

        if value is None or value == "":
            return []

        is_positional = not flag.startswith("-")
        if is_positional:
            return [value]

        takes_value = entry.get("takes_value", True)
        if not takes_value:
            return [flag] if str(value).strip().lower() in ("1", "true", "yes", "on") else []

        return [flag, value]

    def script_path(self, repoRoot):
        return os.path.join(repoRoot, self.moduleSpec["path"])
