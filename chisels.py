#!/usr/bin/env python3

import subprocess
import signal
import sys
import threading

# Color definitions
RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Lists to keep track of subprocesses and threads
processes = []
threads = []

def signal_handler(sig, frame):
    """ Handle Ctrl+C and send the signal to all subprocesses """
    for p in processes:
        p.send_signal(signal.SIGINT)
    sys.exit(0)

def read_output(pipe, color):
    """ Read lines from a pipe and print them with the given color. """
    for line in iter(pipe.readline, b''):
        sys.stdout.write(color + line.decode() + RESET)
    pipe.close()

def execute_command(cmd):
    """ Execute a command and print its output with colors. """
    try:
        p = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(p)

        # Use threads to read stdout and stderr to prevent blocking
        stdout_thread = threading.Thread(target=read_output, args=(p.stdout, GREEN))
        stderr_thread = threading.Thread(target=read_output, args=(p.stderr, RED))

        threads.append(stdout_thread)
        threads.append(stderr_thread)

        stdout_thread.start()
        stderr_thread.start()

    except Exception as e:
        sys.stdout.write(BLUE + str(e) + RESET)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./script_name.py filename.txt")
        sys.exit(1)

    filename = sys.argv[1]

    # Register the Ctrl+C signal handler
    signal.signal(signal.SIGINT, signal_handler)

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                print(BLUE + "Executing: " + line + RESET)
                execute_command(line)

    # Wait for all threads and processes to finish
    for t in threads:
        t.join()
    
    for p in processes:
        p.wait()

