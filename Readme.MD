🚀 Release Notes (版本更新日誌)
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


這兩份 Release Notes 清楚呈現了您的工具如何從單純的腳本封裝進化成專業的多機自動化測試平台。

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