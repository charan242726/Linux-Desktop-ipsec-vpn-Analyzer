import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Activity, 
  Wifi, 
  RefreshCw, 
  Zap, 
  Server, 
  SlidersHorizontal,
  Bell,
  CheckCircle2,
  Lock,
  Minus,
  Square,
  X,
  Download,
  Terminal
} from 'lucide-react';

export const FloatingShell = ({ 
  children, 
  isLiveStream, 
  setIsLiveStream, 
  activeNav, 
  setActiveNav,
  lastTickTime,
  activeTunnelCount,
  totalBandwidth,
  mlFindings,
  ikeFindings
}) => {
  const [notificationOpen, setNotificationOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#040711] text-slate-100 p-[3px] relative overflow-hidden flex flex-col justify-between">
      {/* Ambient background glow orbs - Blue Theme */}
      <div className="ambient-glow-container">
        <div className="ambient-orb-1" />
        <div className="ambient-orb-2" />
        <div className="ambient-orb-3" />
      </div>

      {/* Outer Floating Application Shell */}
      <div className="floating-shell rounded-[24px] md:rounded-[30px] flex-1 flex flex-col z-10 mx-auto w-full border border-white/[0.09]">
        
        {/* Mirror Specular Sheen Top Header Bar — draggable for frameless window */}
        <header
          className="specular-bar px-5 py-3.5 flex flex-wrap items-center justify-between gap-4 z-20"
          style={{ WebkitAppRegion: 'drag' }}
        >
          {/* Brand */}
          <div className="flex items-center gap-3" style={{ WebkitAppRegion: 'no-drag' }}>
            <div className="relative flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600/30 to-cyan-500/20 border border-cyan-400/40 shadow-[0_0_20px_rgba(0,210,255,0.25)]">
              <ShieldCheck className="w-5 h-5 text-cyan-400" />
              <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-400"></span>
              </span>
            </div>
            <h1 className="text-sm font-bold tracking-tight font-mono">
              VPN<span className="text-cyan-400">GUARD</span>
            </h1>
          </div>


          {/* Quick System Telemetry Pills & Global Search */}
          <div className="flex items-center gap-3" style={{ WebkitAppRegion: 'no-drag' }}>
            

            {/* Live Data Ticker Toggle */}
            <button
              onClick={() => setIsLiveStream(!isLiveStream)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-mono transition-all border ${
                isLiveStream 
                  ? 'bg-cyan-500/15 border-cyan-400/40 text-cyan-300 shadow-[0_0_15px_rgba(0,210,255,0.2)]' 
                  : 'bg-slate-900/50 border-white/10 text-slate-400 hover:text-slate-200'
              }`}
            >
              <Zap className={`w-3.5 h-3.5 ${isLiveStream ? 'text-cyan-400 animate-pulse' : ''}`} />
              <span>{isLiveStream ? 'LIVE STREAMING' : 'STREAM PAUSED'}</span>
              <span className={`w-1.5 h-1.5 rounded-full ${isLiveStream ? 'bg-cyan-400' : 'bg-slate-500'}`} />
            </button>

            {/* Status Indicator Badges */}
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/50 border border-white/10 text-xs font-mono text-slate-300">
              <span className="pulse-beacon pulse-beacon-emerald" />
              <span>TUNNELS {activeTunnelCount}/24 ONLINE</span>
            </div>

            <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/50 border border-white/10 text-xs font-mono text-slate-300">
              <Activity className="w-3.5 h-3.5 text-cyan-400" />
              <span>AGGREGATE {totalBandwidth} GB/S</span>
            </div>

            {/* ML Classification Badge */}
            {mlFindings?.ml_available && (
              <div className="hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-400/30 text-xs font-mono text-indigo-300 shadow-[0_0_10px_rgba(99,102,241,0.15)]">
                <Terminal className="w-3.5 h-3.5" />
                <span className="uppercase font-semibold">AI: {mlFindings.traffic_type || 'UNKNOWN'}</span>
                <span className="text-indigo-400/60 ml-1">({Math.round((mlFindings.confidence || 0) * 100)}%)</span>
              </div>
            )}

            {/* Download Latest Report Button */}
            <button 
              onClick={() => window.open('http://localhost:8000/reports/latest/pdf', '_blank')}
              className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-500/10 border border-cyan-400/30 text-xs font-mono text-cyan-300 hover:bg-cyan-400 hover:text-slate-900 transition-all font-semibold shadow-[0_0_10px_rgba(0,210,255,0.1)]"
              title="Download the most recent forensic report"
            >
              <Download className="w-3.5 h-3.5" />
              <span>DOWNLOAD LATEST</span>
            </button>

            {/* Notifications Button */}
            <div className="relative">
              <button 
                onClick={() => setNotificationOpen(!notificationOpen)}
                className="relative p-2 rounded-lg bg-slate-900/50 border border-white/10 text-slate-400 hover:text-white transition-colors"
              >
                <Bell className="w-4 h-4" />
                <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_8px_#00d2ff]" />
              </button>

              {notificationOpen && (
                <div className="absolute right-0 mt-2 w-72 bg-[#090e1a] border border-cyan-500/20 rounded-xl p-3 shadow-2xl z-50 text-xs font-mono">
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-white/10 text-slate-300">
                    <span className="font-semibold text-cyan-400">TELEMETRY ALERTS</span>
                    <span className="text-[10px] text-slate-500">Just Now</span>
                  </div>
                  <div className="space-y-2 text-slate-300">
                    <div className="p-2 rounded bg-cyan-500/10 border border-cyan-500/20 text-[11px]">
                      <span className="text-cyan-300 font-semibold">IKEv2 Re-key:</span> Tunnel #04 (SG-GATEWAY) negotiated AES-256-GCM successfully.
                    </div>
                    <div className="p-2 rounded bg-slate-800/60 border border-white/5 text-[11px]">
                      <span className="text-emerald-400 font-semibold font-mono">Health Check:</span> Zero packet loss across 24 edge nodes.
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Window Controls — minimize, maximize, close */}
            <div
              className="flex items-center gap-1 ml-2"
              style={{ WebkitAppRegion: 'no-drag' }}
            >
              <button
                onClick={() => window.electronAPI?.minimize()}
                title="Minimize"
                className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
              >
                <Minus className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => window.electronAPI?.maximize()}
                title="Maximize"
                className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
              >
                <Square className="w-3 h-3" />
              </button>
              <button
                onClick={() => window.electronAPI?.close()}
                title="Close"
                className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-red-500/80 transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>

          </div>

        </header>

        {/* Main Application Container */}
        <div className="flex-1 flex flex-col lg:flex-row overflow-hidden relative">
          {children}
        </div>

        {/* Specular Footer Bar */}
        <footer className="specular-bar px-5 py-2.5 flex flex-wrap items-center justify-between text-[11px] font-mono text-slate-500 gap-3 border-t border-white/5">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5 text-slate-400">
              <Lock className="w-3 h-3 text-cyan-400" /> IPsec Encapsulation: ESP (Mode 50) + NAT-T
            </span>
            <span className="hidden md:inline text-slate-600">|</span>
            <span className="hidden md:inline">Key Exchange: IKEv2 / Diffie-Hellman {ikeFindings?.dh_group ? `Group ${ikeFindings.dh_group}` : 'Group 19'}</span>
          </div>

          <div className="flex items-center gap-3 text-slate-400">
            <span>Ticks: <strong className="text-slate-200">{lastTickTime}</strong></span>
            <span className="text-slate-600">•</span>
            <span className="text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> FIPS 140-3 COMPLIANT
            </span>
          </div>
        </footer>

      </div>
    </div>
  );
};
