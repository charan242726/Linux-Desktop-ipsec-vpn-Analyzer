import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Download, 
  Inbox,
  RefreshCw,
  Search
} from 'lucide-react';

const API = 'http://localhost:8000';

export const ReportHistory = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchReports = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/reports`);
      if (res.ok) {
        const data = await res.json();
        setReports(data);
      }
    } catch (error) {
      console.error("Failed to fetch reports", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleDownload = (reportId) => {
    window.open(`${API}/reports/${reportId}/pdf`, '_blank');
  };

  const filteredReports = reports.filter(r => 
    r.id.toString().includes(searchTerm) ||
    (r.risk_level && r.risk_level.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="flex-1 p-6 flex flex-col h-full overflow-hidden">
      
      {/* Header Section */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold font-mono tracking-tight text-white mb-1">
            REPORT HISTORY
          </h2>
          <p className="text-sm font-mono text-slate-400">
            Archive of all generated IPsec security & traffic analysis reports
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Search Box */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input 
              type="text"
              placeholder="Search reports..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-900/60 border border-white/10 text-xs text-slate-200 placeholder-slate-500 rounded-lg pl-9 pr-4 py-2 w-56 focus:outline-none focus:border-cyan-500/50 font-mono transition-colors"
            />
          </div>
          
          <button 
            onClick={fetchReports}
            className="p-2 rounded-lg bg-slate-900/60 border border-white/10 text-slate-400 hover:text-cyan-400 hover:border-cyan-400/40 transition-all"
            title="Refresh List"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="mirror-card flex-1 p-0 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
          {loading && reports.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <RefreshCw className="w-8 h-8 text-cyan-500/50 animate-spin" />
            </div>
          ) : filteredReports.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full py-10 text-slate-500 font-mono gap-3">
              <Inbox className="w-12 h-12 text-slate-600 mb-2" />
              <p className="text-sm text-slate-400">No reports found in the archive.</p>
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  className="text-xs text-cyan-400 hover:underline"
                >
                  Clear search filters
                </button>
              )}
            </div>
          ) : (
            <table className="w-full text-left dense-table border-collapse">
              <thead>
                <tr>
                  <th className="py-3 px-4 font-semibold text-slate-300">Analysis ID</th>
                  <th className="py-3 px-4 font-semibold text-slate-300">Capture Start (UTC)</th>
                  <th className="py-3 px-4 font-semibold text-slate-300">Capture End (UTC)</th>
                  <th className="py-3 px-4 font-semibold text-slate-300">Risk Level</th>
                  <th className="py-3 px-4 font-semibold text-slate-300 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 font-mono text-sm">
                {filteredReports.map((report) => (
                  <tr 
                    key={report.id}
                    className="hover:bg-cyan-500/[0.04] transition-colors group"
                  >
                    {/* ID */}
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-cyan-500/50 group-hover:text-cyan-400 transition-colors" />
                        <span className="text-slate-200 font-medium group-hover:text-cyan-400 transition-colors">
                          VG-2026-S{report.id.toString().padStart(4, '0')}
                        </span>
                      </div>
                    </td>

                    {/* Start Time */}
                    <td className="py-3 px-4 text-slate-400">
                      {report.started_at || 'Unknown'}
                    </td>

                    {/* End Time */}
                    <td className="py-3 px-4 text-slate-400">
                      {report.ended_at || <span className="text-emerald-400/70 italic">Active Session</span>}
                    </td>

                    {/* Risk Level */}
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold border tracking-wider ${
                        report.risk_level === 'LOW' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                        report.risk_level === 'MEDIUM' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                        report.risk_level === 'HIGH' || report.risk_level === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
                        'bg-slate-500/10 text-slate-400 border-slate-500/20'
                      }`}>
                        {report.risk_level || 'UNKNOWN'}
                      </span>
                    </td>

                    {/* Actions */}
                    <td className="py-3 px-4 text-right">
                      <button 
                        onClick={() => handleDownload(report.id)}
                        className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-500/10 border border-cyan-400/20 text-cyan-300 hover:bg-cyan-400 hover:text-slate-900 transition-all font-semibold text-xs"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>PDF</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};
