import logging
import multiprocessing
import os
import subprocess
import sys

from flask import Flask, request
from loguru import logger

from src import yaml_file
from src.aggregate import Aggregate
from src.cli import get_latest_block_number, query_protocol_parameters
from src.daemon import create_toml_file
from src.db_manager import DbManager
from src.io_manager import IOManager
from src.sorting import Sorting
from src.utility import create_folder_if_not_exists, parent_directory_path

###############################################################################
# Top level config required for the batcher to run
###############################################################################

# load the environment configuration
config = yaml_file.read("config.yaml")

# start the sqlite3 database
db = DbManager()
db.initialize(config)

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

# get the current protocol parameters
query_protocol_parameters(config["socket_path"], os.path.join(parent_dir, "tmp/protocol.json"), config["network"])

# the latest block at start time
latest_block_number = get_latest_block_number(config['socket_path'], 'tmp/tip.json', config['network'])


@app.route('/webhook', methods=['POST'])
def webhook():
    """The webhook for oura. This is where all the db logic needs to go.

    Returns:
        str: A success/failure string
    """
    data = request.get_json()  # Get the JSON data from the request
    block_number = data['context']['block_number']
    block_hash = data['context']['block_hash']
    block_slot = data['context']['slot']

    # Get the current status
    sync_status = db.status.read()

    # What the db thinks is the current block is
    db_number = sync_status["block_number"]

    # check for a change in the block number
    if block_number != db_number:
        # the block number has changed so update the db
        db.status.update(block_number, block_hash, block_slot)
        try:
            # are we still syncing?
            if int(block_number) > latest_block_number:
                # we are synced, start fulfilling orders
                logger.debug(f"Block: {block_number}")
                # debug mode will not sort and aggregate orders to fulfill
                # it will sync the db only
                if config["debug_mode"] is False:
                    # sort first
                    sorted_queue = Sorting.fifo(db)
                    # then batch
                    Aggregate.orders(db, sorted_queue, config, logger)
            else:
                # we are syncing
                tip_difference = latest_block_number - int(block_number)
                logger.debug(f"Blocks til tip: {tip_difference}")
        except TypeError:
            # incase block number some how isnt a number
            pass

    # try to sync inputs and outputs
    try:
        variant = data['variant']

        # if a rollback occurs we need to handle it somehow
        if variant == 'RollBack':
            logger.debug(data)
            # how do we handle it?
            logger.critical(f"ROLLBACK: {block_number}")

        # tx inputs
        if variant == 'TxInput':
            IOManager.handle_input(db, data, logger)

        # tx outputs
        if variant == 'TxOutput':
            IOManager.handle_output(db, config, data, logger)

    # not the right variant so pass it
    except Exception:
        pass

    # if we are here then everything in the webhook is good
    return 'Webhook Successful'


def run_daemon():
    """
    Run the Oura daemon by searching for the bin in the home directory.
    """
    program_name = "oura"
    # The base directory where user home directories are typically located
    search_directory = "/home"

    # List all subdirectories within the search directory
    user_directories = [
        os.path.join(search_directory, user)
        for user in os.listdir(search_directory)
        if os.path.isdir(os.path.join(search_directory, user))]

    # Iterate through user home directories and check if the program exists
    program_path = ''
    for user_directory in user_directories:
        program_path = os.path.join(
            user_directory, ".cargo", "bin", program_name)
        if os.path.exists(program_path):
            break
        else:
            logger.error("Oura Not Found On System")
            sys.exit(1)
    # run it
    subprocess.run([program_path, 'daemon', '--config', 'daemon.toml'])


def flask_process(start_event: multiprocessing.Event):
    """Start and wait for the flask app to begin.

    Args:
        start_event (Event): The event to wait to complete.
    """
    start_event.wait()  # Wait until the start event is set
    app.run(host='0.0.0.0', port=8008)


def start_processes():
    """
    Start the batcher processes as a multiprocessing event.
    """
    # create the daemon toml file
    sync_status = db.status.read()
    # start log
    logger.info(f"Loading Block {sync_status['block_number']} @ Slot {sync_status['timestamp']} With Hash {sync_status['block_hash']}")

    create_toml_file('daemon.toml', config['socket_path'], sync_status['timestamp'], sync_status['block_hash'], config['delay_depth'])

    # start the processes as events in order
    start_event = multiprocessing.Event()

    # start the webhook
    flask_proc = multiprocessing.Process(
        target=flask_process, args=(start_event,))
    flask_proc.start()

    # start oura daemon
    daemon_proc = multiprocessing.Process(target=run_daemon)
    daemon_proc.start()

    # Set the start event to indicate that the Flask app is ready to run
    start_event.set()
    try:
        # Wait for both processes to complete
        flask_proc.join()
        daemon_proc.join()
    except KeyboardInterrupt:
        # Handle KeyboardInterrupt (CTRL+C)
        logger.error("KeyboardInterrupt detected, terminating processes...")
        # clean up the db
        db.cleanup()
        # terminate and join
        flask_proc.terminate()
        daemon_proc.terminate()
        flask_proc.join()
        daemon_proc.join()


if __name__ == '__main__':
    # start the batcher processes
    logger.info("Starting Batcher...")
    start_processes()
