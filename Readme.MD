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