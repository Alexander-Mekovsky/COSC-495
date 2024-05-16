import configparser
def load_config(file_path, n=False):
    config = configparser.ConfigParser()
    if not n:
        config.read(file_path)
    return config

import csv
def load_from_csv(path, load_struct):
    with open(path, mode='r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            load_struct.Append(row['API'], row)
            
            
import os
import shutil
import logging
import time
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
            os.makedirs(path, exist_ok=True)
            logging.info(f"Directory created: {path}")
            return True
        except FileExistsError:
            logging.info(f"Directory already exists: {path}")
            return True
        except Exception as e:
            logging.error(f"Attempt {attempt} failed: {e}")
            time.sleep(retry_delay)
            attempt += 1
            if attempt > max_retries:
                logging.error(f"Failed to create directory after {max_retries} attempts: {path}")
                return False

def setup_project_directories(base_path, project_dirs):
    log_file_path = os.path.join(base_path, 'project_setup.log')
    # Set up logging with explicit handler
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file_path, 'a')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    created_dirs = []
    try:
        for dir_name in project_dirs:
            dir_path = os.path.join(base_path, dir_name)
            if create_directory(dir_path):
                created_dirs.append(dir_path)
            else:
                logging.error("Setup failed, unable to create required directories. Starting cleanup.")
                for created_dir in created_dirs:
                    try:
                        shutil.rmtree(created_dir)
                        logging.info(f"Deleted directory during cleanup: {created_dir}")
                    except Exception as e:
                        logging.error(f"Failed to delete {created_dir} during cleanup: {e}")
                return False, log_file_path
        return True, log_file_path
    finally:
        # Ensure that all handlers are closed and removed
        for h in logger.handlers[:]:
            h.close()
            logger.removeHandler(h)
        # Attempt to remove the log file if no directories were created successfully
        if not created_dirs:
            os.remove(log_file_path)