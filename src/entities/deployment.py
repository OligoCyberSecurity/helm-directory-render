import shutil
import subprocess
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List
import constants as c

logger = logging.getLogger(__name__)


class Deployment(BaseModel):
    name: str
    release_name: str
    repo_url: str
    chart: str
    target_revision: str
    namespace: str
    values: List[Path] = []
    output_dir: Path
    additional_options: List[str] = []
    debug: bool = False

    def helm_cmd(self):
        cmd = [
            "helm", "template", self.release_name,
            str(Path(c.CHARTS_DIR) / self.chart /
                self.target_revision / self.chart),
            "--namespace", self.namespace,
            "--version", self.target_revision,
            "--set", f"fullnameOverride={self.name}",
            "--output-dir", str(self.output_dir),
        ]

        for file in self.values:
            cmd.extend(["-f", str(file)])

        cmd.extend(self.additional_options)

        if self.debug:
            cmd.append("--debug")

        logger.debug(f"Generated Helm command: {' '.join(cmd)}")
        return cmd

    def render(self):
        output_dir = Path(self.output_dir)
        if output_dir.exists():
            shutil.rmtree(output_dir)

        try:
            result = subprocess.run(
                self.helm_cmd(), capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(
                    f"Helm template command failed for {self.name}\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
                raise subprocess.CalledProcessError(
                    result.returncode, self.helm_cmd(), result.stdout, result.stderr)

            self.normalize_path()
        except Exception as e:
            logger.error(
                f"Error rendering Helm template for {self.name}: {e}", exc_info=True)
            raise

    def normalize_path(self):
        output_dir = Path(self.output_dir)
        helm_output_dir = output_dir / self.chart / "templates"

        if not helm_output_dir.exists():
            logger.warning(
                f"Expected Helm output directory does not exist: {helm_output_dir}")
            return

        try:
            for file in helm_output_dir.glob("*.yaml"):
                target_file = output_dir / file.name
                file.rename(target_file)
                logger.debug(f"Moved {file} to {target_file}")
            shutil.rmtree(output_dir / self.chart)
        except Exception as e:
            logger.error(
                f"Error normalizing Helm output for {self.name}: {e}", exc_info=True)
