import os
import time
import zipfile
import shutil
import datetime

# === CONFIGURATION ===
ADB_PATH = r'"C:\Program Files\Microvirt\MEmu\adb.exe"' # if we have different directory, change this
DEVICE = "127.0.0.1:21503" 
PACKAGE = "com.ea.game.simcitymobile_row"
REMOTE_DIR = f"/sdcard/Android/data/{PACKAGE}/files"
OUTPUT_DIR = r"E:\SUSSSSSSSS\SIMCITY\accounts" # change this to where the zip files will be save
TEMP_DIR = "temp_simcity_data"
LOOP_COUNT = 5
WAIT_SECONDS = 25

# === HELPER FUNCTIONS ===

def run_adb(command):
    full_cmd = f'{ADB_PATH} -s {DEVICE} {command}'
    print(f"🧪 ADB: {full_cmd}")
    result = os.popen(full_cmd).read()
    print(f"📤 Output:\n{result.strip()}")
    return result.strip()

def check_adb_connection():
    print("🔌 Checking ADB connection...")
    result = os.popen(f'{ADB_PATH} devices').read()
    if DEVICE not in result:
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

def backup_account(loop_index):
    print(f"\n📥 Backing up account #{loop_index}")

    run_adb("root")
    run_adb(f"shell su -c 'chmod -R 777 {REMOTE_DIR}'")

    file_list = run_adb(f"shell ls {REMOTE_DIR}")
    print("📁 Files found:")
    print(file_list)

    if "appdata.i3d" not in file_list:
        print("❌ appdata.i3d not found! Skipping this backup.")
        return

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)

    run_adb(f"pull {REMOTE_DIR}/appdata.i3d {os.path.join(TEMP_DIR, 'appdata.i3d')}")
    run_adb(f"pull {REMOTE_DIR}/ids {os.path.join(TEMP_DIR, 'ids')}")

    pulled_files = os.listdir(TEMP_DIR)
    print("📂 Files pulled into TEMP_DIR:")
    for f in pulled_files:
        print(" -", f)

    if not pulled_files:
        print("❌ No files pulled. Skipping ZIP.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    zip_filename = f"#{loop_index}_{timestamp}.zip"
    zip_path = os.path.join(OUTPUT_DIR, zip_filename)

    print(f"🗜 Creating ZIP file: {zip_path}")
    try:
        zip_folder(TEMP_DIR, zip_path)
        print(f"✅ ZIP saved at: {zip_path}")
    except Exception as e:
        print(f"❌ ZIP creation failed: {e}")

def reset_app():
    print("♻️ Resetting SimCity...")
    run_adb(f"shell pm clear {PACKAGE}")
    time.sleep(3)

def input_birth_date():
    print("🎂 Inputting birth year and month...")

    print("🛠 Step 1: Tap Year dropdown")
    run_adb("shell input tap 800 450")
    time.sleep(1)

    print("🛠 Step 2: Swipe Year 1 (scrolling down)")
    run_adb("shell input swipe 581 706 581 50")
    time.sleep(1)

    print("🛠 Step 3: Swipe Year 2 (further scroll)")
    run_adb("shell input swipe 581 706 581 8")
    time.sleep(1)

    print("🛠 Step 4: Swipe to select May")
    run_adb("shell input swipe 1131 697 1131 300")
    time.sleep(1)

    print("🛠 Step 5: Tap Continue button")
    run_adb("shell input tap 1278 377")
    time.sleep(1)

    print("🛠 Step 6: Tap Accept button")
    run_adb("shell input tap 803 586")
    time.sleep(1)

    print("✅ Birthdate input complete.")

def tutorial_phase():
    print("🎓 Tutorial phase started...")

    print("🛠 Step 1: Tap road icon")
    run_adb("shell input tap 1525 351")
    time.sleep(3)

    print("🛠 Step 2: Skip dialog")
    run_adb("shell input tap 522 413")
    time.sleep(3)

    print("🛠 Step 3: Build road")
    run_adb("shell input swipe 501 435 1225 471")
    time.sleep(3)

    print("🛠 Step 4: Tap checkmark")
    run_adb("shell input tap 1391 539")
    time.sleep(3)

    print("🛠 Step 5: Skip dialog again")
    run_adb("shell input tap 522 413")
    time.sleep(3)

    print("🛠 Step 6: Tap house icon")
    run_adb("shell input tap 1513 471")
    time.sleep(3)

    print("🛠 Step 7: Place house")
    run_adb("shell input swipe 864 689 475 400")
    time.sleep(3)

    print("🛠 Step 8: Skip dialog")
    run_adb("shell input tap 522 413")
    time.sleep(3)

    print("🛠 Step 9: Confirm house with checkmark")
    run_adb("shell input tap 803 475")
    time.sleep(10)

    print("🛠 Step 10: Tap house completion check")
    run_adb("shell input tap 612 266")
    time.sleep(3)

    print("🛠 Step 11: Tap metal production")
    run_adb("shell input swipe 517 350 796 433")
    time.sleep(10)

    print("✅ Tutorial input done.")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("📡 Connecting to MEmu ADB...")
    os.system(f'{ADB_PATH} connect {DEVICE}')
    check_adb_connection()

    for i in range(1, LOOP_COUNT + 1):
        print(f"\n🔁 Loop {i}/{LOOP_COUNT}")

        print("📱 Launching SimCity...")
        run_adb(f"shell monkey -p {PACKAGE} -c android.intent.category.LAUNCHER 1")
        time.sleep(WAIT_SECONDS)

        input_birth_date()
        print("⏳ Waiting for tutorial screen to appear...")
        time.sleep(40)

        tutorial_phase()
        print("⏳ Waiting for game to finish loading...")
        time.sleep(20)

        print("🛑 Stopping SimCity...")
        run_adb(f"shell am force-stop {PACKAGE}")
        time.sleep(2)

        try:
            backup_account(i)
        except Exception as e:
            print(f"⚠️ Backup failed for account #{i}: {e}")

        reset_app()
        time.sleep(5)

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

    print("\n✅ All accounts backed up successfully!")

if __name__ == "__main__":
    main()
