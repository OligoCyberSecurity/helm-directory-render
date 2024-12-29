import pytest
from pydantic import ValidationError
from config.config import DeploymentConfig, Config, load_config
from unittest.mock import patch, mock_open
import yaml


def test_deployment_config_default_values():
    """Test DeploymentConfig with default values."""
    deployment = DeploymentConfig(name="test-deployment")
    assert deployment.enabled is True
    assert deployment.name == "test-deployment"
    assert deployment.targetRevision is None
    assert deployment.namespace is None
    assert deployment.additionalOptions == []


def test_deployment_config_custom_values():
    """Test DeploymentConfig with custom values."""
    deployment = DeploymentConfig(
        enabled=False,
        name="custom-deployment",
        targetRevision="1.0.0",
        namespace="custom-namespace",
        additionalOptions=["--debug", "--set key=value"],
    )
    assert deployment.enabled is False
    assert deployment.name == "custom-deployment"
    assert deployment.targetRevision == "1.0.0"
    assert deployment.namespace == "custom-namespace"
    assert deployment.additionalOptions == ["--debug", "--set key=value"]


def test_config_model_valid():
    """Test Config model with valid data."""
    config_data = {
        "apiVersion": "v1",
        "enabled": True,
        "repoURL": "https://example.com/charts",
        "chart": "example-chart",
        "targetRevision": "1.2.3",
        "namespace": "example-namespace",
        "deployments": [
            {"enabled": True, "name": "deployment-1"},
            {"enabled": False, "name": "deployment-2", "namespace": "custom-ns"},
        ],
    }

    config = Config(**config_data)
    assert config.apiVersion == "v1"
    assert config.enabled is True
    assert config.repoURL == "https://example.com/charts"
    assert config.chart == "example-chart"
    assert config.targetRevision == "1.2.3"
    assert config.namespace == "example-namespace"
    assert len(config.deployments) == 2
    assert config.deployments[0].name == "deployment-1"
    assert config.deployments[1].namespace == "custom-ns"


def test_config_model_invalid():
    """Test Config model with invalid data."""
    invalid_data = {
        "enabled": True,  # Missing required field `apiVersion`
        "repoURL": "https://example.com/charts",
        "chart": "example-chart",
        "targetRevision": "1.2.3",
        "namespace": "example-namespace",
        "deployments": [
            {"enabled": True, "name": "deployment-1"},
        ],
    }

    with pytest.raises(ValidationError) as excinfo:
        Config(**invalid_data)

    # Check that the validation error is related to the missing `apiVersion` field
    assert excinfo.value.errors()[0]['loc'] == ('apiVersion',)


@patch("builtins.open", new_callable=mock_open, read_data="""
apiVersion: v1
enabled: true
repoURL: https://example.com/charts
chart: example-chart
targetRevision: 1.2.3
namespace: example-namespace
deployments:
  - enabled: true
    name: deployment-1
  - enabled: false
    name: deployment-2
    namespace: custom-namespace
""")
def test_load_config(mock_file):
    """Test the load_config function."""
    config = load_config("mock_file_path")
    assert config.apiVersion == "v1"
    assert config.enabled is True
    assert config.repoURL == "https://example.com/charts"
    assert config.chart == "example-chart"
    assert config.targetRevision == "1.2.3"
    assert config.namespace == "example-namespace"
    assert len(config.deployments) == 2
    assert config.deployments[0].name == "deployment-1"
    assert config.deployments[1].namespace == "custom-namespace"


@patch("builtins.open", new_callable=mock_open, read_data="invalid_yaml")
def test_load_config_invalid_yaml(mock_file):
    """Test the load_config function with invalid YAML."""
    with pytest.raises(ValueError, match="Invalid YAML format."):
        load_config("mock_file_path")
