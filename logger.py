import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set to lowest level, handlers will filter

    # Create formatters
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Set console log level
    console_handler.setFormatter(console_formatter)

    # Create file handler for individual module logs
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    file_handler = RotatingFileHandler(
        filename=os.path.join(log_directory, f"{name}.log"),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)  # Set file log level
    file_handler.setFormatter(file_formatter)

    # Create file handler for global log
    global_file_handler = RotatingFileHandler(
        filename=os.path.join(log_directory, "global.log"),
        maxBytes=50*1024*1024,  # 50MB
        backupCount=10
    )
    global_file_handler.setLevel(logging.DEBUG)  # Set global file log level
    global_file_handler.setFormatter(file_formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(global_file_handler)

    return logger

# Set up a global logger
global_logger = logging.getLogger('global')
global_logger.setLevel(logging.DEBUG)

# Add the global file handler to the global logger
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
global_file_handler = RotatingFileHandler(
    filename=os.path.join(log_directory, "global.log"),
    maxBytes=50*1024*1024,  # 50MB
    backupCount=10
)
global_file_handler.setLevel(logging.DEBUG)
global_file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
global_file_handler.setFormatter(global_file_formatter)
global_logger.addHandler(global_file_handler)

def log_globally(level, message):
    global_logger.log(level, message)