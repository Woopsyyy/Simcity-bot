import os
import time
import zipfile
import shutil
import datetime
import threading

# === CONFIGURATION ===
ADB_PATH = r'"C:\Program Files\Microvirt\MEmu\adb.exe"'  #change this into your correct adb path

DEVICES = ["123.0.0.1:21503", "124.0.0.1:21513"] # this is your memu address change this, you can find your device using cmd, cd to the C:\Program Files\Microvirt\MEmu\ then type adb devices it will show all the instances
PACKAGE = "com.ea.game.simcitymobile_row"
REMOTE_DIR = f"/sdcard/Android/data/{PACKAGE}/files"
OUTPUT_DIR = r"E:\SUSSSSSSSS\SIMCITY\accounts" # where your gamefile zip will be save, change this
TEMP_DIR = "temp_simcity_data"
LOOP_COUNT = 1000 
WAIT_SECONDS = 25

# Shared counter and lock
zip_counter = 1
zip_lock = threading.Lock()

DEVICE_NAMES = {
    "127.0.0.1:21503": "MEMU1",
    "127.0.0.1:21513": "MEMU2",
    # Add more as needed
}

# === HELPER FUNCTIONS ===

def run_adb(command, device):
    full_cmd = f'{ADB_PATH} -s {device} {command}'
    print(f"🧪 ADB: {full_cmd}")
    result = os.popen(full_cmd).read()
    print(f"📤 Output:\n{result.strip()}")
    return result.strip()

def check_adb_connection(device):
    print("🔌 Checking ADB connection...")
    result = os.popen(f'{ADB_PATH} devices').read()
    if device not in result:
        print("❌ Device not connected via ADB.")
        exit(1)
    print("✅ ADB device connected.")

def zip_folder(source_folder, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, source_folder)
                zipf.write(file_path, arc_path)

def backup_account(loop_index, device):
    global zip_counter
    print(f"\n📥 Backing up account #{loop_index} for device {device}")

    run_adb("root", device)
    run_adb(f"shell su -c 'chmod -R 777 {REMOTE_DIR}'", device)

    file_list = run_adb(f"shell ls {REMOTE_DIR}", device)
    print("📁 Files found:")
    print(file_list)

    if "appdata.i3d" not in file_list:
        print("❌ appdata.i3d not found! Skipping this backup.")
        return

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)

    run_adb(f"pull {REMOTE_DIR}/appdata.i3d {os.path.join(TEMP_DIR, 'appdata.i3d')}", device)
    run_adb(f"pull {REMOTE_DIR}/ids {os.path.join(TEMP_DIR, 'ids')}", device)

    pulled_files = os.listdir(TEMP_DIR)
    print("📂 Files pulled into TEMP_DIR:")
    for f in pulled_files:
        print(" -", f)

    if not pulled_files:
        print("❌ No files pulled. Skipping ZIP.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    date_str = datetime.datetime.now().strftime("%m_%d_%Y")
    memu_name = DEVICE_NAMES.get(device, device.replace(":", "_"))
    with zip_lock:
        current_index = zip_counter
        zip_counter += 1
        zip_filename = f"#{current_index}_{date_str}-{memu_name}.zip"
        zip_path = os.path.join(OUTPUT_DIR, zip_filename)

    print(f"🗜 Creating ZIP file: {zip_path}")
    try:
        zip_folder(TEMP_DIR, zip_path)
        print(f"✅ ZIP saved at: {zip_path}")
    except Exception as e:
        print(f"❌ ZIP creation failed: {e}")

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
    print(f"\n📡 Connecting to MEmu ADB for device {device}...")
    os.system(f'{ADB_PATH} connect {device}')
    check_adb_connection(device)

    for i in range(1, LOOP_COUNT + 1):
        print(f"\n🔁 Loop {i}/{LOOP_COUNT} for device {device}")

        print("📱 Launching SimCity...")
        run_adb(f"shell monkey -p {PACKAGE} -c android.intent.category.LAUNCHER 1", device)
        time.sleep(WAIT_SECONDS)

        input_birth_date(device)
        print("⏳ Waiting for tutorial screen to appear...")
        time.sleep(40)

        tutorial_phase(device)
        print("⏳ Waiting for game to finish loading...")
        time.sleep(20)

        print("🛑 Stopping SimCity...")
        run_adb(f"shell am force-stop {PACKAGE}", device)
        time.sleep(2)

        try:
            backup_account(i, device)
        except Exception as e:
            print(f"⚠️ Backup failed for account #{i} on device {device}: {e}")

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
