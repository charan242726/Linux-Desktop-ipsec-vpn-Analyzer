import { BrowserRouter, Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";

import Overview from "./pages/Overview";
import LiveAnalysis from "./pages/LiveAnalysis";
import Captures from "./pages/Captures";
import Reports from "./pages/Reports";
import Security from "./pages/Security";
import Blockchain from "./pages/Blockchain";
import Settings from "./pages/Settings";

import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <Application />
    </BrowserRouter>
  );
}

function Application() {
  return (
    <div className="app-shell">

      <Sidebar />

      <main className="main-content">

        <Topbar />

        <div className="workspace">

          <Routes>

            <Route
              path="/"
              element={<Overview />}
            />

            <Route
              path="/live"
              element={<LiveAnalysis />}
            />

            <Route
              path="/captures"
              element={<Captures />}
            />

            <Route
              path="/security"
              element={<Security />}
            />

            <Route
              path="/reports"
              element={<Reports />}
            />

            <Route
              path="/blockchain"
              element={<Blockchain />}
            />

            <Route
              path="/settings"
              element={<Settings />}
            />

          </Routes>

        </div>

      </main>

    </div>
  );
}
