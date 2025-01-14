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

    for deployment in deployments:
        deployment.render()


if __name__ == "__main__":
    main()
