from dataclasses import dataclass, field
from typing import Any

from fastmcp.client import Client 
from enum import Enum
from pathlib import Path
from fastmcp.client import StdioTransport , SSETransport
from config.config import MCPServerConfig
import os

class MCPSeverStatus(str, Enum):
    DISCONENCTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connecetd"
    ERRO = "error"


@dataclass
class MCPToolInfo:
    name : str 
    description : str 
    input_schema : dict[str,Any] = field(default_factory=dict)
    server_name : str = "" 

class MCPClient:
    def __init__(self , name : str , config : MCPServerConfig , cwd : Path) -> None:
        self.name = name 
        self.config = config
        self.cwd = cwd 
        self.status = MCPSeverStatus.DISCONENCTED
        self._client = Client | None = None 
        self._tools : dict[str,MCPToolInfo] = dict()

    @property
    def tools(self) -> list[MCPToolInfo]:
        return list(self._tools.values())
 
    def craete_transport(self) -> StdioTransport | SSETransport:
        if self.config.command:
            env = os.environ.copy()
            env.update(self.config.env)

            return StdioTransport(
                command=self.config.command,
                args=list(self.config.args),
                env=env,
                cwd=str(self.config.cwd or self.cwd),
                log_file= Path(os.devnull)
            )

        else :
            return SSETransport(url=self.config.url)

    async def connect(self) -> None:
        if self.status == MCPSeverStatus.CONNECTED:
            return 

        self.status = MCPSeverStatus.CONNECTING

        try:
            self._client = Client(transport=self.craete_transport())

            await self._client.__aenter__()

            tool_result = await self._client.list_tools()

            for tool in tool_result:
                self._tools[tool.name] = MCPToolInfo(
                    name = tool.name,
                    description=tool.description or "",
                    input_schema=(
                        tool.schema if hasattr(tool,"inputSchema") else {},
                    ),
                    server_name=self.name
                )

            self.status = MCPSeverStatus.CONNECTED

        except Exception:
            self.status = MCPSeverStatus.ERRO
            raise

    async def disconenct(self) -> None:
        if self._client:
            await self._client.__aexit__(None,None,None)
            self._client = None

        self._tools.clear()
        self.status = MCPSeverStatus.DISCONENCTED

    async def call_tool(self , tool_name : str , arguments : dict[str,Any]):
        if not self._client or self._client.status != MCPSeverStatus.CONNECTED:
            raise RuntimeError(f"Not connected to server {self.name}")

        result = await self._client.call_tool(tool_name,arguments)

        output = []
        for item in result.content:
            if hasattr(item,"text"):
                output.append(item.text)
            else:
                output.append(str(item))

        return output
