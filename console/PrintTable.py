
from rich.table import Table

try:
    import FlagUtils
except ImportError:  # imported as console.PrintTable (e.g. under pytest from repo root)
    from console import FlagUtils

# Create a nice table from selected modules
def createTable(modules):

    if modules is None:
        return None

    # Initialise table
    table = Table(title="Module List", show_header=True, header_style='bold blue', show_lines=True)

    table.add_column("#")
    table.add_column("Module Name")
    table.add_column("Module Description")

    for module in modules:
        table.add_row(module["id"], module["name"], module["description"])

    return table

# Create a table showing a module's required/optional flags and their
# currently-set values on the given Options instance
def createOptionsTable(module, options):

    if module is None:
        return None

    table = Table(title=f"Options: {module['name']}", show_header=True, header_style='bold blue', show_lines=True)

    table.add_column("Name")
    table.add_column("Required")
    table.add_column("Current Value")
    table.add_column("Description")

    for isRequired, flags in ((True, module["required flags"]), (False, module["optional flags"])):
        for entry in flags:
            attr = FlagUtils.flag_to_attr(entry["flag"])
            value = getattr(options, attr, None) if options is not None else None
            table.add_row(
                entry["flag"],
                "yes" if isRequired else "no",
                str(value) if value is not None else "",
                entry.get("help", ""),
            )

    return table
