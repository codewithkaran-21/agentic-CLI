from config.config import Config
from tool.mcp.client import MCPClient, MCPSeverStatus
import asyncio

from tool.register import ToolRegistry

class MCPManager:
    def __init__(self, config : Config):
        self.config = config
        self._clients : dict[str,MCPClient] = {}
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return

        mcp_configs = self.config.mcp_servers

        if not mcp_configs:
            return

        for name , server_config in mcp_configs.items():
            if not server_config.enabled:
                continue

            self._clients[name] = MCPClient(
                name = name,
                config=server_config,
                cwd=self.config.cwd
            )

        connection_tasks = [await asyncio.wait_for(client.connect()) for name , client in self._clients.items()]

        await asyncio.gather(*connection_tasks, return_exceptions=True)
        self._initialized = True
        

    def register_tools(self , registry : ToolRegistry) -> int:
        count = 0 

        for client in self._client.values():
            if client.status != MCPSeverStatus.CONNECTED:
                continue

            for tool_info in client.tools:
                registry.register_mcp_tool()

