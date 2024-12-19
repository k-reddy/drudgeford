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


# Mac Setup Instructions for Drudgeford Game
Note: we haven't playtested on PCs yet...

## Setup

1. Install Python 3.12:
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

## Playing the Game

1. Open your web browser and go to:
   ```
   https://drudgeford.quest/
   ```

2. Follow the instructions on the website

## Common Issues
- If pip install fails, make sure your virtual environment is activated (you should see "(venv)" at the start of your Terminal prompt)
- To reactivate your virtual environment after closing Terminal:
  ```bash
  cd drudgeford
  source venv/bin/activate
  ```