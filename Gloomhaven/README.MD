# Mac Setup Instructions for Gloomhaven Game

## Setup

1. Open Terminal (you can find this using Spotlight search - press Cmd+Space and type "Terminal")

2. Install Homebrew (macOS package manager) by pasting this command:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

3. Install Python 3.12:
   ```bash
   brew install python@3.12
   ```

4. Clone the repository:
   ```bash
   git clone [repository-url]
   ```

5. Navigate to the Gloomhaven directory:
   ```bash
   cd gloomhaven
   ```

6. Create and activate a virtual environment:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   ```

7. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Playing the Game

1. Open your web browser and go to:
   ```
   http://13.59.128.25:8000/
   ```

2. Click the "Host Game" button

3. Follow the link to start the game - you'll get a port number

4. In Terminal (with your virtual environment still activated), run:
   ```bash
   python3 frontend_main.py
   ```

5. When asked, enter the port number you got from the website

## Common Issues

- If you see "Command not found" for brew commands after installation, try closing and reopening Terminal
- If you get a permissions error during the Homebrew installation, follow the instructions it provides about directory ownership
- If pip install fails, make sure your virtual environment is activated (you should see "(venv)" at the start of your Terminal prompt)
- To reactivate your virtual environment after closing Terminal:
  ```bash
  cd gloomhaven
  source venv/bin/activate
  ```