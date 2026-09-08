import { useState } from 'react';
import Sidebar from './components/Sidebar';
import TopNav from './components/TopNav';
import DashboardView from './components/DashboardView';
import ResultsView from './components/ResultsView';
import { PcapView, LiveCaptureView, PacketViewerView, ReportsView, SettingsView } from './components/OtherViews';
import { useAnalyzer } from './hooks/useAnalyzer';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Lift the hook state up so both views have access to live findings
  const analyzerProps = useAnalyzer();

  return (
    <>
      <div className="grid-bg"></div>
      <div className="app-layout">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
        
        <div className="main-content">
          <TopNav />
          {activeTab === 'dashboard' && <DashboardView {...analyzerProps} />}
          {activeTab === 'pcap' && <PcapView />}
          {activeTab === 'live' && <LiveCaptureView />}
          {activeTab === 'viewer' && <PacketViewerView />}
          {activeTab === 'results' && <ResultsView {...analyzerProps} />}
          {activeTab === 'reports' && <ReportsView />}
          {activeTab === 'settings' && <SettingsView />}
        </div>
      </div>
    </>
  );
}

export default App;
