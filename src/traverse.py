import os

import re
import sys
import logging
import json
from pathlib import Path
from models import TraversalRecord
from utils import delete_empty_folders, rename_rendered_files
# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# get the input and convert it to int
env = os.environ.get("INPUT_ENVIRONMENT")
root_dir = os.environ.get("INPUT_DIRECTORY")
pattern = os.environ.get("INPUT_PATTERN")
chart_dir = os.environ.get("INPUT_CHART")
rendered_path_input = os.environ.get("INPUT_RENDERED_PATH", "rendered").strip()
# Check if required inputs are provided
if not env or not root_dir or not pattern or not chart_dir:
    logging.error("Missing required input")
    sys.exit(1)
PATTERN_REG = re.compile(pattern)  # Match all files ending with input pattern"

output = list()
for item in os.walk(root_dir):
    item_path = Path(item[0])
    env_item_path = item_path.absolute().as_posix()
    jobs_list = os.listdir(env_item_path)
    rendered_path = f"{item_path.parent.absolute().as_posix()
                       }/{rendered_path_input}"
    if PATTERN_REG.search(env_item_path) and os.path.exists(rendered_path):
        logging.info("Found dir: %s %s", env_item_path, rendered_path)
        for job in jobs_list:
            t_record = TraversalRecord(base_path=f"{env_item_path}/{job}/base.yaml", env_path=f"{env_item_path}/{
                                       job}/{env}.yaml", rendered_path=f"{rendered_path}/{env}/{job}", name=job, chart_dir=chart_dir)
            t_record.helm_template()
            # walk the rendered path and mv the files to the correct location
            rename_rendered_files(t_record.rendered_path, [])
            # delete empty folders
            delete_empty_folders(t_record.rendered_path)
            output.append(t_record)

# to set output, print to shell in following syntax
print("::set-output name=jobs:: " +
      json.dumps([i.model_dump() for i in output]))
