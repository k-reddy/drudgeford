from flask import Flask, send_file, render_template_string, jsonify, send_from_directory
import os
import subprocess
import uuid
import threading
from typing import Dict
from dataclasses import dataclass
import socket


@dataclass
class GameInstance:
    id: str
    port: int
    process: subprocess.Popen
    status: str


app = Flask(__name__)

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
    for port in range(start_port, start_port + num_ports):
        if is_port_available(port):
            return port
    return None


# Get the directory where the script is located
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
STATIC_DIR = os.path.join(CURRENT_DIR, "static")
CSS_FILE = os.path.join(CURRENT_DIR, "styles.css")
main_path = os.path.join(BASE_DIR, "main.py")


def run_game_server(game_id: str, port: int):
    """Run the game server in a separate process"""
    try:
        process = subprocess.Popen(
            ["python", main_path, str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        active_games[game_id] = GameInstance(
            id=game_id, port=port, process=process, status="running"
        )

        stdout, stderr = process.communicate()

        # Just mark game as ended, whether error or normal termination
        if game_id in active_games:
            active_games[game_id].status = (
                "ended" if process.returncode == 0 else "error"
            )
            if process.returncode != 0:
                print(f"Game {game_id} ended with error: {stderr.decode()}")

    except Exception as e:
        print(f"Error running game {game_id}: {str(e)}")
        if game_id in active_games:
            active_games[game_id].status = "error"


MAIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gloomhaven Game</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/static/styles.css">
    <script>
        async function hostGame() {
            const hostButton = document.getElementById('hostButton');
            const gameLinkDiv = document.getElementById('gameLink');
            
            hostButton.disabled = true;
            hostButton.textContent = 'STARTING GAME...';
            
            try {
                const response = await fetch('/host-game');
                const data = await response.json();
                
                if (data.success) {
                    const gameUrl = `${window.location.origin}/join/${data.game_id}`;
                    gameLinkDiv.innerHTML = `
                        <p>GO TO THIS LINK FOR START-UP INSTRUCTIONS:</p>
                        <a href="${gameUrl}" class="game-link-button">${gameUrl}</a>
                        <p>GAME PORT: ${data.port}</p>
                    `;
                    gameLinkDiv.style.display = 'block';
                } else {
                    alert('Failed to start game: ' + data.error);
                    hostButton.disabled = false;
                    hostButton.textContent = 'HOST GAME';
                }
            } catch (error) {
                alert('Error starting game');
                hostButton.disabled = false;
                hostButton.textContent = 'HOST GAME';
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>GLOOMHAVEN</h1>
        
        <p>WELCOME, ADVENTURER!</p>
        
        <div class="button-container">
            <button onclick="hostGame()" id="hostButton" class="host-button">
                HOST GAME
            </button>
            
            <a href="/download" class="download-button">
                DOWNLOAD GAME
            </a>
        </div>
        
        <div id="gameLink" class="game-link"></div>
        
        <div class="note">
            <strong>INSTRUCTIONS:</strong>
            <ol>
                <li>DOWNLOAD THE GAME CLIENT</li>
                <li>TO HOST: CLICK "HOST GAME" AND SHARE THE LINK</li>
                <li>TO JOIN: USE A SHARED GAME LINK</li>
            </ol>
        </div>
    </div>
</body>
</html>
"""

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
            <p>1. RUN YOUR GLOOMHAVEN FILE</p>
            <p>2. SET A NUMBER OF PLAYERS</p>
            <p>3. SHARE THE PORT NUMBER WITH YOUR FRIENDS</p>
            <p>4. TELL THEM TO RUN THEIR FILES AND JOIN THE ADVENTURE!</p>
        </div>
        <p>Game Status: RUNNING</p>
        <p>Game Port: {port}</p>
    </div>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(MAIN_HTML)


@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory(STATIC_DIR, path)


@app.route("/download")
def download():
    exe_path = "../frontend_main.dist/frontend_main.bin"
    return send_file(exe_path, as_attachment=True, download_name="gloomhaven.bin")


@app.route("/host-game")
def host_game():
    try:
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
        return jsonify({"success": False, "error": str(e)})


@app.route("/join/<game_id>")
def join_game(game_id):
    if game_id not in active_games:
        return render_template_string(ERROR_HTML), 404

    game = active_games[game_id]
    if game.status != "running":
        return render_template_string(ENDED_HTML), 400

    return render_template_string(JOIN_HTML.format(port=game.port))


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
        print(f"Error copying CSS file: {str(e)}")
        raise

    app.run(host="0.0.0.0", port=8000)
