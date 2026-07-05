TOOLS = {}


def register(tool):
    TOOLS[tool.name] = tool


def get(name):
    return TOOLS[name]


def list_tools():
    return list(TOOLS.keys())