from flask import (
    Flask,
    send_file,
    render_template,
    jsonify,
    send_from_directory,
    request,
)
import os
import time
import subprocess
import uuid
import threading
from typing import Dict
from dataclasses import dataclass
from collections import defaultdict
import socket
from logger import GameLogger


@dataclass
class GameInstance:
    id: str
    port: int
    process: subprocess.Popen
    status: str


class Lobby:
    def __init__(self, current_dir):
        # get some useful directory and file paths
        self.current_dir = current_dir
        self.base_dir = os.path.dirname(current_dir)
        self.static_dir = os.path.join(current_dir, "static")
        self.css_file = os.path.join(current_dir, "styles.css")
        self.backend_main_path = os.path.join(self.base_dir, "backend_main.py")

        # lets us keep track of attemps per IP
        # (resets everytime we reset the server)
        self.ip_attempts = defaultdict(list)  # IP -> list of timestamps
        self.app = Flask(__name__)
        self.logger = GameLogger()

        # Store active games and their info
        self.active_games: Dict[str, GameInstance] = {}

    def is_port_available(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
                return True
            except socket.error:
                return False

    def get_available_port(self, start_port: int = 5000, num_ports: int = 5) -> int:
        used_ports = len(self.active_games)
        self.logger.log_port_allocation(
            None, num_ports, used_ports
        )  # Log current usage
        for port in range(start_port, start_port + num_ports):
            if self.is_port_available(port):
                self.logger.log_port_allocation(
                    port, num_ports, used_ports + 1
                )  # Log allocation
                return port
        return None

    def run_game_server(self, game_id: str, port: int):
        """Run the game server in a separate process"""
        try:
            process = subprocess.Popen(
                ["python", self.backend_main_path, str(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.active_games[game_id] = GameInstance(
                id=game_id, port=port, process=process, status="running"
            )
            self.logger.log_game_start(game_id, port)

            stdout, stderr = process.communicate()

            # Just mark game as ended, whether error or normal termination
            if game_id in self.active_games:
                status = "ended" if process.returncode == 0 else "error"
                self.active_games[game_id].status = status
                if status == "error":
                    error_msg = stderr.decode()
                    self.logger.log_game_end(game_id, status, error_msg)
                    print(f"Game {game_id} ended with error: {stderr.decode()}")
                else:
                    self.logger.log_game_end(game_id, status)  # Log normal end

        except Exception as e:
            error_msg = str(e)
            self.logger.log_game_error(game_id, f"Error running game: {error_msg}")
            print(f"Error running game {game_id}: {str(e)}")
            if game_id in self.active_games:
                self.active_games[game_id].status = "error"
                self.logger.log_game_end(game_id, "error", error_msg)

    def has_started_too_many_games(self, ip) -> bool:
        current_time = time.time()
        # Clean up old attempts (older than 24 hours)
        self.ip_attempts[ip] = [
            t for t in self.ip_attempts[ip] if current_time - t < 86400
        ]  # 24 hours in seconds

        # Check daily limit
        if len(self.ip_attempts[ip]) >= 20:
            self.logger.log_rate_limit(ip)
            return True
        else:
            self.ip_attempts[ip].append(current_time)
            return False

    def setup_routes(self):
        self.app.route("/")(self.home)
        self.app.route("/static/<path:path>")(self.send_static)
        self.app.route("/download")(self.download)
        self.app.route("/host-game")(self.host_game)
        self.app.route("/join/<game_id>")(self.join_game)
        self.app.route("/tutorial")(self.tutorial)

    # route handlers
    def home(self):
        return render_template("main.html")

    def send_static(self, path):
        return send_from_directory(self.static_dir, path)

    def download(self):
        exe_path = "../executable_packaging/executable_file/drudgeford.dmg"
        return send_file(
            exe_path,
            as_attachment=True,
            download_name="drudgeford.dmg",
            mimetype="application/x-apple-diskimage",
        )

    def host_game(self):
        try:
            # first check if this ip has tried to start too many games
            if self.has_started_too_many_games(request.remote_addr):
                return jsonify(
                    {
                        "success": False,
                        "error": "Daily game creation limit reached (20 games per day)",
                    }
                )
            port = self.get_available_port()
            if port is None:
                return jsonify(
                    {
                        "success": False,
                        "error": "No ports available. Please try again later.",
                    }
                )

            game_id = str(uuid.uuid4())
            thread = threading.Thread(target=self.run_game_server, args=(game_id, port))
            thread.start()

            return jsonify({"success": True, "game_id": game_id, "port": port})
        except Exception as e:
            self.logger.log_general_error(str(e))
            return jsonify({"success": False, "error": str(e)})

    def join_game(self, game_id):
        if game_id not in self.active_games:
            return render_template("error.html"), 404

        game = self.active_games[game_id]
        if game.status != "running":
            return render_template("ended.html"), 400

        return render_template("join.html", port=game.port)

    def tutorial(self):
        return render_template("tutorial.html")

    def setup_static_files(self):
        os.makedirs(self.static_dir, exist_ok=True)

        try:
            with open(self.css_file, "r") as source:
                css_content = source.read()

            css_destination = os.path.join(self.static_dir, "styles.css")
            with open(css_destination, "w") as dest:
                dest.write(css_content)

            print(f"Successfully copied CSS from {self.css_file} to {css_destination}")
        except Exception as e:
            self.logger.log_general_error(f"Server failed to start: {str(e)}")
            print(f"Error starting up: {str(e)}")
            raise

    def run(self, host="0.0.0.0", port=8000):
        self.setup_static_files()
        self.setup_routes()
        self.app.run(host=host, port=port)


if __name__ == "__main__":
    folder_path = os.path.dirname(os.path.abspath(__file__))
    lobby = Lobby(folder_path)
    lobby.run()
