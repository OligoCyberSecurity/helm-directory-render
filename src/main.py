import argparse
import os
from typing import List
from entities.helm_template_processor import HelmTemplateProcessor
from entities.deployment import Deployment
from utils.logger import setup_logging
import constants as c

# Setup logging
setup_logging()


def main():
    parser = argparse.ArgumentParser(description="Helm template generator")
    parser.add_argument(
        "--directory",
        default=os.environ.get("HELM_TEMPLATE_PROCESSOR_DIRECTORY"),
        required=True,
        type=str,
        help="Directory to traverse"
    )
    parser.add_argument("--filter", default=".*", required=False,
                        type=str, help="Filter deployments")
    parser.add_argument(
        "--debug",
        default=os.environ.get(
            "HELM_TEMPLATE_PROCESSOR_DEBUG", "false") == "true",
        required=False,
        type=bool,
        help="Debug mode"
    )
    args = parser.parse_args()

    templates: List[HelmTemplateProcessor] = []
    app_name = os.path.basename(args.directory)
    for root, _, files in os.walk(args.directory):
        if c.CONFIG_FILE in files:
            print(f"Found config file in {root}")
            templates.append(HelmTemplateProcessor(
                app_name=app_name, config_path=root, filter=args.filter, debug=args.debug))

    deployments: List[Deployment] = []
    for template in templates:
        deployments.extend(template.generate_deployments())

    charts = {}
    for deployment in deployments:
        chart_key = f"{deployment.chart}-{deployment.target_revision}"
        if chart_key not in charts:
            charts[chart_key] = {
                'repo_url': deployment.repo_url,
                'version': deployment.target_revision,
                'chart': deployment.chart
            }
    for values in charts.values():
        repo_url = values['repo_url']
        chart = values['chart']
        version = values['version']
        if not os.path.exists(f"{c.CHARTS_DIR}/{chart}/{version}"):
            os.makedirs(f"{c.CHARTS_DIR}/{chart}/{version}")
        os.system(
            f"helm pull {repo_url}/{chart} --version {version} --untar --untardir {c.CHARTS_DIR}/{chart}/{version}")

    for deployment in deployments:
        deployment.render()


if __name__ == "__main__":
    main()
