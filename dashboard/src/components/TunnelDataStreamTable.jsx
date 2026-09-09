import React, { useState } from 'react';
import { 
  Network, 
  Search, 
  Eye,
  Inbox
} from 'lucide-react';

export const TunnelDataStreamTable = ({ tunnelsList, onSelectTunnel }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProtocol, setSelectedProtocol] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const defaultTunnels = [
    { 
      id: 'TNL-8041', 
      name: 'SG-CORE-GATEWAY-01', 
      remoteIp: '198.51.100.42', 
      localIp: '10.240.0.12', 
      protocol: 'IKEv2', 
      cipher: 'AES-256-GCM', 
      bandwidth: '420.5 Mbps', 
      latency: '8 ms', 
      jitter: '0.2 ms', 
      rekeyIn: '14m 22s', 
      status: 'ESTABLISHED', 
      health: 100 
    },
    { 
      id: 'TNL-8042', 
      name: 'EU-FRANKFURT-PEER', 
      remoteIp: '203.0.113.88', 
      localIp: '10.240.0.15', 
      protocol: 'IKEv2', 
      cipher: 'AES-256-GCM', 
      bandwidth: '310.2 Mbps', 
      latency: '14 ms', 
      jitter: '0.4 ms', 
      rekeyIn: '42m 10s', 
      status: 'ESTABLISHED', 
      health: 100 
    },
    { 
      id: 'TNL-8043', 
      name: 'US-EAST-VIRGINIA-DC', 
      remoteIp: '198.51.100.104', 
      localIp: '10.240.1.4', 
      protocol: 'IKEv2', 
      cipher: 'AES-256-GCM', 
      bandwidth: '540.8 Mbps', 
      latency: '68 ms', 
      jitter: '1.2 ms', 
      rekeyIn: '08m 45s', 
      status: 'RE-KEYING', 
      health: 98 
    },
    { 
      id: 'TNL-8044', 
      name: 'AP-TOKYO-EDGE-NODE', 
      remoteIp: '203.0.113.190', 
      localIp: '10.240.2.88', 
      protocol: 'IKEv2', 
      cipher: 'ChaCha20-Poly1305', 
      bandwidth: '180.4 Mbps', 
      latency: '184 ms', 
      jitter: '2.1 ms', 
      rekeyIn: '55m 30s', 
      status: 'ESTABLISHED', 
      health: 96 
    },
    { 
      id: 'TNL-8045', 
      name: 'UK-LONDON-EXCHANGE', 
      remoteIp: '198.51.100.220', 
      localIp: '10.240.0.99', 
      protocol: 'IKEv2', 
      cipher: 'AES-256-GCM', 
      bandwidth: '295.0 Mbps', 
      latency: '18 ms', 
      jitter: '0.3 ms', 
      rekeyIn: '22m 14s', 
      status: 'ESTABLISHED', 
      health: 100 
    },
  ];

  const tunnelsToUse = tunnelsList && tunnelsList.length > 0 ? tunnelsList : defaultTunnels;

  // Bug 1 fix: Only show protocols that actually exist in the data
  const availableProtocols = ['ALL', ...new Set(tunnelsToUse.map(t => t.protocol))];

  // Bug 2 fix: Add status filter options from real data
  const availableStatuses = ['ALL', ...new Set(tunnelsToUse.map(t => t.status))];

  const filteredTunnels = tunnelsToUse.filter((t) => {
    const matchesSearch = 
      t.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.remoteIp.includes(searchTerm) ||
      t.id.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesProtocol = selectedProtocol === 'ALL' || t.protocol === selectedProtocol;
    const matchesStatus = statusFilter === 'ALL' || t.status === statusFilter;

    return matchesSearch && matchesProtocol && matchesStatus;
  });

  return (
    <div className="mirror-card p-4 flex flex-col justify-between">
      
      {/* Controls & Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 mb-3 border-b border-white/5">
        
        {/* Title */}
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-400/30 text-cyan-400">
            <Network className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-semibold font-mono text-white tracking-tight">
              LIVE IPsec TUNNEL TELEMETRY MATRIX
            </h3>
            <p className="text-[10px] font-mono text-slate-400">
              Showing {filteredTunnels.length} of {tunnelsToUse.length} Established SAs
            </p>
          </div>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-2">
          
          {/* Search Box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input 
              type="text"
              placeholder="Filter tunnels..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-900/60 border border-white/10 text-xs text-slate-200 placeholder-slate-500 rounded-lg pl-8 pr-3 py-1 w-44 focus:outline-none focus:border-cyan-500/50 font-mono"
            />
          </div>

          {/* Bug 1 fix: Protocol filter - only shows protocols that exist in data */}
          <div className="flex items-center p-0.5 rounded-lg bg-slate-900/60 border border-white/10 text-[10px] font-mono">
            {availableProtocols.map((proto) => (
              <button
                key={proto}
                onClick={() => setSelectedProtocol(proto)}
                className={`px-2 py-0.5 rounded-md transition-all ${
                  selectedProtocol === proto
                    ? 'bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-400/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {proto}
              </button>
            ))}
          </div>

          {/* Bug 2 fix: Status filter - now actually rendered */}
          <div className="flex items-center p-0.5 rounded-lg bg-slate-900/60 border border-white/10 text-[10px] font-mono">
            {availableStatuses.map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-2 py-0.5 rounded-md transition-all ${
                  statusFilter === status
                    ? 'bg-amber-500/20 text-amber-300 font-semibold border border-amber-400/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {status}
              </button>
            ))}
          </div>

        </div>

      </div>

      {/* Dense Table */}
      <div className="overflow-x-auto">
        {filteredTunnels.length === 0 ? (
          /* Bug 1 fix: Empty state when no results */
          <div className="flex flex-col items-center justify-center py-10 text-slate-500 font-mono gap-2">
            <Inbox className="w-8 h-8 text-slate-600" />
            <p className="text-xs">No tunnels match the current filters</p>
            <button
              onClick={() => { setSearchTerm(''); setSelectedProtocol('ALL'); setStatusFilter('ALL'); }}
              className="text-[10px] text-cyan-400 hover:underline mt-1"
            >
              Clear all filters
            </button>
          </div>
        ) : (
          <table className="w-full text-left dense-table border-collapse">
            <thead>
              <tr>
                <th>Tunnel ID & Name</th>
                <th>Endpoints (Local / Remote)</th>
                <th>Protocol & Cipher</th>
                <th>Bandwidth Rate</th>
                <th>Latency / Jitter</th>
                <th>Next Re-key</th>
                <th>Status</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 font-mono">
              {filteredTunnels.map((tunnel) => (
                <tr 
                  key={tunnel.id}
                  className="hover:bg-cyan-500/[0.04] transition-colors cursor-pointer group"
                  onClick={() => onSelectTunnel && onSelectTunnel(tunnel)}
                >
                  {/* ID & Name */}
                  <td>
                    <div className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#10b981]" />
                      <div>
                        <span className="text-slate-100 font-medium block text-xs group-hover:text-cyan-400 transition-colors">
                          {tunnel.name}
                        </span>
                        <span className="text-[10px] text-slate-500">{tunnel.id}</span>
                      </div>
                    </div>
                  </td>

                  {/* Endpoints */}
                  <td>
                    <div className="text-[11px]">
                      <span className="text-slate-200 block">{tunnel.remoteIp}</span>
                      <span className="text-[10px] text-slate-500">{tunnel.localIp}</span>
                    </div>
                  </td>

                  {/* Protocol & Cipher */}
                  <td>
                    <div>
                      <span className="inline-block px-1.5 py-0.5 rounded text-[10px] bg-cyan-500/10 text-cyan-300 border border-cyan-400/20 font-semibold mr-1.5">
                        {tunnel.protocol}
                      </span>
                      <span className="text-slate-400 text-[10px]">{tunnel.cipher}</span>
                    </div>
                  </td>

                  {/* Bandwidth Rate */}
                  <td className="tabular-nums font-semibold text-slate-200">
                    {tunnel.bandwidth}
                  </td>

                  {/* Latency & Jitter */}
                  <td className="tabular-nums">
                    <span className="text-cyan-400 font-semibold">{tunnel.latency}</span>
                    <span className="text-slate-500 text-[10px] block">±{tunnel.jitter}</span>
                  </td>

                  {/* Next Re-key */}
                  <td className="tabular-nums text-slate-400 text-[11px]">
                    {tunnel.rekeyIn}
                  </td>

                  {/* Status Pill */}
                  <td>
                    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium border ${
                      tunnel.status === 'ESTABLISHED'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                    }`}>
                      <span className={`w-1 h-1 rounded-full ${
                        tunnel.status === 'ESTABLISHED' ? 'bg-emerald-400' : 'bg-amber-400 animate-ping'
                      }`} />
                      {tunnel.status}
                    </span>
                  </td>

                  {/* Actions */}
                  <td className="text-right">
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectTunnel && onSelectTunnel(tunnel);
                      }}
                      className="p-1.5 rounded-lg bg-slate-900/60 border border-white/10 text-slate-400 hover:text-cyan-400 hover:border-cyan-400/40 transition-all text-xs"
                      title="Inspect Tunnel SA Details"
                    >
                      <Eye className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

    </div>
  );
};
