# 🛡️ IPsec VPN Analyzer — Windows Desktop Application

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%2F11-blue?logo=windows&logoColor=white" />
  <img src="https://img.shields.io/badge/Electron-44-47848F?logo=electron&logoColor=white" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/XGBoost-ML-orange" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

---

## 🧩 Problem Statement

Modern IPsec VPN deployments are increasingly difficult to audit. Network administrators and security teams lack real-time visibility into:

- Whether VPN tunnels are using secure cryptographic parameters (IKEv2, AES-256-GCM, PFS)
- What application traffic is being tunnelled inside ESP flows (video, VoIP, bulk data)
- Whether active security vulnerabilities exist (IKEv1 Aggressive Mode, missing PFS, weak DH groups)

Existing tools like Wireshark require expert knowledge and cannot provide automated machine-learning-based threat intelligence or one-click PDF reports.

---

## 💡 Proposed Solution

A fully packaged **Windows Desktop Application** that combines:
- **Real-time packet capture** (Scapy + Npcap) to passively inspect IKE/ESP traffic
- **Machine Learning inference** (XGBoost) to classify encrypted traffic without decryption
- **Deterministic security rule engine** to flag misconfigurations
- A **premium glassmorphism UI** (Electron + React + Tailwind) for live telemetry

All bundled into a single `.exe` installer — no Python, no command line needed for end users.

---

## 🚀 Innovation & Uniqueness

| What makes it different | Detail |
|---|---|
| **Zero-decryption ML** | Classifies traffic type inside ESP purely from packet sizes and inter-arrival times — no need to break encryption |
| **Unified Desktop App** | Python backend compiled via PyInstaller, wrapped in Electron — single installer, no dependencies |
| **Real-time IKE parsing** | Decodes live IKE Phase 1/2 exchanges to extract SPI, exchange type, message ID on the fly |
| **Automated PDF reports** | One-click forensic report generation with full findings |
| **Blockchain integrity** | Optional Hardhat/Solidity smart contract to register analysis hashes on-chain for tamper-proof audit trail |

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔴 **Live Telemetry Dashboard** | Real-time throughput, latency, and packet integrity charts |
| 🔬 **Deep Packet Inspection** | Captures and decodes IKE, ESP, AH packets via Scapy + Npcap |
| 🤖 **ML Traffic Classification** | XGBoost classifies encrypted ESP flows without decryption |
| 🚨 **Security Rule Engine** | Flags IKEv1 Aggressive Mode, missing PFS, weak DH groups, replay attacks |
| 📄 **PDF Report Generation** | One-click forensic reports (fpdf2) |
| ⛓️ **Blockchain Integrity** | Optional on-chain hash registration of analysis sessions |
| 🖥️ **Premium Glass UI** | Frameless glassmorphism dashboard — Tailwind CSS + Framer Motion |
| ⚡ **Live API Polling** | Frontend polls backend every 2s for real-time state synchronization |

---

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                    Windows Desktop (Electron 44)               │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │           React UI — Tailwind + Framer Motion            │  │
│  │                                                         │  │
│  │  FloatingShell → SidebarNav → Dashboard / Security /    │  │
│  │                 Telemetry Charts / Diagnostic Logs       │  │
│  │                                                         │  │
│  │          Polls  http://localhost:8000/analysis  (2s)    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                           ↕ HTTP REST                         │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │        Python VPN Analyzer Service (Windows Service)     │  │
│  │                     (Runs as SYSTEM)                    │  │
│  │                                                         │  │
│  │  Thread 1: FastAPI REST Server  (port 8000)             │  │
│  │  Thread 2: Scapy Sniffer  →  Npcap → UDP 500/4500/ESP  │  │
│  │  Thread 3: Analysis Worker  →  IKE Parser               │  │
│  │                              →  ML Engine (XGBoost)     │  │
│  │                              →  Security Rules          │  │
│  │                              →  SharedState             │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  resources/backend/backend.exe  (Registered Windows Service)  │
└───────────────────────────────────────────────────────────────┘
```

---

## 🐧 Linux Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone -b linux-desktop-app https://github.com/LalThota/vpn-ipsec-analyzer.git
   cd vpn-ipsec-analyzer
   ```

2. **Install the Background Daemon (Requires `sudo`):**
   ```bash
   chmod +x install.sh
   sudo ./install.sh
   ```
   *This automatically creates a virtual environment, installs Python dependencies, and starts the `vpnguard-analyzer` systemd daemon in the background to silently monitor for VPN traffic.*

3. **Run the UI Application:**
   ```bash
   cd dashboard
   npm install
   npm run build
   npx electron-builder --linux
   ```
   *Double-click the generated `.AppImage` in `dashboard/dist-electron-final/`. The app will launch and can be minimized to the system tray.*

---

## 🔄 Complete User Workflow

```
1. User runs IPsec VPN Analyzer Setup.exe (Admin mode)
          ↓
2. Setup automatically runs Npcap installer & registers Background Service
          ↓
3. App opens → UI waits in IDLE state (no UAC prompts needed)
          ↓
4. Windows Service (running continuously as SYSTEM) detects IPsec traffic
          ↓
5. OS-level Notification triggers: "VPN Detected"
          ↓
6. User clicks "Start Analysis" on the Dashboard banner
          ↓
7. Scapy decodes IKE packets (UDP 500/4500) and extracts ESP features
          ↓
8. Dual-Path Intelligence kicks in:
   - ML Engine classifies encrypted traffic type (Video, VoIP, etc)
   - Rule Engine deterministically flags cryptographic weaknesses
          ↓
9. UI polls /analysis API → Live dashboard updates with real metrics
          ↓
10. User clicks "Generate Report" → PDF downloaded
```

---

## 🛠️ Technology Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| Electron | 44 | Desktop shell, IPC, frameless window |
| React | 19 | Component framework |
| Tailwind CSS | 3.4 | Utility-first styling |
| Framer Motion | 13 | Animations |
| Recharts | 3 | Real-time telemetry charts |
| Vite | 8 | Frontend bundler |
| Lucide React | — | Icons |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| FastAPI | 0.115 | REST API server |
| Scapy | 2.6 | Packet capture and IKE/ESP decoding |
| XGBoost | — | Traffic classification ML model |
| scikit-learn | — | Feature engineering pipeline |
| fpdf2 | — | PDF report generation |
| SQLite | — | Session and result persistence |
| PyInstaller | — | Compiles Python → backend.exe |

### Blockchain (Optional)
| Technology | Purpose |
|---|---|
| Hardhat + Solidity | Smart contract for tamper-proof audit hashes |

---

## 💻 System Requirements (Windows)

| Requirement | Minimum |
|---|---|
| OS | Windows 10 / Windows 11 (64-bit) |
| RAM | 4 GB |
| Disk | 500 MB free |
| Python | 3.10+ (for building from source only) |
| Node.js | ≥ 18.x (for building from source only) |
| **Npcap** | **Required — must be installed before first launch** |

---

## 📦 Quick Install (End Users)

### Step 1 — Download the Installer
Go to the [**Releases**](../../releases) page → Download `IPsec VPN Analyzer Setup 0.0.0.exe`

### Step 2 — Install
Run the installer. It will:
1. Ask for Administrator privileges.
2. Extract the application files.
3. **Automatically pop up the Npcap installer**. (Complete the Npcap setup manually).
4. Seamlessly register and start the `VPNAnalyzerService` in the Windows background.

### Step 3 — Launch & Analyze
Open the app. It will connect to the background service automatically. Connect to any IKEv2 VPN to trigger the detection!

---

## 🔧 Build from Source (Developers)

### 1. Clone the repository
```bash
git clone https://github.com/LalThota/vpn-ipsec-analyzer.git
cd vpn-ipsec-analyzer
git checkout vpn-analyzer-windows
```

### 2. Set up the Python backend
> Open **PowerShell as Administrator**

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r ..\requirements.txt
```

### 3. Install frontend dependencies
```powershell
cd ..\dashboard
npm install
```

### 4. Run in development mode
Terminal 1 — start backend:
```powershell
cd backend
.\venv\Scripts\activate
python api\main.py
```
Terminal 2 — start Electron app:
```powershell
cd dashboard
npm run electron:dev
```

### 5. Build Windows installer (production)

> ⚠️ **Important: Build the backend FIRST, then Electron.**

**Step A — Build Python backend (run from repo root as Administrator):**
```powershell
.\build_backend.ps1
# Produces: backend\dist\backend.exe
```

**Step B — Build React frontend and package installer:**
```powershell
cd dashboard
npm run build
npx electron-builder --win
# Produces: dashboard\dist-electron-final\IPsec VPN Analyzer Setup 0.0.0.exe
```

---

## 🔬 ML Model

The XGBoost classifier (`ml/model/primary_rf_pipeline.pkl`) was trained on:
- **Dataset:** Custom IPsec testbed captures (see `testbed/`) covering 7 traffic classes
- **Features:** ESP packet sizes, inter-arrival times, burst patterns
- **Classes:** Bulk Transfer, Chat, Email, ICMP, Video Streaming, VoIP, Web Browsing
- **Approach:** Zero-decryption — classifies traffic type purely from encrypted packet metadata

---

## 🔒 Security Rule Engine

The rule engine (`backend/services/`) flags:

| Rule | Description |
|---|---|
| IKEv1 Aggressive Mode | Vulnerable to offline dictionary attacks |
| Missing PFS | No Perfect Forward Secrecy configured |
| Weak DH Group | Groups < 14 (< 2048-bit) flagged |
| Replay Attack Window | Missing or disabled anti-replay protection |
| Weak Cipher | DES, 3DES, MD5-based suites flagged |

---

## 🧠 Dual-Path Intelligence Architecture

The analyzer uses two distinct, parallel intelligence paths answering different questions to avoid "guessing" cryptographic security via ML:

### 1. Deterministic Security Analysis (Rules)
* **Goal:** "Is the IPsec configuration using weak cryptography?"
* **Method:** Deterministic parsing of IKE parameters (Diffie-Hellman groups, ciphers, hashes) extracted directly from the packets.
* **Why:** Security vulnerabilities (like NULL encryption or Aggressive Mode) are absolute facts present in the metadata. The system flags these using hardcoded NSA/NIST guidelines, rather than relying on ML probabilities.

### 2. Machine Learning Traffic Analysis (Behavioral)
* **Goal:** "What type of application traffic is flowing inside the encrypted payload?"
* **Method:** Zero-decryption feature extraction (measuring packet sizes, inter-arrival timing, burst rates, and directionality) fed into an XGBoost/Random Forest model.
* **Why:** ESP payloads cannot be decrypted without the keys. The ML model is purely responsible for behavioral classification (identifying Web, VoIP, Video, Bulk) without accessing plaintext.

---

## 📡 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Backend health check |
| `/analysis` | GET | Current state + all findings |
| `/analysis/start` | POST | Start a new analysis session |
| `/analysis/snap` | POST | Upload PCAP for offline analysis |
| `/reports/{id}` | GET | Download PDF forensic report |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| Window blank after install | Uninstall and reinstall latest `.exe` |
| "Npcap not found" error | Install Npcap from https://npcap.com with WinPcap compat mode |
| No packets captured | Ensure running as Administrator |
| Backend shows OFFLINE | Backend takes ~5s to start; wait and status updates automatically |
| Antivirus flags the app | Whitelist `IPsec VPN Analyzer.exe` — flagged due to raw socket usage |

---

## 📁 Project Structure

```
vpn-ipsec-analyzer/
├── backend/                    # FastAPI + Scapy Python backend
│   ├── api/                    # REST route handlers
│   ├── core/                   # SharedState, VpnState, threading
│   ├── services/               # ML inference, PDF, replay, security rules
│   └── database/               # SQLite session management
├── dashboard/                  # Electron + React frontend
│   ├── electron/               # main.cjs, preload.cjs
│   ├── src/                    # React components + Tailwind UI
│   └── vpn2/                   # Main dashboard view (vpn.jsx)
├── ml/
│   ├── experiment.py           # Model training script
│   └── model/
│       └── primary_rf_pipeline.pkl   # Trained XGBoost model
├── blockchain/                 # Optional Hardhat smart contracts
├── testbed/                    # Sample PCAP metadata for testing
├── docs/                       # Architecture and research docs
├── build_backend.ps1           # PyInstaller build script (run first!)
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
└── README.md
```

---

## 🤝 Contributing

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes with a descriptive message
4. Push and open a Pull Request against `vpn-analyzer-windows`

---

## ⚠️ Known Limitations

- ML model accuracy varies by network environment and traffic mix
- Blockchain feature requires a local Hardhat node or testnet configuration
- Windows only — Linux/macOS desktop builds not yet available

---

## 📜 License

[MIT License](LICENSE) — Built for **SIH 2026** 🇮🇳

---

*For issues, open a [GitHub Issue](../../issues).*
