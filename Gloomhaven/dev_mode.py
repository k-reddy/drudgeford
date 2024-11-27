import signal
import subprocess
import time
from frontend_main import main as frontend_main


def main():
    print("===DEV MODE===")
    print("Starting server...")
    server_process = subprocess.Popen(
        ["python3", "main.py", "8000"],
    )

    # wait for server to start
    time.sleep(2)

    print("Starting client...")
    frontend_main(dev_mode=True)

    server_process.wait()


if __name__ == "__main__":
    main()
