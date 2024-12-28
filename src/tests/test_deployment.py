import os
import pytest
from unittest.mock import patch, MagicMock
from entities.deployment import Deployment


@pytest.fixture
def deployment_instance(tmp_path):
    """Fixture to provide a Deployment instance."""
    return Deployment(
        name="test-deployment",
        release_name="test-release",
        repo_url="https://example.com/repo",
        chart="example-chart",
        target_revision="1.0.0",
        namespace="default",
        values=["/path/to/values1.yaml", "/path/to/values2.yaml"],
        output_dir=str(tmp_path / "output"),
        additional_options=["--set", "key=value"],
        debug=True,
    )


def test_helm_cmd(deployment_instance):
    """Test the helm_cmd method."""
    expected_cmd = (
        "helm template test-release https://example.com/repo/example-chart "
        "--namespace default --version 1.0.0 --output-dir "
        f"{deployment_instance.output_dir} -f /path/to/values1.yaml -f /path/to/values2.yaml "
        "--set key=value --debug"
    )
    assert deployment_instance.helm_cmd() == expected_cmd


@patch("os.path.exists", return_value=True)
@patch("shutil.rmtree")
@patch("subprocess.run")
@patch("entities.deployment.Deployment.normalize_path", return_value=None)
def test_render(mock_normalize_path, mock_subprocess, mock_rmtree, mock_exists, deployment_instance):
    """Test the render method."""
    deployment_instance.render()

    # Check if output directory was removed
    mock_rmtree.assert_called_once_with(deployment_instance.output_dir)

    # Check if the helm command was executed
    mock_subprocess.assert_called_once_with(
        deployment_instance.helm_cmd(), shell=True, check=True
    )

    # Check if normalize_path was called
    mock_normalize_path.assert_called_once()


@patch("os.path.exists", return_value=False)
@patch("shutil.rmtree")
@patch("subprocess.run")
@patch("entities.deployment.Deployment.normalize_path", return_value=None)
def test_render_no_existing_output(
    mock_normalize_path, mock_subprocess, mock_rmtree, mock_exists, deployment_instance
):
    """Test the render method when no existing output directory exists."""
    deployment_instance.render()

    # Check that rmtree is not called since the directory does not exist
    mock_rmtree.assert_not_called()

    # Check if the helm command was executed
    mock_subprocess.assert_called_once_with(
        deployment_instance.helm_cmd(), shell=True, check=True
    )

    # Check if normalize_path was called
    mock_normalize_path.assert_called_once()


@patch("os.path.exists", return_value=False)
@patch("shutil.rmtree")
@patch("subprocess.run")
@patch("entities.deployment.Deployment.normalize_path", return_value=None)
def test_render_no_existing_output(
    mock_normalize_path, mock_subprocess, mock_rmtree, mock_exists, deployment_instance
):
    """Test the render method when no existing output directory exists."""
    deployment_instance.render()

    # Check that rmtree is not called since the directory does not exist
    mock_rmtree.assert_not_called()  # Use assert_not_called, not assert_not_called_with

    # Check if the helm command was executed
    mock_subprocess.assert_called_once_with(
        deployment_instance.helm_cmd(), shell=True, check=True
    )

    # Check if normalize_path was called
    mock_normalize_path.assert_called_once()
