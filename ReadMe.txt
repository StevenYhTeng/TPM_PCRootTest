Release Note: Android ADB Stress Test Console (TPM/APM Edition)
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