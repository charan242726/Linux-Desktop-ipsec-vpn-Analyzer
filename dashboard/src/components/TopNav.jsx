import { Search, Bell, Minus, Square, X } from 'lucide-react';
import './TopNav.css';

export default function TopNav() {
  const handleMinimize = () => window.electronAPI?.minimize();
  const handleMaximize = () => window.electronAPI?.maximize();
  const handleClose = () => window.electronAPI?.close();

  return (
    <header className="topnav">
      <div className="search-container">
        <Search size={16} className="search-icon" />
        <input 
          type="text" 
          placeholder="Search packets, protocols, IP addresses..." 
          className="search-input"
        />
        <div className="shortcut-hint">
          <span className="mono">⌘</span>
          <span className="mono">K</span>
        </div>
      </div>

      <div className="profile-container">
        <button className="bell-btn">
          <Bell size={18} />
          <span className="notification-dot"></span>
        </button>

        <div className="user-profile">
          <div className="avatar">K</div>
          <div className="user-info">
            <span className="user-name">Keerthy</span>
            <span className="user-role">Student</span>
          </div>
        </div>

        {/* Window controls for electron */}
        <div className="window-controls-inline">
          <button onClick={handleMinimize}><Minus size={14} /></button>
          <button onClick={handleMaximize}><Square size={12} /></button>
          <button onClick={handleClose} className="close-btn"><X size={16} /></button>
        </div>
      </div>
    </header>
  );
}
