# CSGO-YouTube-Player
Detects URL in-game and plays them through your mic
Usable GUI to help skip tracks, delete tracks, change volume and more.
Works with timestamp. Thanks to torchlight

# Requirements
- Python3.8
- Virtual Audio Cable. Set this up yourself
- VLC MediaPlayer

# Install
- Install python3
- Do `pip install -r requirements.txt`
- In yt-player.py edit
  - `LOGFILE = ""` to your csgo logfile as stated in con_logfile. Example in script
  - `COMMANDS = ".yt"` to your liking (The command used to input URL ingame)
  - `TIMEOUT = 5` Auto skips track after x time
- Run `python yt-player.py`

# Usage
- In CS:GO, open console and type `con_logfile gtts.log`
- Press START to start reading the logfile.
- In game, type `.yt <link>`
- Alternative method is to add the link manually in the GUI

# Images
Coming soon™
