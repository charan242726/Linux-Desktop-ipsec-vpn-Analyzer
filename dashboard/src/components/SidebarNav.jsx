import React from 'react';
import { 
  LayoutDashboard, 
  Network, 
  Activity, 
  Globe, 
  ShieldAlert, 
  Shield, 
  Settings, 
  Database,
  FileText,
  Sparkles
} from 'lucide-react';

export const SidebarNav = ({ activeNav, setActiveNav }) => {
  
  const navItems = [
    { id: 'dashboard', label: 'Telemetry Overview', icon: LayoutDashboard, badge: 'LIVE' },
    { id: 'tunnels', label: 'IPsec Tunnels', icon: Network, badge: '24' },
    { id: 'reports', label: 'Report History', icon: FileText, badge: 'NEW' },
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


      </div>


    </aside>
  );
};
