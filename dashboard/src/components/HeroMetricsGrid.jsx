import React from 'react';
import { 
  Network, 
  ArrowUpRight, 
  Activity, 
  Clock, 
  ShieldCheck, 
  TrendingUp,
  Radio
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area } from 'recharts';

export const HeroMetricsGrid = ({ metricsData }) => {
  const {
    activeTunnels = 24,
    totalBandwidth = '1.84',
    avgLatency = '12.4',
    packetLoss = '0.002',
    bandwidthTrend = [],
    latencyTrend = [],
    tunnelTrend = []
  } = metricsData || {};

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 mb-5">
      
      {/* Metric Card 1: Active IPsec Tunnels */}
      <div className="mirror-card p-4 flex flex-col justify-between relative group">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-mono font-semibold tracking-wider text-slate-400 uppercase flex items-center gap-1.5">
              <Network className="w-3.5 h-3.5 text-cyan-400" /> ACTIVE TUNNELS
            </span>
            <div className="flex items-baseline gap-2 pt-1">
              <span className="text-2xl font-bold font-mono text-white tabular-nums tracking-tight">
                {activeTunnels}
              </span>
              <span className="text-xs font-mono text-slate-400">/ 24 Established</span>
            </div>
          </div>

          <div className="px-2 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-mono flex items-center gap-1">
            <ArrowUpRight className="w-3 h-3" /> 100% ONLINE
          </div>
        </div>

        {/* Integrated Micro Sparkline - Cyan */}
        <div className="h-10 w-full mt-3 pt-1">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={tunnelTrend.length ? tunnelTrend : [
              { v: 22 }, { v: 24 }, { v: 23 }, { v: 24 }, { v: 24 }, { v: 24 }
            ]}>
              <defs>
                <linearGradient id="gradCyan" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00d2ff" stopOpacity={0.45} />
                  <stop offset="100%" stopColor="#00d2ff" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <Area type="monotone" dataKey="v" stroke="#00d2ff" strokeWidth={2} fill="url(#gradCyan)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-2 border-t border-white/5">
          <span>ESP Encryption: AES-256-GCM</span>
          <span className="text-cyan-400">0 Failures</span>
        </div>
      </div>

      {/* Metric Card 2: Aggregate Bandwidth Throughput */}
      <div className="mirror-card p-4 flex flex-col justify-between relative group">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-mono font-semibold tracking-wider text-slate-400 uppercase flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-blue-400" /> TOTAL THROUGHPUT
            </span>
            <div className="flex items-baseline gap-1.5 pt-1">
              <span className="text-2xl font-bold font-mono text-white tabular-nums tracking-tight">
                {totalBandwidth}
              </span>
              <span className="text-xs font-mono text-slate-400">Gbps</span>
            </div>
          </div>

          <div className="px-2 py-1 rounded-md bg-blue-500/15 border border-blue-400/30 text-blue-300 text-[10px] font-mono flex items-center gap-1">
            <TrendingUp className="w-3 h-3" /> +14.2% Peak
          </div>
        </div>

        {/* Integrated Micro Sparkline - Electric Blue */}
        <div className="h-10 w-full mt-3 pt-1">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={bandwidthTrend.length ? bandwidthTrend : [
              { v: 1.2 }, { v: 1.5 }, { v: 1.4 }, { v: 1.7 }, { v: 1.84 }
            ]}>
              <defs>
                <linearGradient id="gradBlue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#0066ff" stopOpacity={0.45} />
                  <stop offset="100%" stopColor="#0066ff" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <Area type="monotone" dataKey="v" stroke="#0066ff" strokeWidth={2} fill="url(#gradBlue)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-2 border-t border-white/5">
          <span>In: 1.12 Gbps</span>
          <span>Out: 0.72 Gbps</span>
        </div>
      </div>

      {/* Metric Card 3: Mean Tunnel Latency */}
      <div className="mirror-card p-4 flex flex-col justify-between relative group">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-mono font-semibold tracking-wider text-slate-400 uppercase flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-indigo-400" /> MEAN LATENCY
            </span>
            <div className="flex items-baseline gap-1.5 pt-1">
              <span className="text-2xl font-bold font-mono text-white tabular-nums tracking-tight">
                {avgLatency}
              </span>
              <span className="text-xs font-mono text-slate-400">ms</span>
            </div>
          </div>

          <div className="px-2 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-mono flex items-center gap-1">
            <Radio className="w-3 h-3 text-emerald-400 animate-pulse" /> ULTRA LOW
          </div>
        </div>

        {/* Integrated Micro Sparkline - Indigo */}
        <div className="h-10 w-full mt-3 pt-1">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={latencyTrend.length ? latencyTrend : [
              { v: 14.1 }, { v: 13.2 }, { v: 12.8 }, { v: 12.5 }, { v: 12.4 }
            ]}>
              <defs>
                <linearGradient id="gradIndigo" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#6366f1" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="#6366f1" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <Area type="monotone" dataKey="v" stroke="#6366f1" strokeWidth={2} fill="url(#gradIndigo)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-2 border-t border-white/5">
          <span>Jitter: 0.42 ms</span>
          <span>Gateway Ping: 8ms</span>
        </div>
      </div>

      {/* Metric Card 4: Packet Integrity Rate */}
      <div className="mirror-card p-4 flex flex-col justify-between relative group">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-mono font-semibold tracking-wider text-slate-400 uppercase flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> PACKET INTEGRITY
            </span>
            <div className="flex items-baseline gap-1.5 pt-1">
              <span className="text-2xl font-bold font-mono text-white tabular-nums tracking-tight">
                99.998
              </span>
              <span className="text-xs font-mono text-slate-400">%</span>
            </div>
          </div>

          <div className="px-2 py-1 rounded-md bg-slate-800 border border-white/10 text-slate-300 text-[10px] font-mono">
            LOSS: {packetLoss}%
          </div>
        </div>

        {/* Integrated Metric Pulse Gauge */}
        <div className="space-y-1.5 my-3 pt-2">
          <div className="flex justify-between text-[10px] font-mono text-slate-400">
            <span>Buffer Checksums Passed</span>
            <span className="text-emerald-400">48.2M/48.2M</span>
          </div>
          <div className="w-full bg-slate-900 h-2 rounded-full p-0.5 border border-white/10 overflow-hidden">
            <div className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full w-[99.9%]" />
          </div>
        </div>

        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-2 border-t border-white/5">
          <span>Drop Count: 14 pkts</span>
          <span className="text-emerald-400">PFS Group 19</span>
        </div>
      </div>

    </div>
  );
};
