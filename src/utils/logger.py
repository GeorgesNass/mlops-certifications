'''
	__author__ = "Georges Nassopoulos"
	__copyright__ = None
	__version__ = "1.0.0"
	__email__ = "georges.nassopoulos@gmail.com"
	__status__ = "Dev"
	__desc__ = "Centralized logging utility for the project"
'''

import logging
import time
from functools import wraps
import os

def get_logger(name: str = "dvc_project", log_file: str = "logs/pipeline.log") -> logging.Logger:
    """
	Initializes and returns a logger instance with both console and file output
    """

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    ## Avoid duplicate handlers if the logger is reused
    ## ... enriched with timestamp, level/depth of file, file name and finally log message
    if not logger.handlers:
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        ## Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        ## File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def log_step(logger):
    """
	Decorator to log the execution time and errors of a function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Starting function `{func.__name__}`...")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"Finished `{func.__name__}` in {duration:.2f} seconds")
                return result
            except Exception as e:
                logger.exception(f"Error in `{func.__name__}`: {str(e)}")
                raise e
        return wrapper
    return decorator

