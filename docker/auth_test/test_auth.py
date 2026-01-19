'''
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Prod"
__desc__ = "Authentication tests for the permissions endpoint using Docker Compose."
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
    username: str,
    password: str,
    expected_status: int,
) -> None:
    """
        Run an authentication test against the permissions endpoint

        The function sends a GET request to the `/permissions` endpoint and
        validates that the returned HTTP status code matches the expected one

        Args:
            username (str): API username
            password (str): API password
            expected_status (int): Expected HTTP status code
    """
    
    ## Call the permissions endpoint
    response = requests.get(
        f"{API_URL}/permissions",
        params={
            "username": username,
            "password": password,
        },
        timeout=10,
    )

    status_code: Optional[int] = response.status_code
    test_status = (
        "SUCCESS" if status_code == expected_status else "FAILURE"
    )

    output = f"""
============================
    Authentication test
============================

Request done at "/permissions"
| username="{username}"
| password="{password}"

Expected result = {expected_status}
Actual result   = {status_code}

==> {test_status}

"""
    print(output)
    log_message(output)

if __name__ == "__main__":
    ## Valid user with full access
    run_test("alice", "wonderland", 200)

    ## Valid user with limited access
    run_test("bob", "builder", 200)

    ## Invalid user credentials
    run_test("clementine", "mandarine", 403)
