import importlib
import os
import sys
from typing import Dict, Type, Any, List
from core.logger import logger

class PluginManager:
    def __init__(self):
        self.tools: Dict[str, Type[Any]] = {}
        self.agents: Dict[str, Type[Any]] = {}
        self.health_status: Dict[str, bool] = {}

    def register_tool(self, name: str, tool_class: Type[Any]):
        self.tools[name] = tool_class
        self.health_status[name] = True
        logger.log(f"Plugin Registered: Tool [{name}]")

    def register_agent(self, name: str, agent_class: Type[Any]):
        self.agents[name] = agent_class
        logger.log(f"Plugin Registered: Agent [{name}]")

    def get_tool(self, name: str) -> Any:
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found in plugin registry.")
        if not self.health_status.get(name, False):
            logger.log(f"Warning: Tool '{name}' is marked as unhealthy.")
        try:
            return self.tools[name]()
        except Exception as e:
            logger.log(f"Fault Isolation: Failed to instantiate tool '{name}': {e}")
            raise

    def discover_plugins(self, directories: List[str]):
        for directory in directories:
            if not os.path.exists(directory):
                continue
            for filename in os.listdir(directory):
                if filename.endswith("_tool.py") and not filename.startswith("_"):
                    module_name = filename[:-3]
                    try:
                        # Dynamic import to trigger registration decorators
                        importlib.import_module(f"{directory.replace('/', '.')}.{module_name}")
                    except Exception as e:
                        logger.log(f"Plugin Discovery Error in {filename}: {e}")

    def run_health_check(self):
        logger.log("Running plugin health checks...")
        for name, cls in self.tools.items():
            try:
                instance = cls()
                # Optional: Add a 'health_check' method to your Base Tool class
                if hasattr(instance, 'health_check'):
                    instance.health_check()
                self.health_status[name] = True
            except Exception as e:
                logger.log(f"Health Check Failed for Tool '{name}': {e}")
                self.health_status[name] = False

plugin_manager = PluginManager()