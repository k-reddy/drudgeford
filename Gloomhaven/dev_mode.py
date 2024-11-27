import signal
import subprocess
import time
from frontend_main import main as frontend_main


def main():
    # signal handler for SIGINT
    signal.signal(signal.SIGINT, lambda: server_process.terminate())

    print("===DEV MODE===")
    print("Starting server...")
    server_process = subprocess.Popen(
        ["python3", "main.py", "8000"],
    )

    # wait for server to start
    time.sleep(2)

    try:
        print("Starting client...")
        frontend_main(dev_mode=True)
    except:
        server_process.terminate()

    server_process.wait()


if __name__ == "__main__":
    main()
