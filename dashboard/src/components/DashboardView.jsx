import { useState, useEffect } from 'react';
import { Upload, Radio, Terminal, Play, Activity } from 'lucide-react';
import './DashboardView.css';
import './TerminalFeed.css';

export default function DashboardView({ engineState, findings, startAnalysis, error }) {
  const isStartEnabled = engineState === 'VPN_DETECTED';

  // Simulated terminal logs
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    if (engineState === 'IDLE') {
      setLogs(['> systemctl start ipsec-analyzer-daemon', '> [OK] npcap loopback and physical interfaces hooked.', '> Listening on UDP 500, UDP 4500, IP 50...']);
    } else if (engineState === 'VPN_DETECTED') {
      setLogs(prev => [...prev, '', '> [WARN] Encrypted payload detected on port 500 (ISAKMP)', '> Action required: Initialize engine to begin decryption and analysis.']);
    } else if (engineState === 'ANALYZING') {
      setLogs(prev => [...prev, '', '> pipeline initialized...', '> ML Inference model loaded into memory.', '> Waiting for ESP flows...']);
    }
  }, [engineState]);

  useEffect(() => {
    let interval;
    if (engineState === 'ANALYZING' && findings?.esp_features) {
      interval = setInterval(() => {
        const timestamp = new Date().toISOString().substring(11, 23);
        const seq = Math.floor(Math.random() * 10000);
        const len = Math.floor(Math.random() * 1000) + 64;
        setLogs(prev => {
          const next = [...prev, `[${timestamp}] IP 192.168.1.10 > 10.0.0.1: ESP(spi=0x${Math.random().toString(16).substring(2,10)},seq=0x${seq}), length ${len}`];
          if (next.length > 50) return next.slice(next.length - 50);
          return next;
        });
      }, 300);
    }
    return () => clearInterval(interval);
  }, [engineState, findings]);

  return (
    <div className="dashboard-master">
      {/* HEADER SECTION */}
      <div className="master-header">
        <div>
          <div className="hero-badge">VPN ANALYSIS ENGINE</div>
          <h1 className="master-title">Command <span className="highlight-cyan">Center</span></h1>
          <p className="master-subtitle">Select your data source and initialize the inspection pipeline.</p>
        </div>
        <div className={`master-status-badge ${engineState.toLowerCase()}`}>
          <div className="status-dot"></div>
          <div className="status-text">
            <span className="status-label">System Status</span>
            <span className="status-value">{engineState}</span>
          </div>
        </div>
      </div>

      {/* INPUT GRID */}
      <div className="master-grid">
        
        {/* Left: Engine Controls */}
        <div className="master-card control-panel">
          <div className="card-header-sleek">
            <Radio size={18} className="icon-cyan" />
            <h2>Live Capture Mode</h2>
          </div>
          <p className="card-desc">Hook into a physical network interface to monitor traffic in real-time.</p>
          
          <div className="control-group">
            <label>Network Interface</label>
            <select className="master-select">
              <option>Ethernet (eth0) — 1 Gbps Active</option>
              <option>Wi-Fi (wlan0) — Disconnected</option>
            </select>
          </div>

          <div className="control-action">
            {error && <div className="error-text">{error}</div>}
            <button 
              className={`btn-master-start ${isStartEnabled ? 'active' : 'disabled'}`}
              disabled={!isStartEnabled}
              onClick={startAnalysis}
            >
              <Play size={20} fill="currentColor" />
              <span>{isStartEnabled ? "Initialize Pipeline" : "Waiting for VPN Traffic..."}</span>
            </button>
          </div>
        </div>

        {/* Right: PCAP Upload */}
        <div className="master-card upload-panel">
          <div className="card-header-sleek">
            <Upload size={18} className="icon-cyan" />
            <h2>Forensic PCAP Mode</h2>
          </div>
          <p className="card-desc">Upload an existing capture file for offline deep-packet inspection.</p>
          
          <div className="master-dropzone">
            <div className="dropzone-inner">
              <Upload size={32} className="dropzone-icon" />
              <h3>Drag and drop your PCAP file</h3>
              <p>Supports .pcap and .pcapng files up to 500MB</p>
              <button className="btn-secondary mt-3">Browse Files</button>
            </div>
          </div>
        </div>

      </div>

      {/* TERMINAL SECTION */}
      <div className="terminal-wrapper">
        <div className="terminal-container">
          <div className="terminal-header">
            <div className="terminal-dots">
              <span className="dot red"></span>
              <span className="dot yellow"></span>
              <span className="dot green"></span>
            </div>
            <div className="terminal-title">
              <Activity size={14} />
              <span>npcap-stdout-stream</span>
            </div>
          </div>
          <div className="terminal-body mono">
            {logs.map((log, i) => (
              <div key={i} className="log-line">{log}</div>
            ))}
          </div>
        </div>
      </div>

    </div>
  );
}
