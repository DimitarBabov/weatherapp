import os
import time
import shutil  # For moving files
import schedule
from datetime import datetime, timedelta
import threading

# Directories for the PNG and GFS data
PNG_DIR = "/tmp/png_data"
GFS_DIR = "/tmp/gfs_data"
RECYCLE_BIN_DIR = "/tmp/recycle_bin"

# How many days to keep files in the recycle_bin before deleting them
DAYS_TO_KEEP_FILES = 2  # Example: Keep files in recycle_bin for 2 days

# Ensure the recycle bin and its subfolders exist
def ensure_recycle_bin():
    os.makedirs(RECYCLE_BIN_DIR, exist_ok=True)
   

def move_files_to_recycle_bin(src_dir, dest_dir):
    """
    Move all files from src_dir to dest_dir (recycle bin).
    """
    for filename in os.listdir(src_dir):
        file_path = os.path.join(src_dir, filename)
        if os.path.isfile(file_path):
            dest_file_path = os.path.join(dest_dir, filename)
            print(f"Moving {file_path} to {dest_file_path}")
            shutil.move(file_path, dest_file_path)

def move_files_with_prefix_to_recycle_bin(src_dir, dest_dir, prefix):
    """
    Move files from src_dir to dest_dir (recycle bin) if the filename starts with the given prefix.
    
    Args:
    - src_dir: Source directory containing files to move.
    - dest_dir: Destination directory (recycle bin).
    - prefix: The string prefix to filter filenames.
    """
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)  # Ensure the destination directory exists

    for filename in os.listdir(src_dir):
        # Check if the filename starts with the specified prefix
        if filename.startswith(prefix):
            file_path = os.path.join(src_dir, filename)
            if os.path.isfile(file_path):
                dest_file_path = os.path.join(dest_dir, filename)
                print(f"Moving {file_path} to {dest_file_path}")
                shutil.move(file_path, dest_file_path)



def delete_old_files(directory):
    """
    Deletes all files in the specified directory.
    """
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            print(f"Deleting file: {file_path}")
            os.remove(file_path)


def cleanup_job():
    """Job to move files to recycle_bin and delete old files from recycle_bin."""
    print(f"Running cleanup job at {datetime.now()}")

    # Ensure recycle_bin and subfolders exist
    ensure_recycle_bin()

    # Move old files to recycle_bin
    move_files_to_recycle_bin(PNG_DIR, RECYCLE_BIN_DIR)
    

    # Delete files in the recycle_bin older than DAYS_TO_KEEP_FILES
    delete_old_files(RECYCLE_BIN_DIR)
    

def cleanup_old_param_files(param_prefix):
    """
    Job to move files starting with param_prefix to recycle_bin and delete old files from recycle_bin.
    
    Args:
    - param_prefix: The prefix to identify the files to move and delete.
    """
    print(f"Running cleanup job for '{param_prefix}' files at {datetime.now()}")

    # Ensure recycle_bin directories exist
    ensure_recycle_bin()

    # Move files starting with param_prefix to recycle_bin
    move_files_with_prefix_to_recycle_bin(PNG_DIR, RECYCLE_BIN_DIR, param_prefix)
    move_files_with_prefix_to_recycle_bin(GFS_DIR, RECYCLE_BIN_DIR, param_prefix)


def run_scheduler():
    """Runs the scheduler in a separate thread."""
    # Schedule the cleanup job to run every day at midnight
    schedule.every().day.at("00:00").do(cleanup_job)

    while True:
        schedule.run_pending()
        time.sleep(1)

# Run the scheduler in a background thread
def start_scheduler():
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True  # So it doesn't block Flask from shutting down
    scheduler_thread.start()

