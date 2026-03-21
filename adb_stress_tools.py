import os
import sys
import time
import datetime
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# ==========================================
# Basic Configuration
# ==========================================
LOG_DIR = "PC_Test_Logs"
os.makedirs(LOG_DIR, exist_ok=True)

class ADBStressGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Android ADB Stress Test Console (Pro Edition) v1.0.1")
        self.root.geometry("850x700")
        
        self.is_testing = False
        self.current_log_file = None
        self.logcat_proc = None
        self.monkey_proc = None
        self.cpu_procs = []

        self.setup_ui()

    def setup_ui(self):
        # --- Left Control Panel ---
        control_frame = tk.Frame(self.root, width=320, padx=10, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(control_frame, text="⚙️ Select Test Item", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        self.test_type_var = tk.StringVar(value="WiFi ON/OFF Test")
        test_options = [
            "WiFi ON/OFF Test", 
            "Screen Sleep/Wake", 
            "Gallery UI Tap", 
            "Monkey (System-wide Random)", 
            "Monkey (Specific App)",
            "Battery Spoofing & Power State",
            "CPU Thermal Throttling (Mins)",
            "Storage I/O Stress (1GB)",
            "Airplane Mode Toggle",
            "App Cold-Start & Kill"
        ]
        self.combo_test = ttk.Combobox(control_frame, textvariable=self.test_type_var, values=test_options, state="readonly", font=("Arial", 11))
        self.combo_test.pack(fill=tk.X, pady=(0, 15))
        self.combo_test.bind("<<ComboboxSelected>>", self.on_test_type_changed)

        tk.Label(control_frame, text="🎯 Target (Cycles / Events / Mins)", font=("Arial", 10)).pack(anchor=tk.W)
        self.entry_target = tk.Entry(control_frame, font=("Arial", 11))
        self.entry_target.insert(0, "50")
        self.entry_target.pack(fill=tk.X, pady=(0, 15))

        # --- App Specific Settings (Dynamic Frame) ---
        self.app_frame = tk.LabelFrame(control_frame, text="App Specific Settings", padx=10, pady=10)
        
        tk.Label(self.app_frame, text="📦 Target Package (comma-separated):", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_pkg = tk.Entry(self.app_frame, font=("Arial", 10))
        self.entry_pkg.pack(fill=tk.X, pady=(0, 5))
        
        self.btn_fetch_apps = tk.Button(self.app_frame, text="🔍 Fetch 3rd-Party Apps", command=self.fetch_apps_ui)
        self.btn_fetch_apps.pack(fill=tk.X, pady=(0, 10))

        tk.Label(self.app_frame, text="⏱️ Tap Interval (Monkey only, ms):", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_throttle = tk.Entry(self.app_frame, font=("Arial", 10))
        self.entry_throttle.insert(0, "300")
        self.entry_throttle.pack(fill=tk.X, pady=(0, 10))

        self.ignore_crash_var = tk.BooleanVar(value=True)
        self.chk_ignore_crash = tk.Checkbutton(self.app_frame, text="Ignore Crash/ANR (Monkey only)", variable=self.ignore_crash_var)
        self.chk_ignore_crash.pack(anchor=tk.W)

        # --- Buttons Area ---
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=20)

        self.btn_start = tk.Button(btn_frame, text="▶️ START", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=self.start_test)
        self.btn_start.pack(fill=tk.X, pady=(0, 10))

        self.btn_stop = tk.Button(btn_frame, text="⏹️ STOP", font=("Arial", 12, "bold"), bg="#F44336", fg="white", state=tk.DISABLED, command=self.stop_test)
        self.btn_stop.pack(fill=tk.X, pady=(0, 10))

        self.btn_open_logs = tk.Button(btn_frame, text="📁 Open Logs", font=("Arial", 12), bg="#2196F3", fg="white", command=self.open_logs)
        self.btn_open_logs.pack(fill=tk.X)

        # --- Right Log Display Area ---
        log_frame = tk.Frame(self.root, padx=10, pady=10)
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(log_frame, text="📝 Real-time Execution Log", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.text_log = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), bg="#1E1E1E", fg="#00FF00")
        self.text_log.pack(fill=tk.BOTH, expand=True)

        self.ui_log("System ready, waiting for device connection...")
        self.on_test_type_changed(None)

    def on_test_type_changed(self, event):
        """Dynamically show/hide options based on the selected test item"""
        test_type = self.test_type_var.get()
        needs_app = "App" in test_type or "Monkey" in test_type
        
        if needs_app:
            self.app_frame.pack(fill=tk.X, pady=(0, 15), before=self.btn_start.master)
            if "System-wide" not in test_type:
                self.entry_pkg.config(state=tk.NORMAL)
                self.btn_fetch_apps.config(state=tk.NORMAL)
            else:
                self.entry_pkg.config(state=tk.DISABLED)
                self.btn_fetch_apps.config(state=tk.DISABLED)
                
            if "Monkey" in test_type:
                self.entry_throttle.config(state=tk.NORMAL)
                self.chk_ignore_crash.config(state=tk.NORMAL)
            else:
                self.entry_throttle.config(state=tk.DISABLED)
                self.chk_ignore_crash.config(state=tk.DISABLED)
        else:
            self.app_frame.pack_forget()

    def open_logs(self):
        path = os.path.abspath(LOG_DIR)
        try:
            if os.name == 'nt': os.startfile(path)
            elif sys.platform == 'darwin': subprocess.Popen(['open', path])
            else: subprocess.Popen(['xdg-open', path])
            self.ui_log("📁 Log folder opened.")
        except Exception as e:
            self.ui_log(f"Failed to open folder: {e}")

    def ui_log(self, msg):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_msg = f"[{ts}] {msg}"
        self.text_log.insert(tk.END, full_msg + "\n")
        self.text_log.see(tk.END)
        if self.current_log_file:
            try:
                with open(self.current_log_file, "a", encoding="utf-8") as f:
                    f.write(full_msg + "\n")
            except: pass

    def run_adb(self, cmd_list, capture=True):
        try:
            if os.name == 'nt':
                cmd_str = "adb " + " ".join(cmd_list)
                res = subprocess.run(cmd_str, shell=True, capture_output=capture, text=True, timeout=15)
            else:
                res = subprocess.run(["adb"] + cmd_list, capture_output=capture, text=True, timeout=15)
            return res.stdout.strip() if capture else ""
        except Exception as e:
            return ""

    def fetch_apps_ui(self):
        self.ui_log("🔄 Fetching 3rd-party apps from device via ADB...")
        self.btn_fetch_apps.config(state=tk.DISABLED)
        threading.Thread(target=self._bg_fetch_apps, daemon=True).start()

    def _bg_fetch_apps(self):
        out = self.run_adb(["shell", "pm", "list", "packages", "-3"])
        pkgs = [p.replace("package:", "") for p in out.splitlines() if p.startswith("package:")]
        pkgs.sort()
        self.root.after(0, lambda: self._show_app_selector(pkgs))

    def _show_app_selector(self, pkgs):
        self.btn_fetch_apps.config(state=tk.NORMAL)
        if not pkgs:
            messagebox.showwarning("Warning", "No 3rd-party apps found.")
            return

        top = tk.Toplevel(self.root)
        top.title("Select Apps to Test")
        top.geometry("400x500")
        tk.Label(top, text="Please check the apps for testing:", font=("Arial", 11)).pack(pady=10)
        
        listbox = tk.Listbox(top, selectmode=tk.MULTIPLE, font=("Consolas", 11))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10)
        for p in pkgs: listbox.insert(tk.END, p)

        def confirm_selection():
            selected_pkgs = [listbox.get(i) for i in listbox.curselection()]
            self.entry_pkg.delete(0, tk.END)
            self.entry_pkg.insert(0, ",".join(selected_pkgs))
            top.destroy()
            self.ui_log(f"✅ Selected {len(selected_pkgs)} apps.")

        tk.Button(top, text="Confirm Selection", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=confirm_selection).pack(pady=10, fill=tk.X, padx=10)

    # ==========================================
    # Core Testing Logic
    # ==========================================
    def start_test(self):
        target_str = self.entry_target.get().strip()
        if not target_str.isdigit() or int(target_str) <= 0:
            messagebox.showerror("Error", "Please enter a valid number greater than 0!")
            return

        self.is_testing = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.combo_test.config(state=tk.DISABLED)

        test_type = self.test_type_var.get()
        target_val = int(target_str)
        
        type_map = {
            "WiFi ON/OFF Test": "WiFi",
            "Screen Sleep/Wake": "Screen_OnOff",
            "Gallery UI Tap": "Gallery_UI",
            "Monkey (System-wide Random)": "Monkey_Sys",
            "Monkey (Specific App)": "Monkey_App",
            "Battery Spoofing & Power State": "Battery_Spoof",
            "CPU Thermal Throttling (Mins)": "CPU_Thermal",
            "Storage I/O Stress (1GB)": "Storage_IO",
            "Airplane Mode Toggle": "Airplane_Mode",
            "App Cold-Start & Kill": "App_ColdStart"
        }
        
        base_test_name = type_map.get(test_type, "Test")
        if "Monkey" in test_type: unit = "Events"
        elif "Mins" in test_type: unit = "Mins"
        else: unit = "Cycles"
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_log_name = f"{base_test_name}_{target_val}{unit}"
        self.current_log_file = os.path.join(LOG_DIR, f"{self.base_log_name}_running_{timestamp}.txt")

        threading.Thread(target=self._run_test_thread, args=(test_type, target_val, timestamp), daemon=True).start()

    def _run_test_thread(self, test_type, target_val, timestamp):
        status = "FAIL"
        err_msg = ""
        completed = 0
        device_ready = False

        try:
            self.ui_log(f"=== Test Started: {test_type} ===")
            self.ui_log("⏳ Waiting for device connection...")

            for _ in range(30): 
                if not self.is_testing: return
                if "adb_ok" in self.run_adb(["shell", "echo", "adb_ok"]):
                    device_ready = True
                    break
                time.sleep(1)

            if not device_ready:
                raise Exception("Failed to connect to device! (Ensure phone is plugged in and ADB is authorized)")

            self.ui_log("✅ Device connected successfully!")
            
            # Start Background Logcat
            logcat_file = os.path.join(LOG_DIR, f"{self.base_log_name}_{timestamp}_logcat.txt")
            self.run_adb(["logcat", "-c"], capture=False) 
            cmd_logcat = f"adb logcat -v threadtime > {logcat_file}" if os.name == 'nt' else ["adb", "logcat", "-v", "threadtime"]
            self.logcat_proc = subprocess.Popen(cmd_logcat, shell=(os.name == 'nt'), stdout=subprocess.DEVNULL)
            self.ui_log(f"📹 Background Logcat recording started...")

            # === Start Actual Test Logic ===
            if test_type == "WiFi ON/OFF Test":
                for i in range(1, target_val + 1):
                    if not self.is_testing: break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Disable WiFi ---")
                    self.run_adb(["shell", "svc", "wifi", "disable"])
                    time.sleep(3)
                    self.ui_log(f"--- Cycle {i}/{target_val} : Enable WiFi ---")
                    self.run_adb(["shell", "svc", "wifi", "enable"])
                    time.sleep(5)
                    completed = i

            elif test_type == "Screen Sleep/Wake":
                for i in range(1, target_val + 1):
                    if not self.is_testing: break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Turn off screen (Sleep) ---")
                    self.run_adb(["shell", "input", "keyevent", "223"])
                    time.sleep(10)
                    self.ui_log(f"--- Cycle {i}/{target_val} : Wake up screen ---")
                    self.run_adb(["shell", "input", "keyevent", "224"])
                    time.sleep(2)
                    completed = i

            elif test_type == "Gallery UI Tap":
                self.run_adb(["shell", "input", "keyevent", "224"]) 
                for i in range(1, target_val + 1):
                    if not self.is_testing: break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Launching Gallery ---")
                    self.run_adb(["shell", "monkey", "-p", "com.google.android.apps.photos", "-c", "android.intent.category.LAUNCHER", "1"])
                    time.sleep(4)
                    for action in [("tap", "300 800", 2), ("tap", "500 500", 2), ("tap", "300 2000", 3), ("tap", "500 2000", 2)]:
                        if not self.is_testing: break
                        self.run_adb(["shell", "input", action[0]] + action[1].split())
                        time.sleep(action[2])
                    self.run_adb(["shell", "input", "keyevent", "4"])
                    time.sleep(2)
                    completed = i

            elif "Monkey" in test_type:
                cmd = ["shell", "monkey"]
                if test_type == "Monkey (Specific App)":
                    for p in [x.strip() for x in self.entry_pkg.get().split(",") if x.strip()]: 
                        cmd.extend(["-p", p])
                cmd.extend(["--throttle", self.entry_throttle.get().strip() or "300"])
                if self.ignore_crash_var.get():
                    cmd.extend(["--ignore-crashes", "--ignore-timeouts", "--ignore-security-exceptions"])
                cmd.extend(["-v", "-v", "-v", str(target_val)])
                
                self.ui_log(f"🚀 Launching Monkey...")
                cmd_monkey = "adb " + " ".join(cmd) if os.name == 'nt' else ["adb"] + cmd
                self.monkey_proc = subprocess.Popen(cmd_monkey, shell=(os.name == 'nt'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
                
                for line in self.monkey_proc.stdout:
                    if not self.is_testing: break
                    self.ui_log("Monkey: " + line.strip())
                self.monkey_proc.wait()
                completed = target_val if self.monkey_proc.returncode == 0 else 0

            # 🔋 1. Battery Spoofing & Power State
            elif test_type == "Battery Spoofing & Power State":
                for i in range(1, target_val + 1):
                    if not self.is_testing: break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Spoofing 5% Battery & Unplugged ---")
                    self.run_adb(["shell", "dumpsys", "battery", "unplug"])
                    self.run_adb(["shell", "dumpsys", "battery", "set", "level", "5"])
                    time.sleep(5)
                    self.ui_log(f"--- Cycle {i}/{target_val} : Resetting Battery State to Normal ---")
                    self.run_adb(["shell", "dumpsys", "battery", "reset"])
                    time.sleep(5)
                    completed = i

            # 🔥 2. CPU Thermal Throttling Test
            elif test_type == "CPU Thermal Throttling (Mins)":
                self.ui_log(f"🔥 Spawning heavy background processes to max out CPU...")
                # Spawning 4 background processes to calculate md5 of random stream (heavy CPU load)
                for _ in range(4):
                    cmd_cpu = "adb shell \"cat /dev/urandom | md5sum\"" if os.name == 'nt' else ["adb", "shell", "cat /dev/urandom | md5sum"]
                    p = subprocess.Popen(cmd_cpu, shell=(os.name == 'nt'), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.cpu_procs.append(p)
                
                for m in range(target_val):
                    for s in range(60): # 1 minute wait
                        if not self.is_testing: break
                        time.sleep(1)
                    if not self.is_testing: break
                    
                    temp_raw = self.run_adb(["shell", "cat", "/sys/class/thermal/thermal_zone0/temp"])
                    try:
                        temp_c = float(temp_raw) / 1000.0 if len(temp_raw) > 3 else float(temp_raw)
                        self.ui_log(f"--- {m+1}/{target_val} Mins Completed. CPU Thermal Zone 0: {temp_c}°C ---")
                    except:
                        self.ui_log(f"--- {m+1}/{target_val} Mins Completed. CPU Temp: {temp_raw} ---")
                    completed = m + 1

            # 💾 3. Storage eMMC/UFS Stress Test
            elif test_type == "Storage I/O Stress (1GB)":
                for i in range(1, target_val + 1):
                    if not self.is_testing: break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Writing 1GB Dummy File (/data/local/tmp/test_1gb.tmp) ---")
                    out = self.run_adb(["shell", "dd", "if=/dev/zero", "of=/data/local/tmp/test_1gb.tmp", "bs=1M", "count=1000"])
                    self.ui_log(f"DD Write Output: {out}")
                    time.sleep(1)
                    
                    self.ui_log(f"--- Cycle {i}/{target_val} : Deleting 1GB Dummy File ---")
                    self.run_adb(["shell", "rm", "-f", "/data/local/tmp/test_1gb.tmp"])
                    time.sleep(1)
                    completed = i

            # ✈️ 4. Airplane Mode Toggle
            elif test_type == "Airplane Mode Toggle":
                for i in range(1, target_val + 1):
                    if not self.is_testing: break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Airplane Mode ON ---")
                    self.run_adb(["shell", "settings", "put", "global", "airplane_mode_on", "1"])
                    self.run_adb(["shell", "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true"])
                    time.sleep(4)
                    
                    self.ui_log(f"--- Cycle {i}/{target_val} : Airplane Mode OFF ---")
                    self.run_adb(["shell", "settings", "put", "global", "airplane_mode_on", "0"])
                    self.run_adb(["shell", "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "false"])
                    time.sleep(4)
                    completed = i

            # 🚀 5. App Cold-Start & Kill Loop
            elif test_type == "App Cold-Start & Kill":
                pkgs = [x.strip() for x in self.entry_pkg.get().split(",") if x.strip()]
                if not pkgs:
                    raise Exception("Please select or enter a Target Package for Cold-Start Test!")
                pkg = pkgs[0] # Test one package at a time
                
                for i in range(1, target_val + 1):
                    if not self.is_testing: break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Force-Stopping App [{pkg}] ---")
                    self.run_adb(["shell", "am", "force-stop", pkg])
                    time.sleep(2)
                    
                    self.ui_log(f"--- Cycle {i}/{target_val} : Cold-Starting App [{pkg}] ---")
                    self.run_adb(["shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"])
                    time.sleep(5) # Wait for cold start UI to settle
                    completed = i

        except Exception as e:
            status = "FAIL"
            err_msg = str(e)
            self.ui_log(f"❌ Exception occurred: {err_msg}")
            
        finally:
            # ==========================================
            # Safe Teardown Block
            # ==========================================
            if not self.is_testing and status != "FAIL":
                status = "STOPPED"
                
            if self.logcat_proc:
                self.logcat_proc.terminate()
                self.ui_log("🛑 Logcat recording stopped.")

            # Cleanup CPU Stress Procs
            for p in self.cpu_procs:
                try: p.terminate()
                except: pass
            self.cpu_procs.clear()
            self.run_adb(["shell", "killall", "cat"], capture=False)
            self.run_adb(["shell", "killall", "md5sum"], capture=False)

            # Cleanup Battery status
            self.run_adb(["shell", "dumpsys", "battery", "reset"], capture=False)

            if device_ready:
                self.ui_log("\n==========================================")
                self.ui_log("⏳ Fetching Bugreport in background (takes 1~3 mins), do not unplug phone...")
                bugreport_file = os.path.join(LOG_DIR, f"{self.base_log_name}_{status}_{timestamp}_bugreport.zip")
                self.run_adb(["bugreport", bugreport_file], capture=False)
                self.ui_log(f"✅ Bugreport saved: {bugreport_file}")

            self.ui_log("==========================================")
            self.ui_log("             TEST SUMMARY                 ")
            self.ui_log("==========================================")
            self.ui_log(f"TEST RESULT  : {status}")
            self.ui_log(f"TARGET       : {target_val}")
            self.ui_log(f"COMPLETED    : {completed}")
            self.ui_log("==========================================")

            final_log_file = os.path.join(LOG_DIR, f"{self.base_log_name}_{status}_{timestamp}.txt")
            if self.current_log_file and os.path.exists(self.current_log_file):
                os.rename(self.current_log_file, final_log_file)
                self.current_log_file = None

            self.ui_log(f"🎉 Test status reset.")
            self.root.after(0, self.reset_ui) 

    def stop_test(self):
        self.ui_log("🛑 Force stop command received, interrupting test...")
        self.is_testing = False
        
        if self.monkey_proc:
            self.monkey_proc.terminate()
            
        threading.Thread(target=lambda: self.run_adb(["shell", "killall", "com.android.commands.monkey"], capture=False), daemon=True).start()

    def reset_ui(self):
        self.is_testing = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.combo_test.config(state="readonly")

if __name__ == "__main__":
    root = tk.Tk()
    app = ADBStressGUI(root)
    root.mainloop()