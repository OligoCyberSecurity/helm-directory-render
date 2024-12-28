import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError
from config.config import Config, DeploymentConfig
from entities.helm_template_processor import HelmTemplateProcessor

# Mock constants
CONFIG_FILE = ".helm.yaml"
HELM_DIR = "helm"
OUTPUT_DIR = "live"
BASE_VALUES = "base.yaml"


@pytest.fixture
def mock_config():
    """Fixture to create a mock configuration object."""
    return Config(
        apiVersion="v1",
        enabled=True,
        repoURL="https://example.com/repo",
        chart="example-chart",
        targetRevision="1.0.0",
        namespace="default",
        deployments=[
            DeploymentConfig(name="deployment1", enabled=True),
            DeploymentConfig(name="deployment2", enabled=False),
            DeploymentConfig(name="test-deployment", enabled=True),
        ],
    )


@pytest.fixture
def mock_processor(mock_config, tmp_path):
    """Fixture to create a HelmTemplateProcessor instance."""
    config_path = tmp_path / HELM_DIR
    config_file = config_path / CONFIG_FILE
    config_path.mkdir(parents=True)
    # Simulate the existence of the config file
    config_file.write_text("mock configuration content")

    with patch("entities.helm_template_processor.load_config", return_value=mock_config):
        yield HelmTemplateProcessor(
            app_name="test-app",
            config_path=str(config_path),
            filter="^deployment",
            debug=False,
        )


def test_initialization(mock_processor):
    """Test that the processor is initialized correctly."""
    assert mock_processor.app_name == "test-app"
    assert mock_processor.config_path.endswith(HELM_DIR)
    assert mock_processor.config.apiVersion == "v1"
    assert mock_processor.filter == "^deployment"
    assert not mock_processor.debug


def test_release_name(mock_processor):
    """Test that the release_name property is computed correctly."""
    expected_release_name = "test-app"
    assert mock_processor.release_name == expected_release_name


def test_generate_deployments(mock_processor):
    """Test the generate_deployments method."""
    deployments = mock_processor.generate_deployments()

    # Only "deployment1" matches the filter and is enabled
    assert len(deployments) == 1
    deployment = deployments[0]
    assert deployment.name == "deployment1"
    assert deployment.release_name == mock_processor.release_name
    assert deployment.repo_url == mock_processor.config.repoURL
    assert deployment.chart == mock_processor.config.chart


def test_deployment_filter(mock_processor):
    """Test that the filter correctly excludes non-matching deployments."""
    mock_processor.filter = "^test"
    deployments = mock_processor.generate_deployments()

    assert len(deployments) == 1  # Only "test-deployment" matches the filter
    assert deployments[0].name == "test-deployment"


def test_missing_config_file(tmp_path):
    """Test that missing config files raise an appropriate error."""
    config_path = tmp_path / HELM_DIR
    with pytest.raises(FileNotFoundError):
        HelmTemplateProcessor(
            app_name="test-app",
            config_path=str(config_path),
            filter=".*",
            debug=False,
        )


def test_invalid_config():
    """Test invalid initialization data."""
    with pytest.raises(ValidationError):
        HelmTemplateProcessor(
            app_name=None,  # Invalid value
            config_path="invalid/path",
            filter=".*",
            debug=False,
        )
