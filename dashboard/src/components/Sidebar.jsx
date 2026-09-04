import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Radio,
  Database,
  ShieldCheck,
  FileText,
  Blocks,
  Settings,
} from "lucide-react";

const navigation = [
  {
    name: "Overview",
    path: "/",
    icon: LayoutDashboard,
  },
  {
    name: "Live Analysis",
    path: "/live",
    icon: Radio,
  },
  {
    name: "Captures",
    path: "/captures",
    icon: Database,
  },
  {
    name: "Security",
    path: "/security",
    icon: ShieldCheck,
  },
  {
    name: "Reports",
    path: "/reports",
    icon: FileText,
  },
  {
    name: "Blockchain",
    path: "/blockchain",
    icon: Blocks,
  },
  {
    name: "Settings",
    path: "/settings",
    icon: Settings,
  },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">
          <ShieldCheck size={24} />
        </div>

        <div>
          <div className="brand-title">VPN SENTINEL</div>
          <div className="brand-subtitle">IPsec Security Center</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navigation.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "active" : ""}`
              }
            >
              <Icon size={19} />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="system-status">
          <span className="status-dot"></span>
          <span>Analyzer Online</span>
        </div>
      </div>
    </aside>
  );
}
