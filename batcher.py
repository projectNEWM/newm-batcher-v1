import logging
import os

from flask import Flask
from loguru import logger

from src import yaml_file

###############################################################################
# Top level constants required for the batcher to run
###############################################################################

# load the environment configuration
config = yaml_file.read("config.yaml")

# Get the directory of the currently executing script
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.log')

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

if __name__ == '__main__':
    pass
