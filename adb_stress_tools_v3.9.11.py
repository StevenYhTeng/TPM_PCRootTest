import os
import sys
import time
import socket
import ctypes
import datetime
import threading
import subprocess
import urllib.request
import concurrent.futures
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

# ==========================================
# Windows API Constants for preventing sleep
# ==========================================
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001

def prevent_system_sleep():
    """Tells Windows to prevent the system from entering sleep mode."""
    if os.name == 'nt':
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
        except Exception:
            pass

def allow_system_sleep():
    """Reverts the execution state, allowing Windows to sleep normally."""
    if os.name == 'nt':
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        except Exception:
            pass

# ==========================================
# Helper: Completely hide Windows CMD popups
# ==========================================
def get_cflags():
    if os.name == 'nt':
        return {'creationflags': subprocess.CREATE_NO_WINDOW}
    return {}

# ==========================================
# Basic Configuration
# ==========================================
LOG_DIR = "PC_Test_Logs"
os.makedirs(LOG_DIR, exist_ok=True)

class ADBStressGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Android ADB Stress Test Console (TPM/APM Edition) v3.9.11")
        self.root.geometry("1100x980")
        
        try:
            self.root.iconbitmap("app_icon.ico")
        except Exception:
            pass
            
        prevent_system_sleep()
        self.check_gdpr_consent()
        
        self.device_testing_state = {} 
        self.devices_status = {}       
        self.logcat_procs = {}
        self.monkey_procs = {}
        self.cpu_procs = {}
        self.dl_procs = {} 

        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def check_gdpr_consent(self):
        msg = (
            "GDPR & Privacy Data Notice:\n\n"
            "This tool extracts System Logs (Logcat) and Bugreports from connected Android devices.\n"
            "Please be aware that Android logs may contain Personally Identifiable Information (PII) "
            "such as email accounts, location data, Wi-Fi SSIDs, and device identifiers (IMEI/MAC).\n\n"
            "All extracted data is stored STRICTLY LOCALLY in the 'PC_Test_Logs' directory on this machine "
            "and is NEVER transmitted over the internet by this software.\n\n"
            "By clicking 'Yes', you confirm that you are authorized to process this data for testing purposes, "
            "and you agree to comply with GDPR and local data protection laws regarding the handling of these files.\n\n"
            "Do you agree to proceed?"
        )
        consent = messagebox.askyesno("Privacy Consent & GDPR Compliance", msg)
        if not consent:
            allow_system_sleep()
            self.root.destroy()
            sys.exit(0)

    def get_all_local_subnets(self):
        subnets = set()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            parts = local_ip.split('.')
            subnets.add(f"{parts[0]}.{parts[1]}.{parts[2]}.")
        except Exception:
            pass
            
        try:
            hostname = socket.gethostname()
            _, _, ips = socket.gethostbyname_ex(hostname)
            for ip in ips:
                if not ip.startswith("127.") and not ip.startswith("169.254."):
                    parts = ip.split('.')
                    subnets.add(f"{parts[0]}.{parts[1]}.{parts[2]}.")
        except Exception:
            pass
            
        if not subnets:
            return "192.168.1."
            
        return ", ".join(list(subnets))

    def setup_ui(self):
        left_container = tk.Frame(self.root, width=420, padx=10, pady=10)
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
        
        local_prefixes = self.get_all_local_subnets()
        
        tk.Label(scan_frame, text="Subnet:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.entry_ip_prefix = tk.Entry(scan_frame, font=("Arial", 9), width=20)
        self.entry_ip_prefix.insert(0, local_prefixes)
        self.entry_ip_prefix.pack(side=tk.LEFT, padx=(0, 2))
        
        self.entry_ip_start = tk.Entry(scan_frame, font=("Arial", 9), width=3)
        self.entry_ip_start.insert(0, "1")
        self.entry_ip_start.pack(side=tk.LEFT)
        
        tk.Label(scan_frame, text="-", font=("Arial", 9)).pack(side=tk.LEFT)
        
        self.entry_ip_end = tk.Entry(scan_frame, font=("Arial", 9), width=3)
        self.entry_ip_end.insert(0, "254")
        self.entry_ip_end.pack(side=tk.LEFT, padx=(0, 2))

        self.btn_scan = tk.Button(scan_frame, text="📡 Scan", font=("Arial", 9, "bold"), bg="#FF9800", fg="white", command=self.auto_connect_subnet)
        self.btn_scan.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

        manual_conn_frame = tk.Frame(dev_frame)
        manual_conn_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(manual_conn_frame, text="Manual IP:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.entry_manual_ip = tk.Entry(manual_conn_frame, font=("Arial", 9), width=16)
        self.entry_manual_ip.pack(side=tk.LEFT, padx=(0, 2))
        
        self.btn_manual_conn = tk.Button(manual_conn_frame, text="🔗 Connect IP", font=("Arial", 9, "bold"), bg="#03A9F4", fg="white", command=self.manual_connect)
        self.btn_manual_conn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))

        self.btn_init_usb = tk.Button(manual_conn_frame, text="🔌 Init USB", font=("Arial", 9, "bold"), bg="#9C27B0", fg="white", command=self.init_usb_tcpip)
        self.btn_init_usb.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

        self.device_listbox = tk.Listbox(dev_frame, selectmode=tk.MULTIPLE, height=6, font=("Consolas", 10), exportselection=False)
        self.device_listbox.pack(fill=tk.X, pady=(0, 5))
        
        self.btn_refresh_dev = tk.Button(dev_frame, text="🔄 Refresh Devices", command=self.refresh_devices)
        self.btn_refresh_dev.pack(fill=tk.X)

        tk.Label(control_frame, text="⚙️ Configure Next Test", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        self.test_type_var = tk.StringVar(value="Reboot & Shutdown Stress")
        test_options = [
            "Reboot & Shutdown Stress",
            "Fingerprint HAL & Screen Wake Stress",
            "MDM Framework Stress (Work Profile)",
            "Background Download Stress (curl/wget)", 
            "Browser Download Stress (Intent)",       
            "Storage/Fake OOM Fill (%)", 
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
        self.combo_test.pack(fill=tk.X, pady=(0, 10))
        self.combo_test.bind("<<ComboboxSelected>>", self.on_test_type_changed)

        tk.Label(control_frame, text="🎯 Target (Cycles / Mins)", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.entry_target = tk.Entry(control_frame, font=("Arial", 11))
        self.entry_target.insert(0, "60")
        self.entry_target.pack(fill=tk.X, pady=(0, 10))

        # --- Dynamic Sub-Frames ---
        self.reboot_frame = tk.LabelFrame(control_frame, text="Reboot & Shutdown Settings", padx=10, pady=5)
        tk.Label(self.reboot_frame, text="⏱️ Wait after boot (sec):", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_reboot_up = tk.Entry(self.reboot_frame, font=("Arial", 10))
        self.entry_reboot_up.insert(0, "60")
        self.entry_reboot_up.pack(fill=tk.X)
        
        self.do_shutdown_var = tk.BooleanVar(value=False)
        self.chk_do_shutdown = tk.Checkbutton(self.reboot_frame, text="🛑 Include Shutdown Phase", variable=self.do_shutdown_var, fg="#F44336", command=self.verify_shutdown_check)
        self.chk_do_shutdown.pack(anchor=tk.W)

        tk.Label(self.reboot_frame, text="⏳ Wait after shutdown (sec):", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_reboot_down = tk.Entry(self.reboot_frame, font=("Arial", 10))
        self.entry_reboot_down.insert(0, "30")
        self.entry_reboot_down.pack(fill=tk.X)

        self.mdm_frame = tk.LabelFrame(control_frame, text="MDM Test Settings & Provisioning", padx=10, pady=10)
        self.install_mdm_var = tk.BooleanVar(value=True)
        self.chk_install_mdm = tk.Checkbutton(self.mdm_frame, text="📦 Auto-Install MDM APK (-g)", variable=self.install_mdm_var)
        self.chk_install_mdm.pack(anchor=tk.W)
        
        mdm_path_frame = tk.Frame(self.mdm_frame)
        mdm_path_frame.pack(fill=tk.X, pady=(2, 5))
        self.entry_mdm_apk = tk.Entry(mdm_path_frame, font=("Arial", 10))
        self.entry_mdm_apk.insert(0, "mdm_test.apk")
        self.entry_mdm_apk.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.btn_browse_mdm = tk.Button(mdm_path_frame, text="Browse", command=self.browse_mdm_apk)
        self.btn_browse_mdm.pack(side=tk.RIGHT)

        self.set_owner_var = tk.BooleanVar(value=True)
        self.chk_set_owner = tk.Checkbutton(self.mdm_frame, text="👑 Set Device Owner & Grant Permissions", variable=self.set_owner_var)
        self.chk_set_owner.pack(anchor=tk.W, pady=(5,0))

        tk.Label(self.mdm_frame, text="Admin Component (Pkg/.Receiver):", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_mdm_comp = tk.Entry(self.mdm_frame, font=("Arial", 10))
        self.entry_mdm_comp.insert(0, "com.mdm.client/.MyDeviceAdminReceiver")
        self.entry_mdm_comp.pack(fill=tk.X, pady=(0, 5))

        self.oom_frame = tk.LabelFrame(control_frame, text="OOM Storage Fill Settings", padx=10, pady=10)
        tk.Label(self.oom_frame, text="📈 Target Fill Percentage (%):", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_oom_pct = tk.Entry(self.oom_frame, font=("Arial", 10))
        self.entry_oom_pct.insert(0, "95")
        self.entry_oom_pct.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(self.oom_frame, text="⏳ Hold Duration (Mins):", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_oom_mins = tk.Entry(self.oom_frame, font=("Arial", 10))
        self.entry_oom_mins.insert(0, "5")
        self.entry_oom_mins.pack(fill=tk.X, pady=(0, 5))

        self.dl_frame = tk.LabelFrame(control_frame, text="Download Stress Settings", padx=10, pady=10)
        self.dl_presets = {
            "Google CTS Media 1.5 [Global] (~240MB)": {"url": "https://dl.google.com/dl/android/cts/android-cts-media-1.5.zip", "file": "android-cts-media-1.5.zip", "timeout": "300"},
            "Google Platform Tools [Global] (~15MB)": {"url": "https://dl.google.com/android/repository/platform-tools-latest-windows.zip", "file": "platform-tools-latest-windows.zip", "timeout": "120"},
            "Tencent WeChat Setup [China] (~210MB)": {"url": "https://dldir1.qq.com/weixin/Windows/WeChatSetup.exe", "file": "WeChatSetup.exe", "timeout": "300"},
            "Tsinghua Ubuntu ISO [China] (~2.6GB)": {"url": "https://mirrors.tuna.tsinghua.edu.cn/ubuntu-releases/24.04/ubuntu-24.04.1-live-server-amd64.iso", "file": "ubuntu-24.04.1-live-server-amd64.iso", "timeout": "1800"} 
        }
        tk.Label(self.dl_frame, text="📂 Quick Select Test File:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.combo_dl_preset = ttk.Combobox(self.dl_frame, values=list(self.dl_presets.keys()), state="readonly", font=("Arial", 9))
        self.combo_dl_preset.set("Google CTS Media 1.5 [Global] (~240MB)")
        self.combo_dl_preset.pack(fill=tk.X, pady=(0, 5))
        self.combo_dl_preset.bind("<<ComboboxSelected>>", self.on_dl_preset_changed)
        
        tk.Label(self.dl_frame, text="🔗 Download URL:", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_dl_url = tk.Entry(self.dl_frame, font=("Arial", 10))
        self.entry_dl_url.insert(0, self.dl_presets["Google CTS Media 1.5 [Global] (~240MB)"]["url"]) 
        self.entry_dl_url.pack(fill=tk.X)
        
        tk.Label(self.dl_frame, text="📄 Expected Filename:", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_dl_file = tk.Entry(self.dl_frame, font=("Arial", 10))
        self.entry_dl_file.insert(0, self.dl_presets["Google CTS Media 1.5 [Global] (~240MB)"]["file"]) 
        self.entry_dl_file.pack(fill=tk.X)
        
        tk.Label(self.dl_frame, text="⏱️ Timeout (sec):", font=("Arial", 9)).pack(anchor=tk.W)
        self.entry_dl_timeout = tk.Entry(self.dl_frame, font=("Arial", 10))
        self.entry_dl_timeout.insert(0, "300") 
        self.entry_dl_timeout.pack(fill=tk.X)
        
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
        self.entry_throttle.pack(fill=tk.X, pady=(0, 5))

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

        right_frame = tk.Frame(self.root, padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tpm_dashboard = tk.Frame(right_frame, bg="#1E1E1E", bd=2, relief=tk.RAISED)
        self.tpm_dashboard.pack(fill=tk.X, pady=(0, 10))
        
        self.lbl_tpm_title = tk.Label(self.tpm_dashboard, text="⚡ TPM / APM Executive Dashboard", font=("Arial", 16, "bold"), fg="#FFD700", bg="#1E1E1E", pady=10)
        self.lbl_tpm_title.pack(fill=tk.X)
        self.lbl_tpm_title.bind("<Double-Button-1>", self.trigger_easter_egg)
        
        stats_frame = tk.Frame(self.tpm_dashboard, bg="#1E1E1E")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.lbl_stat_devs = tk.Label(stats_frame, text="Connected Devices: 0", font=("Consolas", 12, "bold"), fg="#00FF00", bg="#1E1E1E", width=25)
        self.lbl_stat_devs.pack(side=tk.LEFT, expand=True)
        
        self.lbl_stat_tests = tk.Label(stats_frame, text="Active Tests: 0", font=("Consolas", 12, "bold"), fg="#00FFFF", bg="#1E1E1E", width=25)
        self.lbl_stat_tests.pack(side=tk.RIGHT, expand=True)

        log_header_frame = tk.Frame(right_frame)
        log_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(log_header_frame, text="📝 Real-time Multi-Device Log", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        tk.Button(log_header_frame, text="📋 Copy Logs", font=("Arial", 9, "bold"), bg="#2196F3", fg="white", command=self.copy_logs).pack(side=tk.RIGHT)

        self.text_log = scrolledtext.ScrolledText(right_frame, font=("Consolas", 10), bg="#1E1E1E", fg="#00FF00")
        self.text_log.pack(fill=tk.BOTH, expand=True)

        self.on_test_type_changed(None)
        
        self.ui_log(f"System ready. Automatically detecting local subnets and initializing scan...")
        self.root.after(500, self.auto_connect_subnet)
        
        self.update_dashboard_stats()

    def browse_mdm_apk(self):
        path = filedialog.askopenfilename(title="Select MDM APK", filetypes=[("APK Files", "*.apk"), ("All Files", "*.*")])
        if path:
            self.entry_mdm_apk.delete(0, tk.END)
            self.entry_mdm_apk.insert(0, path)

    def verify_shutdown_check(self):
        if self.do_shutdown_var.get():
            ans = messagebox.askyesno(
                "CRITICAL WARNING",
                "You are about to enable the 'Shutdown' phase.\n\n"
                "Does your device have a hardware auto-wake mechanism?\n\n"
                "If NO, the device will STAY POWERED OFF permanently.\n\n"
                "Do you want to proceed?"
            )
            if not ans:
                self.do_shutdown_var.set(False)

    def copy_logs(self):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.text_log.get("1.0", tk.END))
            messagebox.showinfo("Copied", "✅ All system logs successfully copied to clipboard!")
        except:
            pass

    def get_remote_file_size_pc(self, url):
        try:
            req = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(req, timeout=5) as response:
                return int(response.headers.get('Content-Length', 0))
        except:
            return 0

    def manual_connect(self):
        ip = self.entry_manual_ip.get().strip()
        if not ip:
            messagebox.showerror("Error", "Please enter an IP address to connect manually!")
            return
        self.ui_log(f"🔗 Attempting manual connection to {ip}:5555...")
        threading.Thread(target=self._bg_manual_connect, args=(ip,), daemon=True).start()

    def _bg_manual_connect(self, ip):
        cmd = ["adb", "connect", f"{ip}:5555"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5, **get_cflags())
            self.ui_log(f"Manual Connect Result: {res.stdout.strip()}")
        except Exception as e:
            self.ui_log(f"❌ Failed to connect: {e}")
        self.root.after(500, self.refresh_devices)

    def update_dashboard_stats(self):
        try:
            dev_count = len(self.devices_status)
            active_count = sum(1 for state in self.device_testing_state.values() if state)
            
            self.lbl_stat_devs.config(text=f"Connected Devices: {dev_count}")
            self.lbl_stat_tests.config(text=f"Active Tests: {active_count}")
        except:
            pass
        self.root.after(1000, self.update_dashboard_stats)

    def trigger_easter_egg(self, event):
        self.lbl_tpm_title.config(text="🚀 OVERDRIVE MODE ACTIVATED 🚀", fg="#FF00FF")
        self.text_log.config(fg="#FF00FF") 
        self.ui_log("==================================================")
        self.ui_log("Program Description")
        self.ui_log("This program is primarily designed for testing Android Devices. It was independently developed by the TPM team and is not an official HP Release. Please be mindful of its nature and intended usage during testing.")
        self.ui_log("")
        self.ui_log("Blessing")
        self.ui_log("May God protect us and our project, granting us peace and wisdom.")
        self.ui_log("==================================================")
        
        msg = ("Program Description\n"
               "This program is primarily designed for testing Android Devices. It was independently developed by the TPM team and is not an official HP Release. Please be mindful of its nature and intended usage during testing.\n\n"
               "Blessing\n"
               "May God protect us and our project, granting us peace and wisdom.")
        messagebox.showinfo("🎉 Easter Egg", msg)

    def init_usb_tcpip(self):
        self.ui_log("🔌 Searching for USB connected devices to initialize TCP/IP...")
        try:
            res = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5, **get_cflags())
            
            lines = res.stdout.splitlines()
            usb_devices = []
            
            for line in lines[1:]:
                if "device" in line and "offline" not in line and "unauthorized" not in line:
                    serial = line.split()[0]
                    if ":" not in serial and "." not in serial:
                        usb_devices.append(serial)
                        
            if not usb_devices:
                self.ui_log("⚠️ No USB devices found! Please connect device via USB first.")
                messagebox.showwarning("Warning", "No USB connected device detected!\n\nPlease connect the device to the PC using a physical USB cable, then click this button again.")
                return
                
            for serial in usb_devices:
                self.ui_log(f"   >>> Sending 'adb tcpip 5555' to device [{serial}]...")
                subprocess.run(["adb", "-s", serial, "tcpip", "5555"], capture_output=True, timeout=5, **get_cflags())
            
            self.ui_log("✅ Initialization complete! You can unplug the USB cable now and click 'Scan'.")
            messagebox.showinfo("Success", "Port 5555 has been forced open!\n\nYou can now unplug the USB cable and click the 'Scan' button.")
            
        except Exception as e:
            self.ui_log(f"❌ Failed to init USB devices: {e}")

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

    def _get_storage_info(self, serial):
        out = self.run_adb(["shell", "stat", "-f", "-c", '\"%b %a %S\"', "/data"], serial=serial).strip().replace('"', '')
        try:
            b, a, s = map(int, out.split())
            total_mb = (b * s) / (1024 * 1024)
            free_mb = (a * s) / (1024 * 1024)
            return total_mb, free_mb
        except:
            pass
            
        out = self.run_adb(["shell", "df", "/data"], serial=serial).strip()
        try:
            lines = out.splitlines()
            if len(lines) > 1:
                parts = lines[1].split()
                total_mb = int(parts[1]) / 1024
                free_mb = int(parts[3]) / 1024
                return total_mb, free_mb
        except:
            pass
        return 0, 0

    def on_dl_preset_changed(self, event):
        selected = self.combo_dl_preset.get()
        if selected in self.dl_presets:
            self.entry_dl_url.delete(0, tk.END)
            self.entry_dl_url.insert(0, self.dl_presets[selected]["url"])
            
            self.entry_dl_file.delete(0, tk.END)
            self.entry_dl_file.insert(0, self.dl_presets[selected]["file"])
            
            if "timeout" in self.dl_presets[selected]:
                self.entry_dl_timeout.delete(0, tk.END)
                self.entry_dl_timeout.insert(0, self.dl_presets[selected]["timeout"])

    def auto_connect_subnet(self):
        prefixes_raw = self.entry_ip_prefix.get().strip()
        prefixes = [p.strip() for p in prefixes_raw.split(',') if p.strip()]
        
        if not prefixes:
            messagebox.showerror("Error", "Please enter at least one IP prefix!")
            return
            
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
        threading.Thread(target=self._bg_auto_connect, args=(prefixes, start_ip, end_ip), daemon=True).start()

    def _bg_auto_connect(self, prefixes, start, end):
        self.ui_log(f"📡 Fast scanning subnets: {', '.join(prefixes)} (Range: {start}~{end})...")
        try:
            subprocess.run(["adb", "start-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5, **get_cflags())
        except:
            pass

        def connect_ip(ip):
            try:
                subprocess.run(["adb", "connect", f"{ip}:5555"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2, **get_cflags())
            except Exception:
                pass

        ips_to_scan = []
        for prefix in prefixes:
            for i in range(start, end + 1):
                ips_to_scan.append(f"{prefix}{i}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
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
        allow_system_sleep()
        self.root.destroy()

    def _cleanup_device_force(self, serial):
        self.run_adb(["shell", "killall", "com.android.commands.monkey"], serial=serial, capture=False)
        self.run_adb(["shell", "killall", "tinycap"], serial=serial, capture=False)
        self.run_adb(["shell", "killall", "curl"], serial=serial, capture=False)
        self.run_adb(["shell", "killall", "wget"], serial=serial, capture=False)
        self.run_adb(["shell", "killall", "dd"], serial=serial, capture=False)
        self.run_adb(["shell", "rm", "-f", "/data/local/tmp/oom_fill*"], serial=serial, capture=False) 
        
        dl_file = self.entry_dl_file.get().strip()
        if dl_file:
            base_name = os.path.splitext(dl_file)[0]
            self.run_adb(["shell", "rm", "-f", f"/sdcard/Download/{base_name}*"], serial=serial, capture=False)
            
        try:
            out = self.run_adb(["shell", "pm", "list", "users"], serial=serial, capture=True)
            for line in out.splitlines():
                if "MDM_Stress" in line:
                    uid = line.split("{")[1].split(":")[0]
                    self.run_adb(["shell", "pm", "remove-user", uid], serial=serial, capture=False)
        except: pass

    def refresh_devices(self, auto_recover=True):
        self.device_listbox.delete(0, tk.END)
        self.btn_refresh_dev.config(state=tk.DISABLED)
        
        try:
            res = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=10, **get_cflags())
                
            if res.returncode != 0:
                if auto_recover: raise Exception(f"ADB process failed. Return code: {res.returncode}")
                
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
                
        except Exception as e:
            if auto_recover:
                self.ui_log(f"⚠️ ADB Server unresponsive. Attempting Auto-Recovery...")
                threading.Thread(target=self._bg_recover_adb, daemon=True).start()
            else:
                self.btn_refresh_dev.config(state=tk.NORMAL)

    def _bg_recover_adb(self):
        try:
            subprocess.run(["adb", "kill-server"], timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **get_cflags())
            time.sleep(1)
            subprocess.run(["adb", "start-server"], timeout=10, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **get_cflags())
        except:
            pass
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
        needs_app = "App" in test_type or "Monkey" in test_type or "OOM" in test_type
        needs_screen = "Screen Sleep/Wake" in test_type or "MDM" in test_type or "Fingerprint" in test_type
        needs_dl = "Download" in test_type
        needs_oom = "OOM" in test_type
        needs_reboot = "Reboot" in test_type
        needs_mdm = "MDM" in test_type
        
        self.dl_frame.pack_forget()
        self.app_frame.pack_forget()
        self.screen_frame.pack_forget()
        self.oom_frame.pack_forget()
        self.reboot_frame.pack_forget()
        self.mdm_frame.pack_forget()

        if needs_reboot:
            self.reboot_frame.pack(fill=tk.X, pady=(0, 10))

        if needs_mdm:
            self.mdm_frame.pack(fill=tk.X, pady=(0, 10))

        if needs_dl:
            self.dl_frame.pack(fill=tk.X, pady=(0, 10))
            if "Browser" in test_type:
                self.entry_dl_file.config(state=tk.NORMAL)
            else:
                self.entry_dl_file.config(state=tk.DISABLED)
                
        if needs_oom:
            self.oom_frame.pack(fill=tk.X, pady=(0, 10))

        if needs_app:
            self.app_frame.pack(fill=tk.X, pady=(0, 10))
            if "System-wide" not in test_type and "OOM" not in test_type:
                self.entry_pkg.config(state=tk.NORMAL)
                self.btn_fetch_apps.config(state=tk.NORMAL)
            elif "OOM" in test_type:
                self.entry_pkg.config(state=tk.NORMAL)
                self.btn_fetch_apps.config(state=tk.NORMAL)
            else:
                self.entry_pkg.config(state=tk.DISABLED)
                self.btn_fetch_apps.config(state=tk.DISABLED)
                
            if "Monkey" in test_type or "OOM" in test_type:
                self.entry_throttle.config(state=tk.NORMAL)
                self.chk_ignore_crash.config(state=tk.NORMAL)
            else:
                self.entry_throttle.config(state=tk.DISABLED)
                self.chk_ignore_crash.config(state=tk.DISABLED)

        if needs_screen:
            self.screen_frame.pack(fill=tk.X, pady=(0, 10))

    def open_logs(self):
        path = os.path.abspath(LOG_DIR)
        try: os.startfile(path) if os.name == 'nt' else subprocess.Popen(['xdg-open', path])
        except Exception as e: self.ui_log(f"Failed to open folder: {e}")

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

    def run_adb(self, cmd_list, serial=None, capture=True, timeout=15):
        try:
            cmd = ["adb"]
            if serial: cmd.extend(["-s", serial])
            cmd.extend(cmd_list)
            
            res = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE if capture else subprocess.DEVNULL, 
                stderr=subprocess.STDOUT if capture else subprocess.DEVNULL, 
                text=True, 
                timeout=timeout, 
                **get_cflags()
            )
            return res.stdout.strip() if capture and res.stdout else ""
        except subprocess.TimeoutExpired:
            return "ERROR: TIMEOUT_EXPIRED"
        except Exception as e:
            return str(e)

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
        selections = self.device_listbox.curselection()
        
        if not target_str.isdigit() or int(target_str) <= 0:
            messagebox.showerror("Error", "Please enter a valid number greater than 0!")
            return
            
        if not selections or "No devices" in self.device_listbox.get(selections[0]):
            messagebox.showerror("Error", "Please select at least one device from the list!")
            return
            
        target_serials = [self._get_serial_from_listbox_text(self.device_listbox.get(i)) for i in selections]

        test_type = self.test_type_var.get()
        target_val = int(target_str)
        
        kwargs = {
            "pkgs_str": self.entry_pkg.get().strip(),
            "throttle_val": self.entry_throttle.get().strip() or "300",
            "ignore_crash_val": self.ignore_crash_var.get(),
            "install_mdm": self.install_mdm_var.get(),
            "set_owner": self.set_owner_var.get(),
            "mdm_apk": self.entry_mdm_apk.get().strip(),
            "mdm_comp": self.entry_mdm_comp.get().strip(),
            "do_shutdown": self.do_shutdown_var.get()
        }
        
        if test_type == "MDM Framework Stress (Work Profile)":
            if kwargs["install_mdm"] and not os.path.exists(kwargs["mdm_apk"]):
                messagebox.showerror("Error", f"MDM APK file not found at: {kwargs['mdm_apk']}\nPlease provide a valid path.")
                return
            
            # MDM Pre-Flight Check (Factory Reset Reminder)
            check_msg = (
                "⚠️ MDM TEST PRE-CHECK ⚠️\n\n"
                "Setting a Device Owner requires a CLEAN device.\n\n"
                "Please confirm for ALL selected devices:\n"
                "1. Have you performed a FACTORY RESET?\n"
                "2. Have you skipped the GOOGLE ACCOUNT login?\n"
                "3. Is USB Debugging enabled?\n\n"
                "If there is any account logged in, the test WILL FAIL.\n\n"
                "Proceed now?"
            )
            if not messagebox.askyesno("MDM Provisioning Check", check_msg):
                return
        
        try: oom_pct = float(self.entry_oom_pct.get().strip())
        except: oom_pct = 95.0
        try: oom_mins = float(self.entry_oom_mins.get().strip())
        except: oom_mins = 5.0
        
        try: reboot_up_time = int(self.entry_reboot_up.get().strip())
        except: reboot_up_time = 60
        try: reboot_down_time = int(self.entry_reboot_down.get().strip())
        except: reboot_down_time = 30
        
        do_shutdown = self.do_shutdown_var.get()
        
        try: dl_timeout = int(self.entry_dl_timeout.get().strip())
        except: dl_timeout = 300
        
        try: sleep_sec = int(self.entry_sleep_time.get().strip())
        except: sleep_sec = 10 
        try: wake_sec = int(self.entry_wake_time.get().strip())
        except: wake_sec = 10 
        
        type_map = {
            "Fingerprint HAL & Screen Wake Stress": "Fingerprint_Stress",
            "Reboot & Shutdown Stress": "Reboot_Stress",
            "MDM Framework Stress (Work Profile)": "MDM_Stress",
            "Background Download Stress (curl/wget)": "Bg_Download",
            "Browser Download Stress (Intent)": "Browser_Download",
            "Storage/Fake OOM Fill (%)": "OOM_Fill",
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
                args=(test_type, target_val, timestamp, base_test_name, unit, serial, kwargs, sleep_sec, wake_sec, self.entry_dl_url.get().strip(), self.delete_dl_var.get(), self.entry_dl_file.get().strip(), dl_timeout, oom_pct, oom_mins, reboot_up_time, reboot_down_time, do_shutdown), 
                daemon=True
            ).start()
            dispatched_count += 1

        if dispatched_count > 0:
            self.update_listbox_display()
            self.ui_log(f"🚀 Successfully dispatched '{test_type}' to {dispatched_count} device(s).")

    def _run_test_thread(self, test_type, target_val, timestamp, base_test_name, unit, serial, kw, sleep_sec, wake_sec, dl_url, dl_delete_after, dl_file, dl_timeout, oom_pct, oom_mins, reboot_up, reboot_down, do_shutdown):
        status = "FAIL"
        err_msg = ""
        completed = 0
        device_ready = False
        orig_stay_on = "0" 
        
        safe_serial = serial.replace(":", "_").replace(".", "_")
        log_prefix = f"Dev[{safe_serial}]_{base_test_name}_{target_val}{unit}_{timestamp}"
        run_log_file = os.path.join(LOG_DIR, f"{log_prefix}_running.txt")

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
            
            logcat_file = os.path.join(LOG_DIR, f"{log_prefix}_logcat.txt")
            self.run_adb(["logcat", "-c"], serial=serial, capture=False) 
            
            cmd_logcat = ["adb", "-s", serial, "logcat", "-v", "threadtime"]
            log_f = open(logcat_file, "w", encoding="utf-8")
            proc = subprocess.Popen(cmd_logcat, stdout=log_f, stderr=subprocess.DEVNULL, **get_cflags())
            self.logcat_procs[serial] = (proc, log_f)

            # === Start Actual Test Logic ===
            
            if test_type == "Fingerprint HAL & Screen Wake Stress":
                self.ui_log(f"💡 [Interactive Test] You can touch the fingerprint sensor anytime during the test to check responsiveness.", serial, run_log_file)
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Fingerprint HAL Polling & Screen Off ---", serial, run_log_file)
                    
                    fp_out = self.run_adb(["shell", "dumpsys", "fingerprint"], serial=serial)
                    if "Can't find service" in fp_out or not fp_out.strip():
                        fp_out = self.run_adb(["shell", "dumpsys", "biometric"], serial=serial)
                        
                    if "Can't find service" in fp_out or not fp_out.strip():
                        self.ui_log("⚠️ Warning: Unable to retrieve Fingerprint/Biometric service state (HAL may have crashed or sensor is absent)", serial, run_log_file)
                    else:
                        self.ui_log("✅ Fingerprint Service is ALIVE.", serial, run_log_file)
                        
                    self.run_adb(["shell", "input", "keyevent", "223"], serial=serial)
                    
                    self.ui_log(f"Sleeping for {sleep_sec}s...", serial, run_log_file)
                    for _ in range(sleep_sec):
                        if not self.device_testing_state.get(serial, False): break
                        time.sleep(1)

                    if not self.device_testing_state.get(serial, False): break
                    
                    self.ui_log(f"--- Cycle {i}/{target_val} : Wake up screen ---", serial, run_log_file)
                    self.run_adb(["shell", "input", "keyevent", "224"], serial=serial)

                    self.ui_log(f"Holding screen ON for {wake_sec}s...", serial, run_log_file)
                    for _ in range(wake_sec):
                        if not self.device_testing_state.get(serial, False): break
                        time.sleep(1)

                    completed = i

            elif test_type == "Reboot & Shutdown Stress":
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Issuing Reboot Command ---", serial, run_log_file)
                    
                    self.run_adb(["reboot"], serial=serial)
                    time.sleep(10)
                    
                    self.ui_log("⏳ Waiting for device to boot up and reconnect (Timeout 15 mins)...", serial, run_log_file)
                    wait_start = time.time()
                    device_online = False
                    
                    while time.time() - wait_start < 900:
                        if not self.device_testing_state.get(serial, False): break
                        
                        if ":" in serial:
                            try:
                                subprocess.run(["adb", "disconnect", serial], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **get_cflags())
                                subprocess.run(["adb", "connect", serial], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5, **get_cflags())
                            except:
                                pass 
                        
                        sys_boot = self.run_adb(["shell", "getprop", "sys.boot_completed"], serial=serial)
                        if "1" in sys_boot:
                            device_online = True
                            break
                        elif sys_boot.strip() == "0" or sys_boot.strip() == "":
                            pass
                            
                        time.sleep(5)
                        
                    if not self.device_testing_state.get(serial, False): break
                    
                    if not device_online:
                        check_conn = self.run_adb(["shell", "echo", "ping"], serial=serial)
                        if "ping" in check_conn:
                            raise Exception(f"Cycle {i} Error: Device is stuck in BOOTLOOP! (ADB connected but OS boot failed)")
                        else:
                            raise Exception(f"Cycle {i} Error: Device failed to boot or connect within 15 minutes.")
                        
                    self.ui_log(f"✅ Device boot completed. Holding for {reboot_up} sec...", serial, run_log_file)
                    
                    for remain in range(reboot_up, 0, -1):
                        if not self.device_testing_state.get(serial, False): break
                        if remain % 5 == 0 or remain <= 5:
                            self.ui_log(f"   ... Waiting {remain} sec", serial, run_log_file)
                        time.sleep(1)
                        
                    if not self.device_testing_state.get(serial, False): break
                    
                    if do_shutdown:
                        self.ui_log(f"--- Cycle {i}/{target_val} : Issuing Shutdown Command (reboot -p) ---", serial, run_log_file)
                        self.run_adb(["shell", "reboot", "-p"], serial=serial)
                        
                        self.ui_log(f"⏳ Device shutting down. Holding for {reboot_down} sec before next reboot...", serial, run_log_file)
                        for remain in range(reboot_down, 0, -1):
                            if not self.device_testing_state.get(serial, False): break
                            if remain % 5 == 0 or remain <= 5:
                                self.ui_log(f"   ... {remain} sec remaining until next cycle", serial, run_log_file)
                            time.sleep(1)
                    else:
                        self.ui_log(f"⏳ Skipping Shutdown phase. Waiting {reboot_down} sec interval before next Reboot...", serial, run_log_file)
                        for remain in range(reboot_down, 0, -1):
                            if not self.device_testing_state.get(serial, False): break
                            if remain % 5 == 0 or remain <= 5:
                                self.ui_log(f"   ... {remain} sec remaining until next Reboot", serial, run_log_file)
                            time.sleep(1)
                        
                    completed = i

            elif test_type == "MDM Framework Stress (Work Profile)":
                if kw["install_mdm"]:
                    self.ui_log("🛡️ Disabling Google Play Protect to bypass 'Install Anyway' prompt...", serial, run_log_file)
                    self.run_adb(["shell", "settings", "put", "global", "package_verifier_enable", "0"], serial=serial)
                    self.run_adb(["shell", "settings", "put", "global", "verifier_verify_adb_installs", "0"], serial=serial)
                    
                    self.ui_log(f"📦 Auto-Installing MDM APK (-g -d -t): {kw['mdm_apk']}...", serial, run_log_file)
                    
                    install_out = self.run_adb(["install", "-r", "-t", "-d", "-g", kw["mdm_apk"]], serial=serial, timeout=120)
                    
                    if "Success" not in install_out:
                        raise Exception(f"Failed to install MDM APK. ADB Output: {install_out}")
                    self.ui_log("✅ MDM APK Installed and Runtime Permissions auto-granted successfully.", serial, run_log_file)

                if kw["set_owner"]:
                    pkg_name = kw["mdm_comp"].split("/")[0] if "/" in kw["mdm_comp"] else "com.mdm.client"
                    
                    # 🌟 v3.9.11: APK 'testOnly' X-Ray Verifier
                    self.ui_log("🔍 [Smart Check] Verifying 'testOnly' flag in installed package...", serial, run_log_file)
                    pkg_dump = self.run_adb(["shell", "dumpsys", "package", pkg_name], serial=serial)
                    
                    # Some Android versions output TEST_ONLY, others output testOnly=true
                    if "TEST_ONLY" not in pkg_dump and "testOnly=true" not in pkg_dump.replace(" ", "") and "test_only" not in pkg_dump.lower():
                        err_msg = (f"FATAL: The installed APK is MISSING the 'android:testOnly=\"true\"' flag!\n\n"
                                   f"Android OS completely rejects setting a Device Owner if this flag is missing.\n"
                                   f"Even if RD said they added it, the compilation process (like ProGuard or Release build variant) likely stripped it out.\n\n"
                                   f"💡 SOLUTION: Please send this error to RD and ask for an APK explicitly built with the testOnly flag retained.")
                        raise Exception(err_msg)
                    
                    # 🌟 Smart Environment Pre-checks
                    self.ui_log("🔍 [Smart Check] Scanning for existing accounts...", serial, run_log_file)
                    acc_out = self.run_adb(["shell", "dumpsys", "account"], serial=serial)
                    if "Account {" in acc_out:
                        self.ui_log("❌ [FATAL] Existing accounts detected! Android STRICTLY FORBIDS setting Device Owner.", serial, run_log_file)
                        raise Exception("Accounts found. Please FACTORY RESET the device!")
                        
                    self.ui_log("🔍 [Smart Check] Scanning for lingering users/profiles...", serial, run_log_file)
                    usr_out = self.run_adb(["shell", "pm", "list", "users"], serial=serial)
                    if usr_out.count("UserInfo{") > 1:
                        self.ui_log(f"⚠️ [WARNING] Multiple users detected, this might block DPM: {usr_out.strip().replace(chr(10), ' ')}", serial, run_log_file)

                    self.ui_log(f"🔑 Granting READ_LOGS permission to {pkg_name}...", serial, run_log_file)
                    self.run_adb(["shell", "pm", "grant", pkg_name, "android.permission.READ_LOGS"], serial=serial)
                    
                    dp_check = self.run_adb(["shell", "dumpsys", "device_policy"], serial=serial)
                    if kw["mdm_comp"] in dp_check and ("Device Owner:" in dp_check or "admin=" in dp_check):
                        self.ui_log(f"✅ App '{kw['mdm_comp']}' is ALREADY the Device Owner. Skipping setting process.", serial, run_log_file)
                    else:
                        self.ui_log(f"👑 Setting Device Owner: {kw['mdm_comp']}...", serial, run_log_file)
                        dpm_out = self.run_adb(["shell", "dpm", "set-device-owner", kw["mdm_comp"]], serial=serial)
                        self.ui_log(f"DPM Output: {dpm_out}", serial, run_log_file)
                        
                        if "Success" not in dpm_out and "Active admin set" not in dpm_out and "already" not in dpm_out.lower():
                            err_msg = (f"Failed to set Device Owner.\n\n"
                                       f"⚠️ ANDROID RESTRICTION: Android STRICTLY FORBIDS setting a Device Owner if the device has ANY user accounts logged in (e.g., Google Account), or if a previous Work Profile hasn't been wiped.\n\n"
                                       f"💡 SOLUTION: Please FACTORY RESET the device, skip the Google Sign-in on setup, and try again!\n\n"
                                       f"ADB Output: {dpm_out}")
                            raise Exception(err_msg)
                    time.sleep(2)
            
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Setting up Managed Work Profile ---", serial, run_log_file)
                    
                    out = self.run_adb(["shell", "pm", "create-user", "--profileOf", "0", "--managed", "MDM_Stress"], serial=serial)
                    if "Success: created user id" not in out:
                        raise Exception(f"Cycle {i} Error: Failed to create Managed Profile. Device might not support Multi-User or DPM. Output: {out}")
                    
                    try:
                        user_id = out.split("id")[1].strip()
                    except:
                        raise Exception(f"Cycle {i} Error: Could not parse User ID from: {out}")
                        
                    self.ui_log(f"✅ Work Profile created with User ID: {user_id}. Starting user...", serial, run_log_file)
                    self.run_adb(["shell", "am", "start-user", user_id], serial=serial)
                    
                    self.ui_log(f"⏳ Holding MDM state active for {sleep_sec}s...", serial, run_log_file)
                    for _ in range(sleep_sec):
                        if not self.device_testing_state.get(serial, False): break
                        time.sleep(1)
                        
                    if not self.device_testing_state.get(serial, False): break
                        
                    self.ui_log(f"🧹 Tearing down Work Profile (User ID: {user_id})...", serial, run_log_file)
                    self.run_adb(["shell", "pm", "remove-user", user_id], serial=serial)
                    time.sleep(2) 
                    completed = i

            elif test_type == "Storage/Fake OOM Fill (%)":
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Storage OOM Fill (Target: {oom_pct}%) ---", serial, run_log_file)
                    
                    self.run_adb(["shell", "rm", "-f", "/data/local/tmp/oom_fill*"], serial=serial)
                    
                    total_mb, free_mb = self._get_storage_info(serial)
                    if total_mb <= 0:
                        raise Exception(f"Cycle {i} Error: Cannot retrieve storage info.")
                        
                    current_used_mb = total_mb - free_mb
                    target_used_mb = total_mb * (oom_pct / 100.0)
                    mb_to_fill = int(target_used_mb - current_used_mb)
                    
                    if mb_to_fill <= 0:
                        self.ui_log(f"⚠️ Storage already at {current_used_mb/total_mb*100:.1f}%. Skipping filling step.", serial, run_log_file)
                    else:
                        self.ui_log(f"⏳ Dynamic Calc: Total {total_mb:.1f}MB, Free {free_mb:.1f}MB. Filling {mb_to_fill}MB to reach {oom_pct}%...", serial, run_log_file)
                        start_time = time.time()
                        
                        chunk_size = 200
                        chunks = mb_to_fill // chunk_size
                        remainder = mb_to_fill % chunk_size
                        
                        self.ui_log(f"⏳ Generating payload in {chunk_size}MB chunks to prevent system RAM overflow...", serial, run_log_file)

                        for c in range(int(chunks)):
                            if not self.device_testing_state.get(serial, False): break
                            cmd_dd = ["adb", "-s", serial, "shell", f"dd if=/dev/zero bs=1048576 count={chunk_size} >> /data/local/tmp/oom_fill.tmp"]
                            subprocess.run(cmd_dd, capture_output=True, **get_cflags())
                            cur_mb = (c + 1) * chunk_size
                            pct = (cur_mb / mb_to_fill) * 100
                            self.ui_log(f"   ... Filling progress: {cur_mb} MB / {mb_to_fill} MB ({pct:.1f}%)", serial, run_log_file)

                        if remainder > 0 and self.device_testing_state.get(serial, False):
                            cmd_dd = ["adb", "-s", serial, "shell", f"dd if=/dev/zero bs=1048576 count={int(remainder)} >> /data/local/tmp/oom_fill.tmp"]
                            subprocess.run(cmd_dd, capture_output=True, **get_cflags())
                            self.ui_log(f"   ... Filling progress: {mb_to_fill} MB / {mb_to_fill} MB (100.0%)", serial, run_log_file)
                        
                        if not self.device_testing_state.get(serial, False): break
                        
                        elapsed = time.time() - start_time
                        self.ui_log(f"✅ Filled approx. {mb_to_fill} MB in {elapsed:.1f}s", serial, run_log_file)
                    
                    hold_seconds = int(oom_mins * 60)
                    self.ui_log(f"⏳ Holding OOM state for {oom_mins} minutes...", serial, run_log_file)
                    
                    oom_monkey_proc = None
                    if kw["pkgs_str"].strip():
                        self.ui_log(f"🚀 [OOM-App-Test] Launching Monkey on '{kw['pkgs_str']}' under extreme storage pressure!", serial, run_log_file)
                        cmd = ["adb", "-s", serial, "shell", "monkey"]
                        for p in [x.strip() for x in kw["pkgs_str"].split(",") if x.strip()]: 
                            cmd.extend(["-p", p])
                        cmd.extend(["--throttle", str(kw["throttle_val"])])
                        if kw["ignore_crash_val"]:
                            cmd.extend(["--ignore-crashes", "--ignore-timeouts", "--ignore-security-exceptions"])
                        cmd.extend(["-v", "-v", "-v", "999999999"])
                        
                        oom_monkey_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', **get_cflags())
                        self.monkey_procs[serial] = oom_monkey_proc
                        
                        def log_oom_monkey_output(p, s, log_f):
                            try:
                                for line in p.stdout:
                                    if not self.device_testing_state.get(s, False): break
                                    line_str = line.strip()
                                    if "CRASH" in line_str or "ANR" in line_str or "Exception" in line_str:
                                        self.ui_log("🔥 [OOM-Monkey-CRASH] " + line_str, s, log_f)
                                    else:
                                        with open(log_f, "a", encoding="utf-8") as f:
                                            f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{s}] [OOM-Monkey] {line_str}\n")
                            except: pass
                        
                        threading.Thread(target=log_oom_monkey_output, args=(oom_monkey_proc, serial, run_log_file), daemon=True).start()

                    for _ in range(hold_seconds):
                        if not self.device_testing_state.get(serial, False): break
                        time.sleep(1)
                        
                    if oom_monkey_proc:
                        try: oom_monkey_proc.terminate()
                        except: pass
                        self.run_adb(["shell", "killall", "com.android.commands.monkey"], serial=serial, capture=False)
                        self.ui_log(f"⏹️ [OOM-App-Test] Monkey test finished.", serial, run_log_file)
                    
                    if not self.device_testing_state.get(serial, False): break
                    
                    self.ui_log(f"🧹 Cycle {i} finished. Cleaning up OOM payload...", serial, run_log_file)
                    self.run_adb(["shell", "rm", "-f", "/data/local/tmp/oom_fill*"], serial=serial)
                    completed = i

            elif test_type == "Background Download Stress (curl/wget)":
                if not dl_url: raise Exception("Download URL cannot be empty!")
                
                total_bytes = self.get_remote_file_size_pc(dl_url)
                
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Background Downloading File ---", serial, run_log_file)
                    
                    self.run_adb(["shell", "rm", "-f", "/data/local/tmp/dl_stress.tmp"], serial=serial)
                    start_time = time.time()
                    
                    cmd_dl = ["adb", "-s", serial, "shell", f"curl -s -k -L -o /data/local/tmp/dl_stress.tmp {dl_url} || wget -q --no-check-certificate -O /data/local/tmp/dl_stress.tmp {dl_url}"]
                    dl_proc = subprocess.Popen(cmd_dl, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **get_cflags())
                    self.dl_procs[serial] = dl_proc
                    
                    is_timeout = False
                    last_check_time = time.time()
                    
                    while dl_proc.poll() is None:
                        if not self.device_testing_state.get(serial, False):
                            try: dl_proc.terminate()
                            except: pass
                            self.run_adb(["shell", "killall", "curl"], serial=serial, capture=False)
                            self.run_adb(["shell", "killall", "wget"], serial=serial, capture=False)
                            break
                            
                        current_time = time.time()
                        
                        if current_time - start_time > dl_timeout:
                            is_timeout = True
                            try: dl_proc.terminate()
                            except: pass
                            self.run_adb(["shell", "killall", "curl"], serial=serial, capture=False)
                            self.run_adb(["shell", "killall", "wget"], serial=serial, capture=False)
                            break
                            
                        if current_time - last_check_time >= 3.0:
                            cur_size = self._get_file_size(serial, "/data/local/tmp/dl_stress.tmp")
                            if total_bytes > 0:
                                pct = min(100.0, (cur_size / total_bytes) * 100)
                                self.ui_log(f"   ... Downloading: {cur_size/(1024*1024):.1f} MB / {total_bytes/(1024*1024):.1f} MB ({pct:.1f}%)", serial, run_log_file)
                            else:
                                self.ui_log(f"   ... Downloading: {cur_size/(1024*1024):.1f} MB", serial, run_log_file)
                            last_check_time = current_time
                            
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
                total_bytes = self.get_remote_file_size_pc(dl_url)
                
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
                        time.sleep(3)
                        
                        cr_size = self._get_file_size(serial, f"/sdcard/Download/{dl_file}.crdownload")
                        part_size = self._get_file_size(serial, f"/sdcard/Download/{dl_file}.part")
                        final_size = self._get_file_size(serial, f"/sdcard/Download/{dl_file}")
                        
                        current_size = 0
                        is_temp = False
                        
                        if cr_size > 0 or part_size > 0:
                            current_size = max(cr_size, part_size)
                            is_temp = True
                        else:
                            current_size = final_size
                            
                        if current_size > 0:
                            if total_bytes > 0:
                                pct = min(100.0, (current_size / total_bytes) * 100)
                                self.ui_log(f"   ... Browser downloading: {current_size/(1024*1024):.1f} MB / {total_bytes/(1024*1024):.1f} MB ({pct:.1f}%)", serial, run_log_file)
                            else:
                                self.ui_log(f"   ... Browser downloading: {current_size/(1024*1024):.1f} MB", serial, run_log_file)
                                
                            if not is_temp and current_size == last_size:
                                stable_count += 1
                                if stable_count >= 2: 
                                    downloaded = True
                                    break
                            else:
                                stable_count = 0
                        else:
                            self.ui_log(f"   ... Waiting for browser to start download...", serial, run_log_file)
                            
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
                    
                    cmd_mic = ["adb", "-s", serial, "shell", "tinycap /data/local/tmp/mic_stress.wav"]
                    mic_proc = subprocess.Popen(cmd_mic, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **get_cflags())
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
                cmd = ["adb", "-s", serial, "shell", "monkey"]
                if test_type == "Monkey (Specific App)":
                    for p in [x.strip() for x in kw["pkgs_str"].split(",") if x.strip()]: 
                        cmd.extend(["-p", p])
                cmd.extend(["--throttle", str(kw["throttle_val"])])
                if kw["ignore_crash_val"]:
                    cmd.extend(["--ignore-crashes", "--ignore-timeouts", "--ignore-security-exceptions"])
                
                cmd.extend(["-v", "-v", "-v", "999999999"])
                
                self.ui_log(f"🚀 Launching Monkey for {target_val} minutes...", serial, run_log_file)
                m_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', **get_cflags())
                self.monkey_procs[serial] = m_proc
                
                def log_monkey_output(p, s, log_f):
                    try:
                        for line in p.stdout:
                            if not self.device_testing_state.get(s, False): break
                            self.ui_log("Monkey: " + line.strip(), s, log_f)
                    except: pass
                
                threading.Thread(target=log_monkey_output, args=(m_proc, serial, run_log_file), daemon=True).start()
                
                start_time = time.time()
                target_sec = target_val * 60
                
                while m_proc.poll() is None:
                    if not self.device_testing_state.get(serial, False): break
                    if time.time() - start_time >= target_sec:
                        self.ui_log(f"⏱️ Target time {target_val} minutes reached. Stopping Monkey...", serial, run_log_file)
                        break
                    time.sleep(1)
                
                try: m_proc.terminate()
                except: pass
                self.run_adb(["shell", "killall", "com.android.commands.monkey"], serial=serial, capture=False)
                
                actual_elapsed_mins = int((time.time() - start_time) / 60)
                completed = target_val if (time.time() - start_time) >= target_sec else actual_elapsed_mins

            elif test_type == "App Cold-Start & Kill":
                pkgs = [x.strip() for x in kw["pkgs_str"].split(",") if x.strip()]
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
                pkgs = [x.strip() for x in kw["pkgs_str"].split(",") if x.strip()]
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
                    cmd_cpu = ["adb", "-s", serial, "shell", "cat /dev/urandom | md5sum"]
                    p = subprocess.Popen(cmd_cpu, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **get_cflags())
                    self.cpu_procs[serial].append(p)
                
                for m in range(target_val):
                    for s in range(60): 
                        if not self.device_testing_state.get(serial, False): break
                        time.sleep(1)
                    if not self.device_testing_state.get(serial, False): break
                    
                    temp_raw = self.run_adb(["shell", "cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null"], serial=serial)
                    temps = []
                    for line in temp_raw.splitlines():
                        line = line.strip()
                        if line.isdigit() or (line.startswith('-') and line[1:].isdigit()):
                            try:
                                t = float(line)
                                if t > 1000: t /= 1000.0
                                if 10 < t < 150: 
                                    temps.append(t)
                            except: pass
                            
                    if temps:
                        max_t = max(temps)
                        self.ui_log(f"--- {m+1}/{target_val} Mins. CPU/SoC Max Temp: {max_t:.1f}°C ---", serial, run_log_file)
                    else:
                        dumpsys_out = self.run_adb(["shell", "dumpsys thermalservice | grep -i 'mValue=' | head -n 1"], serial=serial)
                        if "mValue=" in dumpsys_out:
                            try:
                                val = dumpsys_out.split("mValue=")[1].split()[0]
                                self.ui_log(f"--- {m+1}/{target_val} Mins. ThermalService Temp: {val}°C ---", serial, run_log_file)
                            except:
                                self.ui_log(f"--- {m+1}/{target_val} Mins. CPU Temp: [Permission Denied or 0] ---", serial, run_log_file)
                        else:
                            self.ui_log(f"--- {m+1}/{target_val} Mins. CPU Temp: [Permission Denied or 0] ---", serial, run_log_file)
                            
                    completed = m + 1

            elif test_type == "Storage I/O Stress (1GB)":
                for i in range(1, target_val + 1):
                    if not self.device_testing_state.get(serial, False): break
                    self.ui_log(f"--- Cycle {i}/{target_val} : Writing 1GB File ---", serial, run_log_file)
                    
                    cmd_dd = ["adb", "-s", serial, "shell", "dd if=/dev/zero of=/data/local/tmp/test_1gb.tmp bs=1M count=1000"]
                    dd_proc = subprocess.Popen(cmd_dd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, **get_cflags())
                    
                    while dd_proc.poll() is None:
                        if not self.device_testing_state.get(serial, False):
                            try: dd_proc.terminate()
                            except: pass
                            self.run_adb(["shell", "killall", "dd"], serial=serial, capture=False)
                            break
                        time.sleep(1)
                        
                    if not self.device_testing_state.get(serial, False): break
                    
                    out = dd_proc.stdout.read().strip() if dd_proc.stdout else ""
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
            
        finally:
            if not self.device_testing_state.get(serial, False) and status != "FAIL":
                status = "STOPPED"
                
            if serial in self.logcat_procs:
                p, f = self.logcat_procs[serial]
                try: p.terminate()
                except: pass
                try: f.close()
                except: pass

            if test_type == "Background Download Stress (curl/wget)":
                self.ui_log("🧹 Force cleaning downloaded files before exit...", serial, run_log_file)
                self.run_adb(["shell", "rm", "-f", "/data/local/tmp/dl_stress.tmp"], serial=serial, capture=False)
            elif test_type == "Browser Download Stress (Intent)":
                self.ui_log("🧹 Force cleaning browser downloaded files before exit...", serial, run_log_file)
                if dl_file:
                    base_name = os.path.splitext(dl_file)[0]
                    self.run_adb(["shell", "rm", "-f", f"/sdcard/Download/{base_name}*"], serial=serial, capture=False)
            elif test_type == "Storage/Fake OOM Fill (%)":
                self.ui_log("🧹 Force cleaning OOM payload before exit...", serial, run_log_file)
                self.run_adb(["shell", "rm", "-f", "/data/local/tmp/oom_fill*"], serial=serial, capture=False)
            elif test_type == "Storage I/O Stress (1GB)":
                self.run_adb(["shell", "rm", "-f", "/data/local/tmp/test_1gb.tmp"], serial=serial, capture=False)
            elif test_type == "MDM Framework Stress (Work Profile)":
                self.ui_log("🧹 Force cleaning leftover Managed Profiles before exit...", serial, run_log_file)
                out = self.run_adb(["shell", "pm", "list", "users"], serial=serial)
                for line in out.splitlines():
                    if "MDM_Stress" in line:
                        try:
                            uid = line.split("{")[1].split(":")[0]
                            self.run_adb(["shell", "pm", "remove-user", uid], serial=serial, capture=False)
                            self.ui_log(f"   ... Removed leftover user {uid}", serial, run_log_file)
                        except: pass

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
                self.run_adb(["bugreport", bugreport_file], serial=serial, capture=False, timeout=300)
                
            self.ui_log("==========================================", serial, run_log_file)
            self.ui_log("             TEST SUMMARY                 ", serial, run_log_file)
            self.ui_log(f"RESULT    : {status}", serial, run_log_file)
            self.ui_log(f"COMPLETED : {completed}/{target_val}", serial, run_log_file)
            self.ui_log("==========================================", serial, run_log_file)

            final_log_file = os.path.join(LOG_DIR, f"{log_prefix}_{status}.txt")
            if os.path.exists(run_log_file): os.rename(run_log_file, final_log_file)

            self.device_testing_state[serial] = False
            self.devices_status[serial] = "Idle"
            self.root.after(0, self.update_listbox_display)

    def stop_test(self):
        selections = self.device_listbox.curselection()
        if not selections: return
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
                    
                threading.Thread(target=lambda s=serial: self.run_adb(["shell", "killall", "dd"], serial=s, capture=False), daemon=True).start()
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