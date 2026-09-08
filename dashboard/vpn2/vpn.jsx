import React, { useState, useEffect, useRef } from 'react';
import { FloatingShell } from '../src/components/FloatingShell';
import { SidebarNav } from '../src/components/SidebarNav';
import { HeroMetricsGrid } from '../src/components/HeroMetricsGrid';
import { TelemetryChartsSection } from '../src/components/TelemetryChartsSection';
import { TunnelDataStreamTable } from '../src/components/TunnelDataStreamTable';
import { TunnelDetailModal } from '../src/components/TunnelDetailModal';
import { 
  Terminal, 
  Radio,
  Lock
} from 'lucide-react';

export default function VpnDashboard() {
  const [activeNav, setActiveNav] = useState('dashboard');
  const [isLiveStream, setIsLiveStream] = useState(false);
  const [selectedTunnel, setSelectedTunnel] = useState(null);
  const [lastTickTime, setLastTickTime] = useState(new Date().toLocaleTimeString());

  // Backend state
  const [engineState, setEngineState] = useState('DISCONNECTED');
  const [backendFindings, setBackendFindings] = useState(null);
  const [terminalLogs, setTerminalLogs] = useState([]);
  
  // Metrics State
  const [metrics, setMetrics] = useState({
    activeTunnels: 0,
    totalBandwidth: '0.00',
    avgLatency: '0.0',
    packetLoss: '0.000',
    bandwidthTrend: [
      { v: 0 }, { v: 0 }, { v: 0 }, { v: 0 }, { v: 0 }, { v: 0 }
    ],
    latencyTrend: [
      { v: 0 }, { v: 0 }, { v: 0 }, { v: 0 }, { v: 0 }
    ],
    tunnelTrend: [
      { v: 0 }, { v: 0 }, { v: 0 }, { v: 0 }, { v: 0 }
    ]
  });

  // Telemetry Chart Stream Data State
  const [chartData, setChartData] = useState(
    Array(10).fill(0).map((_, i) => ({
      time: new Date(Date.now() - (9 - i) * 1500).toLocaleTimeString(),
      inbound: 0,
      outbound: 0,
      latency: 0
    }))
  );

  // Poll Backend
  useEffect(() => {
    const fetchBackend = async () => {
      try {
        const res = await fetch('http://localhost:8000/analysis');
        if (res.ok) {
          const data = await res.json();
          setEngineState(data.state);
          
          if (data.state === 'ANALYZING' || data.state === 'VPN_DETECTED') {
            setIsLiveStream(true);
            setMetrics(prev => ({ ...prev, activeTunnels: 1 }));
            
            // Push new findings to logs if they change
            if (data.findings) {
              setBackendFindings(data.findings);
              
              const now = new Date().toLocaleTimeString();
              const newLogs = [];
              
              if (data.findings.ml?.predicted_class) {
                newLogs.push(`[${now}] [ML-ENGINE] Classified flow as: ${data.findings.ml.predicted_class} (${Math.round(data.findings.ml.confidence*100)}% confidence)`);
              }
              
              if (data.findings.security_rules) {
                Object.entries(data.findings.security_rules).forEach(([rule, info]) => {
                  newLogs.push(`[${now}] [SECURITY-ALERT] ${rule}: ${info.message}`);
                });
              }

              if (newLogs.length > 0) {
                setTerminalLogs(prev => {
                  const combined = [...prev, ...newLogs];
                  return combined.slice(-50); // Keep last 50 logs
                });
              }
            }
          } else {
            setIsLiveStream(false);
          }
        }
      } catch (err) {
        setEngineState('OFFLINE');
        setIsLiveStream(false);
      }
    };

    fetchBackend();
    const interval = setInterval(fetchBackend, 2000);
    return () => clearInterval(interval);
  }, []);

  // Live telemetry stream simulator effect (only runs when backend is active)
  useEffect(() => {
    if (!isLiveStream) return;

    const interval = setInterval(() => {
      const now = new Date();
      const timeStr = now.toLocaleTimeString();
      setLastTickTime(timeStr);

      // Generate realistic throughput fluctuations if active
      const newInbound = Math.floor(1200 + Math.random() * 350);
      const newOutbound = Math.floor(850 + Math.random() * 280);
      const newLatency = Number((11.5 + Math.random() * 2.2).toFixed(1));
      const newBwTotal = ((newInbound + newOutbound) / 1000).toFixed(2);

      // Append chart point
      setChartData((prev) => {
        const next = [...prev.slice(1), {
          time: timeStr,
          inbound: newInbound,
          outbound: newOutbound,
          latency: newLatency
        }];
        return next;
      });

      // Update summary metrics
      setMetrics((prev) => ({
        ...prev,
        totalBandwidth: newBwTotal,
        avgLatency: newLatency.toString(),
        bandwidthTrend: [...prev.bandwidthTrend.slice(1), { v: Number(newBwTotal) }],
        latencyTrend: [...prev.latencyTrend.slice(1), { v: newLatency }]
      }));
      
    }, 1500);

    return () => clearInterval(interval);
  }, [isLiveStream]);

  const ike = backendFindings?.ike || {};

  return (
    <FloatingShell
      isLiveStream={isLiveStream}
      setIsLiveStream={setIsLiveStream}
      activeNav={activeNav}
      setActiveNav={setActiveNav}
      lastTickTime={lastTickTime}
      activeTunnelCount={metrics.activeTunnels}
      totalBandwidth={metrics.totalBandwidth}
    >
      {/* Sidebar Navigation */}
      <SidebarNav activeNav={activeNav} setActiveNav={setActiveNav} />

      {/* Main Dashboard Content Area */}
      <main className="flex-1 p-4 sm:p-5 md:p-6 overflow-y-auto max-h-[calc(100vh-140px)]">
        
        {/* Render View Based on Nav */}
        {activeNav === 'dashboard' && (
          <div>
            <div className="mb-4 flex items-center justify-between p-4 rounded-xl border border-white/10 bg-black/40">
              <div>
                <h2 className="text-sm font-bold font-mono text-white">SYSTEM STATUS</h2>
                <p className="text-xs font-mono text-slate-400">Backend API Connection</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-mono border ${
                engineState === 'ANALYZING' ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400/30' :
                engineState === 'OFFLINE' ? 'bg-red-500/20 text-red-300 border-red-400/30' :
                'bg-yellow-500/20 text-yellow-300 border-yellow-400/30'
              }`}>
                {engineState}
              </span>
            </div>

            <HeroMetricsGrid metricsData={metrics} />
            <TelemetryChartsSection chartData={chartData} />
            <TunnelDataStreamTable onSelectTunnel={(t) => setSelectedTunnel(t)} />
          </div>
        )}

        {activeNav === 'tunnels' && (
          <div className="space-y-4">
            <div className="mirror-card p-4 border border-white/10 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-bold font-mono text-white">ALL ESTABLISHED IPSEC TUNNELS</h2>
                <p className="text-xs font-mono text-slate-400">ESP Security Associations & Endpoint Matrix</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-400/30">
                {metrics.activeTunnels} Active Tunnels
              </span>
            </div>
            <TunnelDataStreamTable onSelectTunnel={(t) => setSelectedTunnel(t)} />
          </div>
        )}

        {activeNav === 'bandwidth' && (
          <div className="space-y-4">
            <HeroMetricsGrid metricsData={metrics} />
            <TelemetryChartsSection chartData={chartData} />
          </div>
        )}

        {activeNav === 'nodes' && (
          <div className="space-y-4">
            <div className="mirror-card p-5 border border-white/10">
              <h2 className="text-sm font-bold font-mono text-white mb-2">GLOBAL EDGE GATEWAY NODES</h2>
              <p className="text-xs font-mono text-slate-400 mb-4">Direct IPsec Tunnel Latency Matrix</p>
              <TelemetryChartsSection chartData={chartData} />
            </div>
          </div>
        )}

        {activeNav === 'security' && (
          <div className="mirror-card p-5 border border-white/10 font-mono space-y-4">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Lock className="w-4 h-4 text-cyan-400" /> SECURITY POLICY & IKE PARAMETERS
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-2">
                <span className="text-cyan-400 font-bold block">PHASE 1 (IKE_SA) POLICY</span>
                <div className="text-slate-300">Exchange Type: {ike.exchange_type || "Awaiting Packets..."}</div>
                <div className="text-slate-300">Initiator SPI: {ike.init_spi || "—"}</div>
                <div className="text-slate-300">Responder SPI: {ike.resp_spi || "—"}</div>
                <div className="text-slate-300">Message ID: {ike.message_id !== undefined ? ike.message_id : "—"}</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-2">
                <span className="text-cyan-400 font-bold block">PHASE 2 (CHILD_SA) & ML</span>
                <div className="text-slate-300">Encapsulation: ESP (IP Protocol 50)</div>
                {backendFindings?.ml ? (
                  <>
                    <div className="text-emerald-400 mt-2 font-bold">ML INFERENCE RESULTS:</div>
                    <div className="text-slate-300">Predicted Traffic: {backendFindings.ml.predicted_class}</div>
                    <div className="text-slate-300">Confidence: {Math.round(backendFindings.ml.confidence * 100)}%</div>
                  </>
                ) : (
                  <div className="text-slate-500">Awaiting ML Inference Data...</div>
                )}
              </div>
            </div>
            
            {backendFindings?.security_rules && Object.keys(backendFindings.security_rules).length > 0 && (
              <div className="mt-4 p-4 rounded-xl bg-red-900/20 border border-red-500/20 space-y-2">
                 <span className="text-red-400 font-bold block">ACTIVE SECURITY ALERTS</span>
                 {Object.entries(backendFindings.security_rules).map(([rule, info]) => (
                   <div key={rule} className="text-red-300">- {rule}: {info.message}</div>
                 ))}
              </div>
            )}

          </div>
        )}

        {activeNav === 'logs' && (
          <div className="mirror-card p-5 border border-white/10 font-mono space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-white/5">
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Terminal className="w-4 h-4 text-cyan-400" /> DIAGNOSTIC TELEMETRY LOG STREAM
              </h2>
              <span className={`text-xs flex items-center gap-1 ${isLiveStream ? 'text-emerald-400' : 'text-slate-500'}`}>
                <Radio className={`w-3 h-3 ${isLiveStream ? 'animate-pulse' : ''}`} /> 
                {isLiveStream ? 'LIVE STREAMING' : 'STREAM PAUSED'}
              </span>
            </div>

            <div className="p-4 rounded-xl bg-black/80 border border-white/10 text-xs text-slate-300 space-y-2 font-mono max-h-96 overflow-y-auto flex flex-col-reverse">
              {terminalLogs.length > 0 ? (
                [...terminalLogs].reverse().map((log, i) => (
                  <div key={i} className={log.includes('SECURITY') ? 'text-red-400' : log.includes('ML-ENGINE') ? 'text-cyan-300' : ''}>
                    {log}
                  </div>
                ))
              ) : (
                <div className="text-slate-500 italic">Waiting for analysis engine output...</div>
              )}
            </div>
          </div>
        )}

      </main>

      {/* Detail Modal Popup */}
      {selectedTunnel && (
        <TunnelDetailModal
          tunnel={selectedTunnel}
          onClose={() => setSelectedTunnel(null)}
        />
      )}

    </FloatingShell>
  );
}
