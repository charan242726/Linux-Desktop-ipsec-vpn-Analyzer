import React, { useState } from 'react';
import { 
  X, 
  ShieldCheck, 
  Terminal, 
  RefreshCw, 
  Copy, 
  Check,
  Lock,
  CheckCircle2
} from 'lucide-react';

export const TunnelDetailModal = ({ tunnel, onClose }) => {
  const [copiedKey, setCopiedKey] = useState(false);
  const [rekeying, setRekeying] = useState(false);
  // Bug 11 fix: track rekey success toast
  const [rekeySuccess, setRekeySuccess] = useState(false);

  if (!tunnel) return null;

  // Bug 10 fix: copy the actual tunnel's SPI based on its id, not a hardcoded value
  const spiIn  = `0x${tunnel.id.replace('TNL-', '')}C902`;
  const spiOut = `0xF${tunnel.id.replace('TNL-', '')}B93E`;

  const handleCopySpi = () => {
    navigator.clipboard.writeText(`${spiIn} | ${spiOut}`);
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2000);
  };

  const handleTriggerRekey = () => {
    setRekeying(true);
    setTimeout(() => {
      setRekeying(false);
      // Bug 11 fix: show success state after rekey
      setRekeySuccess(true);
      setTimeout(() => setRekeySuccess(false), 3000);
    }, 1800);
  };

  return (
    // Bug 5 fix: clicking backdrop closes modal
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md"
      onClick={onClose}
    >
      {/* Dark Glass Modal Container — stop propagation so clicking inside doesn't close */}
      <div
        className="relative w-full max-w-2xl bg-[#090e1a] border border-cyan-500/25 rounded-2xl shadow-[0_25px_70px_rgba(0,0,0,0.85)] overflow-hidden font-mono text-slate-200"
        onClick={(e) => e.stopPropagation()}
      >
        
        {/* Specular Header Bar */}
        <div className="specular-bar px-5 py-4 flex items-center justify-between border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-400/30 text-cyan-400">
              <Lock className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-white tracking-tight">{tunnel.name}</h3>
                <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  {tunnel.status}
                </span>
              </div>
              <p className="text-[11px] text-slate-400">ID: {tunnel.id} • Gateway SA Telemetry</p>
            </div>
          </div>

          <button 
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-900 border border-white/10 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body Content */}
        <div className="p-5 space-y-5 max-h-[80vh] overflow-y-auto">
          
          {/* Bug 11 fix: Rekey success toast */}
          {rekeySuccess && (
            <div className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-500/15 border border-emerald-400/30 text-emerald-300 text-xs font-mono animate-pulse">
              <CheckCircle2 className="w-4 h-4" />
              IKE SA re-key completed successfully for {tunnel.id}. New SPI pair negotiated.
            </div>
          )}

          {/* Top Quick Status Row */}
          <div className="grid grid-cols-3 gap-3 text-xs">
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
              <span className="text-[10px] text-slate-500 block">REMOTE ENDPOINT</span>
              <span className="text-cyan-400 font-bold">{tunnel.remoteIp}</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
              <span className="text-[10px] text-slate-500 block">LATENCY / JITTER</span>
              <span className="text-slate-100 font-bold">{tunnel.latency} (±{tunnel.jitter})</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
              <span className="text-[10px] text-slate-500 block">THROUGHPUT RATE</span>
              <span className="text-emerald-400 font-bold">{tunnel.bandwidth}</span>
            </div>
          </div>

          {/* IKEv2 Phase 1 & 2 Security Association Details */}
          <div className="mirror-card p-4 space-y-3 bg-slate-900/40 border border-white/10">
            <div className="flex items-center justify-between text-xs font-semibold text-cyan-400 border-b border-white/5 pb-2">
              <span className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4" /> SECURITY ASSOCIATION (SA) ATTRIBUTES
              </span>
              <span className="text-[10px] text-slate-500 font-normal">ESP NAT-Traversal</span>
            </div>

            <div className="grid grid-cols-2 gap-y-2 text-xs text-slate-300">
              <div>
                <span className="text-slate-500 text-[11px] block">Encryption Algorithm</span>
                <span className="text-white font-medium">{tunnel.cipher}</span>
              </div>
              <div>
                <span className="text-slate-500 text-[11px] block">Integrity Auth (HMAC)</span>
                <span className="text-white font-medium">HMAC-SHA2-384</span>
              </div>
              <div>
                <span className="text-slate-500 text-[11px] block">Diffie-Hellman Group</span>
                <span className="text-white font-medium">Curve25519 (Group 19)</span>
              </div>
              <div>
                <span className="text-slate-500 text-[11px] block">Perfect Forward Secrecy</span>
                <span className="text-emerald-400 font-medium">ENABLED (PFS-19)</span>
              </div>
            </div>

            {/* Bug 10 fix: SPI values derived from actual tunnel */}
            <div className="pt-2 border-t border-white/5">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-slate-500">Inbound / Outbound SPI Pair:</span>
                <button 
                  onClick={handleCopySpi}
                  className="flex items-center gap-1 text-cyan-400 hover:underline text-[10px]"
                >
                  {copiedKey ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  {copiedKey ? 'COPIED' : 'COPY SPI'}
                </button>
              </div>
              <div className="mt-1 p-2 rounded bg-black/60 border border-white/10 text-[11px] text-slate-300 font-mono">
                SPI-IN: {spiIn} | SPI-OUT: {spiOut}
              </div>
            </div>
          </div>

          {/* Diagnostic Log Terminal Output */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="flex items-center gap-1.5 font-semibold text-slate-300">
                <Terminal className="w-3.5 h-3.5 text-cyan-400" /> RECENT IKE ENGINE LOGS
              </span>
              <span className="text-[10px] text-slate-500">Live Buffer</span>
            </div>

            <div className="p-3 rounded-xl bg-black/70 border border-white/10 font-mono text-[11px] text-slate-300 space-y-1 max-h-32 overflow-y-auto">
              <div className="text-slate-500">[11:12:04] IKE_SA_INIT request sent to {tunnel.remoteIp}:500</div>
              <div className="text-slate-400">[11:12:05] IKE_SA_INIT response received (DH Group 19 OK)</div>
              <div className="text-slate-300">[11:12:05] Establishing CHILD_SA [{tunnel.id}] ESP mode...</div>
              <div className="text-emerald-400">[11:12:06] CHILD_SA established successfully (AES-256-GCM)</div>
              <div className="text-slate-400">[11:13:10] Heartbeat ACK received (0.4ms response time)</div>
              {rekeySuccess && (
                <div className="text-cyan-400">[{new Date().toLocaleTimeString()}] IKE SA re-key completed. New SPI pair: {spiIn}</div>
              )}
            </div>
          </div>

        </div>

        {/* Modal Footer Controls */}
        <div className="specular-bar px-5 py-3.5 flex items-center justify-between border-t border-white/10">
          <button 
            onClick={handleTriggerRekey}
            disabled={rekeying}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg border transition-all text-xs font-semibold ${
              rekeySuccess
                ? 'bg-emerald-500/15 border-emerald-400/30 text-emerald-300'
                : 'bg-cyan-500/15 border-cyan-400/30 text-cyan-300 hover:bg-cyan-500/25'
            }`}
          >
            {rekeying ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : rekeySuccess ? (
              <CheckCircle2 className="w-3.5 h-3.5" />
            ) : (
              <RefreshCw className="w-3.5 h-3.5" />
            )}
            <span>
              {rekeying ? 'RE-KEYING IN PROGRESS...' : rekeySuccess ? 'RE-KEY SUCCESSFUL' : 'FORCE RE-KEY IKE SA'}
            </span>
          </button>

          <button 
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 border border-white/10 text-slate-200 hover:bg-slate-700 transition-colors text-xs font-medium"
          >
            Close Window
          </button>
        </div>

      </div>

    </div>
  );
};
