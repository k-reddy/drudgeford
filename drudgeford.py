import argparse
import wx
from pyxel_ui.engine import PyxelEngine


def main(dev_mode=False):
    host = "13.59.128.25"

    if dev_mode:
        port = "8000"
        host = "localhost"
    else:
        app = wx.App()
        valid_ports = ["5000", "5001", "5002", "5003", "5004"]
        dialog = wx.SingleChoiceDialog(
            None, "Select a port:", "Port Selection", valid_ports
        )
        dialog.Raise()  # Brings window to front

        if dialog.ShowModal() == wx.ID_OK:
            port = dialog.GetStringSelection()
        else:
            return

        # port = input("Please enter the port number").strip()
        # valid_ports = ["5000", "5001", "5002", "5003", "5004", "8000"]
        # while port not in valid_ports:
        #     port = input("Please enter a valid port number")
    port = int(port)
    pyxel_view = PyxelEngine(port, host=host)
    pyxel_view.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    args = parser.parse_args()
    main(dev_mode=args.dev)
