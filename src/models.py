from pydantic import BaseModel, Field
from typing import Optional


class TraversalRecord(BaseModel):
    """_description_

    Args:
        BaseModel (_type_): _description_
    """
    base_path: str
    env_path: str
    helm_exec_string: str
    rendered_path: str
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    name: str = Field(init=True)
