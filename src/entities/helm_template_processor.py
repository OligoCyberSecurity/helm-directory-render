import os
import re
from typing import List
from pydantic import BaseModel, Field
from config.config import load_config, Config
from entities.deployment import Deployment
import constants as c


class HelmTemplateProcessor(BaseModel):
    app_name: str
    config_path: str
    config: Config = None
    filter: str
    debug: bool = Field(default=False)

    def __init__(self, **data):
        super().__init__(**data)
        config_file_path = os.path.join(self.config_path, c.CONFIG_FILE)
        self.config = load_config(config_file_path)

    def output_dir(self, deployment: str):
        return self.config_path.replace(
            c.HELM_DIR, os.path.join(c.OUTPUT_DIR, deployment)
        )

    def values(self, deployment: str):
        return [os.path.join(self.config_path, f) for f in [c.BASE_VALUES, f"{deployment}.yaml"]]

    def generate_deployments(self) -> List[Deployment]:
        deployment_filter = re.compile(self.filter)
        deployments: List[Deployment] = []
        for deployment in self.config.deployments:
            if deployment.enabled and self.config.enabled and deployment_filter.match(deployment.name):
                deployments.append(
                    Deployment(
                        name=deployment.name,
                        release_name=self.app_name,
                        repo_url=self.config.repoURL,
                        chart=self.config.chart,
                        target_revision=deployment.targetRevision or self.config.targetRevision,
                        namespace=deployment.namespace or self.config.namespace,
                        values=self.values(deployment.name),
                        output_dir=self.output_dir(deployment.name),
                        additional_options=deployment.additionalOptions,
                        debug=self.debug,
                    )
                )
        return deployments
