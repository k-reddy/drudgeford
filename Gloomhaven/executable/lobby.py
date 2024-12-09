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
    <title>Drudgeford Game</title>
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

            <a href="/tutorial" class="tutorial-button">
                LEARN TO PLAY
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

TUTORIAL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>How to Play - Gloomhaven</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/static/styles.css">
    <script>
        let currentSlide = 0;
        const slides = [
            {
                image: "/static/help_images/log.png",
                text: "WELCOME TO DRUDGEFORD!<br><br>Drudgeford is a turn-based, dungeon-crawling, cooperative strategy game.<br><br>When you enter the game, you'll see a screen like this. The <span style='color: #FF1493'>log</span> will tell you what each character does on their turn.<br><br>"
            },
            {
                image: "/static/help_images/initiative_bar.png",
                text: "The <span style='color: #FF1493'>initiative bar</span> will show you how much health each character has, the turn order for the round, and who's on what team.<br><br>Turn order is randomly set each round.<br><br><br>"
            },
            {
                image: "/static/help_images/action_cards.png",
                text: "During your turn, you will choose an <span style='color: #FF1493'>action card</span>.<br><br>Your available <span style='color: #FF1493'>action cards</span> are displayed below the map/log area. You can use the left and right arrows to scroll through them.<br><br>"
            },
            {
                image: "/static/help_images/short_rest.png",
                image_size: 150,
                text: "When you use a card, you cannot use it again until you <span style='color: #8FBC8F'>short rest</span>.<br><br>During a <span style='color: #8FBC8F'>short rest</span>, you lose a random used card and get back all your other used cards. If you lose all your cards, you get exhausted and lose the game.<br><br>"
            },
            {
                image: "/static/help_images/card_highlighted.png",
                image_size: 200,
                text: "Most cards have <span style='color: #FFC87C'>movement</span> (or jump, which lets you jump over things on the board), <span style='color: #00BFFF'>attacks</span>, and other <span style='color: #FF8FA7'>special abilities</span>.<br><br>"
            },
            {
                image: "/static/help_images/modifier_deck.png",
                image_size: 50,
                text: "When you attack, you will draw a random modifier from your <span style='color: #00BFFF'>attack modifier deck</span> - this adds some excitement to the game!<br><br>If you attack for 3 but draw a -2 modifier, your attack does only 1 damage :(<br><br>"
            },
            {
                alignment: "left",
                text: `<div>
                    <div>Some <span style='color: #FF8FA7'>special abilities</span> affect your <span style="color: #00BFFF">attack modifier deck</span>:</div>
                    <div class="grid-container">
                        <div class="grid-item">
                            <h3>Fortify by 2</h3>
                            <p>Puts a +2 card on top of your attack modifier deck</p>
                        </div>
                        <div class="grid-item">
                            <h3>Weaken by 2</h3>
                            <p>Puts a -2 card on top of your attack modifier deck</p>
                        </div>
                        <div class="grid-item">
                            <h3>Bless</h3>
                            <p>Puts a 2x card in a random spot in your attack modifier deck - this doubles your attack</p>
                        </div>
                        <div class="grid-item">
                            <h3>Curse</h3>
                            <p>Puts a null card in a random spot attack modifier deck - you miss your attack</p>
                        </div>
                    </div>
                </div>`
            },
            {
                alignment: "left",
                text: `<div>
                    <p style="margin: 16px 0 8px 0;"><br>Other <span style="color: #FF8FA7">special abilities</span> include:</p>
                    <div class="grid-container">
                        <div class="grid-item special-grid-item">
                            <h3>Shield</h3>
                            <p>Decreases damage you take from attacks, expires on your turn</p>
                        </div>
                        <div class="grid-item special-grid-item">
                            <h3>Area Attacks</h3>
                            <p>Let you hit an area rather than a specific target</p>
                        </div>
                        <div class="grid-item special-grid-item">
                            <h3>Knock Down (50%)</h3>
                            <p>Gives you a 50% chance of knocking down an enemy, which skips their next turn</p>
                        </div>
                    </div>
                </div>`
            },
            {
                text: "On some abilities, you will also see a <span style='color: #FFC87C'><2></span> - this means your ability can be done to anyone within 2 squares of you.<br><br>If it's not specified, the ability can only be done to squares adjacent to you.<br><br>"
            },
            {
                image: "/static/help_images/range_attack.png",
                image_size: 200,
                text: "Some of your attacks are <span style='color: #00BFFF'>area effect attacks</span>. These hit a full area rather than a single character.<br><br>You will be able to <span style='color: #B19CD9'>rotate</span> these attack shapes. If they have <span style='color: #FFC87C'>range</span>, you will then be able to pick a square to attack.<br><br>"
            },
            {
                alignment: "left",
                text: `<div>
                    <p style="margin-bottom: 16px;">
                    There are also some <span style="color: #BC8F82">element effects</span>. If you start in or move through an element that does damage, you'll lose health.<br><br>Some characters have <span style="color: #BC8F82">element affinities</span>, which means they will heal from that element instead.<br><br>
                    </p>
                </div>`
            },
            {
                image: "/static/help_images/elements.png",
                image_size: 75,
                alignment: "left",
                text: `<div>
                    <p style="margin-bottom: 16px;">
                    Here are some common <span style="color: #BC8F82">elements</span>. The rest you can figure out by experimenting!
                    </p>
                    <ul style="list-style-type: none; padding-left: 20px; margin: 16px 0;">
                    <li style="margin-bottom: 12px;">
                        - <span style="color: #BC8F82">Fire</span>: Does 1 damage
                    </li>
                    <li style="margin-bottom: 12px;">
                        - <span style="color: #BC8F82">Ice</span>: Gives you a 25% chance of slipping when you pass through it
                    </li>
                    <li style="margin-bottom: 12px;">
                        - <span style="color: #BC8F82">Rotting Flesh</span>: Has a 50% chance of infecting you and doing 3 damage
                    </li>
                    <li style="margin-bottom: 12px;">
                        - <span style="color: #BC8F82">Shadow</span>: Gives any attack that moves through it a 10% chance of missing per square. If your attack passes through 3 shadow squares, it has a 30% chance of missing.
                    </li>
                    </ul>
                </div>`
            }
        ];

        function updateSlide() {
            const imageElement = document.getElementById('tutorialImage');
            const textElement = document.getElementById('tutorialText');
            
            if (slides[currentSlide].image) {
                imageElement.src = slides[currentSlide].image;
                imageElement.style.display = 'block';
                
                if (slides[currentSlide].image_size) {
                    imageElement.style.width = 'auto';
                    imageElement.style.height = slides[currentSlide].image_size + 'px';
                } else {
                    imageElement.style.width = '500px';
                    imageElement.style.height = 'auto';
                }
            } else {
                imageElement.style.display = 'none';
            }
            
            textElement.style.textAlign = slides[currentSlide].alignment === 'left' ? 'left' : 'center';
            textElement.innerHTML = slides[currentSlide].text;
            
            document.getElementById('slideCounter').textContent = `${currentSlide + 1} / ${slides.length}`;
            document.getElementById('prevButton').disabled = currentSlide === 0;
            document.getElementById('nextButton').disabled = currentSlide === slides.length - 1;
        }

        function nextSlide() {
            if (currentSlide < slides.length - 1) {
                currentSlide++;
                updateSlide();
            }
        }

        function prevSlide() {
            if (currentSlide > 0) {
                currentSlide--;
                updateSlide();
            }
        }

        window.onload = updateSlide;
    </script>
</head>
<body>
    <div class="container">
        <h1>HOW TO PLAY</h1>
        
        <div class="tutorial-content">
            <div class="tutorial-controls">
                <button onclick="prevSlide()" class="nav-button" id="prevButton">←</button>
                <span id="slideCounter" class="slide-counter"></span>
                <button onclick="nextSlide()" class="nav-button" id="nextButton">→</button>
            </div>
            <div class="carousel-container">
                <p id="tutorialText" class="tutorial-text"></p>
                <img id="tutorialImage" alt="Tutorial" class="tutorial-image" style="width: 500px; height: auto;">
            </div>
        </div>
        
        <div class="back-button-container">
            <a href="/" class="host-button back-button">
                BACK TO LOBBY
            </a>
        </div>
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


@app.route("/tutorial")
def tutorial():
    return render_template_string(TUTORIAL_HTML)


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
