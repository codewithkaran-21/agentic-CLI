from pydantic import BaseModel , Field

from tool.base import Tool, ToolInvocation, ToolKind, ToolResult


class TestToolParams(BaseModel):
    messsage : str = Field(...,description="The message to echo back")

class TestTool(Tool):
    name = "test_tool"
    description = (
        "A test tool that echoes back the input message. "
        "This tool is discovered from .unified_agent/tool/test_tool.py"
    )

    kind = ToolKind.READ

    schema = TestToolParams

    async def execute(self,invocation : ToolInvocation) -> ToolResult:
        params = TestToolParams(**invocation.params)
        message = params.messsage

        output = f"Test tool recieved: {message}\n"
        output += "Tool was discovered from: .ai-agent/tool/test_tool.py"

        return ToolResult.success_result(output)