from pydantic import BaseModel
from typing import List, Optional
import yaml


class DeploymentConfig(BaseModel):
    enabled: bool = True
    name: str
    targetRevision: Optional[str] = None
    namespace: Optional[str] = None
    additionalOptions: List[str] = []


class Config(BaseModel):
    apiVersion: str
    enabled: bool = True
    repoURL: str
    chart: str
    targetRevision: str
    namespace: str
    deployments: List[DeploymentConfig]


def load_config(file_path: str) -> Config:
    """Loads the config YAML and parses it into a Config object."""
    try:
        with open(file_path, 'r') as file:
            config_data = yaml.safe_load(file)
            if not isinstance(config_data, dict):
                raise ValueError("Invalid YAML format.")
        return Config(**config_data)
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {e}")
