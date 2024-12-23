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
input_path = os.environ.get("INPUT_DIRECTORY").rstrip("/")
pattern = os.environ.get("INPUT_PATTERN")
chart_name = os.environ.get("INPUT_CHART")
rendered_path_input = os.environ.get("INPUT_RENDERED_PATH", "rendered").strip()
# Check if required inputs are provided
if not env or not input_path or not pattern or not chart_name:
    logging.error("Missing required input")
    sys.exit(1)
PATTERN_REG = re.compile(pattern)  # Match all files ending with input pattern"

output = list()
templates: List[TraversalRecord] = []
instance = os.path.basename(input_path)
for root, _, files in os.walk(input_path):
    # in root dir we have globals.yaml but in every other dir we have base, dev, prod...
    if len(files) > 0 and PATTERN_REG.search(root):
        logging.info("Found dir: %s", root)
        templates.append(TraversalRecord(input_path=input_path,
                                         env=env,
                                         instance=instance,
                                         values_path=root,
                                         chart_name=chart_name,
                                         helm_path=pattern,
                                         rendered_path=rendered_path_input))


for template in templates:
    template.helm_template()
    output.append(template)
    template.normalize_path()

# to set output, print to shell in following syntax
print("::set-output name=jobs:: " +
      json.dumps([i.model_dump() for i in output]))
