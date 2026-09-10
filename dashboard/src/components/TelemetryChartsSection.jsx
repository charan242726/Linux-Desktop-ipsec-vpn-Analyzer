import React from 'react';
import { 
  Activity, 
  Layers, 
  Globe, 
  Download,
  PauseCircle
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';

export const TelemetryChartsSection = ({ chartData, edgeNodes, isLiveStream, ikeFindings }) => {

  const defaultChartData = [
    { time: '11:00:00', inbound: 0, outbound: 0, latency: 0 },
    { time: '11:00:05', inbound: 0, outbound: 0, latency: 0 },
  ];

  const dataToUse = chartData && chartData.length > 0 ? chartData : defaultChartData;

  // Bug 7 fix: compute live inbound/outbound from latest chart data point
  const latest = dataToUse[dataToUse.length - 1] || {};
  const liveInbound  = latest.inbound  ? (latest.inbound  / 1000).toFixed(2) : '0.00';
  const liveOutbound = latest.outbound ? (latest.outbound / 1000).toFixed(2) : '0.00';

  // Build cipherData from actual IKE findings
  const cipherData = ikeFindings && ikeFindings.encryption_algorithm && ikeFindings.encryption_algorithm !== "unknown"
    ? [{ name: ikeFindings.encryption_algorithm, throughput: latest.inbound || 0, tunnels: 1, color: '#00d2ff' }]
    : [];

  const nodesToUse = edgeNodes && edgeNodes.length > 0 ? edgeNodes : [];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-5">
      
      {/* Chart Card 1: Primary Throughput Telemetry Stream */}
      <div className="mirror-card p-4 lg:col-span-2 flex flex-col justify-between">
        
        {/* Card Header Controls */}
        <div className="flex flex-wrap items-center justify-between gap-3 pb-3 mb-2 border-b border-white/5">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-400/30 text-cyan-400">
              <Activity className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-xs font-semibold font-mono text-white tracking-tight">
                REAL-TIME THROUGHPUT STREAM (Mbps)
              </h3>
              <p className="text-[10px] font-mono text-slate-400">
                ESP Packet Encapsulation Stream • ESP SPI-0x84A1
              </p>
            </div>
          </div>

          {/* Controls: Download & LIVE indicator */}
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-md bg-cyan-500/10 border border-cyan-400/30 text-cyan-300 text-[10px] font-mono">
              LIVE
            </span>
            <button className="p-1.5 rounded-lg bg-slate-900/60 border border-white/10 text-slate-400 hover:text-white text-xs">
              <Download className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Bug 8 fix: Show paused overlay when stream is not live */}
        <div className="relative h-64 w-full pt-2">
          {isLiveStream === false && (
            <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-black/50 rounded-xl backdrop-blur-sm gap-2">
              <PauseCircle className="w-8 h-8 text-slate-400" />
              <span className="text-xs font-mono text-slate-400">STREAM PAUSED — Click LIVE STREAMING to resume</span>
            </div>
          )}
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={dataToUse} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorInboundBlue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00d2ff" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="#00d2ff" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="colorOutboundBlue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#0066ff" stopOpacity={0.45} />
                  <stop offset="100%" stopColor="#0066ff" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" />
              <XAxis 
                dataKey="time" 
                stroke="#64748b" 
                fontSize={10} 
                fontFamily="JetBrains Mono" 
                tickLine={false} 
              />
              <YAxis 
                stroke="#64748b" 
                fontSize={10} 
                fontFamily="JetBrains Mono" 
                tickLine={false} 
                axisLine={false} 
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#090e1a', 
                  borderColor: 'rgba(0,210,255,0.3)', 
                  borderRadius: '8px', 
                  fontSize: '11px',
                  fontFamily: 'JetBrains Mono',
                  color: '#fff',
                  boxShadow: '0 10px 25px rgba(0,0,0,0.8)'
                }} 
              />
              <Area 
                type="monotone" 
                dataKey="inbound" 
                name="Inbound ESP"
                stroke="#00d2ff" 
                strokeWidth={2.5} 
                fillOpacity={1} 
                fill="url(#colorInboundBlue)" 
              />
              <Area 
                type="monotone" 
                dataKey="outbound" 
                name="Outbound ESP"
                stroke="#0066ff" 
                strokeWidth={2.5} 
                fillOpacity={1} 
                fill="url(#colorOutboundBlue)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Bug 7 fix: Footer values now derived from live chart data */}
        <div className="flex flex-wrap items-center justify-between text-[11px] font-mono text-slate-400 pt-3 border-t border-white/5 gap-2">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-[0_0_8px_#00d2ff]" />
              Inbound: <strong className="text-slate-100">{liveInbound} Gbps</strong>
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-600 shadow-[0_0_8px_#0066ff]" />
              Outbound: <strong className="text-slate-100">{liveOutbound} Gbps</strong>
            </span>
          </div>

          <div className="text-slate-500">
            Sampling: <span className="text-cyan-400">1000ms UDP-Heartbeat</span>
          </div>
        </div>

      </div>

      {/* Card 2: Cipher Suite Breakdown & Global Gateways */}
      <div className="mirror-card p-4 flex flex-col justify-between space-y-4">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-white/5">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-blue-500/10 border border-blue-400/20 text-blue-400">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-xs font-semibold font-mono text-white tracking-tight">
                CIPHER SUITES & GATEWAYS
              </h3>
              <p className="text-[10px] font-mono text-slate-400">PFS Group 19 / DH-19 Allocation</p>
            </div>
          </div>
        </div>

        {/* Cipher Breakdown Bar List */}
        <div className="space-y-3">
          {cipherData.length > 0 ? (
            cipherData.map((cipher) => (
              <div key={cipher.name} className="space-y-1">
                <div className="flex justify-between text-[11px] font-mono">
                  <span className="text-slate-200">{cipher.name}</span>
                  <span className="text-slate-400">{cipher.tunnels} Tunnels</span>
                </div>
                <div className="w-full bg-slate-900/80 h-2 rounded-full overflow-hidden p-0.5 border border-white/10">
                  <div 
                    className="h-full rounded-full transition-all duration-500"
                    style={{ 
                      width: `${Math.min((cipher.throughput / 1500) * 100, 100)}%`,
                      backgroundColor: cipher.color,
                      boxShadow: `0 0 10px ${cipher.color}80`
                    }} 
                  />
                </div>
              </div>
            ))
          ) : (
            <div className="text-[10px] font-mono text-slate-500 italic text-center py-4 border border-dashed border-white/10 rounded-lg">
              Awaiting Cryptographic Telemetry...
            </div>
          )}
        </div>

        {/* Global Edge Gateways Grid */}
        <div className="pt-3 border-t border-white/5 space-y-2">
          <span className="text-[10px] font-mono font-semibold tracking-wider text-slate-400 uppercase block mb-1">
            EDGE NODE LATENCY MATRIX
          </span>

          <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
            {nodesToUse.length > 0 ? (
              nodesToUse.map((node) => (
                <div 
                  key={node.name}
                  className="flex items-center justify-between p-2 rounded-lg bg-slate-900/40 border border-white/5 hover:border-cyan-500/20 transition-all text-xs font-mono"
                >
                  <div className="flex items-center gap-2">
                    <span className="pulse-beacon pulse-beacon-emerald" />
                    <div>
                      <span className="text-slate-200 font-medium block text-[11px]">{node.name}</span>
                      <span className="text-[9px] text-slate-500">{node.region}</span>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="text-cyan-400 font-bold text-[11px] block">{node.ping}</span>
                    <span className="text-[9px] text-slate-500">{node.tunnels} Tunnels</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-[10px] font-mono text-slate-500 italic text-center py-4 border border-dashed border-white/10 rounded-lg">
                No active edge nodes detected
              </div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
};
