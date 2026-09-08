# 🛡️ IPsec VPN Analyzer — Windows Desktop App

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%2F11-blue?logo=windows&logoColor=white" />
  <img src="https://img.shields.io/badge/Electron-44-47848F?logo=electron&logoColor=white" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

A fully packaged **Windows Desktop Application** for real-time deep-packet inspection and machine learning analysis of IPsec/VPN network traffic. Built with **Electron + React (Tailwind)** on the frontend and **FastAPI + Scapy + XGBoost** on the backend — all bundled into a single `.exe` installer.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔴 **Real-Time Dashboard** | Live telemetry stream with throughput, latency, and packet integrity charts |
| 🔬 **Deep Packet Inspection** | Captures & decodes IKE, ESP, AH packets via Scapy + Npcap |
| 🤖 **ML Traffic Classification** | XGBoost model classifies encrypted ESP flows (Streaming, VoIP, Browsing, etc.) |
| 🚨 **Security Rule Engine** | Flags weak ciphers, missing PFS, IKEv1 Aggressive Mode and more |
| 📄 **PDF Report Generation** | One-click forensic reports with full analysis breakdown (fpdf2) |
| 🖥️ **Frameless Glass UI** | Premium glassmorphism design with Tailwind CSS + Framer Motion |
| ⚡ **Live API Polling** | Frontend polls backend `/analysis` every 2s for real-time state sync |

---

## 📸 Screenshots

> Dark glassmorphism UI with real-time IPsec telemetry, IKE parameter extraction, and ML inference results.

---

## 🚀 Quick Install (Windows)

### Option 1 — Download the Installer (Recommended)

1. Go to the [**Releases**](../../releases) page of this repository
2. Download `IPsec VPN Analyzer Setup 0.0.0.exe`
3. **Double-click** the installer — it will install and launch automatically
4. Allow the **UAC Administrator prompt** — this is required for Npcap to capture network packets

> ⚠️ **Prerequisite: Install Npcap first!**
> The app uses Npcap to capture raw network packets. Download it from **https://npcap.com** before launching the app. Make sure to check **"Install Npcap in WinPcap API-compatible mode"** during installation.

---

### Option 2 — Build from Source (Developers)

#### Prerequisites

| Tool | Version | Download |
|---|---|---|
| Node.js | ≥ 18.x | https://nodejs.org |
| Python | ≥ 3.10 | https://python.org |
| Npcap | Latest | https://npcap.com |
| Git | Any | https://git-scm.com |

#### Step 1 — Clone the repo

```bash
git clone https://github.com/LalThota/vpn-ipsec-analyzer.git
cd vpn-ipsec-analyzer
git checkout vpn-analyzer-windows
```

#### Step 2 — Set up the Python Backend

Open **PowerShell as Administrator** and run:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r ..\requirements.txt
```

#### Step 3 — Install Frontend Dependencies

```powershell
cd ..\dashboard
npm install
```

#### Step 4 — Run in Development Mode

In one terminal, start the backend:
```powershell
cd backend
.\venv\Scripts\activate
python api\main.py
```

In another terminal, start the Electron app:
```powershell
cd dashboard
npm run electron:dev
```

#### Step 5 — Build the Production `.exe`

**Build the Python backend:**
```powershell
# From repo root (as Administrator)
.\build_backend.ps1
```

**Build the Electron installer:**
```powershell
cd dashboard
npm run build
npx electron-builder --win
```

The installer will be at:
```
dashboard\dist-electron\IPsec VPN Analyzer Setup 0.0.0.exe
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Electron Shell (main.cjs)               │
│  ┌──────────────────────────────────────────────────┐   │
│  │         React UI (Tailwind + Framer Motion)       │   │
│  │  FloatingShell → SidebarNav → Dashboard Views     │   │
│  │         Polls  localhost:8000/analysis  (2s)       │   │
│  └──────────────────────────────────────────────────┘   │
│                         ↕ HTTP REST                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │        FastAPI Backend (backend.exe)              │   │
│  │  Thread 1: Scapy Sniff (Npcap, UDP 500/4500)     │   │
│  │  Thread 2: Analysis Worker (IKE, ESP, ML, Rules) │   │
│  │  Thread 3: FastAPI REST Server (port 8000)       │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Backend health check |
| `/analysis` | GET | Current analysis state + findings |
| `/analysis/start` | POST | Start a new analysis session |
| `/analysis/snap` | POST | Upload a PCAP file for analysis |
| `/reports/{id}` | GET | Download PDF report |

---

## 🔒 Permissions & Security

The app **requires Administrator privileges** to capture raw packets:

- **Windows:** The Electron app uses `sudo-prompt` to trigger a UAC elevation dialog at startup
- The Python backend (`backend.exe`) is launched with elevated privileges
- All network capture is done locally — **no data leaves your machine**

---

## 🛠️ Tech Stack

### Frontend
- **Electron 44** — Desktop shell, frameless window management
- **React 19** — Component framework
- **Tailwind CSS 3** — Utility-first styling
- **Framer Motion** — Animations
- **Recharts** — Real-time telemetry charts
- **Lucide React** — Icons

### Backend
- **FastAPI** — REST API server (uvicorn)
- **Scapy** — Raw packet capture and IKE/ESP decoding
- **XGBoost / scikit-learn** — Traffic classification ML model
- **fpdf2** — PDF report generation
- **SQLite** — Session and result persistence

### Build Tools
- **PyInstaller** — Compiles Python backend into `backend.exe`
- **electron-builder** — Packages Electron + backend into NSIS Windows installer
- **Vite 8** — Frontend bundler

---

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| App icon in taskbar but window blank | Uninstall old version, install the latest `.exe` (fixed in this release) |
| "Npcap not found" error | Install Npcap from https://npcap.com with WinPcap compatibility mode |
| No packets captured | Run as Administrator, check Windows Firewall isn't blocking Npcap |
| Backend OFFLINE in UI | The Python engine takes ~5s to start; wait and the status will update automatically |
| Antivirus flags the app | Add `IPsec VPN Analyzer.exe` to your AV whitelist — it's flagged due to raw socket usage |

---

## 📁 Project Structure

```
vpn-ipsec-analyzer/
├── backend/                # FastAPI + Scapy Python backend
│   ├── api/                # REST routes (/analysis, /reports, etc.)
│   ├── core/               # SharedState, VpnState, threading
│   ├── services/           # ML inference, PDF generation, replay
│   └── models/             # XGBoost + sklearn classifiers
├── dashboard/              # Electron + React frontend
│   ├── electron/           # main.cjs (Electron entry), preload.cjs
│   ├── src/                # React components + Tailwind UI
│   ├── vpn2/               # Main dashboard view (vpn.jsx)
│   └── dist-electron/      # Built installer output (gitignored)
├── testbed/                # Sample PCAP files for testing
├── build_backend.ps1       # PyInstaller build script
└── requirements.txt        # Python dependencies
```

---

## 🤝 Contributing

1. Fork this repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes
4. Push and open a Pull Request against `vpn-analyzer-windows`

---

## 📜 License

MIT License — Built for **SIH 2026** 🇮🇳

---

*For issues or questions, open a GitHub Issue.*
