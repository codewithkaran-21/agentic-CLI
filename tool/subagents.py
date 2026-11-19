from config.config import Config
from dataclasses import dataclass
from tool.base import Tool


class SubAgentParams:
    goal : str 

@dataclass
class SubAgentDefinition:
    name : str
    description : str 
    goal_prompt : str 
    allowed_tools : list[str] | None = None 
    max_turns : int = 20
    timeout_seconds : float = 600


class SubagentTool(Tool):
    def __init__(self , config : Config , definition :SubAgentDefinition):
        super().__init__(config)
        self.definiton = definition

    @property
    def name(self)->str:
        return f"subagent_{self.definition.name}"
