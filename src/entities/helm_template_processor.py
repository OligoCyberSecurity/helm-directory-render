import re
import logging
from typing import List
from pydantic import BaseModel, Field
from pathlib import Path
from config.config import load_config
from entities.deployment import Deployment
import constants as c

logger = logging.getLogger(__name__)


class HelmTemplateProcessor(BaseModel):
    app_name: str
    config_path: Path
    config: dict = {}
    filter: str
    debug: bool = Field(default=False)

    def __init__(self, **data):
        super().__init__(**data)
        config_file_path = Path(self.config_path) / c.CONFIG_FILE
        try:
            self.config = load_config(config_file_path)
        except Exception as e:
            logger.error(
                f"Failed to load config from {config_file_path}: {e}", exc_info=True)
            self.config = {}

    def output_dir(self, deployment: str) -> Path:
        output_directory = Path(str(self.config_path).replace(
            c.HELM_DIR, str(Path(c.OUTPUT_DIR) / deployment)))
        logger.debug(f"Output directory for {deployment}: {output_directory}")
        return output_directory

    def values(self, deployment: str) -> List[Path]:
        values_files = [Path(self.config_path) /
                        f for f in [c.BASE_VALUES, f"{deployment}.yaml"]]
        logger.debug(f"Values files for {deployment}: {values_files}")
        return values_files

    @property
    def name(self) -> str:
        relative_path = '-'.join(self.config_path.as_posix().split(c.HELM_DIR)
                                 [1].strip("/").split("/"))
        name = f"{self.app_name}-{relative_path}"
        logger.debug(f"Generated name: {name}")
        return name

    def generate_deployments(self) -> List[Deployment]:
        deployment_filter = re.compile(self.filter)
        deployments: List[Deployment] = []

        if not self.config:
            logger.warning(
                "Skipping deployment generation due to missing configuration")
            return deployments

        for deployment in getattr(self.config, 'deployments', []):
            if not getattr(deployment, 'enabled', False) or not getattr(self.config, 'enabled', False):
                continue

            if not deployment_filter.match(deployment.name):
                logger.debug(
                    f"Skipping deployment {deployment.name} due to filter mismatch")
                continue

            try:
                deployment_obj = Deployment(
                    name=self.name,
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
                deployments.append(deployment_obj)
            except Exception as e:
                logger.error(
                    f"Error generating deployment {deployment.name}: {e}", exc_info=True)

        return deployments
