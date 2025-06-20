# 📦 SimCity Account Backup Automation

This Python script automates the creation of fresh SimCity BuildIt accounts in MEmu and backs them up by saving the game's `appdata.i3d` and `ids` files into timestamped `.zip` files.

## 🔧 Requirements

- Windows OS
- [Python 3.x](https://www.python.org/downloads/)
- [MEmu Android Emulator](https://www.memuplay.com/)
- ADB (bundled with MEmu or Android SDK)
- Game: `SimCity BuildIt` installed on MEmu

## 📁 Folder Structure

```plaintext
project_folder/
├── script.py              # Your main Python automation script
├── temp_simcity_data/     # Temporary storage for pulled game files
└── accounts/              # Final backups saved as ZIPs
