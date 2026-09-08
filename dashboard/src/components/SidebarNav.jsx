import React from 'react';
import { 
  LayoutDashboard, 
  Network, 
  Activity, 
  Globe, 
  ShieldAlert, 
  FileText, 
  Settings, 
  Cpu, 
  HardDrive,
  Layers,
  LogOut,
  ChevronRight,
  Sparkles
} from 'lucide-react';

export const SidebarNav = ({ activeNav, setActiveNav }) => {
  
  const navItems = [
    { id: 'dashboard', label: 'Telemetry Overview', icon: LayoutDashboard, badge: 'LIVE' },
    { id: 'tunnels', label: 'IPsec Tunnels', icon: Network, badge: '24' },
    { id: 'bandwidth', label: 'Throughput Stream', icon: Activity },
    { id: 'nodes', label: 'Global Edge Grid', icon: Globe },
    { id: 'security', label: 'Security & Ciphers', icon: ShieldAlert },
    { id: 'logs', label: 'Diagnostic Logs', icon: FileText },
  ];

  return (
    <aside className="w-full lg:w-64 bg-slate-950/40 border-r border-white/5 p-4 flex flex-col justify-between shrink-0 font-sans">
      
      {/* Upper Navigation Section */}
      <div className="space-y-6">
        
        {/* Navigation Category Label */}
        <div>
          <div className="px-3 text-[10px] font-mono font-semibold tracking-wider text-slate-500 uppercase mb-2 flex items-center justify-between">
            <span>CORE SYSTEMS</span>
            <Sparkles className="w-3 h-3 text-cyan-400/70" />
          </div>

          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeNav === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveNav(item.id)}
                  className={`nav-pill w-full group justify-between ${isActive ? 'active' : ''}`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className={`w-4 h-4 transition-colors ${
                      isActive ? 'text-cyan-400' : 'text-slate-400 group-hover:text-slate-200'
                    }`} />
                    <span className="text-xs">{item.label}</span>
                  </div>

                  {item.badge && (
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-medium ${
                      item.badge === 'LIVE' 
                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30' 
                        : 'bg-slate-800 text-slate-400'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* System Health Overview Card */}
        <div className="mirror-card p-3.5 space-y-3 border border-white/10 bg-slate-900/40">
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
            <span className="flex items-center gap-1.5 text-slate-300 font-semibold">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" /> CLUSTER ENGINE
            </span>
            <span className="text-emerald-400 text-[10px]">99.99% UP</span>
          </div>

          {/* Progress Bar 1: Gateway Load */}
          <div className="space-y-1">
            <div className="flex justify-between text-[10px] font-mono text-slate-400">
              <span>CPU Core Allocation</span>
              <span className="text-slate-200">28.4%</span>
            </div>
            <div className="w-full bg-slate-900/80 h-1.5 rounded-full overflow-hidden p-0.5 border border-white/5">
              <div className="bg-gradient-to-r from-blue-600 to-cyan-400 h-full rounded-full w-[28.4%]" />
            </div>
          </div>

          {/* Progress Bar 2: Memory Buffers */}
          <div className="space-y-1">
            <div className="flex justify-between text-[10px] font-mono text-slate-400">
              <span>Ring Buffer Usage</span>
              <span className="text-slate-200">42.1%</span>
            </div>
            <div className="w-full bg-slate-900/80 h-1.5 rounded-full overflow-hidden p-0.5 border border-white/5">
              <div className="bg-gradient-to-r from-blue-500 to-indigo-400 h-full rounded-full w-[42.1%]" />
            </div>
          </div>

          {/* Encryption Quick Status */}
          <div className="pt-2 border-t border-white/5 flex items-center justify-between text-[10px] font-mono text-slate-400">
            <span>Hardware Offload</span>
            <span className="text-cyan-400 font-medium">AES-NI ENABLED</span>
          </div>
        </div>

        {/* Protocol Shortcuts */}
        <div>
          <div className="px-3 text-[10px] font-mono font-semibold tracking-wider text-slate-500 uppercase mb-2">
            VPN MODES
          </div>
          <div className="grid grid-cols-2 gap-1.5 text-xs font-mono">
            <div className="p-2 rounded-lg bg-slate-900/40 border border-white/5 text-center text-slate-300 hover:border-cyan-500/30 transition-colors cursor-pointer">
              <span className="text-[10px] text-cyan-400 block font-semibold">IPsec / IKEv2</span>
              <span className="text-[9px] text-slate-500">24 Tunnels</span>
            </div>
            <div className="p-2 rounded-lg bg-slate-900/20 border border-white/5 text-center text-slate-400 hover:border-slate-700 transition-colors cursor-pointer">
              <span className="text-[10px] text-slate-400 block font-semibold">WireGuard</span>
              <span className="text-[9px] text-slate-600">Standby</span>
            </div>
          </div>
        </div>

      </div>

      {/* Lower Profile & System Actions */}
      <div className="pt-4 border-t border-white/5 space-y-3">
        
        {/* User Account / Node Owner */}
        <div className="flex items-center gap-3 p-2 rounded-xl bg-slate-900/50 border border-white/5 hover:border-white/15 transition-all cursor-pointer">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-cyan-400 flex items-center justify-center font-mono font-bold text-xs text-white shadow-[0_0_12px_rgba(0,210,255,0.3)]">
            OP
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-semibold text-slate-200 truncate">SecOps Gateway</div>
            <div className="text-[10px] font-mono text-slate-400 truncate">admin@aero-vpn.internal</div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-500" />
        </div>

        {/* Quick Settings & Help */}
        <div className="flex items-center justify-between text-xs text-slate-400 px-1">
          <button className="flex items-center gap-1.5 hover:text-slate-200 transition-colors">
            <Settings className="w-3.5 h-3.5 text-slate-500" />
            <span>Config</span>
          </button>
          <button className="flex items-center gap-1.5 hover:text-red-400 transition-colors">
            <LogOut className="w-3.5 h-3.5 text-slate-500" />
            <span>Disconnect</span>
          </button>
        </div>

      </div>

    </aside>
  );
};
