import { BrowserRouter, Routes, Route } from "react-router-dom";

import { AnalysisProvider } from "./context/AnalysisContext";

import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";

import Overview from "./pages/Overview";
import LiveAnalysis from "./pages/LiveAnalysis";
import Captures from "./pages/Captures";
import Security from "./pages/Security";
import Reports from "./pages/Reports";
import Blockchain from "./pages/Blockchain";
import Settings from "./pages/Settings";

import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <AnalysisProvider>
        <div className="app-shell">
          <Sidebar />

          <div className="app-main">
            <Topbar />

            <main className="app-content">
              <Routes>
                <Route path="/" element={<Overview />} />
                <Route path="/live" element={<LiveAnalysis />} />
                <Route path="/captures" element={<Captures />} />
                <Route path="/security" element={<Security />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/blockchain" element={<Blockchain />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </main>
          </div>
        </div>
      </AnalysisProvider>
    </BrowserRouter>
  );
}
