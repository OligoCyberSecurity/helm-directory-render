import os
import subprocess
from typing import Optional

from pydantic import BaseModel, Field


class TraversalRecord(BaseModel):
    """_description_

    Args:
        BaseModel (_type_): _description_
    """
    base_path: str
    env_path: str
    chart_dir: str
    rendered_path: str
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    name: str = Field(init=True)

    def helm_exec_string(self):
        return f"helm template {self.name} {self.chart_dir} -f {self.base_path} -f {self.env_path} --output-dir {self.rendered_path}"

    def helm_template(self):
        if not os.path.exists(self.rendered_path):
            raise FileNotFoundError(f"Job path does not exist: {self.rendered_path}")

        res = subprocess.run(self.helm_exec_string(), shell=True, check=True)
        self.stdout = str(res.stdout)
        self.stderr = str(res.stderr)
        res.check_returncode()
