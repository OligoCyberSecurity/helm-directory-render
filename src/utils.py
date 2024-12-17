import os

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

def rename_rendered_files(job_rendered_path,output):
    # walk the rendered path and mv the files to the correct location
    for root, dirs, files in os.walk(job_rendered_path):
        for file in files:
            if file.endswith(".yaml"):
                output_path = f"{job_rendered_path}/{file}"
                os.rename(f"{root}/{file}", f"{output_path}")
                output.append(output_path)
    return output
