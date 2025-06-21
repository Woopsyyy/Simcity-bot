import os
import time
import zipfile
import shutil
import datetime
import subprocess

# === CONFIGURATION ===
ADB_PATH = r"C:\Program Files\Microvirt\MEmu\adb.exe"  # Change if using a different ADB
DEVICES = [
    "192.168.254.126:6556",  # change this to your abd add in your adroid emulator
]
DEVICE_NAMES = {
    "192.168.254.126:6556": "MY_PHONE",
}
PACKAGE = "com.ea.game.simcitymobile_row"  # Change to your app's package if needed
REMOTE_DIR = f"/sdcard/Android/data/{PACKAGE}/files"
FILES_TO_BACKUP = ["appdata.i3d", "ids"]
OUTPUT_DIR = "/storage/emulated/0/Download/Accounts"
TEMP_DIR = "temp_simcity_data"
LOOP_COUNT = 1  # Set how many times to run the automation
WAIT_SECONDS = 10

zip_counter = 1

# === HELPER FUNCTIONS ===
def run_adb(args, device):
    """Runs an ADB command using subprocess for better path handling."""
    try:
        command = [ADB_PATH, "-s", device] + args
        print(f"COMMAND: {' '.join(command)}")
        subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        print(f"Error: ADB not found at '{ADB_PATH}'. Please check the path.")
        exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(e.cmd)}")
        print(f"Stderr: {e.stderr.strip()}")

def check_adb_connection(device):
    """Checks if the device is connected via ADB."""
    print("Checking ADB connection...")
    try:
        command = [ADB_PATH, "devices"]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        if device not in result.stdout:
            print(f"Error: Device {device} not found or is offline.")
            print(f"ADB output:\n{result.stdout}")
            exit(1)
        print(f"ADB device {device} connected.")
    except FileNotFoundError:
        print(f"Error: ADB not found at '{ADB_PATH}'. Please check the path.")
        exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error checking ADB devices: {e.stderr}")
        exit(1)

def zip_folder(source_folder, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, source_folder)
                zipf.write(file_path, arc_path)

def backup_account(device):
    global zip_counter
    print(f"\nBacking up account for device {device}")

    temp_device_dir = f"{TEMP_DIR}_{device.replace(':', '_').replace('.', '_')}"
    if os.path.exists(temp_device_dir):
        shutil.rmtree(temp_device_dir)
    os.makedirs(temp_device_dir, exist_ok=True)

    print("Pulling files from device...")
    for filename in FILES_TO_BACKUP:
        remote_path = f"{REMOTE_DIR}/{filename}"
        local_path = os.path.join(temp_device_dir, filename)
        run_adb(["pull", remote_path, local_path], device)

    # --- Verification Step ---
    pulled_files = os.listdir(temp_device_dir)
    if len(pulled_files) < len(FILES_TO_BACKUP):
        print("\n--- WARNING: Incomplete Backup ---")
        print("Not all required files were found on the device.")
        print(f"Expected: {FILES_TO_BACKUP}")
        print(f"Found: {pulled_files}")
        print("Aborting backup process.")
        shutil.rmtree(temp_device_dir)
        return  # Stop the function here

    # 2. Create ZIP file on the PC
    date_str = datetime.datetime.now().strftime("%m_%d_%Y")
    memu_name = DEVICE_NAMES.get(device, device.replace(":", "_"))
    
    current_index = zip_counter
    zip_counter += 1
    
    zip_filename = f"#{current_index}_{date_str}-{memu_name}.zip"
    local_zip_path = os.path.join(os.getcwd(), zip_filename)

    print(f"Creating ZIP file: {local_zip_path}")
    zip_folder(temp_device_dir, local_zip_path)

    # 3. Push ZIP file from PC to device's download folder
    print(f"Pushing {zip_filename} to device...")
    remote_zip_path = f"{OUTPUT_DIR}/{zip_filename}"
    run_adb(["push", local_zip_path, remote_zip_path], device)
    
    # 4. Clean up temporary files on PC
    print("Cleaning up temporary files...")
    os.remove(local_zip_path)
    shutil.rmtree(temp_device_dir)
    
    print(f"Backup successful for device {device}")

def reset_app(device):
    """Clears the app data to reset the game for the next loop."""
    print("\nResetting SimCity app data...")
    run_adb(["shell", "pm", "clear", PACKAGE], device)
    print("Waiting 5 seconds for app to reset...")
    time.sleep(5)

# === MAIN AUTOMATION LOGIC ===
def automate_device(device):
    check_adb_connection(device)
    run_adb(["shell", "mkdir", "-p", OUTPUT_DIR], device) # Ensure output directory exists on device
    for i in range(1, LOOP_COUNT + 1):
        print(f"\nLoop {i}/{LOOP_COUNT} for device {device}")
        # Example: Launch app
        run_adb(["shell", "monkey", "-p", PACKAGE, "-c", "android.intent.category.LAUNCHER", "1"], device)
        
        
        print("SIMCITY LOADING") #if have high end phone reduce the time, its 15 seconds
        time.sleep(15)
        
        print("BIRTHMONTH DROPDOWN")
        run_adb(["shell", "input", "tap", "773", "385"], device)
        time.sleep(1)

        print("YEAR SWIPE") # swipe to select birthmonth
        run_adb(["shell", "input", "swipe", "552", "519", "557", "107"], device)
        time.sleep(1)

        print("YEAR SWIPE") # swipe to select birth year
        run_adb(["shell", "input", "swipe", "550", "470", "550", "60"], device)
        time.sleep(1)

        print("YEAR SWIPE") # swipe to select birth year
        run_adb(["shell", "input", "swipe", "560", "440", "600", "40"], device)
        time.sleep(1)

        print("YEAR SWIPE") # swipe to select birth year
        run_adb(["shell", "input", "swipe", "550", "440", "560", "230"], device)
        time.sleep(1)

        print("SELECT MONTH")
        run_adb(["shell", "input", "swipe", "1100", "430", "1100", "80"], device) # swipe to select birth month
        time.sleep(1)
        

        print("CONTINUE")
        run_adb(["shell", "input", "tap", "1330", "200"], device)
        time.sleep(1)

        print("ACCEPT")
        run_adb(["shell", "input", "tap", "800", "480"], device)
        
        print("Waiting 90 seconds for SimCity to load...") # i put 90 seconds because my phone is slow
        time.sleep(90)
        
        print("ROAD ICON")
        run_adb(["shell", "input", "tap", "1530", "300"], device)
        time.sleep(3)

        print("BUILDING ROAD ")
        run_adb(["shell", "input", "swipe", "540", "350", "1070", "390"], device)
        time.sleep(1)

        print("CHECKMARK ICON")
        run_adb(["shell", "input", "tap", "1200", "430"], device)
        time.sleep(1)

        print("SKIP DIALOG")
        run_adb(["shell", "input", "tap", "890", "500"], device)
        time.sleep(3)

        print("BUILDING ICON")
        run_adb(["shell", "input", "tap", "1500", "366"], device)
        time.sleep(1)

        print("BUILDING RESIDENTIAL")
        run_adb(["shell", "input", "swipe", "800", "640", "560", "304"], device)
        time.sleep(1)

        print("CHECKMARK ICON")
        run_adb(["shell", "input", "tap", "720", "355"], device)
        time.sleep(1)

        print("WAITING FOR BUILDING TO COMPLETE")
        time.sleep(15)

        print("CONSTRUCTION ICON")
        run_adb(["shell", "input", "tap", "800", "330"], device)
        time.sleep(1)

        print("METAL ICON")
        run_adb(["shell", "input", "swipe", "640", "300", "800", "430"], device)
        time.sleep(1)

        print("WAITING FOR BUILDING TO COMPLETE")
        time.sleep(30)

        # Backup the account data
        backup_account(device)
        
        #print("Opening ZArchiver to check the file...") # i put this to check if the account has been addes to my directory you can remove this
        #run_adb(["shell", "monkey", "-p", "ru.zdevs.zarchiver", "-c", "android.intent.category.LAUNCHER", "1"], device)
        
        # Reset the app before the next loop
        if i < LOOP_COUNT:
            reset_app(device)

        print(f"Automation loop {i} for device {device} complete.")

if __name__ == "__main__":
    for device in DEVICES:
        automate_device(device) 
