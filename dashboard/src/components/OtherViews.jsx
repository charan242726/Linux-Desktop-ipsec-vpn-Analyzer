import { Upload, Radio, Binary, FileText, Settings, Shield, Activity, Save, HardDrive } from 'lucide-react';

export function PcapView() {
  return (
    <div className="dashboard-view">
      <div className="hero-section" style={{marginBottom: '24px'}}>
        <h2 className="hero-title" style={{fontSize: '2rem'}}>PCAP <span className="highlight-cyan">Analysis</span></h2>
        <p className="hero-subtitle">Upload packet captures for deep forensic analysis.</p>
      </div>
      <div className="action-card" style={{padding: '48px', textAlign: 'center', border: '1px dashed var(--accent-cyan-dim)'}}>
        <Upload size={48} style={{color: 'var(--accent-cyan)', margin: '0 auto 24px auto', opacity: 0.8}} />
        <h3 style={{fontSize: '1.2rem', marginBottom: '8px', color: 'var(--text-primary)'}}>Drag & Drop Capture Files</h3>
        <p style={{color: 'var(--text-muted)', marginBottom: '24px'}}>Supports .pcap, .pcapng up to 500MB.</p>
        <button className="btn-primary" style={{margin: '0 auto'}}>Select Files</button>
      </div>
    </div>
  );
}

export function LiveCaptureView() {
  return (
    <div className="dashboard-view">
      <div className="hero-section" style={{marginBottom: '24px'}}>
        <h2 className="hero-title" style={{fontSize: '2rem'}}>Live <span className="highlight-cyan">Capture</span></h2>
        <p className="hero-subtitle">Monitor physical and virtual interfaces in real-time.</p>
      </div>
      <div className="architecture-grid" style={{gridTemplateColumns: '1fr 1fr'}}>
        <div className="arch-card">
          <div className="card-header">
             <div className="card-icon"><Radio size={20} /></div>
             <h3>Select Interface</h3>
          </div>
          <div className="card-content">
             <div style={{padding: '16px', background: 'var(--bg-app)', borderRadius: '8px', marginBottom: '12px', border: '1px solid var(--accent-cyan)'}}>
                <strong>eth0</strong> <span style={{float: 'right', color: 'var(--accent-green)'}}>● Active (1 Gbps)</span>
             </div>
             <div style={{padding: '16px', background: 'var(--bg-app)', borderRadius: '8px', marginBottom: '12px', opacity: 0.5}}>
                <strong>wlan0</strong> <span style={{float: 'right'}}>Disconnected</span>
             </div>
             <div style={{padding: '16px', background: 'var(--bg-app)', borderRadius: '8px', opacity: 0.5}}>
                <strong>lo</strong> <span style={{float: 'right'}}>Loopback</span>
             </div>
          </div>
        </div>
        <div className="arch-card">
          <div className="card-header">
             <div className="card-icon"><Activity size={20} /></div>
             <h3>Capture Filters</h3>
          </div>
          <div className="card-content">
             <input type="text" placeholder="e.g. udp port 500 or udp port 4500" style={{width: '100%', padding: '12px', background: 'var(--bg-app)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'var(--text-primary)', marginBottom: '16px'}} />
             <label style={{display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', marginBottom: '8px'}}>
                <input type="checkbox" defaultChecked /> IPsec Traffic Only (IKE/ESP)
             </label>
             <label style={{display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)'}}>
                <input type="checkbox" defaultChecked /> Enable ML Inference
             </label>
          </div>
        </div>
      </div>
    </div>
  );
}

export function PacketViewerView() {
  return (
    <div className="dashboard-view" style={{height: '100%', display: 'flex', flexDirection: 'column'}}>
      <div className="hero-section" style={{marginBottom: '24px', flexShrink: 0}}>
        <h2 className="hero-title" style={{fontSize: '2rem'}}>Packet <span className="highlight-cyan">Viewer</span></h2>
        <p className="hero-subtitle">Hex dump and protocol tree for individual frames.</p>
      </div>
      <div style={{flex: 1, background: '#050505', borderRadius: '8px', border: '1px solid var(--border-color)', overflow: 'hidden', display: 'flex', flexDirection: 'column'}}>
         <div style={{padding: '12px 16px', background: '#111', borderBottom: '1px solid var(--border-color)', display: 'flex', gap: '24px', fontSize: '0.8rem', color: 'var(--text-muted)'}}>
            <span>No.</span><span>Time</span><span>Source</span><span>Destination</span><span>Protocol</span><span>Info</span>
         </div>
         <div style={{padding: '16px', color: 'var(--text-primary)', opacity: 0.5, textAlign: 'center', margin: 'auto'}}>
            <Binary size={48} style={{margin: '0 auto 16px auto', opacity: 0.2}} />
            <p>No packets selected. Start a capture or upload a PCAP.</p>
         </div>
      </div>
    </div>
  );
}

export function ReportsView() {
  return (
    <div className="dashboard-view">
      <div className="hero-section" style={{marginBottom: '24px'}}>
        <h2 className="hero-title" style={{fontSize: '2rem'}}>Generate <span className="highlight-cyan">Reports</span></h2>
        <p className="hero-subtitle">Export forensic findings and compliance audits.</p>
      </div>
      <div className="architecture-grid" style={{gridTemplateColumns: '1fr 1fr'}}>
        <div className="arch-card">
          <div className="card-header">
             <div className="card-icon"><FileText size={20} /></div>
             <h3>Export Format</h3>
          </div>
          <div className="card-content">
             <button className="btn-primary" style={{width: '100%', marginBottom: '12px'}}>Export as PDF Report</button>
             <button style={{width: '100%', padding: '10px 20px', background: 'transparent', border: '1px solid var(--accent-cyan)', color: 'var(--accent-cyan)', borderRadius: '8px', cursor: 'pointer', fontWeight: 600}}>Export as JSON (Machine Readable)</button>
          </div>
        </div>
        <div className="arch-card">
          <div className="card-header">
             <div className="card-icon"><Save size={20} /></div>
             <h3>Recent Reports</h3>
          </div>
          <div className="card-content">
             <p style={{color: 'var(--text-muted)', fontSize: '0.9rem', textAlign: 'center', marginTop: '24px'}}>No reports generated yet.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export function SettingsView() {
  return (
    <div className="dashboard-view">
      <div className="hero-section" style={{marginBottom: '24px'}}>
        <h2 className="hero-title" style={{fontSize: '2rem'}}>Engine <span className="highlight-cyan">Settings</span></h2>
        <p className="hero-subtitle">Configure analysis rules and system preferences.</p>
      </div>
      <div className="arch-card" style={{marginBottom: '24px'}}>
          <div className="card-header">
             <div className="card-icon"><Shield size={20} /></div>
             <h3>Security Rules</h3>
          </div>
          <div className="card-content">
             <div style={{display: 'flex', justifyContent: 'space-between', padding: '16px 0', borderBottom: '1px solid var(--border-color)'}}>
                <div>
                   <div style={{fontWeight: 600, color: 'var(--text-primary)'}}>Strict IKE Enforcement</div>
                   <div style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Flag any IKEv1 connections as HIGH severity.</div>
                </div>
                <div style={{width: '40px', height: '20px', background: 'var(--accent-green)', borderRadius: '10px', position: 'relative'}}>
                   <div style={{width: '16px', height: '16px', background: '#fff', borderRadius: '50%', position: 'absolute', right: '2px', top: '2px'}}></div>
                </div>
             </div>
             <div style={{display: 'flex', justifyContent: 'space-between', padding: '16px 0'}}>
                <div>
                   <div style={{fontWeight: 600, color: 'var(--text-primary)'}}>PFS Requirement</div>
                   <div style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Require Perfect Forward Secrecy (DH groups in Phase 2).</div>
                </div>
                <div style={{width: '40px', height: '20px', background: 'var(--accent-green)', borderRadius: '10px', position: 'relative'}}>
                   <div style={{width: '16px', height: '16px', background: '#fff', borderRadius: '50%', position: 'absolute', right: '2px', top: '2px'}}></div>
                </div>
             </div>
          </div>
      </div>
      <div className="arch-card">
          <div className="card-header">
             <div className="card-icon"><HardDrive size={20} /></div>
             <h3>Storage</h3>
          </div>
          <div className="card-content">
             <div style={{display: 'flex', justifyContent: 'space-between', padding: '16px 0'}}>
                <div>
                   <div style={{fontWeight: 600, color: 'var(--text-primary)'}}>Auto-delete PCAPs</div>
                   <div style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Delete capture files after analysis completes.</div>
                </div>
                <div style={{width: '40px', height: '20px', background: 'var(--bg-app)', border: '1px solid var(--border-color)', borderRadius: '10px', position: 'relative'}}>
                   <div style={{width: '16px', height: '16px', background: 'var(--text-muted)', borderRadius: '50%', position: 'absolute', left: '2px', top: '2px'}}></div>
                </div>
             </div>
          </div>
      </div>
    </div>
  );
}
