'''
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Prod"
__desc__ = "Content tests for the sentiment API (v1/v2) using Docker Compose."
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

def run_sentiment_test(
    endpoint: str,
    username: str,
    password: str,
    sentence: str,
    expected_sign: str,
) -> None:
    """
        Run a sentiment test against the API and validate the result sign

        The function sends a GET request to the sentiment endpoint, extracts
        the returned score, and checks whether its sign matches the expected
        sentiment (positive or negative)

        Args:
            endpoint (str): API endpoint path (e.g. "v1/sentiment")
            username (str): API username
            password (str): API password
            sentence (str): Input sentence to analyze
            expected_sign (str): Expected sentiment sign ("positive" or "negative")
    """
    
    ## Call the API endpoint
    response = requests.get(
        f"{API_URL}/{endpoint}",
        params={
            "username": username,
            "password": password,
            "sentence": sentence,
        },
        timeout=10,
    )

    score: Optional[float]
    try:
        result = response.json()
        score = result.get("score", 0)
    except Exception:
        score = None

    ## Evaluate test status based on expected sentiment
    if expected_sign == "positive":
        test_status = "SUCCESS" if score is not None and score > 0 else "FAILURE"
    elif expected_sign == "negative":
        test_status = "SUCCESS" if score is not None and score < 0 else "FAILURE"
    else:
        test_status = "FAILURE"

    output = f"""
============================
      Content test
============================

Request done at "/{endpoint}"
| username="{username}"
| password="{password}"
| sentence="{sentence}"

Expected sentiment = {expected_sign}
Returned score     = {score}

==> {test_status}

"""
    print(output)
    log_message(output)

if __name__ == "__main__":
    ## Test two sentences (positive and negative) with Bob for v1
    run_sentiment_test(
        "v1/sentiment",
        "bob",
        "builder",
        "life is beautiful",
        "positive",
    )
    run_sentiment_test(
        "v1/sentiment",
        "bob",
        "builder",
        "that sucks",
        "negative",
    )

    ## Test two sentences (positive and negative) with Alice for v2 (authorized)
    run_sentiment_test(
        "v2/sentiment",
        "alice",
        "wonderland",
        "life is beautiful",
        "positive",
    )
    run_sentiment_test(
        "v2/sentiment",
        "alice",
        "wonderland",
        "that sucks",
        "negative",
    )
