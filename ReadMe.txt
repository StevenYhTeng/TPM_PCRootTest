🚀 Release Notes (版本更新日誌)
🚀 Release Notes: ADB Stress Test Console (v4.0.18 ➔ v4.1.0)
🇹🇼 中文版 (Chinese Version)
🌟 新功能與核心升級 (New Features & Core Upgrades)
🧠 音訊智慧點擊與防護機制 (Smart Audio Intent & Automation)

泛用型安全呼叫 (Generic Intent)：全面重構音訊播放指令。捨棄強制綁定 App 套件名稱的做法，改用 Android 合法的泛用廣播 (Generic VIEW Intent)。完美解決在 Android 11+ 設備上因存取 file:// 路徑而觸發 FileUriExposedException 導致播放器瞬間閃退的致命問題。

自動突破選擇視窗 (Chooser Bypass)：加入全新的 UI 盲操作邏輯。當系統跳出「請選擇開啟應用程式 (Open with...)」視窗時，腳本會自動發送 Tab 與 Enter 的底層鍵盤指令，全自動選取預設播放器，實現零人工干預。

🐛 修正問題與優化 (Bug Fixes & Improvements)
🎯 螢幕中心盲點擊支援 (Dynamic Center Screen Tap)

修正許多 OEM 原廠預設播放器（如 AudioPreview）在透過指令喚醒後，必須人工點擊畫面中央才會發聲的問題。腳本現在會自動攔截並計算手機的真實螢幕解析度 (wm size)，精準點擊螢幕幾何正中央，強制觸發播放。

🌙 背景續播強制喚醒修復 (Background Playback Force-Wake)

針對 Audio - Background Play & Screen Lock 測試，修正了部分手機在螢幕休眠黑屏瞬間，會被系統省電機制強行暫停音樂的問題。現在腳本會在鎖定螢幕後，額外補發一次實體的媒體播放鍵指令 (KEYCODE_MEDIA_PLAY)，確保音樂在休眠環境下依然持續高壓播放。

🧹 程式碼結構優化 (Code Structure Optimization)

移除前一版遺留的無效強制除錯指令，使整體測試迴圈的異常處理 (Exception Handling) 更加純淨與精準。

🇺🇸 英文版 (English Version)
🌟 New Features & Core Upgrades
🧠 Smart Audio Intent & Automation Engine

Generic Secure Intent: Completely refactored the audio playback command. Abandoned hardcoded app component targeting in favor of legitimate Generic VIEW Intents. This perfectly resolves the fatal FileUriExposedException crash on Android 11+ devices caused by accessing file:// URIs under Scoped Storage restrictions.

Auto-Dismiss App Chooser (Chooser Bypass): Implemented a new blind UI automation logic. If the Android system prompts an "Open with..." app chooser dialog, the script now automatically injects low-level Tab (D-Pad Right) and Enter keystrokes to auto-select the default media player, achieving zero-touch automation.

🐛 Bug Fixes & Improvements
🎯 Dynamic Center Screen Tap for AudioPreview

Fixed an issue where many OEM default media players (like AudioPreview) required manual user interaction to start playing after being launched via intents. The script now dynamically fetches the device's real-time screen resolution (wm size) and performs a precision tap at the exact geometric center to force audio playback.

🌙 Background Playback Force-Wake Fix

Resolved an issue in the Audio - Background Play & Screen Lock test where aggressive OEM battery optimization would pause the music the exact moment the screen turned off. The script now injects an extra hardware KEYCODE_MEDIA_PLAY event immediately after screen lock, guaranteeing continuous high-stress playback in doze mode.

🧹 Code Structure Optimization

Cleaned up invalid residual debugging commands from the previous iteration, resulting in a purer and more accurate Exception Handling flow within the main execution loop.
🚀 Release Notes: ADB Stress Test Console (v4.0.4 ➔ v4.0.18)
🇹🇼 中文版 (Chinese Version)
🌟 新功能 (New Features)
🎵 音訊自動化測試全面升級 (Audio Automation Upgrade)

自訂音檔與自動派送：新增 Audio 測試專屬面板，允許 QA 選擇電腦本機端的音訊檔 (.mp3/.wav)，腳本會自動 Push 至手機指定目錄。

導入原生播放引擎：全面捨棄容易卡畫面的 UI 播放器，改用語法直接呼叫 Android 底層開發者專用的 stagefright 媒體引擎，完美繞過 Android 10+ 的檔案安全限制，確保每次測試 100% 成功發聲。

📡 WiFi 智慧掃描與自動連線 (Smart WiFi Scanner)

在 WiFi 下載測試模組中加入 🔍 Scan AP 功能。點擊後能即時掃描設備周圍的 WiFi 訊號、自動編號排序，並支援密碼輸入。測試開始前會確保設備成功連線後再進行高壓下載。

🎛️ APM 連線測試細部勾選 (Selective APM Toggles)

針對 [APM] Connectivity Toggle 新增控制面板。QA 現在可以自由勾選/取消勾選 WiFi、藍牙、飛航模式，系統只會針對「有勾選」的硬體進行循環開關壓測。

🛡️ Chrome 歡迎畫面自動繞過 (Chrome FRE Bypass)

[APM] Data I/O (Browser Download) 加入自動繞過機制。在啟動 Chrome 前注入底層參數，直接跳過第一次開機的「歡迎使用 / 同步帳號」畫面，徹底解決測試卡住需要人工點擊的問題。

🐛 修正問題與優化 (Bug Fixes & Improvements)
🛑 重啟壓測終極防呆驗證 (Ultimate Reboot Verification) [v4.0.18]

完全重寫 [APM] System Restart 邏輯。新增三階段嚴格驗證：

斷線確認：持續 Ping 直到設備真正離線（抓出死機 Hang up）。

動畫結束確認：讀取 init.svc.bootanim 確認開機動畫已跑完。

UI 渲染確認：讀取 Window Manager 確保桌面完全繪製成功，才發送下一次 Reboot 指令。徹底根除「手機還沒開好就重啟」導致的死機與假 Pass 問題。

⚙️ 多執行緒競爭條件修復 (Race-Condition Fix)

分離了「運行鎖定」與「停止訊號」的變數。解決了「前一個測試正在背景花時間抓取 Bugreport 時，啟動新測試會導致新測試跑一圈就自動停止」的嚴重邏輯衝突。

🏢 企業管理框架 (MDM) 全系列修復

修復 no_add_managed_profile：測試前自動偵測並清除上一圈殘留的 Device Owner，解鎖權限衝突。

修復 Unknown admin 崩潰：使用 pm install-existing 確保 MDM APK 正確被安裝進新建的「工作空間 (Work Profile)」沙盒內。

修復 MDM 測試秒 Pass 問題：修正因未被納入 Monkey 黑名單變數範圍，導致 for 迴圈被跳過、測試 0 圈就顯示 PASS 的判斷式錯誤。

✅ User Build 全面相容 (100% User Build Compatibility)

全面移除所有會引發 SELinux 權限阻擋的 adb root 與 su 指令，確保測試工具能在完全沒有 Root 的一般消費機 (User Build) 上穩定運行。

🛠️ 漏跑測試項目補回 (Restored Execution Loops)

修正前版架構合併時遺漏的執行區塊。將所有獨立硬體測試 (Standalone WiFi/BT/Mic/Fingerprint) 及部分 APM (Power/Camera) 加回執行迴圈，解決「點選後一圈都沒跑直接 Pass」的漏洞。

💡 動態亮度盲測真實化 (True Random Brightness)

Power & Display 的亮度測試從「固定最大與最小」，改為真正的 random 隨機取值 (10~255)，更真實地還原使用者操作邊界。

🗑️ 移除無效的 LED 測試 (Removed Invalid LED Tests)

經實驗證明，User Build 下的特規 NFC LED 完全受到 OEM 硬體層封鎖，無法透過標準 ADB 點亮。為避免產出無效測試數據，已將該模組從介面中移除。

🇺🇸 英文版 (English Version)
🌟 New Features
🎵 Audio Automation Upgrade

Custom Audio & Auto-Push: Added a dedicated Audio test panel allowing QAs to select a local PC audio file (.mp3/.wav). The tool automatically pushes the file to the target device.

Native Playback Engine: Replaced UI-based music players with Android's native developer media engine (stagefright). This perfectly bypasses Android 10+ URI exposure limits, ensuring 100% reliable audio playback without UI interruptions.

📡 Smart WiFi Scanner & Auto-Connect

Introduced a 🔍 Scan AP UI in the WiFi Download module. It instantly scans nearby networks, auto-numbers them, and accepts password inputs to automatically connect the device to the internet before extreme download tests.

🎛️ Selective APM Connectivity Toggles

Added a control panel for [APM] Connectivity Toggle. QAs can now independently check/uncheck WiFi, Bluetooth, or Airplane mode. The script will dynamically run stress tests only on the enabled components.

🛡️ Chrome First-Run Experience (FRE) Bypass

The [APM] Data I/O test now automatically injects command-line flags to skip the Chrome "Welcome/Sync" screens entirely. This prevents the automation script from hanging on newly flashed devices.

🐛 Bug Fixes & Improvements
🛑 Ultimate Reboot Verification System [v4.0.18]

Completely rewrote the [APM] System Restart logic with a strict 3-stage validation process:

Offline Confirmation: Continuously Pings until the device is truly offline (catches Hang ups).

Boot Animation Check: Polls init.svc.bootanim to ensure the boot animation has stopped.

UI Render Check: Verifies Window Manager to ensure the home screen is fully rendered before issuing the next reboot command. This completely eliminates "Fake Passes" and device crashing caused by overlapping reboots.

⚙️ Race-Condition & Threading Fix

Separated "Run Lock" and "Stop Event" variables. Fixed a critical threading bug where starting a new test while a previous bugreport was still generating in the background caused the new test to abort after just 1 cycle.

🏢 Comprehensive MDM Framework Fixes

Fixed no_add_managed_profile: Automatically detects and clears lingering Device Owners from previous cycles to prevent permission locking.

Fixed Unknown admin Crash: Utilizes pm install-existing to properly inject the MDM APK into the newly sandboxed "Work Profile."

Fixed Zero-Cycle Pass Bug: Resolved a logic error where MDM tests would instantly pass without running any cycles due to a variable conflict with Monkey blacklists.

✅ 100% User Build Compatibility

Removed all adb root and su commands that triggered SELinux permission blocks. This guarantees absolute stability on standard, non-rooted consumer devices (User Builds).

🛠️ Restored Missing Execution Loops

Fixed an oversight from a previous code merge. Re-added missing standalone hardware tests (WiFi/BT/Mic/Fingerprint) and APM modules (Power/Camera) to the main execution loop, fixing the issue where they stopped without running a single cycle.

💡 True Random Brightness Toggle

Updated the Power & Display stress test to generate genuinely randomized brightness values (10~255) on every cycle instead of fixed max/min values, simulating real-world edge cases.

🗑️ Removed Invalid LED Tests

Confirmed that NFC LEDs on User Builds are strictly locked by OEM hardware abstraction layers and cannot be triggered via standard ADB. The LED testing module has been removed to prevent the generation of invalid test results.🚀 Release Notes: ADB Stress Test Console (v3.9.29 ➔ v4.0.4)
🇹🇼 中文版 (Chinese Version)
⚠️ 【重要測試前置作業】
在開始進行任何測試之前，請務必確認最新版（v7.0）的 TPM_OSD.apk 已與 Python 執行檔放置於同一個資料夾，並強烈建議「手動安裝」至測試設備中一次。若未安裝此 APK，最新導入的 OSD 浮水印系統與防止系統殺後台的雙重喚醒機制將無法正常運作。

🌟 重大功能更新 (Major Features)
全新企業級 APM 核心測試模組 (APM Suites)

完美對接商業級壓力測試規範，新增包含「系統重啟與關機、連線切換 (WiFi/BT/飛航)、資料讀寫 (網頁下載)、燒機測試 (影片串流)、電源與顯示 (喚醒與亮度)、相機與媒體壓測」等 6 大 APM 綜合場景。

Monkey 系統 App 黑名單防呆機制 (System Apps Blacklist)

執行 Monkey 壓測前，腳本會自動掃描設備中所有的系統 App，並跳出「確認對話框」供測試人員檢閱。

確認後自動生成並推送黑名單檔案 (--pkg-blacklist-file)，確保 Monkey 絕對不會誤觸設定、電話等核心系統功能導致測試中斷。

🛠️ 測試模組大幅擴充 (Testing Module Enhancements)
📷 相機與媒體 (Camera & Media)

前後鏡頭與錄影: 自動切換前鏡頭連拍 2 張照片，接著切換至後鏡頭錄影 5 秒。

百連拍測試: 模擬長按相機快門，連續高頻觸發 100 張照片拍攝。

儲存空間切換: 模擬修改系統屬性，在內部儲存與外部記憶體 (SD Card) 之間反覆切換並執行拍攝。

🎵 音訊與播放 (Audio Playback)

播放控制壓力: 模擬真實情境，包含播放、上下首切換、音量極值 (Max/Min) 切換、暫停與進度條拖曳。

背景播放與鎖屏: 啟動音樂背景播放後鎖定螢幕 (Standby 2 分鐘)，嚴格驗證後續的喚醒解鎖與音訊中斷/恢復情況。

🌐 網路與下載 (Network & Download)

WiFi 智慧併發下載: 執行下載前自動偵測 WiFi 狀態，未連線將直接報錯阻擋。支援自訂併發數，進行多檔小型 (<100MB) 或大型 (>200MB) 檔案同時下載測試。

⚡ 系統與效能 (System & Performance)

動態亮度切換: 隨機生成亮度值 (10~255) 並頻繁切換，測試 Display HAL 與背光模組壽命。

一鍵清理與多工作業: 瞬間啟動超過 10 個第三方/系統 App 至背景，呼叫近期任務 (Recents) 並執行一鍵清理 (kill-all)，後續進行 Ping 測試檢查系統是否發生畫面凍結 (Freeze)。

本機檔案複製: 支援自訂 Source/Dest 路徑，高壓複製檔案/資料夾並於驗證後自動清理。

APK 批次安裝: 指定本機資料夾，腳本將依序自動讀取並安裝所有 APK 檔案，遇錯自動停止並記錄 Log。

🐛 介面優化與錯誤修正 (UI Improvements & Bug Fixes)
全新純英文分類選單與防選機制 (v4.0.4):

重新梳理下拉式選單，全面去除中文，改用純英文的四大直覺分類（如 --- 📷 Camera & Media ---）。

導入防呆退回機制：當使用者不小心點選到 --- 開頭的分類分隔線時，系統會自動退回上一次選擇的有效測試項目，完全防止誤選報錯。

Target Cycles 鎖死修正: 修復了因測試名稱包含 "Video" 單字導致目標圈數 (Target Cycles) 被誤判並反灰鎖死的字串比對 Bug。

🇺🇸 英文版 (English Version)
⚠️ [IMPORTANT PREREQUISITE]
Before starting any tests, please ensure that the latest TPM_OSD.apk (v7.0) is placed in the exact same directory as the Python script, and we highly recommend manually installing it on the test device first. If this APK is missing, the OSD Watermark system and the double-wake mechanism will fail to function properly.

🌟 Major Features
New Enterprise APM Core Test Suites

Perfectly aligned with commercial stress testing specifications. Introduced 6 major APM scenarios: System Restart & Shutdown, Connectivity Toggle (WiFi/BT/Airplane), Data I/O (Browser Download), Burn-in (Video Streaming), Power & Display (Wake-up & Brightness), and Camera & Media Stress.

Monkey System Apps Blacklist Failsafe

Introduced an interception mechanism before Monkey tests. The script automatically scans all system apps on the device and prompts a confirmation dialog.

Once confirmed, it generates and pushes a --pkg-blacklist-file to the device, ensuring the Monkey test strictly avoids touching critical system functionalities (e.g., Settings, Dialer).

🛠️ Testing Module Massive Expansion
📷 Camera & Media

Front/Rear & Video: Automatically switches to the front camera to take 2 photos, then switches to the rear camera for a 5-second video recording.

Continuous Shooting: Simulates holding the shutter button to trigger a 100-shot high-speed continuous burst.

Storage Switch: Simulates changing system properties to alternate camera save locations between Internal Storage and External Memory (SD Card) followed by image captures.

🎵 Audio Playback

Playback & Controls Stress: Simulates real-user behaviors including play, next/previous track, min/max volume toggle, pause, and progress bar seeking.

Background Play & Lock: Plays music in the background, locks the screen (Standby for 2 minutes), and strictly verifies wake/unlock stability and audio continuity.

🌐 Network & Download

Smart WiFi Concurrent Downloads: Auto-verifies WiFi connectivity before execution (blocks if disconnected). Supports concurrent downloading of multiple small (<100MB) or large (>200MB) files with customizable thread counts.

⚡ System & Performance

Random Brightness Toggle: Rapidly switches display brightness to random levels (10~255) to stress the Display HAL and backlight module.

Multi-App & One-Click Clean: Launches 10+ apps into the background, triggers the Recents menu, performs a simulated one-click clean (kill-all), and runs an immediate Ping test to check for system freeze.

Local File Copy: High-stress file/folder duplication between user-defined Source and Destination paths with post-check auto-cleanup.

Batch APK Installation: Automatically reads and sequentially installs all APK files from a designated local PC folder, logging any failures immediately.

🐛 UI Improvements & Bug Fixes
English-Only Categorized Menu & Selection Failsafe (v4.0.4):

Reorganized the dropdown menu into 4 intuitive, English-only categories (e.g., --- 📷 Camera & Media ---).

Implemented an auto-revert failsafe: If a user accidentally selects a --- category separator, the UI immediately reverts to the last valid test selection, preventing execution errors.

Target Cycles Input Fix: Fixed a substring-matching bug where tests containing the word "Video" falsely disabled and grayed out the Target Cycles input box.
# 🚀 Release Notes: ADB Stress Test Console (v3.9.11 ➔ v3.9.29)
### ⚠️ 【重要測試前置作業】
**在開始進行任何測試之前，請務必確認最新版（v7.0）的 `TPM_OSD.apk` 已與 Python 執行檔放置於同一個資料夾，並強烈建議「手動安裝」至測試設備中一次**。若未安裝此 APK，最新導入的 OSD 浮水印系統與防止系統殺後台的雙重喚醒機制將無法正常運作！
### 🌟 重大功能更新 (Major Features)
* **全新 OSD 浮水印系統 (整合 v7.0 APK)**
* 現在可於測試機螢幕右上角即時顯示「設備序號、IP 位置、當前執行測試」。
* **終極換行修復**：首創使用自訂 `||` 符號傳輸機制，徹底避開 Windows CMD 與 Android Shell 之間的「逃脫字元 (Escape Character)」衝突，實現完美斷行與大字體顯示。

* **智慧儀表板與快速連線模組**
* 新增 **Executive Dashboard (測試儀表板)**，即時監控連線設備數量與活躍測試數。
* 支援 **Subnet Scan (網段全區掃描)** 與 **USB 快速初始化 TCP/IP (Port 5555)** 功能。

### 🛡️ 系統相容性與穩定性 (System Compatibility)
* **全面支援 Android 14 / 15 / 16 安全機制**
* **突破背景限制 (BAL)**：使用「跳板 Activity (Trampoline)」雙重喚醒機制，完美繞過系統對背景啟動 Service 的封殺。
* **突破廣播攔截**：加入 `RECEIVER_EXPORTED` 標籤與「定向廣播 (`-p`)」，防止廣播被 Android 安全子系統靜默丟棄。
* **防休眠白名單**：加入 `dumpsys deviceidle whitelist`，防止長期測試下 OSD 或背景任務被電池管家 (Doze Mode) 獵殺。

### 🛠️ 測試模組強化 (Testing Module Enhancements)
* **進階 Storage I/O (NVMe/UFS) 測試面板**
* 支援動態掃描 (Fetch) 設備上所有真實可讀寫的儲存掛載路徑。
* 支援多路徑選擇，並可自由切換 **「並發 (Concurrent)」** 或 **「循序 (Sequential)」** 寫入 1GB 壓力測試。

* **Monkey 追蹤器與系統 App 抓取**
* 新增 `Include System Apps` 選項，可將系統原生 App (如相機、設定) 納入 Monkey 測試範圍。
* **指令追蹤**：UI 與 Log 會精準印出每一次 `adb shell monkey...` 的實際執行參數。
* **即時串流**：Monkey 執行的 Log 會即時回傳至 UI，並高亮標示 `CRASH` 與 `ANR` 崩潰事件。

* **YouTube 全螢幕自動化**
* 針對 Video Streaming，自動注入按鍵事件 (模擬按 `F` 鍵)，強制觸發 YouTube 全螢幕播放。

### 📝 日誌與介面優化 (Logging & UI Improvements)
* **智慧 Log 命名機制**：生成的 Log 檔名會根據測試類型，自動在結尾加上 `_Cycle` (圈數) 或 `_Mins` (分鐘數) 的單位標籤，方便後續 QA 追蹤。
* **OOM 測試防呆**：優化了 Fake OOM 的容量計算邏輯，防止 `dd` 指令生成過大暫存檔導致系統 RAM 溢出崩潰。

### ⚠️ [IMPORTANT PREREQUISITE]
**Before starting any tests, please ensure that the latest `TPM_OSD.apk` (v7.0) is placed in the exact same directory as the Python script, and we highly recommend manually installing it on the test device first.** If this APK is missing, the newly integrated OSD Watermark system and the double-wake mechanism (designed to prevent background app killing) will fail to function!

### 🌟 Major Features
* **New OSD Watermark System (v7.0 APK Integration)**
* Real-time display of "Device Serial, IP Address, and Current Test" directly on the device screen.
* **Ultimate LineBreak Fix**: Introduced a custom `||` delimiter mechanism to completely bypass the Escape Character conflicts between Windows CMD and Android Shell, achieving perfect multi-line formatting with enlarged fonts.

* **Smart Dashboard & Quick Connect Module**
* Added the **Executive Dashboard** to monitor connected devices and active tests in real time.
* Supported **Local Subnet Scan** and 1-click **USB TCP/IP (Port 5555) Initialization**.

### 🛡️ System Compatibility & Stability
* **Full Support for Android 14 / 15 / 16 Security Restrictions**
* **Bypass Background Execution Limits (BAL)**: Implemented a "Trampoline Activity" double-wake mechanism to bypass the OS blockade on background service launches.
* **Bypass Broadcast Restrictions**: Added `RECEIVER_EXPORTED` flags and targeted intents (`-p`) to prevent broadcasts from being silently dropped by the Android security subsystem.
* **Doze Mode Whitelist**: Automatically whitelists the OSD service via `dumpsys deviceidle` to prevent background tasks from being killed during long-term testing.

### 🛠️ Testing Module Enhancements
* **Advanced Storage I/O (NVMe/UFS) Dashboard**
* Dynamically fetches all actual read/write-capable storage mount paths on the device.
* Supports multi-path selection with toggleable **Concurrent** or **Sequential** 1GB I/O Stress Testing.

* **Monkey Tracker & System Apps Integration**
* Added `Include System Apps` checkbox to inject native system applications (e.g., Camera, Settings) into the Monkey target list.
* **Command Tracking**: Prints the exact executed `adb shell monkey...` command syntax to the UI and Logs.
* **Live Log Streaming**: Real-time streaming of Monkey logs to the console, specifically highlighting `CRASH` and `ANR` events.

* **YouTube Fullscreen Automation**
* Automatically injects key events (simulating the `F` keypress) to force YouTube playback into full-screen mode during Video Streaming Stress.

🚀 Android ADB Stress Test Console - 完整發布日誌 (v3.9.5 - v3.9.11)
[Latest Build] v3.9.11 — Pre-flight Check & Flag Verifier Update
•	🇹🇼 中文更新說明：
o	MDM 測試前置強制預檢機制：當使用者選擇「MDM Framework Stress」並點擊 START 派發測試時，程式會立刻跳出一個醒目的紅色警告提示框。要求人工最後確認裝置是否已執行過 Factory Reset 且處於無帳號登入的純淨狀態，從源頭杜絕因環境不乾淨導致的配置失敗。
o	APK 'testOnly' 屬性照妖鏡：在執行 Device Owner 超級管理員提權前，系統會自動透過底層 dumpsys package 進行深度掃描，檢查剛安裝好的 APK 是否真正包含 android:testOnly="true" 標記。若偵測到該標籤被編譯器或混淆工具剝離，工具將自動攔截並跳出明確的修正指引，避免盲目測試。
o	基礎核心架構優化：精簡並模組化重構代碼，優化多執行緒併發處理能力，提升網域大量掃描時的介面響應速度與防假死效能。
•	🇬🇧 English Release Notes:
o	Mandatory MDM Pre-flight UI Prompt: Added a high-visibility safeguard confirmation dialog before starting MDM tests, forcing manual verification that target devices are factory reset and free of logged-in accounts.
o	APK 'testOnly' Flag Verifier: Implemented an automated system-level package dump check (dumpsys package) to verify the android:testOnly="true" attribute before DPM execution, flashing clear diagnostic instructions if stripped by build optimization variants.
o	Core Architecture Optimization: Modularized code blocks and enhanced multi-device concurrent stability, boosting UI responsiveness and crash-resistance during high-density subnet discoveries.
________________________________________
v3.9.10 — Auto-Bypass & Smart Account Check
•	🇹🇼 中文更新說明：
o	全面靜默繞過 Google Play Protect 審查：佈署 APK 前自動下達指令關閉全域包驗證器 (package_verifier_enable 0 與 verifier_verify_adb_installs 0)，徹底消滅實體設備畫面上彈出的 "Install Anyway" 的手動點擊阻擋，實現 100% 靜默佈署。
o	環境智能預檢系統 (Smart Check)：提權前利用底層核心自動像 X 光一樣掃描手機內現存帳戶 (dumpsys account) 與殘留的多用戶配置 (pm list users)。若發現任何阻礙 Device Owner 提權的帳號，會立刻在日誌中印出明確的錯誤提示。
o	框架異常轉譯：解碼 AOSP 框架底層的 set-device-owner 報錯訊息，將混淆的 RuntimeException 自動轉譯為具體可維護的中文排查方案（如提醒使用者 Factory Reset 等）。
•	🇬🇧 English Release Notes:
o	Google Play Protect Bypass: Automatically disabled package verification parameters during provisioning to eliminate the disruptive "Install Anyway" screen prompt on devices, achieving 100% silent deployment.
o	Smart Account Pre-check: Integrated an automated account and profile scanner that logs explicit error advice immediately if a lingering Google or OEM account is blocking the device owner provisioning.
o	Framework Exception Decoupling: Decoded AOSP underlying device policy shell errors into highly readable, actionable troubleshooting descriptions within the session log.
________________________________________
v3.9.8 - v3.9.9 — Deploy Fix & Parameter Decoupling
•	🇹🇼 中文更新說明：
o	安裝與授權模組解耦：將「安裝 APK」與「設定 Device Owner」拆分為兩個獨立打勾選項，支援使用者手動裝完 App 後、僅由工具進行提權測試。
o	開放自訂管理員元件名稱 (Component Name)：UI 面板開放文字輸入框，支援自訂 Receiver 類別路徑（預設為 com.mdm.client/.MyDeviceAdminReceiver），防止因開發團隊中途修改包名（Package Name）導致自動化腳本失效。
o	佈署超時延長與引號修復：移除底層傳遞時多餘的路徑引號 Bug，並為大容量企業級 MDM APK 提供 120 秒專屬超時緩衝；同時合併 stderr 輸出，提供更豐富的錯誤捕獲。
•	🇬🇧 English Release Notes:
o	Deployment Parameter Decoupling: Separated APK installation and Device Owner assignment into independent UI checkboxes, allowing standalone privilege promotion on pre-installed app assets.
o	Custom Admin Component Input: Added a text field for flexible target component definition (Package/.Receiver), resolving script breaks caused by development branch package renames.
o	Timeout Extension & Quoting Fix: Fixed an OS path quoting bug and extended the provisioning timeout to 120 seconds to guarantee smooth processing for larger enterprise apps, merging stderr for clean diagnostics.
________________________________________
v3.9.6 - v3.9.7 — MDM Provisioning Initial Framework
•	🇹🇼 中文更新說明：
o	首度導入 MDM 自動化生命週期壓力測試：新增專屬「MDM Framework Stress (Work Profile)」測試選項，自動循環下達 pm create-user --profileOf 0 --managed MDM_Stress 與 pm remove-user，模擬企業託管設定檔的建立與撕毀極限測試。
o	批次靜默動態權限授予：在佈署階段強制導入 -g 參數，迫使系統在安裝時直接靜默批准清單中的所有動態敏感權限。
o	自動化連鎖指令核心：實現一鍵連鎖：Play Protect 關閉 $\rightarrow$ 安裝 $\rightarrow$ Device Owner 提權 $\rightarrow$ 靜默賦予系統日誌讀取權限 (READ_LOGS) $\rightarrow$ 開始壓力測試。
•	🇬🇧 English Release Notes:
o	Introduction of MDM Life-cycle Stress Testing: Released the dedicated "MDM Framework Stress (Work Profile)" test matrix, automatically cycling profile creation and deletion via commands to simulate intense enterprise container life cycles.
o	Silent Runtime Permission Auto-Grant (-g): Enforced the critical -g runtime parameter during app push sequences to automatically grant all dynamic manifest privileges silently.
o	Chained Automation Protocol: Enabled seamless single-click sequence orchestration: Verifier bypass $\rightarrow$ Push $\rightarrow$ Device Owner lock $\rightarrow$ READ_LOGS bypass $\rightarrow$ Stress iteration.

v3.9.5 - May 04, 2026
🇹🇼 中文更新說明：
【系統守護與核心穩定性修復 (Anti-Zombie & Insomnia Update)】

☕ 新增系統不眠機制 (Insomnia Update)： 導入 Windows 底層 API (SetThreadExecutionState)。程式執行期間將自動阻擋電腦進入睡眠或休眠模式，確保動輒數天的長時間壓力測試（如 10000 分鐘 Monkey）絕不因 PC 睡著而中斷；程式關閉後自動還原電源設定。

🧟 消滅 ADB 殭屍進程死鎖： 拔除底層的 shell=True 呼叫，確保 Python 能夠 100% 獵殺超時的連線程序。徹底解決多網段掃描時，背景殘留大量 adb.exe 導致 ADB 伺服器癱瘓、無法再次 Scan 的死鎖問題。

⚖️ 全網域掃描負載平衡： 將同時併發的網路掃描執行緒（Threads）從 200 智慧調降至 50。在維持極速掃描的同時，完美保護 ADB daemon 不受 DDoS 級別的請求衝擊。

⏱️ 啟動時序與 UI 防假死修正： 調整 GDPR 隱私視窗的攔截順序，將其移至計時器與自動掃描觸發之前，解決程式剛開啟時卡住的 Bug。

🧹 Logcat 記憶體洩漏修復： 完善背景系統日誌程序的文件控制代碼 (File Handles) 管理，防止執行超長天期測試時可能引發的記憶體洩漏 (Memory Leak)。

🇬🇧 English Release Notes:
【System Guardian & Core Stability Fixes (Anti-Zombie & Insomnia Update)】

☕ Added System Insomnia Mechanism: Integrated Windows underlying APIs (SetThreadExecutionState). The application now automatically prevents the PC from entering sleep or hibernation modes during execution, ensuring long-term stress tests (e.g., 10000-min Monkey tests) are never interrupted. Normal power settings are restored upon exit.

🧟 Eradicated ADB Zombie Process Deadlocks: Removed shell=True calls to ensure Python can 100% terminate timed-out connection processes. This completely resolves the severe deadlock issue where hundreds of residual adb.exe zombie processes paralyzed the ADB server during Omni-Network scanning.

⚖️ Omni-Network Scanning Load Balancing: Intelligently reduced concurrent network scanning threads from 200 to 50. This maintains rapid scanning speeds while perfectly protecting the ADB daemon from DDoS-level connection spikes.

⏱️ Startup Sequence & UI Freeze Correction: Reordered the GDPR privacy dialog to intercept before background timers and auto-scans trigger, resolving the UI freeze bug upon initial launch.

🧹 Logcat Memory Leak Fix: Improved the file handle management for background logging processes, preventing potential memory leaks during extremely long-term stress testing.

[Archived Version] v3.9.3 - May 01, 2026
🇹🇼 中文更新說明：
【重大更新與安全性升級】

🔒 新增 GDPR 隱私合規機制 (GDPR Privacy Consent)： 程式啟動時加入強制性隱私權同意聲明，明確告知系統日誌 (Logcat / Bugreport) 皆採「本地端存儲，絕不上傳」，確保測試流程符合國際資料保護法規。

🌐 全網域智能掃描引擎 (Omni-Network Discovery)： 突破過往雙網卡掃描盲區！現已支援同時動態偵測並掃描電腦上所有的 Wi-Fi 與 Ethernet (有線網路) 網段，實現真正的多設備「隨插即掃」。

🧠 智能死機偵測系統 (Smart Bootloop Detector)： 升級設備離線的判定邏輯。能精準分辨設備是「單純網路斷線」還是「卡在開機畫面 (Bootloop)」，大幅消除自動化測試的誤判。

🛑 關機指令雙重防呆 (Double Confirmation Safety)： 當使用者勾選「徹底斷電 (Shutdown)」時，新增高警示級別的確認視窗，避免無人值守機台因缺乏硬體喚醒機制而永久失聯。

🐛 狀態鎖定修復： 修正了切換測試項目時，設備選取狀態會意外清空的 UI 臭蟲 (exportselection=False)。

🇬🇧 English Release Notes:
【Major Updates & Security Enhancements】

🔒 Added GDPR Privacy Consent Mechanism: Implemented a mandatory privacy consent dialog on startup. It explicitly clarifies that all system logs (Logcat / Bugreport) are "stored locally and never uploaded," ensuring the testing process complies with international data protection regulations.

🌐 Omni-Network Discovery Engine: Breakthrough in multi-NIC scanning! Now supports simultaneous, dynamic detection and scanning across all active Wi-Fi and Ethernet subnets on the host PC, enabling true "Plug & Play" for multiple devices.

🧠 Smart Bootloop Detector: Upgraded offline determination logic. Accurately distinguishes between a "simple network disconnection" and a "device stuck in a bootloop," drastically reducing false alarms in automated testing.

🛑 Double Confirmation Safety for Shutdown: Added a high-priority warning dialog when the "Shutdown" option is checked. This prevents unattended devices from being permanently lost if they lack a hardware auto-wake mechanism.

🐛 UI State Lock Fix: Resolved an annoying UI bug where the device selection state would inadvertently clear when switching test options (exportselection=False).

[v3.8.2] - 2026-04-21 (TPM/APM Edition)
English
This release, dubbed the TPM/APM Edition, significantly expands the tool's capabilities into deep system-level and framework stress testing. It introduces advanced hardware interaction simulations and highly requested UI/UX features for professional lab environments.
New Features & Enhancements:
•	Deep System Stressors:
•	Fingerprint HAL Stress: Simulates biometric polling and response stability during screen wake cycles.
•	MDM Framework Stress: Automates the creation and teardown of Managed Work Profiles to test Enterprise/DPM stability.
•	Storage/Fake OOM Fill: Dynamically calculates and fills storage to a target percentage (e.g., 95%) to test device behavior under extreme low-space conditions.
•	Enhanced Reboot Logic:
•	Reboot & Shutdown Stress: Now supports a dual-phase "Reboot + Optional Shutdown" cycle with configurable wait timers.
•	Robust Reconnection: Improved TCP/IP reconnection logic that suppresses timeout errors during device boot-up for smoother automated loops.
•	Enterprise Connectivity:
•	Multi-Subnet Scanning: Supports scanning multiple network segments simultaneously (e.g., 15.38.67.x and 15.38.65.x).
•	USB Initialization Tool: New "Wake USB" (喚醒 USB) button to quickly toggle adb tcpip 5555 mode across all connected cables.
•	UI/UX Improvements:
•	Executive Dashboard: Integrated a high-visibility stats panel showing real-time connected devices and active test counts.
•	Silent Execution: Implemented hidden CMD window flags for Windows to prevent annoying pop-ups during automated tasks.
•	TPM Easter Egg: Added an interactive "Overdrive Mode" providing project context and team blessings.
________________________________________
中文版
此版本命名為 TPM/APM 特仕版，將工具能力大幅擴展至深層系統級與框架壓力測試。本版本引入了先進的硬體互動模擬，以及針對專業實驗室環境設計的 UI/UX 優化。
新功能與強化項目：
•	深層系統壓力測試：
•	指紋 HAL 壓力測試：模擬生物辨識輪詢與螢幕喚醒期間的反應穩定性。
•	MDM 框架壓力測試：自動化建立與移除「受管工作設定檔」(Work Profile)，用以測試企業級 DPM 的穩定性。
•	空間佔滿/模擬 OOM：動態計算並將儲存空間填寫至目標百分比（如 95%），以測試設備在極低空間下的行為。
•	強化版重啟邏輯：
•	重啟與關機壓力測試：新增支援「重啟 + 選配關機」雙階段循環，並可自訂等待計時器。
•	強韌連線機制：優化了 TCP/IP 重連邏輯，能自動忽略開機過程中的逾時錯誤，使自動化循環更順暢。
•	企業級連線能力：
•	多網段掃描：支援同時掃描多組區域網路路徑（例如 15.38.67.x 與 15.38.65.x）。
•	USB 初始化工具：新增「喚醒 USB」按鈕，快速將所有實體連線設備切換至 adb tcpip 5555 模式。
•	UI/UX 優化項目：
•	戰情儀表板：整合高能見度統計面板，即時顯示已連線設備數與執行中的測試總數。
•	靜默執行：針對 Windows 環境實作了 CMD 視窗隱藏標記，防止自動化任務期間彈出大量視窗。
•	TPM 隱藏彩蛋：新增互動式「Overdrive 模式」，提供專案背景資訊與團隊祝福。

## Release Note: Android ADB Stress Test Console

### [v2.1.0] - 2026-04-17 (Pro Edition)

#### **English**
This version represents a major architectural leap from a single-device tool to a **distributed multi-device testing platform**. Version 2.1.0 introduces professional-grade automation features and significant performance optimizations for enterprise-level QA environments.

**Key New Features:**
* **Multi-Device Concurrent Control**: Completely redesigned to support simultaneous testing on multiple connected devices with independent state management and logging.
* **High-Speed Subnet Scanner**: Replaced manual connection with a high-speed parallel scanner (100 threads) that can probe an entire local subnet (254 IPs) in approximately 3 seconds.
* **Enhanced Network Stress Tests**: Added specialized "Background Download Stress" (via `curl`/`wget`) and "Browser Download Stress" (via Android Intents) with global and regional presets.
* **Professional Hardware Stressors**: Introduced new modules for Microphone Audio HAL stress, Microphone/Camera privacy toggling, and Mobile Data toggling.
* **Intelligent Auto-Recovery**: Implemented an ADB server monitoring system that automatically detects and restarts unresponsive ADB services.
* **UI Modernization**: A dual-panel layout (380px control container) optimized for multi-device status monitoring and real-time consolidated logging.

---

#### **中文版**
本版本是從單機版工具向**分散式多機測試平台**邁進的重大架構演進。v2.1.0 為企業級 QA 環境引入了專業自動化功能與顯著的效能優化。

**主要更新項目：**
* **多機併發控制**：全新設計的架構，支援多台設備同時執行不同測試，並具備獨立的狀態管理與日誌系統。
* **高速區域網路掃描器**：取代手動連線，採用 100 執行緒的高速併發掃描技術，可在約 3 秒內掃描整個網段 (254 個 IP) 並自動連線。
* **強化版網路壓力測試**：新增專業「背景下載壓力測試」(透過 `curl`/`wget`) 以及「瀏覽器 Intent 下載測試」，並提供全球與區域常用下載預設值。
* **專業硬體壓力模組**：新增麥克風 Audio HAL 壓力測試、麥克風/鏡頭隱私開關切換以及行動數據開關測試。
* **智慧自動修復機制**：內建 ADB 伺服器監測系統，當偵測到 ADB 無回應時會自動執行 Kill/Start Server 進行修復。
* **UI 介面現代化**：採用雙面板配置（380px 控制側欄），專為多機狀態監控與即時彙整日誌顯示而優化。


🚀 Release Notes: Android ADB Stress Test Console (Pro Edition)
Version: 1.0.1
Release Date: March 2026

Overview
The Android ADB Stress Test Console is a comprehensive, GUI-based automation tool designed for system-level and application-level stability testing. Built for Android developers and QA engineers, it streamlines repetitive ADB commands, handles background log collection, and ensures safe test teardowns.

Key Features & Capabilities

10 Built-in Stress Scenarios: * Hardware toggles: WiFi, Airplane Mode, Screen Sleep/Wake.

System stress: CPU Thermal Throttling (via background md5sum processes), Storage eMMC/UFS I/O Stress (1GB file writes).

Power manipulation: Battery Spoofing (forces 5% state and unplugged status).

UI & App level: App Cold-Start & Kill loops, Gallery UI tap automation, and system-wide/app-specific UI Exerciser Monkey testing.

Smart Dynamic UI: The interface automatically adapts based on the selected test, revealing package selection and Monkey throttle controls only when relevant.

On-Device App Fetching: Directly queries the connected device for 3rd-party applications, allowing users to select target packages via a checklist UI rather than typing package names manually.

Automated Log & Bugreport Collection: * Automatically spins up background logcat threads upon test execution.

Triggers an automatic system bugreport generation during test teardown.

Centralized PC_Test_Logs directory for easy artifact retrieval.

Failsafe Teardown: Automatically resets battery states, kills heavy background CPU processes, and interrupts Monkey instances if a test is manually stopped or errors out.