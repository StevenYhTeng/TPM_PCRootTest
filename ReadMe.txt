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