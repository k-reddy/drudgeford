# Gloomhaven Game Setup Instructions

## Initial Setup

1. Clone the repository:
   ```bash
   git clone [repository-url]
   ```

2. Navigate to the Gloomhaven directory:
   ```bash
   cd gloomhaven
   ```

3. Create and activate a virtual environment:
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

4. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Playing the Game

1. Open your web browser and navigate to:
   ```
   http://13.59.128.25:8000/
   ```

2. Click the "Host Game" button.

3. Follow the provided link to start the game. You will receive a port number - keep this number handy.

4. In your terminal (with the virtual environment activated), run:
   ```bash
   python3 frontend_main.py
   ```

5. When prompted, enter the port number you received from the web interface.

## Troubleshooting

- Make sure your virtual environment is activated before running any Python commands
- If you encounter any dependency issues, try removing and recreating your virtual environment
- Ensure you're using Python 3.x