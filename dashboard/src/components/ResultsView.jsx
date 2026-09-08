import { Search, ShieldAlert, Cpu, Database } from 'lucide-react';
import './DashboardView.css'; // Reusing dashboard styles for consistency

export default function ResultsView({ engineState, findings, error }) {
  // Helper to format bytes
  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const ike = findings?.ike;
  const rules = findings?.security_rules;
  const esp = findings?.esp_features;
  const ml = findings?.ml;

  // Determine rule pass/fail
  const getRuleStatus = (ruleResult) => {
    if (!ruleResult) return 'pending';
    return ruleResult.status === 'PASS' ? 'pass' : 'fail';
  };

  return (
    <div className="dashboard-view">
      <div className="hero-section" style={{marginBottom: '24px'}}>
        <h2 className="hero-title" style={{fontSize: '2rem'}}>Analysis <span className="highlight-cyan">Results</span></h2>
        <p className="hero-subtitle">
          Real-time outputs from the IPsec Protocol Engine.
        </p>
      </div>

      <div className="architecture-grid">
        {/* 1. IKE Parser */}
        <div className="arch-card">
          <div className="card-header">
            <div className="card-icon"><Search size={20} /></div>
            <div className="card-titles">
              <span className="card-overline">SECURITY METADATA</span>
              <h3>IKE Parser</h3>
            </div>
          </div>
          <div className="card-content mono">
            <div className="data-row"><span>Version:</span> <span className="highlight-white">{ike?.version || 'Waiting...'}</span></div>
            <div className="data-row"><span>Encryption:</span> <span className="highlight-white">{ike?.encryption_algo || '--'}</span></div>
            <div className="data-row"><span>Auth:</span> <span className="highlight-white">{ike?.auth_algo || '--'}</span></div>
            <div className="data-row"><span>DH Group:</span> <span className="highlight-white">{ike?.dh_group || '--'}</span></div>
          </div>
        </div>

        {/* 2. Security Rule Engine */}
        <div className="arch-card">
          <div className="card-header">
            <div className="card-icon"><ShieldAlert size={20} /></div>
            <div className="card-titles">
              <span className="card-overline">DETERMINISTIC</span>
              <h3>Security Rule Engine</h3>
            </div>
          </div>
          <div className="card-content mono rules-list">
             <div className={`rule-item ${getRuleStatus(rules?.weak_cipher)}`}>
               <span className="dot"></span> Strong Ciphers Validated
             </div>
             <div className={`rule-item ${getRuleStatus(rules?.pfs)}`}>
               <span className="dot"></span> Perfect Forward Secrecy
             </div>
             <div className={`rule-item ${ike ? 'pass' : 'pending'}`}>
               <span className="dot"></span> IKE Protocol Parsed
             </div>
          </div>
        </div>

        {/* 3. ESP Flow Analyzer */}
        <div className="arch-card">
          <div className="card-header">
            <div className="card-icon"><Database size={20} /></div>
            <div className="card-titles">
              <span className="card-overline">FEATURE EXTRACTION</span>
              <h3>ESP Flow Analyzer</h3>
            </div>
          </div>
          <div className="card-content mono">
            <div className="data-row"><span>Flow Duration:</span> <span className="highlight-white">{esp ? `${esp.duration_sec.toFixed(2)}s` : '--'}</span></div>
            <div className="data-row"><span>Packets:</span> <span className="highlight-white">{esp?.packet_count || '--'}</span></div>
            <div className="data-row"><span>Bytes Sent:</span> <span className="highlight-white">{esp ? formatBytes(esp.total_bytes) : '--'}</span></div>
            <div className="data-row"><span>Avg Packet Size:</span> <span className="highlight-white">{esp ? `${Math.round(esp.avg_packet_size)} B` : '--'}</span></div>
          </div>
        </div>

        {/* 4. ML Inference */}
        <div className="arch-card">
          <div className="card-header">
            <div className="card-icon"><Cpu size={20} /></div>
            <div className="card-titles">
              <span className="card-overline">TRAFFIC CLASSIFICATION</span>
              <h3>ML Inference</h3>
            </div>
          </div>
          <div className="card-content">
            <div className="ml-model-badge">Random Forest Model Loaded</div>
            <div className="classification-result mt-4 mono">
              <span className="label">Prediction:</span>
              <span className="value text-green">
                {ml ? `${ml.prediction} (${Math.round(ml.confidence * 100)}%)` : 'Waiting for flow data...'}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Small status footer for results */}
      <div className="action-footer" style={{padding: '16px 24px'}}>
         <div className="status-indicator">
            <span className="status-label">Engine State:</span>
            <span className="status-value highlight-cyan">{engineState}</span>
            {error && <span style={{color: '#F43F5E', marginLeft: '16px', fontSize: '0.8rem'}}>{error}</span>}
         </div>
      </div>
    </div>
  );
}
