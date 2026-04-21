import os
import sys
import time
import socket
import datetime
import threading
import subprocess
import concurrent.futures
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
        self.root.title("Android ADB Stress Test Console (Pro Edition) v2.1.0")
        self.root.geometry("1000x900")
        
        try:
            self.root.iconbitmap("app_icon.ico")
        except Exception:
            pass
        
        self.device_testing_state = {} 
        self.devices_status = {}       
        self.logcat_procs = {}
        self.monkey_procs = {}
        self.cpu_procs = {}
        self.dl_procs = {} 

        self.setup_ui()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_local_subnet_prefix(self):
        """自動獲取本機電腦當前所在的網段 (例如 192.168.1.)"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # 連線到一個外部公網 IP 來取得本機的正確對外網卡 IP
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            parts = local_ip.split('.')
            return f"{parts[0]}.{parts[1]}.{parts[2]}."
        except Exception:
            return "192.168.1." # 失敗時的預設值

    def setup_ui(self):
        left_container = tk.Frame(self.root, width=380, padx=10, pady=10)
        left_container.pack(side=tk.LEFT, fill=tk.Y)
        left_container.pack_propagate(False)

        self.btn_frame = tk.Frame(left_container)
        self.btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.btn_start = tk.Button(self.btn_frame, text="▶️ START Selected", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=self.start_test)
        self.btn_start.pack(fill=tk.X, pady=(0, 10))

        self.btn_stop = tk.Button(self.btn_frame, text="⏹️ STOP Selected", font=("Arial", 12, "bold"), bg="#F44336", fg="white", command=self.stop_test)
        self.btn_stop.pack(fill=tk.X, pady=(0, 10))

        self.btn_open_logs = tk.Button(self.btn_frame, text="📁 Open Logs", font=("Arial", 12), bg="#2196F3", fg="white", command=self.open_logs)
        self.btn_open_logs.pack(fill=tk.X)

        control_frame = tk.Frame(left_container)
        control_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        dev_frame = tk.LabelFrame(control_frame, text="📱 Connected Devices Dashboard", font=("Arial", 10, "bold"), padx=10, pady=5)
        dev_frame.pack(fill=tk.X, pady=(0, 15))
        
        scan_frame = tk.Frame(dev_frame)
        scan_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 🌟 自動填入本機網段，並預設掃描 1 ~ 254
        local_prefix = self.get_local_subnet_prefix()
        
        tk.Label(scan_frame, text="IP:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.entry_ip_prefix = tk.Entry(scan_frame, font=("Arial", 9), width=11)
        self.entry_ip_prefix.insert(0, local_prefix)
        self.entry_ip_prefix.pack(side=tk.LEFT, padx=(0, 2))
        
        self.entry_ip_start = tk.Entry(scan_frame, font=("Arial", 9), width=4)
        self.entry_ip_start.insert(0, "1")
        self.entry_ip_start.pack(side=tk.LEFT)
        
        tk.Label(scan_frame, text="-", font=("Arial", 9)).pack(side=tk.LEFT)
        
        self.entry_ip_end = tk.Entry(scan_frame, font=("Arial", 9), width=4)
        self.entry_ip_end.insert(0, "254")
        self.entry_ip_end.pack(side=tk.LEFT, padx=(0, 2))

        self.btn_scan = tk.Button(scan_frame, text="🔌 Scan Subnet", font=("Arial", 9, "bold"), bg="#FF9800", fg="white", command=self.auto_connect_subnet)
        self.btn_scan.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

        self.device_listbox = tk.Listbox(dev_frame, selectmode=tk.MULTIPLE, height=10, font=("Consolas", 10))
        self.device_listbox.pack(fill=tk.X, pady=(0, 5))
        
        self.btn_refresh_dev = tk.Button(dev_frame, text="🔄 Refresh Devices", command=self.refresh_devices)
        self.btn_refresh_dev.pack(fill=tk.X)

        tk.Label(control_frame, text="⚙️ Configure Next Test", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        self.test_type_var = tk.StringVar(value="Background Download Stress (curl/wget)")
        test_options = [
            "Background Download Stress (curl/wget)", 
            "Browser Download Stress (Intent)",       
            "WiFi ON/OFF Test", 
            "Bluetooth ON/OFF Test",
            "Mobile Data Toggle",
            "Microphone Audio HAL Stress",   
            "Mic/Camera Privacy Toggle",     
            "Screen Sleep/Wake", 
            "Gallery UI Tap", 
            "Monkey (System-wide Random)", 
            "Monkey (Specific App)",
            "App Cold-Start & Kill",
            "App Clear Data & Restart",
            "Battery Spoofing & Power State",
            "CPU Thermal Throttling (Mins)",
            "Storage I/O Stress (1GB)",
            "Airplane Mode Toggle"
        ]
        self.combo_test = ttk.Combobox(control_frame, textvariable=self.test_type_var, values=test_options, state="readonly", font=("Arial", 11))
        self.combo_test.pack(fill=tk.X, pady=(0, 15))
        self.combo_test.bind("<<ComboboxSelected>>", self.on_test_type_changed)

        tk.Label(control_frame, text="🎯 Target (Cycles / Mins)", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.entry_target = tk.Entry(control_frame, font=("Arial", 11))
        self.entry_target.insert(0, "60")
        self.entry_target.pack(fill=tk.X, pady=(0, 15))

        self.dl_frame = tk.LabelFrame(control_frame, text="Download Stress Settings", padx=10, pady=10)
        
        self.dl_presets = {
            "Google CTS Media 1.5 [Global] (~240MB)": {
                "url": "https://dl.google.com/dl/android/cts/android-cts-media-1.5.zip",
                "file": "android-cts-media-1.5.zip"
            },
            "Google Platform Tools [Global] (~15MB)": {
                "url": "https://dl.google.com/android/repository/platform-tools-latest-windows.zip",
                "file": "platform-tools-latest-windows.zip"
            },
            "Tencent WeChat Setup [China] (~210MB)": {
                "url": "https://dldir1.qq.com/weixin/Windows/WeChatSetup.exe",
                "file": "WeChatSetup.exe"
            },
            "Tsinghua Ubuntu ISO [China] (~2.6GB)": {
                "url": "https://mirrors.tuna.tsinghua.edu.cn/ubuntu-releases/24.04/ubuntu-24.04.1-live-server-amd64.iso",
                "file": "ubuntu-24.04.1-live-server-amd64.iso"
            },
            "Hetzner Speed Test [Europe] (~100MB)": {
                "url": "https://speed.hetzner.de/100MB.bin",
                "file": "100MB.bin"
            },
            "Hetzner Speed Test [Europe] (~1GB)": {
                "url": "https://speed.hetzner.de/1GB.bin",
                "file": "1GB.bin"
            }
        }
        
        tk.Label(self.dl_frame, text="📂 Quick Select Test File:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.combo_dl_preset = ttk.Combobox(self.dl_frame, values=list(self.dl_presets.keys()), state="readonly", font=("Arial", 9))
        self.combo_dl_preset.set("Google CTS Media 1.5 [Global] (~240MB)")
        self.combo_dl_preset.pack(fill=tk.X, pady=(0, 10))
        self.combo_dl_preset.bind("<<ComboboxSelected>>", self.on_dl_preset_changed)
        
        tk.Label(self.dl_frame, text="🔗 Download URL:", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_dl_url = tk.Entry(self.dl_frame, font=("Arial", 10))
        self.entry_dl_url.insert(0, self.dl_presets["Google CTS Media 1.5 [Global] (~240MB)"]["url"]) 
        self.entry_dl_url.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(self.dl_frame, text="📄 Expected Filename (Browser only):", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_dl_file = tk.Entry(self.dl_frame, font=("Arial", 10))
        self.entry_dl_file.insert(0, self.dl_presets["Google CTS Media 1.5 [Global] (~240MB)"]["file"]) 
        self.entry_dl_file.pack(fill=tk.X, pady=(0, 5))

        tk.Label(self.dl_frame, text="⏱️ Timeout (sec):", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_dl_timeout = tk.Entry(self.dl_frame, font=("Arial", 10))
        self.entry_dl_timeout.insert(0, "300") 
        self.entry_dl_timeout.pack(fill=tk.X, pady=(0, 5))
        
        self.delete_dl_var = tk.BooleanVar(value=True)
        self.chk_delete_dl = tk.Checkbutton(self.dl_frame, text="Delete file after cycle/test completes", variable=self.delete_dl_var)
        self.chk_delete_dl.pack(anchor=tk.W)

        self.app_frame = tk.LabelFrame(control_frame, text="App Specific Settings", padx=10, pady=10)
        tk.Label(self.app_frame, text="📦 Target Package (comma-separated):", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_pkg = tk.Entry(self.app_frame, font=("Arial", 10))
        self.entry_pkg.pack(fill=tk.X, pady=(0, 5))
        
        self.btn_fetch_apps = tk.Button(self.app_frame, text="🔍 Fetch Apps from 1st Selected Device", command=self.fetch_apps_ui)
        self.btn_fetch_apps.pack(fill=tk.X, pady=(0, 10))

        tk.Label(self.app_frame, text="⏱️ Tap Interval (Monkey only, ms):", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_throttle = tk.Entry(self.app_frame, font=("Arial", 10))
        self.entry_throttle.insert(0, "300")
        self.entry_throttle.pack(fill=tk.X, pady=(0, 10))

        self.ignore_crash_var = tk.BooleanVar(value=True)
        self.chk_ignore_crash = tk.Checkbutton(self.app_frame, text="Ignore Crash/ANR (Monkey only)", variable=self.ignore_crash_var)
        self.chk_ignore_crash.pack(anchor=tk.W)

        self.screen_frame = tk.LabelFrame(control_frame, text="Screen ON/OFF Settings", padx=10, pady=10)
        tk.Label(self.screen_frame, text="🌙 Sleep Duration (sec):", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_sleep_time = tk.Entry(self.screen_frame, font=("Arial", 10))
        self.entry_sleep_time.insert(0, "10") 
        self.entry_sleep_time.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(self.screen_frame, text="☀️ Wake Duration (sec):", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_wake_time = tk.Entry(self.screen_frame, font=("Arial", 10))
        self.entry_wake_time.insert(0, "10") 
        self.entry_wake_time.pack(fill=tk.X, pady=(0, 5))

        log_frame = tk.Frame(self.root, padx=10, pady=10)
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(log_frame, text="📝 Real-time Multi-Device Log", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.text_log = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), bg="#1E1E1E", fg="#00FF00")
        self.text_log.pack(fill=tk.BOTH, expand=True)

        self.on_test_type_changed(None)
        
        self.ui_log(f"System ready. Local subnet detected: {local_prefix}x")
        self.root.after(500, self.auto_connect_subnet)

    def _get_file_size(self, serial, path):
        out = self.run_adb(["shell", "stat", "-c", "%s", f'"{path}"'], serial=serial).strip()
        if out and out.isdigit():
            return int(out)
            
        out = self.run_adb(["shell", "/system/bin/ls", "-nl", f'"{path}"'], serial=serial).strip()
        if not out or "No such" in out or "Not a" in out:
            return 0
            
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 5:
                size_str = parts[4]
                if size_str.isdigit():
                    return int(size_str)
                size_str = size_str.upper()
                if size_str.endswith('K') and size_str[:-1].isdigit(): return int(size_str[:-1]) * 1024
                if size_str.endswith('M') and size_str[:-1].isdigit(): return int(size_str[:-1]) * 1024 * 1024
                if size_str.endswith('G') and size_str[:-1].isdigit(): return int(size_str[:-1]) * 1024 * 1024 * 1024
        return 0

    def on_dl_preset_changed(self, event):
        selected = self.combo_dl_preset.get()
        if selected in self.dl_presets:
            self.entry_dl_url.delete(0, tk.END)
            self.entry_dl_url.insert(0, self.dl_presets[selected]["url"])
            
            self.entry_dl_file.delete(0, tk.END)
            self.entry_dl_file.insert(0, self.dl_presets[selected]["file"])

    # 🌟 核心升級：全網域超高速並發掃描
    def auto_connect_subnet(self):
        prefix = self.entry_ip_prefix.get().strip()
        try:
            start_ip = int(self.entry_ip_start.get().strip())
            end_ip = int(self.entry_ip_end.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid IP range!")
            return
            
        if start_ip > end_ip:
            messagebox.showerror("Error", "Start IP must be <= End IP")
            return
            
        self.btn_scan.config(state=tk.DISABLED)
        self.btn_refresh_dev.config(state=tk.DISABLED)
        threading.Thread(target=self._bg_auto_connect, args=(prefix, start_ip, end_ip), daemon=True).start()

    def _bg_auto_connect(self, prefix, start, end):
        self.ui_log(f"🔍 Fast scanning local subnet {prefix}{start} ~ {end}... (Takes ~3 seconds)")
        
        def connect_ip(ip):
            cmd = f"adb connect {ip}:5555" if os.name == 'nt' else ["adb", "connect", f"{ip}:5555"]
            try:
                # 只等 2 秒，能連上的馬上就會連上，沒回應的直接放生
                subprocess.run(cmd, shell=(os.name == 'nt'), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            except:
                pass

        ips_to_scan = [f"{prefix}{i}" for i in range(start, end + 1)]
        
        # 使用線程池同時執行 100 個 IP 的探測，瞬間掃完 254 個網址
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(connect_ip, ips_to_scan)
            
        self.ui_log(f"✅ Subnet scan finished. Refreshing list...")
        self.root.after(0, self.refresh_devices)
        self.root.after(0, lambda: self.btn_scan.config(state=tk.NORMAL))

    def on_closing(self):
        active_tests = any(self.device_testing_state.values())
        if active_tests:
            self.ui_log("⚠️ App close requested. Force cleaning up devices before exit...")
            
        for serial in list(self.devices_status.keys()):
            self.device_testing_state[serial] = False
            threading.Thread(target=self._cleanup_device_force, args=(serial,), daemon=True).start()
            
        time.sleep(1 if active_tests else 0.2)
        self.root.destroy()

    def _cleanup_device_force(self, serial):
        self.run_adb(["shell", "killall", "com.android.commands.monkey"], serial=serial, capture=False)
        self.run_adb(["shell", "killall", "tinycap"], serial=serial, capture=False)
        self.run_adb(["shell", "killall", "curl"], serial=serial, capture=False)
        self.run_adb(["shell", "killall", "wget"], serial=serial, capture=False)
        self.run_adb(["shell", "rm", "-f", "/data/local/tmp/dl_stress.tmp"], serial=serial, capture=False)
        self.run_adb(["shell", "rm", "-f", "/data/local/tmp/mic_stress.wav"], serial=serial, capture=False)
        dl_file = self.entry_dl_file.get().strip()
        if dl_file:
            base_name = os.path.splitext(dl_file)[0]
            self.run_adb(["shell", "rm", "-f", f"/sdcard/Download/{base_name}*"], serial=serial, capture=False)

    def refresh_devices(self, auto_recover=True):
        self.device_listbox.delete(0, tk.END)
        self.btn_refresh_dev.config(state=tk.DISABLED)
        
        try:
            if os.name == 'nt':
                res = subprocess.run("adb devices", shell=True, capture_output=True, text=True, timeout=15)
            else:
                res = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=15)
                
            if res.returncode != 0:
                if "not recognized" in res.stderr or "not found" in res.stderr or "is not recognized" in res.stdout:
                    raise FileNotFoundError("ADB not found in PATH")
                elif auto_recover:
                    raise Exception(f"ADB process failed. Return code: {res.returncode}")
                
            out = res.stdout
            lines = out.splitlines()
            current_serials = []
            
            for line in lines[1:]:
                if "device" in line and "offline" not in line and "unauthorized" not in line:
                    serial = line.split()[0]
                    current_serials.append(serial)
                    if serial not in self.devices_status:
                        self.devices_status[serial] = "Idle"
                        self.device_testing_state[serial] = False
            
            keys_to_remove = [s for s in self.devices_status if s not in current_serials]
            for s in keys_to_remove:
                del self.devices_status[s]
                if s in self.device_testing_state: del self.device_testing_state[s]

            self.update_listbox_display()
            
            if not current_serials:
                self.device_listbox.insert(tk.END, "No devices found")
                self.device_listbox.config(state=tk.DISABLED)
                self.btn_start.config(state=tk.DISABLED)
            else:
                self.device_listbox.config(state=tk.NORMAL)
                self.btn_start.config(state=tk.NORMAL)
                
            self.btn_refresh_dev.config(state=tk.NORMAL)
                
        except FileNotFoundError:
            self.device_listbox.insert(tk.END, "Error: ADB not found")
            self.device_listbox.config(state=tk.DISABLED)
            self.btn_start.config(state=tk.DISABLED)
            self.btn_refresh_dev.config(state=tk.NORMAL)
            self.ui_log("❌ Error: Cannot find 'adb'. Please put this executable in the SAME folder as adb.exe, or add ADB to PATH.")
            
        except Exception as e:
            if auto_recover:
                self.ui_log(f"⚠️ ADB Server unresponsive ({str(e)}). Attempting Auto-Recovery...")
                self.device_listbox.insert(tk.END, "Restarting ADB Server...")
                self.device_listbox.config(state=tk.DISABLED)
                self.root.update()
                threading.Thread(target=self._bg_recover_adb, daemon=True).start()
            else:
                self.device_listbox.insert(tk.END, "Error detecting devices")
                self.device_listbox.config(state=tk.DISABLED)
                self.btn_start.config(state=tk.DISABLED)
                self.btn_refresh_dev.config(state=tk.NORMAL)
                self.ui_log(f"❌ ADB recovery failed: {str(e)}")

    def _bg_recover_adb(self):
        try:
            if os.name == 'nt':
                subprocess.run("adb kill-server", shell=True, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1)
                subprocess.run("adb start-server", shell=True, timeout=10, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.run(["adb", "kill-server"], timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1)
                subprocess.run(["adb", "start-server"], timeout=10, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
        
        self.ui_log("🔄 ADB Server restart completed. Re-checking devices...")
        self.root.after(500, lambda: self.refresh_devices(auto_recover=False))

    def update_listbox_display(self):
        selections = self.device_listbox.curselection()
        selected_serials = [self._get_serial_from_listbox_text(self.device_listbox.get(i)) for i in selections] if selections else []
        
        self.device_listbox.delete(0, tk.END)
        for i, (serial, status) in enumerate(self.devices_status.items()):
            display_text = f"{serial} - {status}"
            self.device_listbox.insert(tk.END, display_text)
            if serial in selected_serials:
                self.device_listbox.select_set(i)

    def _get_serial_from_listbox_text(self, text):
        if " - " in text:
            return text.split(" - ")[0]
        return text

    def on_test_type_changed(self, event):
        test_type = self.test_type_var.get()
        needs_app = "App" in test_type or "Monkey" in test_type
        needs_screen = "Screen Sleep/Wake" in test_type
        needs_dl = "Download" in test_type
        
        self.dl_frame.pack_forget()
        self.app_frame.pack_forget()
        self.screen_frame.pack_forget()

        if needs_dl:
            self.dl_frame.pack(fill=tk.X, pady=(0, 15))
            if "Browser" in test_type:
                self.entry_dl_file.config(state=tk.NORMAL)
            else:
                self.entry_dl_file.config(state=tk.DISABLED)

        if needs_app:
            self.app_frame.pack(fill=tk.X, pady=(0, 15))
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

        if needs_screen:
            self.screen_frame.pack(fill=tk.X, pady=(0, 15))

    def open_logs(self):
        path = os.path.abspath(LOG_DIR)
        try:
            if os.name == 'nt': os.startfile(path)
            elif sys.platform == 'darwin': subprocess.Popen(['open', path])
            else: subprocess.Popen(['xdg-open', path])
            self.ui_log("📁 Log folder opened.")
        except Exception as e:
            self.ui_log(f"Failed to open folder: {e}")

    def ui_log(self, msg, serial=None, log_file=None):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = f"[{serial}] " if serial else ""
        full_msg = f"[{ts}] {prefix}{msg}"
        
        self.root.after(0, lambda: self._gui_log_insert(full_msg))
        
        if log_file:
            try:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(full_msg + "\n")
            except: pass

    def _gui_log_insert(self, full_msg):
        self.text_log.insert(tk.END, full_msg + "\n")
        self.text_log.see(tk.END)

    def run_adb(self, cmd_list, serial=None, capture=True):
        try:
            cmd = ["adb"]
            if serial:
                cmd.extend(["-s", serial])
            cmd.extend(cmd_list)
            
            if os.name == 'nt':
                cmd_str = " ".join(cmd)
                res = subprocess.run(cmd_str, shell=True, capture_output=capture, text=True, timeout=15)
            else:
                res = subprocess.run(cmd, capture_output=capture, text=True, timeout=15)
            return res.stdout.strip() if capture else ""
        except Exception as e:
            return ""

    def fetch_apps_ui(self):
        selections = self.device_listbox.curselection()
        if not selections or "No devices" in self.device_listbox.get(selections[0]):
            messagebox.showerror("Error", "Please select at least one device to fetch apps from.")
            return
            
        target_serial = self._get_serial_from_listbox_text(self.device_listbox.get(selections[0]))
        self.ui_log(f"🔄 Fetching apps from device [{target_serial}]...")
        self.btn_fetch_apps.config(state=tk.DISABLED)
        threading.Thread(target=self._bg_fetch_apps, args=(target_serial,), daemon=True).start()

    def _bg_fetch_apps(self, serial):
        out = self.run_adb(["shell", "pm", "list", "packages", "-3"], serial=serial)
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
            
        selections = self.device_listbox.curselection()
        if not selections or "No devices" in self.device_listbox.get(selections[0]):
            messagebox.showerror("Error", "Please select at least one device from the list!")
            return
            
        target_serials = [self._get_serial_from_listbox_text(self.device_listbox.get(i)) for i in selections]

        test_type = self.test_type_var.get()
        target_val = int(target_str)
        pkgs_str = self.entry_pkg.get().strip()
        throttle_val = self.entry_throttle.get().strip() or "300"
        ignore_crash_val = self.ignore_crash_var.get()
        
        dl_url = self.entry_dl_url.get().strip()
        dl_file = self.entry_dl_file.get().strip()
        dl_delete_after = self.delete_dl_var.get()
        
        try: dl_timeout = int(self.entry_dl_timeout.get().strip())
        except: dl_timeout = 300
        
        try: sleep_sec = int(self.entry_sleep_time.get().strip())
        except: sleep_sec = 10 
        try: wake_sec = int(self.entry_wake_time.get().strip())
        except: wake_sec = 10 
        
        type_map = {
            "Background Download Stress (curl/wget)": "Bg_Download",
            "Browser Download Stress (Intent)": "Browser_Download",
            "WiFi ON/OFF Test": "WiFi",
            "Bluetooth ON/OFF Test": "Bluetooth",
            "Mobile Data Toggle": "Mobile_Data",
            "Microphone Audio HAL Stress": "Mic_HAL",
            "Mic/Camera Privacy Toggle": "Privacy_Toggle",
            "Screen Sleep/Wake": "Screen_OnOff",
            "Gallery UI Tap": "Gallery_UI",
            "Monkey (System-wide Random)": "Monkey_Sys",
            "Monkey (Specific App)": "Monkey_App",
            "App Cold-Start & Kill": "App_ColdStart",
            "App Clear Data & Restart": "App_ClearData",
            "Battery Spoofing & Power State": "Battery_Spoof",
            "CPU Thermal Throttling (Mins)": "CPU_Thermal",
            "Storage I/O Stress (1GB)": "Storage_IO",
            "Airplane Mode Toggle": "Airplane_Mode"
        }
        
        base_test_name = type_map.get(test_type, "Test")
        unit = "Mins" if ("Monkey" in test_type or "Mins" in test_type) else "Cycles"
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        dispatched_count = 0
        for serial in target_serials:
            if self.device_testing_state.get(serial, False):
                self.ui_log(f"⚠️ Device [{serial}] is already running a test. Ignoring start command.")
                continue
                
            self.device_testing_state[serial] = True
            self.devices_status[serial] = f"Running: {test_type}"
            self.cpu_procs[serial] = []
            
            threading.Thread(
                target=self._run_test_thread, 
                args=(test_type, target_val, timestamp, base_test_name, unit, serial, pkgs_str, throttle_val, ignore_crash_val, sleep_sec, wake_sec, dl_url, dl_delete_after, dl_file, dl_timeout), 
                daemon=True
            ).start()
            dispatched_count += 1

        if dispatched_count > 0:
            self.update_listbox_display()
            self.ui_log(f"🚀 Successfully dispatched '{test_type}' to {dispatched_count} device(s).")

    def _run_test_thread(self, test_type, target_val, timestamp, base_test_name, unit, serial, pkgs_str, throttle_val, ignore_crash_val, sleep_sec, wake_sec, dl_url, dl_delete_after, dl_file, dl_timeout):
        status = "FAIL"
        err_msg = ""
        completed = 0
        device_ready = False
        orig_stay_on = "0" 
        
        safe_serial = serial.replace(":", "_").replace(".", "_")
        log_prefix = f"Dev[{safe_serial}]_{base_test_name}_{target_val}{unit}"
        run_log_file = os.path.join(LOG_DIR, f"{log_prefix}_running_{timestamp}.txt")

        try:
            self.ui_log(f"=== Test Started: {test_type} ===", serial, run_log_file)

            for _ in range(10): 
                if not self.device_testing_state.get(serial, False): return
                if "adb_ok" in self.run_adb(["shell", "echo", "adb_ok"], serial=serial):
                    device_ready = True
                    break
                time.sleep(1)

            if not device_ready:
                raise Exception("Failed to connect to device!")
            
            orig_stay_on = self.run_adb(["shell", "settings", "get", "global", "stay_on_while_plugged_in"], serial=serial)
            self.run_adb(["shell", "settings", "put", "global", "stay_on_while_plugged_in", "7"], serial=serial) 
            self.run_adb(["shell", "input", "keyevent", "224"], serial=serial) 
            time.sleep(1)
            self.run_adb(["shell", "input", "keyevent", "82"], serial=serial)  
            
            logcat_file = os.path.join(LOG_DIR, f"{log_prefix}_{timestamp}_logcat.txt")
            self.run_adb(["logcat", "-c"], serial=serial, capture=False) 
            
            if os.name == 'nt':
                cmd_logcat = f"adb -s {serial} logcat -v threadtime > {logcat_file}"
            else:
                cmd_logcat = ["adb", "-s", serial, "logcat", "-v", "threadtime"]
                
            proc = subprocess.Popen(cmd_logcat, shell=(os.name == 'nt'), stdout=subprocess.DEVNULL)
            self.logcat_procs[serial] = proc

            # === Start Actual Test Logic ===
            if test_type == "Background Download Stress (curl/wget)":
                if not dl_url: raise Exception("Download URL cannot be empty!")
                    
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Background Downloading File ---", serial, run_log_file)
                    
                    self.run_adb(["shell", "rm", "-f", "/data/local/tmp/dl_stress.tmp"], serial=serial)
                    start_time = time.time()
                    
                    if os.name == 'nt':
                        cmd_dl = f"adb -s {serial} shell \"curl -s -k -L -o /data/local/tmp/dl_stress.tmp {dl_url} || wget -q --no-check-certificate -O /data/local/tmp/dl_stress.tmp {dl_url}\""
                    else:
                        cmd_dl = ["adb", "-s", serial, "shell", f"curl -s -k -L -o /data/local/tmp/dl_stress.tmp {dl_url} || wget -q --no-check-certificate -O /data/local/tmp/dl_stress.tmp {dl_url}"]
                        
                    dl_proc = subprocess.Popen(cmd_dl, shell=(os.name == 'nt'), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.dl_procs[serial] = dl_proc
                    
                    is_timeout = False
                    while dl_proc.poll() is None:
                        if not self.device_testing_state.get(serial, False):
                            try: dl_proc.terminate()
                            except: pass
                            self.run_adb(["shell", "killall", "curl"], serial=serial, capture=False)
                            self.run_adb(["shell", "killall", "wget"], serial=serial, capture=False)
                            break
                            
                        if time.time() - start_time > dl_timeout:
                            is_timeout = True
                            try: dl_proc.terminate()
                            except: pass
                            self.run_adb(["shell", "killall", "curl"], serial=serial, capture=False)
                            self.run_adb(["shell", "killall", "wget"], serial=serial, capture=False)
                            break
                            
                        time.sleep(1)
                        
                    if not self.device_testing_state.get(serial, False): break
                    if is_timeout: raise Exception(f"Cycle {i} Error: Download timed out after {dl_timeout}s.")
                    
                    size_bytes = self._get_file_size(serial, "/data/local/tmp/dl_stress.tmp")
                    if size_bytes == 0:
                        raise Exception(f"Cycle {i} Error: Download failed or file is 0 bytes.")
                        
                    elapsed = time.time() - start_time
                    size_mb = size_bytes / (1024 * 1024)
                    self.ui_log(f"✅ Downloaded {size_mb:.2f} MB in {elapsed:.1f}s", serial, run_log_file)
                    
                    if dl_delete_after:
                        self.ui_log(f"🧹 Cycle {i} finished. Cleaning up downloaded files...", serial, run_log_file)
                        self.run_adb(["shell", "rm", "-f", "/data/local/tmp/dl_stress.tmp"], serial=serial)
                    completed = i

            elif test_type == "Browser Download Stress (Intent)":
                if not dl_url or not dl_file:
                    raise Exception("Download URL and Expected Filename cannot be empty!")
                
                base_name = os.path.splitext(dl_file)[0]
                
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Launching Browser to Download ---", serial, run_log_file)
                    
                    self.run_adb(["shell", "rm", "-f", f"/sdcard/Download/{base_name}*"], serial=serial)
                    
                    self.run_adb(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", f"\"{dl_url}\""], serial=serial)
                    
                    start_time = time.time()
                    last_size = -1
                    stable_count = 0
                    downloaded = False
                    
                    self.ui_log("⏳ Waiting for browser download to complete...", serial, run_log_file)
                    
                    while time.time() - start_time < dl_timeout:
                        if not self.device_testing_state.get(serial, False): break
                        time.sleep(2)
                        
                        current_size = 0
                        out = self.run_adb(["shell", "/system/bin/ls", "-nl", "/sdcard/Download/"], serial=serial).strip()
                        for line in out.splitlines():
                            if base_name in line:
                                parts = line.split()
                                if len(parts) >= 5:
                                    size_str = parts[4]
                                    s = 0
                                    if size_str.isdigit():
                                        s = int(size_str)
                                    else:
                                        ss = size_str.upper()
                                        if ss.endswith('K') and ss[:-1].isdigit(): s = int(ss[:-1]) * 1024
                                        elif ss.endswith('M') and ss[:-1].isdigit(): s = int(ss[:-1]) * 1024 * 1024
                                        elif ss.endswith('G') and ss[:-1].isdigit(): s = int(ss[:-1]) * 1024 * 1024 * 1024
                                    if s > current_size:
                                        current_size = s
                                        
                        if current_size > 0:
                            if current_size == last_size:
                                stable_count += 1
                                if stable_count >= 3: 
                                    downloaded = True
                                    break
                            else:
                                stable_count = 0
                                size_mb = current_size / (1024 * 1024)
                                self.ui_log(f"   ... Browser downloading: {size_mb:.2f} MB", serial, run_log_file)
                        last_size = current_size
                            
                    if not self.device_testing_state.get(serial, False): break
                    
                    self.run_adb(["shell", "am", "force-stop", "com.android.chrome"], serial=serial)
                    self.run_adb(["shell", "am", "force-stop", "com.android.browser"], serial=serial)
                    self.run_adb(["shell", "am", "force-stop", "org.mozilla.firefox"], serial=serial)
                    
                    if downloaded:
                        size_mb = last_size / (1024 * 1024)
                        elapsed = time.time() - start_time
                        self.ui_log(f"✅ Browser downloaded {size_mb:.2f} MB in {elapsed:.1f}s", serial, run_log_file)
                    else:
                        raise Exception(f"Cycle {i} Error: Browser download timed out after {dl_timeout}s.")
                    
                    if dl_delete_after:
                        self.ui_log(f"🧹 Cycle {i} finished. Cleaning up downloaded files...", serial, run_log_file)
                        self.run_adb(["shell", "rm", "-f", f"/sdcard/Download/{base_name}*"], serial=serial)
                    
                    time.sleep(2)
                    completed = i

            elif test_type == "Microphone Audio HAL Stress":
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Opening Audio HAL & Recording (3s) ---", serial, run_log_file)
                    
                    if os.name == 'nt':
                        cmd_mic = f"adb -s {serial} shell \"tinycap /data/local/tmp/mic_stress.wav\""
                    else:
                        cmd_mic = ["adb", "-s", serial, "shell", "tinycap /data/local/tmp/mic_stress.wav"]
                        
                    mic_proc = subprocess.Popen(cmd_mic, shell=(os.name == 'nt'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    for _ in range(3):
                        if not self.device_testing_state.get(serial, False): break
                        time.sleep(1)
                        
                    try: mic_proc.terminate()
                    except: pass
                    self.run_adb(["shell", "killall", "tinycap"], serial=serial, capture=False)
                    
                    time.sleep(1)
                    self.ui_log(f"--- Cycle {i}/{target_val} : Deleting Audio File ---", serial, run_log_file)
                    self.run_adb(["shell", "rm", "-f", "/data/local/tmp/mic_stress.wav"], serial=serial)
                    time.sleep(2)
                    completed = i

            elif test_type == "Mic/Camera Privacy Toggle":
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Enable Privacy Mute (Sensors OFF) ---", serial, run_log_file)
                    self.run_adb(["shell", "cmd", "sensor_privacy", "enable", "microphone"], serial=serial)
                    self.run_adb(["shell", "cmd", "sensor_privacy", "enable", "camera"], serial=serial)
                    time.sleep(3)
                    
                    self.ui_log(f"--- Cycle {i}/{target_val} : Disable Privacy Mute (Sensors ON) ---", serial, run_log_file)
                    self.run_adb(["shell", "cmd", "sensor_privacy", "disable", "microphone"], serial=serial)
                    self.run_adb(["shell", "cmd", "sensor_privacy", "disable", "camera"], serial=serial)
                    time.sleep(3)
                    completed = i

            elif test_type == "WiFi ON/OFF Test":
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Disable WiFi ---", serial, run_log_file)
                    self.run_adb(["shell", "svc", "wifi", "disable"], serial=serial)
                    time.sleep(3)
                    self.ui_log(f"--- Cycle {i}/{target_val} : Enable WiFi ---", serial, run_log_file)
                    self.run_adb(["shell", "svc", "wifi", "enable"], serial=serial)
                    time.sleep(5)
                    completed = i

            elif test_type == "Bluetooth ON/OFF Test":
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Disable Bluetooth ---", serial, run_log_file)
                    self.run_adb(["shell", "svc", "bluetooth", "disable"], serial=serial)
                    time.sleep(3)
                    self.ui_log(f"--- Cycle {i}/{target_val} : Enable Bluetooth ---", serial, run_log_file)
                    self.run_adb(["shell", "svc", "bluetooth", "enable"], serial=serial)
                    time.sleep(5)
                    completed = i

            elif test_type == "Mobile Data Toggle":
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Disable Mobile Data ---", serial, run_log_file)
                    self.run_adb(["shell", "svc", "data", "disable"], serial=serial)
                    time.sleep(3)
                    self.ui_log(f"--- Cycle {i}/{target_val} : Enable Mobile Data ---", serial, run_log_file)
                    self.run_adb(["shell", "svc", "data", "enable"], serial=serial)
                    time.sleep(5)
                    completed = i

            elif test_type == "Screen Sleep/Wake":
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Turn off screen ---", serial, run_log_file)
                    self.run_adb(["shell", "input", "keyevent", "223"], serial=serial)
                    
                    self.ui_log(f"Sleeping for {sleep_sec}s...", serial, run_log_file)
                    for _ in range(sleep_sec):
                        if not self.device_testing_state.get(serial, False): break
                        time.sleep(1)
                        
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Wake up screen ---", serial, run_log_file)
                    self.run_adb(["shell", "input", "keyevent", "224"], serial=serial)
                    
                    time.sleep(2) 
                    power_state = self.run_adb(["shell", "dumpsys", "power"], serial=serial)
                    if not power_state:
                        raise Exception(f"Cycle {i} Error: ADB disconnected or device frozen.")
                    if "mWakefulness=Awake" not in power_state:
                        raise Exception(f"Cycle {i} Wakeup Fail: Stuck in sleep state.")
                    
                    self.ui_log(f"Keeping screen ON for {wake_sec}s...", serial, run_log_file)
                    for _ in range(wake_sec):
                        if not self.device_testing_state.get(serial, False): break
                        time.sleep(1)
                        
                    completed = i

            elif test_type == "Gallery UI Tap":
                self.run_adb(["shell", "input", "keyevent", "224"], serial=serial) 
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Launching Gallery ---", serial, run_log_file)
                    self.run_adb(["shell", "monkey", "-p", "com.google.android.apps.photos", "-c", "android.intent.category.LAUNCHER", "1"], serial=serial)
                    time.sleep(4)
                    for action in [("tap", "300 800", 2), ("tap", "500 500", 2), ("tap", "300 2000", 3), ("tap", "500 2000", 2)]:
                        if not self.device_testing_state.get(serial, False): break
                        self.run_adb(["shell", "input", action[0]] + action[1].split(), serial=serial)
                        time.sleep(action[2])
                    self.run_adb(["shell", "input", "keyevent", "4"], serial=serial)
                    time.sleep(2)
                    completed = i

            elif "Monkey" in test_type:
                cmd = ["shell", "monkey"]
                if test_type == "Monkey (Specific App)":
                    for p in [x.strip() for x in pkgs_str.split(",") if x.strip()]: 
                        cmd.extend(["-p", p])
                cmd.extend(["--throttle", throttle_val])
                if ignore_crash_val:
                    cmd.extend(["--ignore-crashes", "--ignore-timeouts", "--ignore-security-exceptions"])
                
                cmd.extend(["-v", "-v", "-v", "999999999"])
                
                self.ui_log(f"🚀 Launching Monkey for {target_val} minutes...", serial, run_log_file)
                if os.name == 'nt':
                    cmd_monkey = f"adb -s {serial} " + " ".join(cmd)
                else:
                    cmd_monkey = ["adb", "-s", serial] + cmd
                    
                proc = subprocess.Popen(cmd_monkey, shell=(os.name == 'nt'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
                self.monkey_procs[serial] = proc
                
                def log_monkey_output(p, s, log_f):
                    try:
                        for line in p.stdout:
                            if not self.device_testing_state.get(s, False): break
                            self.ui_log("Monkey: " + line.strip(), s, log_f)
                    except: pass
                
                threading.Thread(target=log_monkey_output, args=(proc, serial, run_log_file), daemon=True).start()
                
                start_time = time.time()
                target_sec = target_val * 60
                
                while proc.poll() is None:
                    if not self.device_testing_state.get(serial, False): break
                    if time.time() - start_time >= target_sec:
                        self.ui_log(f"⏱️ Target time {target_val} minutes reached. Stopping Monkey...", serial, run_log_file)
                        break
                    time.sleep(1)
                
                try: proc.terminate()
                except: pass
                self.run_adb(["shell", "killall", "com.android.commands.monkey"], serial=serial, capture=False)
                
                actual_elapsed_mins = int((time.time() - start_time) / 60)
                completed = target_val if (time.time() - start_time) >= target_sec else actual_elapsed_mins

            elif test_type == "App Cold-Start & Kill":
                pkgs = [x.strip() for x in pkgs_str.split(",") if x.strip()]
                if not pkgs: raise Exception("Target Package is required!")
                pkg = pkgs[0] 
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Force-Stopping App [{pkg}] ---", serial, run_log_file)
                    self.run_adb(["shell", "am", "force-stop", pkg], serial=serial)
                    time.sleep(2)
                    self.ui_log(f"--- Cycle {i}/{target_val} : Cold-Starting App [{pkg}] ---", serial, run_log_file)
                    self.run_adb(["shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"], serial=serial)
                    time.sleep(5) 
                    completed = i

            elif test_type == "App Clear Data & Restart":
                pkgs = [x.strip() for x in pkgs_str.split(",") if x.strip()]
                if not pkgs: raise Exception("Target Package is required!")
                pkg = pkgs[0] 
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Wiping Data for [{pkg}] ---", serial, run_log_file)
                    self.run_adb(["shell", "pm", "clear", pkg], serial=serial)
                    time.sleep(2)
                    self.ui_log(f"--- Cycle {i}/{target_val} : Starting App [{pkg}] ---", serial, run_log_file)
                    self.run_adb(["shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"], serial=serial)
                    time.sleep(5) 
                    completed = i

            elif test_type == "Battery Spoofing & Power State":
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Spoofing 5% Battery ---", serial, run_log_file)
                    self.run_adb(["shell", "dumpsys", "battery", "unplug"], serial=serial)
                    self.run_adb(["shell", "dumpsys", "battery", "set", "level", "5"], serial=serial)
                    time.sleep(5)
                    self.ui_log(f"--- Cycle {i}/{target_val} : Resetting Battery State ---", serial, run_log_file)
                    self.run_adb(["shell", "dumpsys", "battery", "reset"], serial=serial)
                    time.sleep(5)
                    completed = i

            elif test_type == "CPU Thermal Throttling (Mins)":
                self.ui_log(f"🔥 Spawning heavy processes...", serial, run_log_file)
                for _ in range(4):
                    if os.name == 'nt':
                        cmd_cpu = f"adb -s {serial} shell \"cat /dev/urandom | md5sum\""
                    else:
                        cmd_cpu = ["adb", "-s", serial, "shell", "cat /dev/urandom | md5sum"]
                    p = subprocess.Popen(cmd_cpu, shell=(os.name == 'nt'), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.cpu_procs[serial].append(p)
                
                for m in range(target_val):
                    for s in range(60): 
                        if not self.device_testing_state.get(serial, False): break
                        time.sleep(1)
                    if not self.device_testing_state.get(serial, False): break
                    
                    temp_raw = self.run_adb(["shell", "cat", "/sys/class/thermal/thermal_zone0/temp"], serial=serial)
                    try:
                        temp_c = float(temp_raw) / 1000.0 if len(temp_raw) > 3 else float(temp_raw)
                        self.ui_log(f"--- {m+1}/{target_val} Mins. CPU Zone0: {temp_c}°C ---", serial, run_log_file)
                    except:
                        self.ui_log(f"--- {m+1}/{target_val} Mins. CPU Temp: {temp_raw} ---", serial, run_log_file)
                    completed = m + 1

            elif test_type == "Storage I/O Stress (1GB)":
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Writing 1GB File ---", serial, run_log_file)
                    out = self.run_adb(["shell", "dd", "if=/dev/zero", "of=/data/local/tmp/test_1gb.tmp", "bs=1M", "count=1000"], serial=serial)
                    self.ui_log(f"DD Output: {out}", serial, run_log_file)
                    time.sleep(1)
                    self.ui_log(f"--- Cycle {i}/{target_val} : Deleting 1GB File ---", serial, run_log_file)
                    self.run_adb(["shell", "rm", "-f", "/data/local/tmp/test_1gb.tmp"], serial=serial)
                    time.sleep(1)
                    completed = i

            elif test_type == "Airplane Mode Toggle":
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Airplane Mode ON ---", serial, run_log_file)
                    self.run_adb(["shell", "settings", "put", "global", "airplane_mode_on", "1"], serial=serial)
                    self.run_adb(["shell", "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true"], serial=serial)
                    time.sleep(4)
                    self.ui_log(f"--- Cycle {i}/{target_val} : Airplane Mode OFF ---", serial, run_log_file)
                    self.run_adb(["shell", "settings", "put", "global", "airplane_mode_on", "0"], serial=serial)
                    self.run_adb(["shell", "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "false"], serial=serial)
                    time.sleep(4)
                    completed = i

            status = "PASS"

        except Exception as e:
            status = "FAIL"
            err_msg = str(e)
            self.ui_log(f"❌ Exception: {err_msg}", serial, run_log_file)
            self.root.after(0, lambda msg=f"Device [{serial}]: {err_msg}": messagebox.showerror("Device Error", msg))
            
        finally:
            if not self.device_testing_state.get(serial, False) and status != "FAIL":
                status = "STOPPED"
                
            if serial in self.logcat_procs:
                self.logcat_procs[serial].terminate()

            if test_type == "Background Download Stress (curl/wget)":
                self.ui_log("🧹 Force cleaning downloaded files before exit...", serial, run_log_file)
                self.run_adb(["shell", "rm", "-f", "/data/local/tmp/dl_stress.tmp"], serial=serial, capture=False)
            elif test_type == "Browser Download Stress (Intent)":
                self.ui_log("🧹 Force cleaning browser downloaded files before exit...", serial, run_log_file)
                if dl_file:
                    base_name = os.path.splitext(dl_file)[0]
                    self.run_adb(["shell", "rm", "-f", f"/sdcard/Download/{base_name}*"], serial=serial, capture=False)

            try:
                if orig_stay_on and orig_stay_on != "null":
                    self.run_adb(["shell", "settings", "put", "global", "stay_on_while_plugged_in", orig_stay_on], serial=serial, capture=False)
                else:
                    self.run_adb(["shell", "settings", "put", "global", "stay_on_while_plugged_in", "0"], serial=serial, capture=False)
            except Exception: pass

            for p in self.cpu_procs.get(serial, []):
                try: p.terminate()
                except: pass
            self.run_adb(["shell", "killall", "cat"], serial=serial, capture=False)
            self.run_adb(["shell", "killall", "md5sum"], serial=serial, capture=False)
            self.run_adb(["shell", "dumpsys", "battery", "reset"], serial=serial, capture=False)
            self.run_adb(["shell", "killall", "tinycap"], serial=serial, capture=False)

            if device_ready:
                self.ui_log("⏳ Fetching Bugreport...", serial, run_log_file)
                bugreport_file = os.path.join(LOG_DIR, f"{log_prefix}_{status}_{timestamp}_bugreport.zip")
                self.run_adb(["bugreport", bugreport_file], serial=serial, capture=False)
                self.ui_log(f"✅ Bugreport saved: {bugreport_file}", serial, run_log_file)

            self.ui_log("==========================================", serial, run_log_file)
            self.ui_log("             TEST SUMMARY                 ", serial, run_log_file)
            self.ui_log(f"RESULT    : {status}", serial, run_log_file)
            self.ui_log(f"COMPLETED : {completed}/{target_val}", serial, run_log_file)
            self.ui_log("==========================================", serial, run_log_file)

            final_log_file = os.path.join(LOG_DIR, f"{log_prefix}_{status}_{timestamp}.txt")
            if os.path.exists(run_log_file):
                os.rename(run_log_file, final_log_file)

            self.device_testing_state[serial] = False
            self.devices_status[serial] = "Idle"
            self.root.after(0, self.update_listbox_display)

    def stop_test(self):
        selections = self.device_listbox.curselection()
        if not selections or "No devices" in self.device_listbox.get(selections[0]):
            messagebox.showinfo("Info", "Please select a device to stop.")
            return

        target_serials = [self._get_serial_from_listbox_text(self.device_listbox.get(i)) for i in selections]
        
        stopped_count = 0
        for serial in target_serials:
            if self.device_testing_state.get(serial, False):
                self.ui_log(f"🛑 Stopping test on device [{serial}]...")
                self.device_testing_state[serial] = False 
                
                if serial in self.monkey_procs:
                    try: self.monkey_procs[serial].terminate()
                    except: pass
                if serial in self.dl_procs:
                    try: self.dl_procs[serial].terminate()
                    except: pass
                    
                threading.Thread(target=lambda s=serial: self.run_adb(["shell", "killall", "com.android.commands.monkey"], serial=s, capture=False), daemon=True).start()
                threading.Thread(target=lambda s=serial: self.run_adb(["shell", "killall", "tinycap"], serial=s, capture=False), daemon=True).start()
                threading.Thread(target=lambda s=serial: self.run_adb(["shell", "killall", "curl"], serial=s, capture=False), daemon=True).start()
                threading.Thread(target=lambda s=serial: self.run_adb(["shell", "killall", "wget"], serial=s, capture=False), daemon=True).start()
                
                threading.Thread(target=lambda s=serial: self.run_adb(["shell", "am", "force-stop", "com.android.chrome"], serial=s, capture=False), daemon=True).start()
                threading.Thread(target=lambda s=serial: self.run_adb(["shell", "am", "force-stop", "com.android.browser"], serial=s, capture=False), daemon=True).start()
                threading.Thread(target=lambda s=serial: self.run_adb(["shell", "am", "force-stop", "org.mozilla.firefox"], serial=s, capture=False), daemon=True).start()
                
                stopped_count += 1
                
        if stopped_count > 0:
            self.ui_log(f"✅ Interrupt signals sent to {stopped_count} device(s).")
        else:
            self.ui_log("⚠️ Selected devices are currently idle. Nothing to stop.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ADBStressGUI(root)
    root.mainloop()