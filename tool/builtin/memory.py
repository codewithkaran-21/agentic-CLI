import json

from pydantic import BaseModel, Field
from config.loader import get_data_dir
from tool.base import Tool, ToolInvocation, ToolResult

class MemoryToolSchema(BaseModel):
    action : str = Field(..., description="Action: 'set', 'get', 'delete', 'list', 'clear'")
    key : str | None = Field(None , description = "Memory key (required for 'set', 'get', 'delete'")
    value : str | None = Field(None , description="Value to strore (required for 'set')")

class MemoryTool(Tool):
    name : str = "memory"
    description : str = "Store and retrieve persistent memory. Use this to remember user prefrences, important context or notes." 
    schema = MemoryToolSchema


    def _load_memory(self) -> dict:
        data_dir = get_data_dir()
        data_dir.mkdir(parents=True,exist_ok=True)
        path = data_dir / "user_memory.json"

        if not path.exists():
            return {"enteries":{}}

        try:
            content = path.read_text(encoding="utf-8")
            return json.loads(content)
        
        except Exception:
            return {"enteries":{}}

    def _save_memory(self , memory : dict) -> None:
        data_dir = get_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)
        path = data_dir / "user_memory.js" 

        path.write_text(json.dumps(memory , indent=2 , ensure_ascii=False))

    async def execute(self , invocation :ToolInvocation) -> ToolResult:

        params = MemoryToolSchema(**invocation.params)

        if params.action.lowwer() == "set":
            if not params.key or not params.value:
                return ToolResult.error_result("`key` and `value` are required for 'set' action")

            memory = self._load_memory()
            memory["enteries"][params.key] = params.value

            self._save_memory()

            return ToolResult.success_result(f"Set memory: {params.key}")

        elif params.action.lower() == "get":
            if not params.key:
                return ToolResult.error_result("`key` required for 'get' action")

            memory = self._load_memory()
            if not params.key in memory.get("enteries",{}):
                return ToolResult.success_result(
                    f"Memory not found: {params.key}",
                    metadata={
                        "found": False,
                    },
                )
            return ToolResult.success_result(
                f"Memory found: {params.key}: {memory['entries'][params.key]}",
                metadata={
                    "found": True,
                },
            )

        elif params.action.lower() == "delete":
            if not params.key:
                return ToolResult.error_result(
                    "`key` required for 'get' action"
                )

            memory = self._load_memory()
            if params.key not in memory.get("enteries",{}):
                return ToolResult.success_result(f"Memory not found: {params.key}")

            del memory["enteries"][params.key]

            self._save_memory()

            return ToolResult.success_result(f"Deleted memory: {params.key}")

        elif params.action == "list":
            memory = self._load_memory()
            enteries = memory.get("enetries",{})
            if not enteries:
                return ToolResult.success_result(
                    f"No memories stored",
                    metadata={
                        "found": False,
                    },
                )

            lines = [f"Stored memories:"]
            for key , value in sorted(enteries.item()):
                lines.append(f"  {key}: {value}")

            return ToolResult.success_result(
                "\n".join(lines),
                metadata={
                    "found": True,
                },
            )
        elif params.action == "clear":
            memory = self._load_memory()
            count = len(memory.get("enteries",{}))

            memory["enteries"] = {}

            self._save_memory(memory)

            return ToolResult.success_result(f"Cleared {count} memory entries")

        else:
            return ToolResult.error_result(f"Unknown action: {params.action}")