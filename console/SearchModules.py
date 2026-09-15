# Case-insensitive search for specific modules
def searchModule(modules, searchString):

    searchFields = ["name", "description"]

    if isinstance(searchString, str):
        terms = searchString.split()
    else:
        return "No modules found"

    terms =[term.lower() for term in terms]

    results = []
    for module in modules:
        haystack = " ".join(str(module[field]).lower() for field in searchFields)
        if all(term in haystack for term in terms):
            results.append(module)

    return results, len(results)

# Search for module based on id
def searchModuleId(modules, searchId):

    searchId = str(searchId)

    for module in modules:
        if module["id"] == searchId:
            return module

    return None

# Exact (case-insensitive) match on module name, with or without the ".py" suffix
def searchModuleName(modules, name):

    name = name.lower()
    if not name.endswith(".py"):
        name += ".py"

    for module in modules:
        if module["name"].lower() == name:
            return module

    return None