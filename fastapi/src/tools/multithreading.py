#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Dev"
__desc__ = "Parallel execution of curl requests using multiprocessing (exam-oriented load testing tool)."
"""

from __future__ import annotations

import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path
from typing import List, Tuple

## Resolve base directory (fastapi/)
BASE_DIR = Path(__file__).resolve().parents[2]

## Path to the file containing curl commands
REQUESTS_FILE_PATH = BASE_DIR / "requests" / "requests.txt"

def read_commands() -> List[str]:
    """
        Read curl commands from the requests file

        Returns:
            list[str]: List of non-empty curl command strings
    """
    
    with open(REQUESTS_FILE_PATH, "r", encoding="utf-8") as file:
        ## Strip empty lines and whitespace
        return [line.strip() for line in file if line.strip()]

def execute_command(command: str) -> Tuple[float, str]:
    """
        Execute a single curl command and measure execution time

        Args:
            command (str): Full curl command as a string

        Returns:
            tuple:
                - float: Elapsed execution time in seconds
                - str: Standard output of the command
    """
    
    start_time = time.time()

    ## Execute the command (split is kept to preserve original behavior)
    result = subprocess.run(
        command.split(),
        capture_output=True,
        text=True,
    )

    end_time = time.time()

    return end_time - start_time, result.stdout.strip()

def _command_wrapper(args: Tuple[int, List[str]]) -> Tuple[float, str]:
    """
        Wrapper used by multiprocessing Pool

        This function selects a command based on the index to avoid index overflow

        Args:
            args (tuple): (index, list_of_commands)

        Returns:
            tuple: Output of execute_command()
    """
    
    index, commands = args
    command = commands[index % len(commands)]
    return execute_command(command)

def overflow_requests(mode: str = "sync", parallelism: int = 5) -> None:
    """
        Execute multiple curl requests in parallel using multiprocessing

        Notes:
            - The `mode` parameter is kept for compatibility with the original script
            - Both 'sync' and 'async' modes rely on multiprocessing here
              (this is NOT asyncio-based asynchronous I/O)

        Args:
            mode (str): Symbolic execution mode ('sync' or 'async')
            parallelism (int): Number of parallel processes to spawn
    """
    
    ## Read commands from file
    commands = read_commands()

    if not commands:
        print("No curl commands found in requests.txt")
        return

    ## Build arguments for multiprocessing
    args = [(i, commands) for i in range(parallelism)]

    ## Execute commands in parallel
    with Pool(parallelism) as pool:
        results = pool.map(_command_wrapper, args)

    ## Display results
    for index, (elapsed, output) in enumerate(results, start=1):
        print(f"--- Request {index} ---")
        print(f"Response time: {elapsed:.3f}s")
        print(output)
        print()

if __name__ == "__main__":
    ## Parse CLI arguments (kept minimal for exam scope)
    selected_mode = sys.argv[1] if len(sys.argv) > 1 else "sync"
    selected_parallelism = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    overflow_requests(selected_mode, selected_parallelism)