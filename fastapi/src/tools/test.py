#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Dev"
__desc__ = "Utility script to execute curl requests against the FastAPI service (batch or manual mode)."
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

## Resolve base directory (fastapi/)
BASE_DIR = Path(__file__).resolve().parents[2]

## Paths for input requests and output results
REQUESTS_FILE_PATH = BASE_DIR / "requests" / "requests.txt"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_FILE_PATH = RESULTS_DIR / "responses.txt"

def _read_requests() -> List[str]:
    """
        Read curl requests from the requests file

        Returns:
            list[str]: List of non-empty curl command strings
    """
    
    with open(REQUESTS_FILE_PATH, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

def execute_from_file() -> None:
    """
        Execute all curl requests from `requests.txt` sequentially

        Each response is written to `results/responses.txt
    """
    
    requests = _read_requests()

    ## Ensure output directory exists
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(RESULTS_FILE_PATH, "w", encoding="utf-8") as output:
        for index, command in enumerate(requests, start=1):
            output.write(f"===== Request {index} =====\n")
            output.write(f"Command: {command}\n")
            output.write("---------------------------\n")

            try:
                ## Execute curl command (kept split() to preserve original behavior)
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                )
                output.write(result.stdout + "\n")
            except Exception as exc:
                output.write(f"Execution error: {str(exc)}\n")

            output.write("\n")

    print(f"Results written to: {RESULTS_FILE_PATH}")

def execute_custom() -> None:
    """
        Prompt the user for a custom curl command and execute it

        The response is written to `results/responses.txt
    """
    
    command = input("Enter a full curl command:\n").strip()

    ## Ensure output directory exists
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(RESULTS_FILE_PATH, "w", encoding="utf-8") as output:
        output.write("===== Manual Request =====\n")
        output.write(f"{command}\n")
        output.write("---------------------------\n")

        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
            )
            output.write(result.stdout + "\n")
        except Exception as exc:
            output.write(f"Execution error: {str(exc)}\n")

    print(f"Result written to: {RESULTS_FILE_PATH}")

if __name__ == "__main__":

    ## Simple interactive menu (kept minimal for exam scope)
    print("1. Execute all requests from requests.txt")
    print("2. Enter a custom curl request")

    choice = input("Choice (1/2): ").strip()

    if choice == "1":
        execute_from_file()
    elif choice == "2":
        execute_custom()
    else:
        print("Invalid choice.")