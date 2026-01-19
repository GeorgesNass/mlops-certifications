'''
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Prod"
__desc__ = "Authorization tests for the sentiment API (v1/v2) using Docker Compose."
'''

import os
from typing import Optional

import requests

API_URL = "http://api-sentiment:8000"
LOG_FILE_PATH = "/logs/api_test.log"
LOG_ENV_VAR = "LOG"


def log_message(message: str) -> None:
    """
        Append log messages to a shared log file when logging is enabled

        Logging is controlled via the LOG environment variable. When LOG=1,
        messages are appended to the shared Docker volume

        Args:
            message (str): Message to be logged
    """
    
    ## Write logs only if explicitly enabled
    if os.environ.get(LOG_ENV_VAR) == "1":
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as file:
            file.write(message)


def run_test(
    endpoint: str,
    username: str,
    password: str,
    expected_status: int,
) -> None:
    """
        Run an authorization test against the API and validate the HTTP status code

        The function sends a GET request to the specified endpoint and checks
        whether the returned HTTP status code matches the expected one

        Args:
            endpoint (str): API endpoint path (e.g. "v1/sentiment")
            username (str): API username
            password (str): API password
            expected_status (int): Expected HTTP status code
    """
    
    ## Call the API endpoint
    response = requests.get(
        f"{API_URL}/{endpoint}",
        params={
            "username": username,
            "password": password,
            "sentence": "i love this product",
        },
        timeout=10,
    )

    status_code: Optional[int] = response.status_code
    test_status = (
        "SUCCESS" if status_code == expected_status else "FAILURE"
    )

    output = f"""
============================
    Authorization test
============================

Request done at "/{endpoint}"
| username="{username}"
| password="{password}"

Expected status = {expected_status}
Actual status   = {status_code}

==> {test_status}

"""
    print(output)
    log_message(output)

if __name__ == "__main__":
    ## Bob: only v1 endpoint should be authorized
    run_test("v1/sentiment", "bob", "builder", 200)
    run_test("v2/sentiment", "bob", "builder", 403)

    ## Alice: both v1 and v2 endpoints should be authorized
    run_test("v1/sentiment", "alice", "wonderland", 200)
    run_test("v2/sentiment", "alice", "wonderland", 200)
