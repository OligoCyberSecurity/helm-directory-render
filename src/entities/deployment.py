import os
import shutil
import subprocess
from pydantic import BaseModel
from typing import List


class Deployment(BaseModel):
    name: str
    release_name: str
    repo_url: str
    chart: str
    target_revision: str
    namespace: str
    values: List[str] = []
    output_dir: str
    additional_options: List[str] = []
    debug: bool = False

    def helm_cmd(self):
        cmd = [
            "helm", "template", self.release_name,
            f'{self.repo_url}/{self.chart}',
            "--namespace", self.namespace,
            "--version", self.target_revision,
            "--output-dir", self.output_dir,
            "--dependency-update",
        ]

        for file in self.values:
            cmd.extend(["-f", file])

        cmd.extend(self.additional_options)

        if self.debug:
            cmd.append("--debug")

        return ' '.join(cmd)

    def render(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

        subprocess.run(self.helm_cmd(), shell=True, check=True)
        self.normalize_path()

    def normalize_path(self):
        helm_output_dir = os.path.join(
            self.output_dir, self.chart, "templates")
        for file in os.listdir(helm_output_dir):
            if file.endswith(".yaml"):
                shutil.move(
                    os.path.join(helm_output_dir, file),
                    os.path.join(self.output_dir, file)
                )
        shutil.rmtree(os.path.join(self.output_dir, self.chart))
