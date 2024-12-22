import os

import re
import sys
import logging
import json
from pathlib import Path
from models import TraversalRecord
from typing import List
# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# get the input and convert it to int
env = os.environ.get("INPUT_ENVIRONMENT")
root_dir = os.environ.get("INPUT_DIRECTORY")
pattern = os.environ.get("INPUT_PATTERN")
chart_name = os.environ.get("INPUT_CHART")
rendered_path_input = os.environ.get("INPUT_RENDERED_PATH", "rendered").strip()
use_globals = os.environ.get(
    "INPUT_USE_GLOBALS", "false").strip().lower() == "true"
# Check if required inputs are provided
if not env or not root_dir or not pattern or not chart_name:
    logging.error("Missing required input")
    sys.exit(1)
PATTERN_REG = re.compile(pattern)  # Match all files ending with input pattern"

output = list()
output_base_path = f"{root_dir}/{rendered_path_input}"
templates: List[TraversalRecord] = []
for root, dir, _ in os.walk(root_dir):
    for d in dir:
        full_path = os.path.join(root, d)
        if PATTERN_REG.search(full_path):
            logging.info("Found dir: %s", full_path)
            templates.append(TraversalRecord(base_path=root,
                                             values_path=full_path,
                                             output_base_path=output_base_path,
                                             env=env,
                                             name=d,
                                             chart_name=chart_name,
                                             use_globals=use_globals))

for template in templates:
    template.helm_template()
    output.append(template)

# to set output, print to shell in following syntax
print("::set-output name=jobs:: " +
      json.dumps([i.model_dump() for i in output]))
