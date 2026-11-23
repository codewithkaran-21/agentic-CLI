from config.config import Config
from tool.base import ToolInvocation, ToolKind, ToolResult
from tool.builtin.list_dir import ListDirParams
from tool.mcp.client import MCPClient, MCPToolInfo


class MCPTool:

    def __init__(self , config : Config , client : MCPClient , tool_info : MCPToolInfo , name : str) -> None:
        super.__init__(config)
        self._tool_info = tool_info
        self._client = client
        self.name = name 
        self.description = self._tool_info.description
        input_schema = self._tool_info.input_schema or {}
        self.schema = {
            "type":"object",
            "properties":input_schema.get("properties",{}),
            "required":input_schema.get("required",{})
        }
        self.is_mutatingmutating = True

    description = "" 
    kind = ToolKind.MCP
    schema = ListDirParams


    async def execute(self,invocation : ToolInvocation) -> ToolResult:
        try:
            result = await self._client.call_tool(
                self._tool_info.name,
                invocation.params
            )

            output = result.get("output","")
            is_error = result.get("erorr",True)

            if is_error:
                return ToolResult.error_result(output)

            return ToolResult.success_result(output)

        except Exception as e:
            return ToolResult.error_result(f"MCP tool failed: {e}")