"""
Runner for GetUserSPNs.py (kerberoasting). The generic ModuleRunner
already handles this module fully - target is the one positional/required
flag, everything else is an optional "-flag [value]" - so there's nothing
to override. Kept as its own class (rather than just registering the base
class directly) so it's the template to copy for the next module: give it
a bespoke method only when the generic behaviour in base.py isn't enough.
"""
from .base import ModuleRunner


class GetUserSPNsModule(ModuleRunner):
    pass
