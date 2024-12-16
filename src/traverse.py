import os
import subprocess
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
chart_dir = os.environ.get("INPUT_CHART")
rendered_path_input = os.environ.get("INPUT_RENDERED_PATH", "rendered").strip()
print("Rendered path: " + rendered_path_input)
output = []
job_dict = dict()
if env and root_dir and pattern and chart_dir:
    pattern_reg = re.compile(pattern)  # Match all files ending with input pattern"
    logging.info("Pattern regex: %s", pattern_reg)
    for item in os.walk(root_dir):
        # print(item[0])
        item_path = Path(item[0])
        env_item_path = item_path.absolute().as_posix()+ "/" + env
        rendered_path = item_path.parent.absolute().as_posix() + "/" + rendered_path_input
        
        # logging.info("Checking file: " + item[0]+ " " + item[1]) 
        if pattern_reg.search(env_item_path) and os.path.exists(rendered_path):
            
            logging.info("Found dir: " + env_item_path + " " + rendered_path)
            jobs_list = os.listdir(env_item_path)
            logging.info("Jobs list: " + str(jobs_list))
            for job in jobs_list:
                base_job_path = item_path.absolute().as_posix() + "/base/" + job
                job_path = env_item_path + "/" + job
                logging.info("Job path: " + job_path)
                job_rendered_path = rendered_path + "/"+env  +"/"  + job
                logging.info("Job rendered path: " + job_rendered_path)
                if os.path.exists(job_rendered_path):
                    logging.info("Job rendered path exists: " + job_rendered_path)
                    
                    job_dict[job] = dict()
                    job_dict[job]["rendered_path"] = job_rendered_path
                    job_dict[job]["base_path"] = base_job_path
                    job_dict[job]["env_path"] = job_path
                    base_values = base_job_path + "/" + [i if i.endswith(".yaml") else ""  for i in os.listdir(base_job_path)][0]
                    env_values = job_path + "/" + [i if i.endswith(".yaml") else ""  for i in os.listdir(job_path)][0]
                    helm_exec_string = f"helm template {job} {chart_dir} -f {base_values} -f {env_values} --output-dir {job_rendered_path}/"
                    job_dict[job]["helm_exec_string"] = helm_exec_string
                    logging.info(helm_exec_string)
                    res = subprocess.run(helm_exec_string, shell=True)
                    job_dict[job]["stdout"] = res.stdout
                    job_dict[job]["stderr"] = res.stderr
                    
                    # logging.info("Base values: " + str(base_values))
                else:
                    logging.info("Job rendered path does not exist: " + job_rendered_path)
else:
    exit('ERROR: the INPUT_NUM or INPUT_ENVIRONMENT is not provided')
print("Output: ")
for item in output:
    print(f"{item}")
    
# to set output, print to shell in following syntax
print("::set-output name=jobs:: " + json.dumps(job_dict))