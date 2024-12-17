import os
import subprocess
import re
import logging
import json
from io import StringIO

from pathlib import Path
from models import TraversalRecord
# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def delete_empty_folders(root):

    deleted = set()
    
    for current_dir, subdirs, files in os.walk(root, topdown=False):

        still_has_subdirs = False
        for subdir in subdirs:
            if os.path.join(current_dir, subdir) not in deleted:
                still_has_subdirs = True
                break
    
        if not any(files) and not still_has_subdirs:
            os.rmdir(current_dir)
            deleted.add(current_dir)

    return deleted
# get the input and convert it to int
env = os.environ.get("INPUT_ENVIRONMENT")
root_dir = os.environ.get("INPUT_DIRECTORY")
pattern = os.environ.get("INPUT_PATTERN")
chart_dir = os.environ.get("INPUT_CHART")
rendered_path_input = os.environ.get("INPUT_RENDERED_PATH", "rendered").strip()
print("Rendered path: " + rendered_path_input)
output = []
job_dict = dict()
if env and root_dir and pattern and chart_dir:
    pattern_reg = re.compile(pattern)  # Match all files ending with input pattern"
    logging.info("Pattern regex: %s", pattern_reg)
    for item in os.walk(root_dir):
        item_path = Path(item[0])
        env_item_path = item_path.absolute().as_posix()
        jobs_list = os.listdir(env_item_path)
        rendered_path = f"{item_path.parent.absolute().as_posix()}/{rendered_path_input}"
        if pattern_reg.search(env_item_path) and os.path.exists(rendered_path):
            logging.info("Found dir: %s %s", env_item_path, rendered_path)
            logging.info("Jobs list: %s", str(jobs_list))
            for job in jobs_list:
                
                base_job_path = f"{env_item_path}/{job}/base.yaml"
                job_path = f"{env_item_path}/{job}/{env}.yaml"
                logging.info("BaseJob path: %s", base_job_path)
                logging.info("EnvJob path: %s", job_path)
                job_rendered_path = rendered_path + "/"+env  +"/"  + job
                logging.info("Job rendered path: %s", job_rendered_path)
                if os.path.exists(job_path):
                    logging.info("Job path exists: %s", job_path)
                    helm_exec_string = f"helm template {job} {chart_dir} -f {base_job_path} -f {job_path} --output-dir {job_rendered_path}"
                    t_record = TraversalRecord(base_path=base_job_path, env_path=job_path, helm_exec_string=helm_exec_string, rendered_path=job_rendered_path, name=job)
                    logging.info(helm_exec_string)
                    res = subprocess.run(helm_exec_string, shell=True, check=True)
                    t_record.stdout = str(res.stdout)
                    t_record.stderr = str(res.stderr)
                    job_dict[job] = t_record
                    res.check_returncode()
                    # walk the rendered path and mv the files to the correct location
                    for root, dirs, files in os.walk(job_rendered_path):
                        for file in files:
                            if file.endswith(".yaml"):
                                output_path = f"{job_rendered_path}/{file}"
                                os.rename(f"{root}/{file}", f"{output_path}")
                                output.append(output_path)
                    # delete empty folders
                    delete_empty_folders(job_rendered_path)
                    
                else:
                    logging.info("Job path does not exist: %s", job_path)
else:
    exit('ERROR: the INPUT_NUM or INPUT_ENVIRONMENT is not provided')
print("Output: ")
for item in set(output):
    print(f"{item}")
    
# to set output, print to shell in following syntax
print("::set-output name=jobs:: " + json.dumps([i.model_dump() for i in job_dict.values()]))