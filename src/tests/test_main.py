from unittest.mock import patch, MagicMock
from main import main  # Ensure the main function is correctly imported

# Test for HelmTemplateProcessor initialization


@patch('entities.helm_template_processor.HelmTemplateProcessor')
@patch('os.walk')
@patch('entities.helm_template_processor.load_config')
@patch('builtins.open', create=True)  # Mocking the built-in open function
def test_helm_template_processor_initialization(mock_open, mock_load_config, mock_os_walk, MockHelmTemplateProcessor):
    # Mocking load_config to return a mock config
    mock_config = MagicMock()
    mock_load_config.return_value = mock_config

    # Mocking open to simulate reading a file (prevent FileNotFoundError)
    # Mock the file context manager
    mock_open.return_value.__enter__.return_value = MagicMock()

    # Simulate os.walk returning directories with a .helm.yaml file
    mock_os_walk.return_value = [
        ('/test/dir/helm', ('subdir1', 'subdir2'), ['.helm.yaml']),
        ('/test/dir/helm/subdir1', (), ['.helm.yaml']),
    ]

    # Mock HelmTemplateProcessor
    mock_processor = MagicMock()
    MockHelmTemplateProcessor.return_value = mock_processor

    # Patch sys.argv to simulate command-line arguments
    with patch('sys.argv', ['main.py', '--directory', '/test/dir', '--filter', 'prod', '--debug', 'true']):
        main()

# Test for generating deployments


@patch('entities.helm_template_processor.HelmTemplateProcessor')
@patch('entities.deployment.Deployment')
@patch('entities.helm_template_processor.load_config')
@patch('builtins.open', create=True)  # Mocking the built-in open function
def test_generate_deployments(mock_open, mock_load_config, MockDeployment, MockHelmTemplateProcessor):
    # Mocking load_config to return a mock config
    mock_config = MagicMock()
    mock_load_config.return_value = mock_config

    # Mocking open to simulate reading a file
    mock_open.return_value.__enter__.return_value = MagicMock()

    # Mocking HelmTemplateProcessor and Deployment
    mock_processor = MagicMock()
    mock_deployment = MagicMock()
    MockHelmTemplateProcessor.return_value = mock_processor
    MockDeployment.return_value = mock_deployment
    mock_processor.generate_deployments.return_value = [mock_deployment]

    # Simulate os.walk to find the .helm.yaml file
    with patch('os.walk', return_value=[('/test/dir/helm', (), ['.helm.yaml'])]):
        with patch('sys.argv', ['main.py', '--directory', '/test/dir', '--filter', 'prod', '--debug', 'false']):
            main()

# Test for deployment rendering


@patch('subprocess.run')
@patch('entities.deployment.Deployment')
@patch('entities.helm_template_processor.load_config')
@patch('builtins.open', create=True)  # Mocking the built-in open function
def test_deployment_rendering(mock_open, mock_load_config, MockDeployment, mock_subprocess_run):
    mock_deployment = MagicMock()
    MockDeployment.return_value = mock_deployment
    mock_deployment.render.return_value = None  # Mock the render behavior

    # Mocking load_config to return a mock config
    mock_config = MagicMock()
    mock_load_config.return_value = mock_config

    # Mocking open to simulate reading a file
    mock_open.return_value.__enter__.return_value = MagicMock()

    # Simulate os.walk to find the .helm.yaml file
    with patch('os.walk', return_value=[('/test/dir/helm', (), ['.helm.yaml'])]):
        with patch('sys.argv', ['main.py', '--directory', '/test/dir', '--filter', 'prod', '--debug', 'true']):
            main()
