import os
import shutil
import subprocess

from pydantic import BaseModel, Field


class TraversalRecord(BaseModel):
    """_description_

    Args:
        BaseModel (_type_): _description_
    """
    input_path: str
    env: str
    chart_name: str
    values_path: str
    instance: str
    helm_path: str = Field(default="helm")
    rendered_path: str = Field(default="rendered")

    @property
    def get_values_path(self):
        return [os.path.join(self.input_path, self.helm_path, self.component_path, f) for f in ["base.yaml", f"{self.env}.yaml"]]

    @property
    def output_dir(self):
        return os.path.join(self.input_path, self.rendered_path, self.env, self.component_path)

    @property
    def component_path(self):
        helm_path = os.path.join(self.input_path, self.helm_path) + "/"
        return self.values_path.replace(helm_path, "")

    def helm_exec_string(self):
        cmd = ["helm", "template", self.instance,
               f'charts/{self.chart_name}', "--output-dir", self.output_dir]
        for values in self.get_values_path:
            cmd.append("-f")
            cmd.append(values)
        return ' '.join(cmd)

    def helm_template(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir + "/")

        res = subprocess.run(self.helm_exec_string(), shell=True, check=True)
        res.check_returncode()

    def normalize_path(self):
        helm_output_dir = os.path.join(
            self.output_dir, self.chart_name, "templates")
        for file in os.listdir(helm_output_dir):
            if file.endswith(".yaml"):
                shutil.move(os.path.join(helm_output_dir, file),
                            os.path.join(self.output_dir, file))
        shutil.rmtree(os.path.join(self.output_dir, self.chart_name))
