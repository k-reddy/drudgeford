from flask import (
    Flask,
    send_file,
    render_template_string,
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


app = Flask(__name__)
logger = GameLogger()
# Store active games and their info
active_games: Dict[str, GameInstance] = {}


def is_port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("localhost", port))
            return True
        except socket.error:
            return False


def get_available_port(start_port: int = 5000, num_ports: int = 5) -> int:
    used_ports = len(active_games)
    logger.log_port_allocation(None, num_ports, used_ports)  # Log current usage
    for port in range(start_port, start_port + num_ports):
        if is_port_available(port):
            logger.log_port_allocation(
                port, num_ports, used_ports + 1
            )  # Log allocation
            return port
    return None


# Get the directory where the script is located
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
STATIC_DIR = os.path.join(CURRENT_DIR, "static")
CSS_FILE = os.path.join(CURRENT_DIR, "styles.css")
backend_main_path = os.path.join(BASE_DIR, "backend_main.py")


def run_game_server(game_id: str, port: int):
    """Run the game server in a separate process"""
    try:
        process = subprocess.Popen(
            ["python", backend_main_path, str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        active_games[game_id] = GameInstance(
            id=game_id, port=port, process=process, status="running"
        )
        logger.log_game_start(game_id, port)

        stdout, stderr = process.communicate()

        # Just mark game as ended, whether error or normal termination
        if game_id in active_games:
            status = "ended" if process.returncode == 0 else "error"
            active_games[game_id].status = status
            if status == "error":
                error_msg = stderr.decode()
                logger.log_game_end(game_id, status, error_msg)
                print(f"Game {game_id} ended with error: {stderr.decode()}")
            else:
                logger.log_game_end(game_id, status)  # Log normal end

    except Exception as e:
        error_msg = str(e)
        logger.log_game_error(game_id, f"Error running game: {error_msg}")
        print(f"Error running game {game_id}: {str(e)}")
        if game_id in active_games:
            active_games[game_id].status = "error"
            logger.log_game_end(game_id, "error", error_msg)


ERROR_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Game Not Found</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
    <div class="container error-container">
        <h1 class="error-heading">GAME NOT FOUND</h1>
        <p>This game session no longer exists or has ended.</p>
    </div>
</body>
</html>
"""

ENDED_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Game Ended</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
    <div class="container error-container">
        <h1 class="error-heading">GAME HAS ENDED</h1>
        <p>This game session has already ended.</p>
    </div>
</body>
</html>
"""

JOIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Join Game</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
    <div class="container">
        <h1 class="success-heading">JOIN GAME</h1>
        <div class="note">
            <strong>INSTRUCTIONS:</strong>
            <p>1. RUN YOUR DOWNLOADED DRUDGEFORD APP</p>
            <p>2. SET A NUMBER OF PLAYERS</p>
            <p>3. SHARE THE PORT NUMBER WITH YOUR FRIENDS</p>
            <p>4. TELL THEM TO RUN THEIR APPS AND JOIN THE ADVENTURE!</p>
        </div>
        <p>Game Status: RUNNING</p>
        <p>Game Port: {port}</p>
    </div>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template("main.html")


@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory(STATIC_DIR, path)


@app.route("/download")
def download():
    exe_path = "../executable_packaging/executable_file/drudgeford.dmg"
    return send_file(
        exe_path,
        as_attachment=True,
        download_name="drudgeford.dmg",
        mimetype="application/x-apple-diskimage",
    )


# create limits of number of games hosted per IP
# resets every time we reset this script, which is fine b/c we just
# are wary of spam bots
ip_attempts = defaultdict(list)  # IP -> list of timestamps


def has_started_too_many_games(ip) -> bool:
    current_time = time.time()
    # Clean up old attempts (older than 24 hours)
    ip_attempts[ip] = [
        t for t in ip_attempts[ip] if current_time - t < 86400
    ]  # 24 hours in seconds

    # Check daily limit
    if len(ip_attempts[ip]) >= 20:
        logger.log_rate_limit(ip)
        return True
    else:
        ip_attempts[ip].append(current_time)
        return False


@app.route("/host-game")
def host_game():
    try:
        # first check if this ip has tried to start too many games
        if has_started_too_many_games(request.remote_addr):
            return jsonify(
                {
                    "success": False,
                    "error": "Daily game creation limit reached (20 games per day)",
                }
            )
        port = get_available_port()
        if port is None:
            return jsonify(
                {
                    "success": False,
                    "error": "No ports available. Please try again later.",
                }
            )

        game_id = str(uuid.uuid4())
        thread = threading.Thread(target=run_game_server, args=(game_id, port))
        thread.start()

        return jsonify({"success": True, "game_id": game_id, "port": port})
    except Exception as e:
        logger.log_general_error(str(e))
        return jsonify({"success": False, "error": str(e)})


@app.route("/join/<game_id>")
def join_game(game_id):
    if game_id not in active_games:
        return render_template_string(ERROR_HTML), 404

    game = active_games[game_id]
    if game.status != "running":
        return render_template_string(ENDED_HTML), 400

    return render_template_string(JOIN_HTML.format(port=game.port))


@app.route("/tutorial")
def tutorial():
    return render_template("tutorial.html")


if __name__ == "__main__":
    # Create static folder if it doesn't exist
    os.makedirs(STATIC_DIR, exist_ok=True)

    # Write CSS file
    try:
        with open(CSS_FILE, "r") as source:
            css_content = source.read()

        css_destination = os.path.join(STATIC_DIR, "styles.css")
        with open(css_destination, "w") as dest:
            dest.write(css_content)

        print(f"Successfully copied CSS from {CSS_FILE} to {css_destination}")
    except Exception as e:
        logger.log_general_error(f"Server failed to start: {str(e)}")
        print(f"Error starting up: {str(e)}")
        raise

    app.run(host="0.0.0.0", port=8000)
