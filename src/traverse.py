import os
import re
import logging
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# get the input and convert it to int
env = os.environ.get("INPUT_ENVIRONMENT")
root_dir = os.environ.get("INPUT_DIRECTORY")
pattern = os.environ.get("INPUT_PATTERN")
rendered_path_input = os.environ.get("INPUT_RENDERED_PATH", "rendered").strip()
print("Rendered path: " + rendered_path_input)
output = []
if env and root_dir and pattern:
    pattern_reg = re.compile(pattern)  # Match all files ending with input pattern"
    logging.info("Pattern regex: %s", pattern_reg)
    for item in os.walk(root_dir):
        # print(item[0])
        item_path = Path(item[0])
        rendered_path = item_path.parent.absolute().as_posix() + "/" + rendered_path_input
        
        # logging.info("Checking file: " + item[0]+ " " + item[1]) 
        if pattern_reg.search(item_path.absolute().as_posix()) and os.path.exists(rendered_path):
            logging.info(rendered_path)
            logging.info("Found file: " + item[0] + " " + rendered_path)
            output.append(item[0])
else:
    exit('ERROR: the INPUT_NUM or INPUT_ENVIRONMENT is not provided')

# to set output, print to shell in following syntax
print("::set-output name=num_squared:: " + json.dumps(list(set(output))))