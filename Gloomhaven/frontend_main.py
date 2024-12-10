import textwrap
from pyxel_ui.engine import PyxelEngine
from backend.utils.config import TEXT_WIDTH


def main(dev_mode=False):
    host = "13.59.128.25"

    if dev_mode:
        port = "8000"
        host = "localhost"
    else:
        port = input("Please enter the port number").strip()
        valid_ports = ["5000", "5001", "5002", "5003", "5004", "8000"]
        while port not in valid_ports:
            port = input("Please enter a valid port number")
    port = int(port)
    pyxel_view = PyxelEngine(port, host=host)
    pyxel_view.start()


if __name__ == "__main__":
    main()
