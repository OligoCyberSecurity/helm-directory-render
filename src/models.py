import os
import shutil
import subprocess

from pydantic import BaseModel, Field


class TraversalRecord(BaseModel):
    """_description_

    Args:
        BaseModel (_type_): _description_
    """
    base_path: str
    values_path: str
    env: str
    chart_name: str
    output_base_path: str
    name: str = Field(init=True)
    use_globals: bool = Field(default=False)

    def get_values_path(self, values_file: str):
        return f"{self.values_path}/{values_file}"

    @property
    def output_dir(self):
        return f"{self.output_base_path}/{self.env}/{self.name}"

    def helm_exec_string(self):
        cmd = ["helm", "template", self.name, self.chart_name]
        if self.use_globals:
            cmd.extend(["-f", f"{self.base_path}/globals.yaml"])
        cmd.extend(["-f", self.get_values_path("base.yaml"), "-f",
                   self.get_values_path(f"{self.env}.yaml"), "--output-dir", self.output_dir])
        return ' '.join(cmd)

    def helm_template(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir + "/")

        res = subprocess.run(self.helm_exec_string(), shell=True, check=True)

        res.check_returncode()
