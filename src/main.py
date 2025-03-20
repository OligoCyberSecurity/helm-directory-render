import os
import argparse
import subprocess
import concurrent.futures
import logging
from pathlib import Path
from typing import List
from entities.helm_template_processor import HelmTemplateProcessor
from entities.deployment import Deployment
from utils.logger import setup_logging
import constants as c

setup_logging()
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Helm template generator")
    parser.add_argument(
        "--directory",
        default=os.environ.get("HELM_TEMPLATE_PROCESSOR_DIRECTORY"),
        required=True,
        type=Path,
        help="Directory to traverse"
    )
    parser.add_argument("--filter", default=".*",
                        required=False, type=str, help="Filter deployments")
    parser.add_argument(
        "--debug",
        action=argparse.BooleanOptionalAction,
        default=os.environ.get(
            "HELM_TEMPLATE_PROCESSOR_DEBUG", "false").lower() == "true",
        help="Debug mode"
    )
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logger.setLevel(log_level)
    logger.debug("Debug mode enabled")

    templates: List[HelmTemplateProcessor] = []
    app_name = args.directory.name

    for config_file in args.directory.rglob(c.CONFIG_FILE):
        logger.info(f"Found config file in {config_file.parent}")
        templates.append(
            HelmTemplateProcessor(
                app_name=app_name, config_path=config_file.parent, filter=args.filter, debug=args.debug
            )
        )

    deployments: List[Deployment] = []
    for template in templates:
        try:
            deployments.extend(template.generate_deployments())
        except Exception as e:
            logger.error(
                f"Failed to generate deployments for {template.config_path}: {e}", exc_info=True)

    charts = {}
    for deployment in deployments:
        chart_key = f"{deployment.chart}-{deployment.target_revision}"
        if chart_key not in charts:
            charts[chart_key] = {
                'repo_url': deployment.repo_url,
                'version': deployment.target_revision,
                'chart': deployment.chart
            }

    def download_chart(values):
        repo_url, chart, version = values['repo_url'], values['chart'], values['version']
        chart_dir = Path(c.CHARTS_DIR) / chart / version

        if not chart_dir.exists():
            chart_dir.mkdir(parents=True, exist_ok=True)
            try:
                logger.info(
                    f"Downloading chart {chart} version {version} from {repo_url}")
                subprocess.run(
                    ["helm", "pull", f"{repo_url}/{chart}",
                        "--version", version, "--untar"],
                    check=True,
                    cwd=str(chart_dir)
                )
            except subprocess.CalledProcessError as e:
                logger.error(
                    f"Failed to download chart {chart} version {version}: {e}", exc_info=True)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(download_chart, charts.values())

    def render_deployment(deployment):
        try:
            deployment.render()
            logger.info(f"Successfully rendered deployment: {deployment}")
        except Exception as e:
            logger.error(
                f"Failed to render deployment {deployment}: {e}", exc_info=True)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(render_deployment, deployments)


if __name__ == "__main__":
    main()
