import os
import shutil
import subprocess
from typing import Optional

from pydantic import BaseModel, Field

import logging

class TraversalRecord(BaseModel):
    """_description_

    Args:
        BaseModel (_type_): _description_
    """
    base_path: str
    env_path: str
    chart_dir: str
    rendered_path: str
    name: str = Field(init=True)

    def helm_exec_string(self):
        return f"helm template {self.name} {self.chart_dir} -f {self.base_path} -f {self.env_path} --output-dir {self.rendered_path}"

    def helm_template(self):
        if not os.path.exists(self.rendered_path):
            logging.warning("Job path does not exist: %s creating it", self.rendered_path)
            os.makedirs(self.rendered_path)
        else:
            shutil.rmtree(self.rendered_path+ "/")
        res = subprocess.run(self.helm_exec_string(), shell=True, check=True)
        
        res.check_returncode()
