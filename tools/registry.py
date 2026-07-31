from core.plugin_manager import plugin_manager
TOOLS = {}


def register(tool):
    TOOLS[tool.name] = tool


def get(name: str):
    """Retrieve a tool instance via the PluginManager."""
    return plugin_manager.get_tool(name)


def list_tools():
    return list(TOOLS.keys())