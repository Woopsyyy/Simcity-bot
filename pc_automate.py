import os
import time
import zipfile
import shutil
import datetime
import threading
import requests

# === CONFIGURATION ===
ADB_PATH = r'"C:\\Program Files\\Microvirt\\MEmu\\adb.exe"'  # Set your ADB path here
DEVICES = ["127.0.0.1:PORT"]  # <-- Replace with your emulator/device IPs and ports
PACKAGE = "com.ea.game.simcitymobile_row"
REMOTE_DIR = f"/sdcard/Android/data/{PACKAGE}/files"
OUTPUT_DIR = r"E:\\YOUR_PATH\\SIMCITY\\accounts"  # <-- Set your desired output path
TEMP_DIR = "temp_simcity_data"
LOOP_COUNT = 1000 
WAIT_SECONDS = 25

# === WEBHOOK CONFIGURATION ===
WEBHOOK_ENABLED = False  # Set to True to enable webhook feature
WEBHOOK_URL = "https://discord.com/api/webhooks/your_webhook_url_here"  # <-- Set your Discord webhook URL here

# Shared counter and lock
zip_counter = 1
zip_lock = threading.Lock()

DEVICE_NAMES = {
    "127.0.0.1:PORT": "MEMU1"  # <-- Replace with your emulator/device IPs and names
}

# === HELPER FUNCTIONS ===
def run_adb(command, device):
    full_cmd = f'{ADB_PATH} -s {device} {command}'
    result = os.popen(full_cmd).read()
    return result.strip()

def check_adb_connection(device):
    try:
        result = os.popen(f'{ADB_PATH} devices').read()
    except FileNotFoundError:
        print("[ERROR] adb executable not found")
        send_webhook("[ERROR] adb executable not found")
        exit(1)
    except Exception as e:
        print(f"[ERROR] unknown error: {e}")
        send_webhook(f"[ERROR] unknown error: {e}")
        exit(1)
    if device not in result:
        if 'offline' in result:
            print("[ERROR] device is offline")
            send_webhook("[ERROR] device is offline")
        else:
            print("[ERROR] cant connect into adb")
            send_webhook("[ERROR] cant connect into adb")
        exit(1)
    # No print if successful

def zip_folder(source_folder, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, source_folder)
                zipf.write(file_path, arc_path)

def get_group_folder_and_index(base_dir, date_str):
    # Scan all group folders for today
    group_num = 1
    folders_to_check = []
    while True:
        group_folder = os.path.join(base_dir, f"{date_str} #{group_num}")
        if not os.path.exists(group_folder):
            break
        folders_to_check.append(group_folder)
        group_num += 1
    # Check for folders with missing zips
    for idx, group_folder in enumerate(folders_to_check):
        zip_files = [f for f in os.listdir(group_folder) if f.endswith('.zip')]
        used_numbers = set()
        for fname in zip_files:
            if fname.startswith('#'):
                try:
                    num = int(fname.split('_')[0][1:])
                    used_numbers.add(num)
                except Exception:
                    pass
        # Find the lowest missing number in 1-100
        for i in range(1, 101):
            if i not in used_numbers:
                return group_folder, i
    # If all existing folders are full, create a new one
    group_folder = os.path.join(base_dir, f"{date_str} #{group_num}")
    os.makedirs(group_folder, exist_ok=True)
    return group_folder, 1

def send_webhook(message):
    if not ('WEBHOOK_ENABLED' in globals() and WEBHOOK_ENABLED):
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"[ERROR] Failed to send webhook: {e}")

def backup_account(loop_index, device):
    global zip_counter
    date_str = datetime.datetime.now().strftime("%m-%d-%Y")
    memu_name = DEVICE_NAMES.get(device, device.replace(":", "_"))
    with zip_lock:
        group_folder, missing_index = get_group_folder_and_index(OUTPUT_DIR, date_str)
        zip_filename = f"#{missing_index}_{date_str}-{memu_name}.zip"
        zip_path = os.path.join(group_folder, zip_filename)
    zip_files = [f for f in os.listdir(group_folder) if f.endswith('.zip')]
    progress_msg = f"{len(zip_files)+1}/100\nFolder name: {os.path.basename(group_folder)}\nZIP name: {zip_filename}"
    print(f"\n{progress_msg}")
    send_webhook(progress_msg)
    run_adb("root", device)
    run_adb(f"shell su -c 'chmod -R 777 {REMOTE_DIR}'", device)
    file_list = run_adb(f"shell ls {REMOTE_DIR}", device)
    if "appdata.i3d" not in file_list:
        print("[SKIP] appdata.i3d not found!")
        send_webhook("[SKIP] appdata.i3d not found!")
        return
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)
    run_adb(f"pull {REMOTE_DIR}/appdata.i3d {os.path.join(TEMP_DIR, 'appdata.i3d')}", device)
    run_adb(f"pull {REMOTE_DIR}/ids {os.path.join(TEMP_DIR, 'ids')}", device)
    pulled_files = os.listdir(TEMP_DIR)
    if not pulled_files:
        print("[SKIP] No files pulled.")
        send_webhook("[SKIP] No files pulled.")
        return
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Saving files...")
    try:
        zip_folder(TEMP_DIR, zip_path)
        print(f"[SAVED] {zip_path}")
        send_webhook(f"[SAVED] {zip_path}")
    except Exception as e:
        print(f"[ERROR] ZIP creation failed: {e}")
        send_webhook(f"[ERROR] ZIP creation failed: {e}")

def reset_app(device):
    print("♻️ Resetting SimCity...")
    run_adb(f"shell pm clear {PACKAGE}", device)
    time.sleep(3)

def input_birth_date(device):
    print("🎂 Inputting birth year and month...")

    print("🛠 Step 1: Tap Year dropdown")
    run_adb("shell input tap 800 450", device)
    time.sleep(1)

    print("🛠 Step 2: Swipe Year 1 (scrolling down)")
    run_adb("shell input swipe 581 706 581 50", device)
    time.sleep(1)

    print("🛠 Step 3: Swipe Year 2 (further scroll)")
    run_adb("shell input swipe 581 706 581 8", device)
    time.sleep(1)

    print("🛠 Step 4: Swipe to select May")
    run_adb("shell input swipe 1131 697 1131 300", device)
    time.sleep(1)

    print("🛠 Step 5: Tap Continue button")
    run_adb("shell input tap 1278 377", device)
    time.sleep(1)

    print("🛠 Step 6: Tap Accept button")
    run_adb("shell input tap 803 586", device)
    time.sleep(1)

    print("✅ Birthdate input complete.")

def tutorial_phase(device):
    print("🎓 Tutorial phase started...")

    print("🛠 Step 1: Tap road icon")
    run_adb("shell input tap 1525 351", device)
    time.sleep(3)

    print("🛠 Step 2: Skip dialog")
    run_adb("shell input tap 522 413", device)
    time.sleep(3)

    print("🛠 Step 3: Build road")
    run_adb("shell input swipe 501 435 1225 471", device)
    time.sleep(3)

    print("🛠 Step 4: Tap checkmark")
    run_adb("shell input tap 1391 539", device)
    time.sleep(3)

    print("🛠 Step 5: Skip dialog again")
    run_adb("shell input tap 522 413", device)
    time.sleep(3)

    print("🛠 Step 6: Tap house icon")
    run_adb("shell input tap 1513 471", device)
    time.sleep(3)

    print("🛠 Step 7: Place house")
    run_adb("shell input swipe 864 689 475 400", device)
    time.sleep(3)

    print("🛠 Step 8: Skip dialog")
    run_adb("shell input tap 522 413", device)
    time.sleep(3)

    print("🛠 Step 9: Confirm house with checkmark")
    run_adb("shell input tap 803 475", device)
    time.sleep(10)

    print("🛠 Step 10: Tap house completion check")
    run_adb("shell input tap 612 266", device)
    time.sleep(3)

    print("🛠 Step 11: Tap metal production")
    run_adb("shell input swipe 517 350 796 433", device)
    time.sleep(10)

    print("✅ Tutorial input done.")

def automate_device(device):
    print(f"\n[LAUNCH] Connecting to MEmu ADB for device {device}...")
    os.system(f'{ADB_PATH} connect {device}')
    check_adb_connection(device)
    for i in range(1, LOOP_COUNT + 1):
        print(f"\n[PROGRESS] Loop {i}/{LOOP_COUNT} for device {device}")
        print("Launching SimCity...")
        run_adb(f"shell monkey -p {PACKAGE} -c android.intent.category.LAUNCHER 1", device)
        time.sleep(WAIT_SECONDS)
        print("Inputting birth year and month...")
        input_birth_date(device)
        print("[WAIT] Waiting for tutorial screen to appear...")
        time.sleep(40)
        print("[TUTORIAL] Running tutorial phase...")
        tutorial_phase(device)
        print("[WAIT] Waiting for game to finish loading...")
        time.sleep(20)
        print("Stopping SimCity...")
        run_adb(f"shell am force-stop {PACKAGE}", device)
        time.sleep(2)
        try:
            backup_account(i, device)
        except Exception as e:
            print(f"[ERROR] Backup failed for account #{i} on device {device}: {e}")
        print("[RESET] Resetting app...")
        reset_app(device)
        time.sleep(5)
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    threads = []
    for device in DEVICES:
        t = threading.Thread(target=automate_device, args=(device,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    print("\n✅ All accounts backed up successfully!")

if __name__ == "__main__":
    main() 
