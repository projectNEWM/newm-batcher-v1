import logging
import os

from flask import Flask
from loguru import logger

from src import yaml_file
from src.cli import query_protocol_parameters
from src.utility import create_folder_if_not_exists, parent_directory_path

###############################################################################
# Top level constants required for the batcher to run
###############################################################################

# load the environment configuration
config = yaml_file.read("config.yaml")

# Get the directory of the currently executing script
parent_dir = parent_directory_path()

# Log path
log_file_path = os.path.join(parent_dir, 'app.log')

# Configure log rotation with a maximum file size, retention, and log level
logger.add(
    log_file_path,
    rotation=config["max_log_file_size"],
    retention=config["max_num_log_files"],
    level=config["logging_level"]
)

# Initialize Flask
app = Flask(__name__)
# Disable Flask's default logger
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# create the tmp directory if it doesn't exist already
tmp_folder = os.path.join(parent_dir, "tmp")
create_folder_if_not_exists(tmp_folder)

query_protocol_parameters(config["socket_path"], os.path.join(parent_dir, "tmp/protocol.json"), config["network"])

if __name__ == '__main__':
    pass
