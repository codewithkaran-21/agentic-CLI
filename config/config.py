import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel , Field, model_validator 


class ModelConfig(BaseModel):
    name : str = "nvidia/nemotron-3.5-super-vl:free"
    temperature : float = Field(default=1,ge=0.0,le=2.0)
    context_window : int = 256_000

class MCPServerConfig(BaseModel):
    enabled : bool = True
    startup_timeout_sec : float = 10 

    command : str | None  = None 
    args : list[str] = Field(default_factory=list)
    env : dict[str,str] = Field(default_factory=dict)
    cwd : Path | None = None 

    url : str | None = None 
    
    @model_validator(mode='after')
    def validate_transport(self) -> MCPServerConfig:
        has_command = self.command is not None
        has_url = self.url is not None

        if not has_command and not has_url:
            raise ValueError("MCP Server must have either 'command' (stdio) or 'url' (http/sse)")
        
        if has_command and has_url:
            raise ValueError("MCP Server can not have both 'command' (stdio) and 'url' (http/sse)")

        return self

class Config(BaseModel):
    model : ModelConfig = Field(default_factory=ModelConfig)
    cwd :  Path = Field(default_factory=Path.cwd)

    max_turns : int = 100
    mcp_servers : dict[str,MCPServerConfig] = Field(default_factory=dict)
    allowed_tools : list[str] | None = Field(...,description="If set, only these tools are availabile for the agent")

    max_tool_output_tokens : int = 50000
    devloper_instructions : str | None = None
    user_instructions : str | None = None 
    debug : bool =  False 


    @property
    def api_key(self)->str:
        return os.environ.get("API_KEY")

    @property
    def base_url(self) -> str | None:
        return os.environ.get("BASE_URL")

    @property
    def model_name(self) -> str:
        return self.model.name

    @model_name.setter
    def model_name(self,value:str) -> None:
        self.model.name = value

    @property
    def temperature(self) -> float:
        return self.model.temperature

    @model_name.setter
    def model_name(self,value:str) -> None:
        self.model.temperature = value

    def validate(self) -> list[str]:
        error : list[str] = [] 

        if not self.api_key:
            error.append("No API Key found. Set API_KEY environment variable")
        if not self.cwd.exists():
            error.append(f"Working directory does not exist {self.cwd}")

        return error

    def to_dict(self) -> dict[str,Any]:
        return self.model.model_dump(mode="json")


