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
  Search,
  CheckCircle2,
  Lock,
  Globe2
} from 'lucide-react';

export const FloatingShell = ({ 
  children, 
  isLiveStream, 
  setIsLiveStream, 
  activeNav, 
  setActiveNav,
  lastTickTime,
  activeTunnelCount,
  totalBandwidth
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [notificationOpen, setNotificationOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#040711] text-slate-100 p-3 sm:p-5 md:p-6 lg:p-7 relative overflow-hidden flex flex-col justify-between">
      {/* Ambient background glow orbs - Blue Theme */}
      <div className="ambient-glow-container">
        <div className="ambient-orb-1" />
        <div className="ambient-orb-2" />
        <div className="ambient-orb-3" />
      </div>

      {/* Outer Floating Application Shell */}
      <div className="floating-shell rounded-[24px] md:rounded-[30px] flex-1 flex flex-col z-10 max-w-[1720px] mx-auto w-full border border-white/[0.09]">
        
        {/* Mirror Specular Sheen Top Header Bar */}
        <header className="specular-bar px-5 py-3.5 flex flex-wrap items-center justify-between gap-4 z-20">
          
          {/* Brand & Connection Matrix Title */}
          <div className="flex items-center gap-3.5">
            <div className="relative flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600/30 to-cyan-500/20 border border-cyan-400/40 shadow-[0_0_20px_rgba(0,210,255,0.25)]">
              <ShieldCheck className="w-5 h-5 text-cyan-400" />
              <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-400"></span>
              </span>
            </div>
            
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-sm font-semibold tracking-tight text-white font-mono">
                  AERO-VPN <span className="text-cyan-400">//</span> TELEMETRY
                </h1>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-cyan-500/15 text-cyan-300 border border-cyan-400/30">
                  v4.2.8-PROD
                </span>
              </div>
              <p className="text-[11px] text-slate-400 flex items-center gap-1.5 font-mono">
                <Globe2 className="w-3 h-3 text-cyan-500/70" /> IPsec Gateway Cluster • Frankfurt-01-EHR
              </p>
            </div>
          </div>

          {/* Quick System Telemetry Pills & Global Search */}
          <div className="flex items-center gap-3">
            
            {/* Search Input */}
            <div className="relative hidden md:block">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                type="text" 
                placeholder="Search tunnels, IPs, endpoints..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-slate-900/60 border border-white/10 text-xs text-slate-200 placeholder-slate-500 rounded-lg pl-8 pr-3 py-1.5 w-56 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30 transition-all font-mono"
              />
            </div>

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
            <span className="hidden md:inline">Key Exchange: IKEv2 / Diffie-Hellman Group 19</span>
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
