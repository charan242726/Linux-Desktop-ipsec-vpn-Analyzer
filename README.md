# IPsec VPN Analyzer

A cross-platform, enterprise-grade forensic suite for deep packet inspection and real-time machine learning analysis of IPsec VPN traffic.

![Dashboard Preview](https://via.placeholder.com/1000x600.png?text=Command+Center+Dashboard)

## 🚀 Overview

This application bridges a powerful **Python/Scapy backend** with a sleek, frameless **Electron & React frontend**. It provides a "Command Center" masterpiece layout to instantly monitor network interfaces, capture IKE/ESP packets, and analyze IPsec deployment configurations against known security vulnerabilities (like IKEv1 aggressive mode, missing PFS, or weak ciphers).

## ✨ Features

- **Live Capture Mode:** Hooks directly into physical/virtual network interfaces (e.g., `eth0`, `wlan0`) to monitor encrypted traffic in real-time.
- **Forensic PCAP Mode:** Drag-and-drop offline `.pcap` or `.pcapng` files for historical deep-packet inspection.
- **Masterpiece UI Dashboard:** A highly polished "Bento" grid layout featuring a live glowing system status, and a cinematic `stdout` terminal feed.
- **Machine Learning Inference:** Leverages an embedded Random Forest model to classify ESP flows into application traffic categories (Streaming, VoIP, Browsing, Downloads) purely from packet lengths and inter-arrival times.
- **Rule-Based Engine:** Deterministic fallbacks to flag weak crypto suites and missing Perfect Forward Secrecy (PFS).
- **Automated Windows Packaging:** Fully configured GitHub Actions pipeline to compile the Python backend and package the Electron app into a standalone `.exe`.

## 🏗️ Architecture

The application operates as a unified Desktop Application but runs two distinct layers:
1. **Frontend (Electron + React):** Responsible for the frameless "Command Center" window and state management. It communicates with the backend via REST and spawns the engine using `sudo-prompt` to ensure OS-level capture permissions.
2. **Backend (FastAPI + Python):** A unified thread pool architecture. The `main.py` entry point spins up a Scapy `sniff()` thread, pushing captured packets into a processing queue. An analysis thread pops these packets, runs them through the Rules/ML engines, and serves the results via a FastAPI REST interface.

## 📦 Building & Installation

### Windows (`.exe`) via GitHub Actions
We use a CI/CD pipeline to overcome cross-platform C-extension compilation limits.
1. Go to the **Actions** tab in this GitHub repository.
2. Click on **Build Windows Executable**.
3. Click **Run workflow**.
4. Once completed, download the `IPsecAnalyzer-Windows` artifact. It contains the standalone installer!

### Linux (Development)
To run the project locally on a Linux machine:

1. **Setup Python Environment:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Start the Electron App:**
   ```bash
   cd dashboard
   npm install
   npm run electron:dev
   ```
   *Note: When you click "Initialize Pipeline" in the UI, the app will prompt you for your `sudo` password. This is strictly required for `scapy` to bind to the network interface in promiscuous mode.*

## 🔒 Permissions & Security
To capture raw network packets, the underlying backend executable must run with root/Administrator privileges. 
- **Windows:** The `.exe` uses `sudo-prompt` to invoke UAC (User Account Control).
- **Linux:** Requires PolicyKit (`pkexec`) or standard `sudo`.

---
*Built for SIH 2026.*
