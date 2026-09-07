import { LayoutDashboard, FileArchive, Radio, Binary, LineChart, FileText, Settings } from 'lucide-react';
import './Sidebar.css';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'pcap', label: 'PCAP Analysis', icon: FileArchive },
  { id: 'live', label: 'Live Capture', icon: Radio },
  { id: 'viewer', label: 'Packet Viewer', icon: Binary },
  { id: 'results', label: 'Analysis Results', icon: LineChart },
  { id: 'reports', label: 'Reports', icon: FileText },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export default function Sidebar({ activeTab, setActiveTab }) {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="logo-badge">IP</div>
        <div className="title-group">
          <h2>IPsec Analyzer</h2>
          <span className="mono">V1.0 - LOCAL-FIRST</span>
        </div>
      </div>

      <div className="nav-section-title">NAVIGATION RAIL</div>
      
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <button 
            key={item.id}
            className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
            onClick={() => setActiveTab(item.id)}
          >
            <item.icon size={18} className="nav-icon" />
            <span>{item.label}</span>
            {activeTab === item.id && <div className="active-dot" />}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="daemon-status">
          <div className="daemon-dot"></div>
          <div className="daemon-text">
            <span className="daemon-title">analyzer daemon</span>
            <span className="daemon-state mono">running</span>
          </div>
        </div>
      </div>
    </div>
  );
}
