<table border="0" cellspacing="0" cellpadding="0" style="border:none;">
  <tr>
    <td width="50%" style="border:none;"><img src="/gifs/character_picker.gif" alt="Character Picker"/></td>
    <td width="50%" style="border:none;"><img src="/gifs/ai_attack.gif" alt="AI Attack"/></td>
  </tr>
  <tr>
    <td width="50%" style="border:none;"><img src="/gifs/movement.gif" alt="Movement"/></td>
    <td width="50%" style="border:none;"><img src="/gifs/fireball.gif" alt="Fireball"/></td>
  </tr>
</table>


# Mac Setup Instructions for Running Drudgeford Locally
Note: we haven't playtested on PCs yet...

## Setup 
We recommend downloading the game frontend as an app on http://drudgeford.quest and running the backend on our server via the website. But if you prefer (or if you have a PC), you can pull the code from this repos and run the game locally. It may take a little debugging to get it to work for PCs. 

To set up for running the code locally:

1. Install Python 3.12 if you don't have it already
   ```bash
   brew install python@3.12
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/k-reddy/drudgeford.git
   ```

3. Navigate to the Drudgeford directory:
   ```bash
   cd drudgeford
   ```

4. Create and activate a virtual environment:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   ```

5. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the game locally
You have two options:

1. For single player, navigate to the Drudgeford folder and run: 
   ```bash
   python3 dev_mode.py
   ```

2. For two-player on the same computer, you'll need to open three terminal windows and navigate each to the Drudgeford folder. In one, run:
   ```bash
   python3 backend_main.py
   ```
   In the other two, run:   
   ```bash
   python3 drudgeford.py --dev
   ```
   Each terminal window will run an instance of the pyxel frontend.

## Common Issues
- If pip install fails, make sure your virtual environment is activated (you should see "(venv)" at the start of your Terminal prompt)
- To reactivate your virtual environment after closing Terminal:
  ```bash
  cd drudgeford
  source venv/bin/activate
  ```