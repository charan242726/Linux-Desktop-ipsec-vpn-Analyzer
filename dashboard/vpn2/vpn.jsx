import React, { useState, useEffect, useRef } from 'react';
import { FloatingShell } from '../src/components/FloatingShell';
import { SidebarNav } from '../src/components/SidebarNav';
import { HeroMetricsGrid } from '../src/components/HeroMetricsGrid';
import { TelemetryChartsSection } from '../src/components/TelemetryChartsSection';
import { TunnelDataStreamTable } from '../src/components/TunnelDataStreamTable';
import { TunnelDetailModal } from '../src/components/TunnelDetailModal';
import { ReportHistory } from '../src/components/ReportHistory';
import { 
  Terminal, 
  Radio,
  Lock
} from 'lucide-react';

const API = 'http://localhost:8000';

export default function VpnDashboard() {
  const [activeNav, setActiveNav] = useState('dashboard');
  const [isLiveStream, setIsLiveStream] = useState(false);
  const [selectedTunnel, setSelectedTunnel] = useState(null);

  // Clock — always ticks every second regardless of backend state
  const [lastTickTime, setLastTickTime] = useState(new Date().toLocaleTimeString());
  useEffect(() => {
    const id = setInterval(() => setLastTickTime(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(id);
  }, []);

  const [engineState, setEngineState] = useState('DISCONNECTED');
  const prevStateRef = useRef('DISCONNECTED');
  const notifiedRulesRef = useRef(new Set());
  const [backendFindings, setBackendFindings] = useState(null);
  const [terminalLogs, setTerminalLogs] = useState([]);

  // ── Live bandwidth from backend ───────────────────────────────────────────
  const [bandwidth, setBandwidth] = useState({
    inbound_mbps: 0, outbound_mbps: 0,
    total_packets: 0, latency_ms: 0,
  });

  // ── Active sessions (peer IP table) ──────────────────────────────────────
  const [sessions, setSessions] = useState([]);
  const [tunnelCount, setTunnelCount] = useState(0);

  // ── System stats (CPU/Memory from psutil) ────────────────────────────────
  const [systemStats, setSystemStats] = useState({
    cpu_percent: 0, memory_percent: 0,
    memory_used_gb: 0, memory_total_gb: 0, aes_ni: true,
  });

  // ── Chart stream ──────────────────────────────────────────────────────────
  const [chartData, setChartData] = useState(
    Array(10).fill(0).map((_, i) => ({
      time: new Date(Date.now() - (9 - i) * 1500).toLocaleTimeString(),
      inbound: 0,
      outbound: 0,
      latency: 0,
    }))
  );

  // ── Poll /analysis every 2s ───────────────────────────────────────────────
  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const res = await fetch(`${API}/analysis`);
        if (res.ok) {
          const data = await res.json();
          const state = typeof data.state === 'string' ? data.state : data.state?.value ?? 'UNKNOWN';
          
          // Trigger OS Notification when state transitions to VPN_DETECTED
          if (state === 'VPN_DETECTED' && prevStateRef.current !== 'VPN_DETECTED') {
            if (window.electronAPI) {
              if (window.electronAPI.wakeUp) window.electronAPI.wakeUp();
              window.electronAPI.sendNotification({
                title: 'VPN Connection Detected',
                body: 'IPsec VPN traffic detected. Click here to open the Analyzer and start inspection.',
                urgency: 'normal'
              });
            }
          }
          
          // Only auto-update the stream toggle if the backend state transitioned
          if (state !== prevStateRef.current) {
            setIsLiveStream(state === 'ANALYZING' || state === 'VPN_DETECTED');
          }
          
          prevStateRef.current = state;
          setEngineState(state);

          // Bandwidth
          if (data.bandwidth) {
            setBandwidth(data.bandwidth);
            // Push to chart
            const now = new Date().toLocaleTimeString();
            setChartData(prev => [...prev.slice(1), {
              time: now,
              inbound: Math.round((data.bandwidth.inbound_mbps || 0) * 1000),  // Kbps
              outbound: Math.round((data.bandwidth.outbound_mbps || 0) * 1000),
              latency: data.bandwidth.latency_ms || 0,
            }]);
          }

          // Sessions / tunnels
          if (Array.isArray(data.sessions)) {
            setSessions(data.sessions);
            setTunnelCount(data.tunnel_count ?? data.sessions.length);
          }

          // Findings → logs
          if (data.findings) {
            setBackendFindings(data.findings);
            const now = new Date().toLocaleTimeString();
            const newLogs = [];
            if (data.findings.ml?.predicted_class) {
              newLogs.push(`[${now}] [ML-ENGINE] Classified flow as: ${data.findings.ml.predicted_class} (${Math.round(data.findings.ml.confidence * 100)}% confidence)`);
            }
            if (data.findings.security_rules) {
              Object.entries(data.findings.security_rules).forEach(([rule, info]) => {
                newLogs.push(`[${now}] [SECURITY-ALERT] ${rule}: ${info.message}`);
                
                if (!notifiedRulesRef.current.has(rule)) {
                  notifiedRulesRef.current.add(rule);
                  if (window.electronAPI) {
                    window.electronAPI.sendNotification({
                      title: 'Security Vulnerability Detected',
                      body: `Flaw: ${rule} - ${info.message}`,
                      urgency: 'critical'
                    });
                  }
                }
              });
            }
            if (data.findings.ike?.ike_version && data.findings.ike.ike_version !== 'unknown') {
              newLogs.push(`[${now}] [IKE] Version: ${data.findings.ike.ike_version} | Cipher: ${data.findings.ike.encryption_algorithm}`);
            }
            if (newLogs.length > 0) {
              setTerminalLogs(prev => [...prev, ...newLogs].slice(-50));
            }
          }
        } else if (res.status === 404) {
          setEngineState('IDLE');
          setIsLiveStream(false);
        }
      } catch {
        setEngineState('OFFLINE');
        setIsLiveStream(false);
      }
    };

    fetchAnalysis();
    const id = setInterval(fetchAnalysis, 2000);
    return () => clearInterval(id);
  }, []);

  // ── Poll /system/stats every 3s ───────────────────────────────────────────
  useEffect(() => {
    const fetchSystem = async () => {
      try {
        const res = await fetch(`${API}/system/stats`);
        if (res.ok) {
          const data = await res.json();
          setSystemStats(data);
        }
      } catch {
        // backend offline — keep previous values
      }
    };

    fetchSystem();
    const id = setInterval(fetchSystem, 3000);
    return () => clearInterval(id);
  }, []);

  // ── Derived metrics for HeroMetricsGrid ──────────────────────────────────
  const totalBandwidthGbps = ((bandwidth.inbound_mbps + bandwidth.outbound_mbps) / 1000).toFixed(3);

  const ike = backendFindings?.ike || {};

  const handleStartAnalysis = async () => {
    try {
      await fetch(`${API}/analysis/start`, { method: 'POST' });
    } catch (e) {
      console.error("Failed to start analysis:", e);
    }
  };

  return (
    <FloatingShell
      isLiveStream={isLiveStream}
      setIsLiveStream={setIsLiveStream}
      activeNav={activeNav}
      setActiveNav={setActiveNav}
      lastTickTime={lastTickTime}
      activeTunnelCount={tunnelCount}
      totalBandwidth={totalBandwidthGbps}
    >
      {/* Sidebar Navigation */}
      <SidebarNav
        activeNav={activeNav}
        setActiveNav={setActiveNav}
        systemStats={systemStats}
      />

      {/* Main Dashboard Content Area */}
      <main className="flex-1 p-4 sm:p-5 md:p-6 overflow-y-auto max-h-[calc(100vh-140px)]">
        
        {/* Render View Based on Nav */}
        {activeNav === 'reports' && (
          <ReportHistory />
        )}
        
        {activeNav === 'dashboard' && (
          <div>
            <div className="mb-4 flex items-center justify-between p-4 rounded-xl border border-white/10 bg-black/40">
              <div>
                <h2 className="text-sm font-bold font-mono text-white">SYSTEM STATUS</h2>
                <p className="text-xs font-mono text-slate-400">Backend API Connection</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-mono border ${
                engineState === 'ANALYZING' || engineState === 'VPN_DETECTED'
                  ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400/30' :
                engineState === 'OFFLINE'
                  ? 'bg-red-500/20 text-red-300 border-red-400/30' :
                engineState === 'DISCONNECTED'
                  ? 'bg-slate-700/50 text-slate-400 border-slate-600/40' :
                engineState === 'IDLE'
                  ? 'bg-yellow-500/20 text-yellow-300 border-yellow-400/30' :
                  'bg-slate-700/50 text-slate-400 border-slate-600/40'
              }`}>
                {engineState === 'DISCONNECTED' ? 'CONNECTING...' : engineState}
              </span>
            </div>

            {engineState === 'VPN_DETECTED' && (
              <div className="mb-4 p-5 rounded-xl border border-cyan-500/50 bg-cyan-900/20 flex flex-col sm:flex-row items-center justify-between gap-4 animate-pulse-slow">
                <div>
                  <h3 className="text-sm font-bold font-mono text-cyan-300">VPN CONNECTION DETECTED</h3>
                  <p className="text-xs font-mono text-cyan-400/80 mt-1">
                    IPsec traffic detected on the network. Start the ML analysis engine to inspect flows and evaluate security.
                  </p>
                </div>
                <button 
                  onClick={handleStartAnalysis}
                  className="whitespace-nowrap px-6 py-2.5 rounded-lg bg-cyan-500 text-slate-900 font-bold font-mono text-sm hover:bg-cyan-400 transition-colors shadow-[0_0_20px_rgba(0,210,255,0.4)]"
                >
                  START ANALYSIS
                </button>
              </div>
            )}

            <HeroMetricsGrid
              activeTunnels={tunnelCount}
              totalBandwidthGbps={totalBandwidthGbps}
              latencyMs={bandwidth.latency_ms}
              totalPackets={bandwidth.total_packets}
              inboundMbps={bandwidth.inbound_mbps}
              outboundMbps={bandwidth.outbound_mbps}
            />
            <TelemetryChartsSection
              chartData={chartData}
              isLiveStream={isLiveStream}
              ikeFindings={backendFindings?.ike}
            />
            <TunnelDataStreamTable
              tunnelsList={sessions}
              onSelectTunnel={(t) => setSelectedTunnel(t)}
            />
          </div>
        )}

        {activeNav === 'tunnels' && (
          <div className="space-y-4">
            <div className="mirror-card p-4 border border-white/10 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-bold font-mono text-white">ALL ACTIVE IPSEC SESSIONS</h2>
                <p className="text-xs font-mono text-slate-400">ESP Security Associations & Endpoint Matrix</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-400/30">
                {tunnelCount} Active Sessions
              </span>
            </div>
            <TunnelDataStreamTable
              tunnelsList={sessions}
              onSelectTunnel={(t) => setSelectedTunnel(t)}
            />
          </div>
        )}

        {activeNav === 'bandwidth' && (
          <div className="space-y-4">
            <HeroMetricsGrid
              activeTunnels={tunnelCount}
              totalBandwidthGbps={totalBandwidthGbps}
              latencyMs={bandwidth.latency_ms}
              totalPackets={bandwidth.total_packets}
              inboundMbps={bandwidth.inbound_mbps}
              outboundMbps={bandwidth.outbound_mbps}
            />
            <TelemetryChartsSection
              chartData={chartData}
              isLiveStream={isLiveStream}
              ikeFindings={backendFindings?.ike}
            />
          </div>
        )}

        {activeNav === 'nodes' && (
          <div className="space-y-4">
            <div className="mirror-card p-5 border border-white/10">
              <h2 className="text-sm font-bold font-mono text-white mb-2">DETECTED PEER NODES</h2>
              <p className="text-xs font-mono text-slate-400 mb-4">Active Remote Endpoints from ESP Sessions</p>
              <TelemetryChartsSection
                chartData={chartData}
                isLiveStream={isLiveStream}
                ikeFindings={backendFindings?.ike}
                edgeNodes={sessions.map(s => ({
                  name: s.remote_ip,
                  region: 'Detected Peer',
                  ping: s.latency,
                  status: s.status,
                  tunnels: 1,
                }))}
              />
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
                <div className="text-slate-300">Version: {ike.ike_version || '—'}</div>
                <div className="text-slate-300">Exchange Type: {ike.mode || 'Awaiting Packets...'}</div>
                <div className="text-slate-300">DH Group: {ike.dh_group ? `Group ${ike.dh_group}` : '—'}</div>
                <div className="text-slate-300">PFS: {ike.pfs_enabled ? '✅ Enabled' : ike.pfs_enabled === false ? '❌ Disabled' : '—'}</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-2">
                <span className="text-cyan-400 font-bold block">PHASE 2 (CHILD_SA) & ML</span>
                <div className="text-slate-300">Encryption: {ike.encryption_algorithm || '—'}</div>
                <div className="text-slate-300">Auth: {ike.auth_algorithm || '—'}</div>
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
                terminalLogs.map((log, i) => (
                  <div key={i} className={
                    log.includes('SECURITY') ? 'text-red-400' :
                    log.includes('ML-ENGINE') ? 'text-cyan-300' :
                    log.includes('IKE') ? 'text-blue-300' : ''
                  }>
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
