import os
import time
import shutil
import logging

def create_directory(path, max_retries=3, retry_delay=2):
    """
    Attempts to create a directory with a specified number of retries.
    
    Args:
        path (str): The directory path to create.
        max_retries (int): Maximum number of retries if the directory creation fails.
        retry_delay (int): Seconds to wait between retries.
        
    Returns:
        bool: True if the directory was created, False otherwise.
    """
    attempt = 0
    while attempt <= max_retries:
        try:
            os.makedirs(path, exist_ok=True)  # exist_ok=True avoids error if dir exists
            logging.info(f"Directory created: {path}")
            return True
        except FileExistsError:
            logging.info(f"Directory already exists: {path}")
            return True  # Directory exists, considered a success.
        except Exception as e:
            logging.error(f"Attempt {attempt} failed: {e}")
            time.sleep(retry_delay)  # Wait before retrying
            attempt += 1
            if attempt > max_retries:
                logging.error(f"Failed to create directory after {max_retries} attempts: {path}")
                return False
            
def setup_project_directories(base_path, project_dirs):
    log_file_path = os.path.join(base_path, 'project_setup.log')
    logging.basicConfig(
        filename=log_file_path,  # Name of the log file
        filemode='a',  # Mode 'a' means append (add new logs to the end of the file)
        level=logging.INFO,  # Minimum level of logs to capture
        format='%(asctime)s - %(levelname)s - %(message)s'  # Format of log messages
    )
    created_dirs = []
    for dir_name in project_dirs:
        dir_path = os.path.join(base_path, dir_name)
        if create_directory(dir_path):
            created_dirs.append(dir_path)  # Track successfully created directories
        else:
            logging.error(f"Setup failed, unable to create required directories. Starting cleanup.")
            # Cleanup all created directories if any directory setup fails
            for created_dir in created_dirs:
                try:
                    shutil.rmtree(created_dir)
                    logging.info(f"Deleted directory during cleanup: {created_dir}")
                except Exception as e:
                    logging.error(f"Failed to delete {created_dir} during cleanup: {e}")
            return False, log_file_path
    os.remove(log_file_path)
    return True, None
    