
# SimCity Backup Automation 

This script automates the process of backing up SimCity game data from an Android emulator (MEmu) using ADB. It organizes backups into folders by date, fills missing slots, and can send progress and error notifications to a Discord channel via webhook.

## Features
- Automated backup of SimCity game files from emulator
- Organizes ZIP backups into date-based folders, filling missing slots before creating new folders
- Discord webhook notifications for progress and errors (optional, can be toggled)
- Multi-threaded for multiple devices (if enabled)

## Requirements
- Python 3.7+
- MEmu Android Emulator (with ADB)
- SimCity installed on the emulator
- Windows OS
- [requests](https://pypi.org/project/requests/) Python package

## Setup Instructions (This steps only if you want to use the webhook to monitor your bot, if you are not using the webhook feature just ignore this steps)

### 1. Clone or Download the Project
Place all files in a folder, e.g. `E:/SUSSSSSSSS/SIMCITY`.

### 2. Create and Activate a Virtual Environment (.venv)
Open Command Prompt in your project folder and run:

```
python -m venv .venv
```

Activate the virtual environment:
- **Windows:**
  - Command Prompt:
    ```
    .venv\Scripts\activate
    ```
  - PowerShell:
    ```
    .venv\Scripts\Activate.ps1
    ```

### 3. Install Requirements
With the virtual environment activated, run:
```
pip install -r requirements.txt
```

### 4. Configure the Script
- Set your ADB path, device IPs, and Discord webhook URL in `pc_automate.py` as needed.
- To enable/disable webhook notifications, set `WEBHOOK_ENABLED = True` or `False` at the top of the script.

### 5. Run the Script
With the virtual environment activated, run:
```
python pc_automate.py
```

## Notes
- Backups are saved in the `accounts` folder, organized by date and group.
- Only today's folders are filled; previous dates are not affected.
- Webhook notifications are optional and can be toggled in the script.

## Troubleshooting
- If you see `ModuleNotFoundError: No module named 'requests'`, make sure you installed requirements in the correct environment.
- Ensure ADB is installed and accessible at the path specified in the script.
- For Discord notifications, ensure your webhook URL is correct.

--- 
