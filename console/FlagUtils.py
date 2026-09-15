"""
Shared flag <-> Options-attribute name mapping.

Used by both generate_modules.py (which builds Options.py's attribute
list from impacket's example scripts) and console.py at runtime (do_set /
do_options need to map a module's "-dc-ip" style flag to the matching
Options attribute). Keeping this in one place guarantees the generator
and the console always agree on the mapping. Generated with the help of AI
"""


def flag_to_attr(flag):
    """Normalise a CLI flag (e.g. "-dc-ip", "--target", "target", "-6")
    into a valid Python attribute name (e.g. "dc_ip", "target", "flag_6")."""
    name = flag.lstrip("-")
    name = name.replace("-", "_")
    if name[:1].isdigit():
        name = "flag_" + name
    return name
