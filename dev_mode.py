import signal
import subprocess
import time
import traceback
from drudgeford import main as drudgeford_main

"""
starts both the backend and 1 frontend locally
"""


def main():
    # signal handler for SIGINT
    signal.signal(signal.SIGINT, lambda: server_process.terminate())

    print("===DEV MODE===")
    print("Starting server...")
    server_process = subprocess.Popen(
        ["python3", "backend_main.py", "8000"],
    )

    # wait for server to start
    time.sleep(2)

    try:
        print("Starting client...")
        drudgeford_main(dev_mode=True)
    except Exception as e:
        print(f"Error occurred: {e}")
        print("Full traceback:")
        traceback.print_exc()
        server_process.terminate()

    server_process.wait()


if __name__ == "__main__":
    main()
