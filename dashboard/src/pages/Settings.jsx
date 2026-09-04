import {
  Check,
  Cpu,
  Network,
  Radio,
  RotateCcw,
  Save,
  Settings as SettingsIcon,
  Shield,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

const STORAGE_KEY =
  "vpn-sentinel-settings";

const DEFAULT_SETTINGS = {
  networkInterface: "Automatic",
  vpnDetection: true,
  aiAnalysis: true,
  securityAssessment: true,
};

export default function Settings() {
  const [settings, setSettings] =
    useState(DEFAULT_SETTINGS);

  const [saved, setSaved] =
    useState(false);

  useEffect(() => {
    try {
      const stored =
        localStorage.getItem(STORAGE_KEY);

      if (stored) {
        const parsed =
          JSON.parse(stored);

        setSettings({
          ...DEFAULT_SETTINGS,
          ...parsed,
        });
      }
    } catch (error) {
      console.error(
        "Unable to load settings:",
        error
      );
    }
  }, []);

  function updateSetting(key, value) {
    setSettings((previous) => ({
      ...previous,
      [key]: value,
    }));

    setSaved(false);
  }

  function saveSettings() {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(settings)
      );

      setSaved(true);

      window.setTimeout(() => {
        setSaved(false);
      }, 2500);
    } catch (error) {
      console.error(
        "Unable to save settings:",
        error
      );
    }
  }

  function resetSettings() {
    setSettings(DEFAULT_SETTINGS);

    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(DEFAULT_SETTINGS)
      );
    } catch (error) {
      console.error(
        "Unable to reset settings:",
        error
      );
    }

    setSaved(true);

    window.setTimeout(() => {
      setSaved(false);
    }, 2500);
  }

  return (
    <div className="application-page">

      <div className="page-kicker">
        SYSTEM CONFIGURATION
      </div>

      <div className="page-heading-row">

        <div>
          <h2>Settings</h2>

          <p className="page-description">
            Analysis engine and infrastructure configuration.
          </p>
        </div>

        <div className="settings-actions">

          <button
            type="button"
            className="secondary-action"
            onClick={resetSettings}
          >
            <RotateCcw size={15} />
            RESET
          </button>

          <button
            type="button"
            className="agent-action"
            onClick={saveSettings}
          >
            {saved ? (
              <>
                <Check size={15} />
                SAVED
              </>
            ) : (
              <>
                <Save size={15} />
                SAVE CONFIGURATION
              </>
            )}
          </button>

        </div>

      </div>

      <section className="app-panel">

        <div className="panel-header">

          <div>
            <div className="panel-kicker">
              ANALYSIS ENGINE
            </div>

            <h3>Runtime Configuration</h3>
          </div>

          <SettingsIcon size={18} />

        </div>

        <div className="settings-list">

          <Setting
            icon={<Network size={18} />}
            title="Network Interface"
            description="Select how the analyzer chooses the active network interface."
            type="select"
            value={settings.networkInterface}
            options={[
              "Automatic",
              "Default Route",
            ]}
            onChange={(value) =>
              updateSetting(
                "networkInterface",
                value
              )
            }
          />

          <Setting
            icon={<Radio size={18} />}
            title="VPN Detection"
            description="Enable IKE, ESP and AH traffic detection."
            type="toggle"
            value={settings.vpnDetection}
            onChange={(value) =>
              updateSetting(
                "vpnDetection",
                value
              )
            }
          />

          <Setting
            icon={<Cpu size={18} />}
            title="AI Analysis"
            description="Enable protocol and traffic feature analysis."
            type="toggle"
            value={settings.aiAnalysis}
            onChange={(value) =>
              updateSetting(
                "aiAnalysis",
                value
              )
            }
          />

          <Setting
            icon={<Shield size={18} />}
            title="Security Assessment"
            description="Enable rule-based security scoring and findings."
            type="toggle"
            value={settings.securityAssessment}
            onChange={(value) =>
              updateSetting(
                "securityAssessment",
                value
              )
            }
          />

        </div>

      </section>

      <section className="app-panel">

        <div className="panel-header">

          <div>
            <div className="panel-kicker">
              CONFIGURATION STATUS
            </div>

            <h3>Current Runtime State</h3>
          </div>

          <Check size={18} />

        </div>

        <div className="evidence-grid">

          <Evidence
            label="NETWORK"
            value={settings.networkInterface}
          />

          <Evidence
            label="VPN DETECTION"
            value={
              settings.vpnDetection
                ? "ENABLED"
                : "DISABLED"
            }
          />

          <Evidence
            label="AI ANALYSIS"
            value={
              settings.aiAnalysis
                ? "ENABLED"
                : "DISABLED"
            }
          />

          <Evidence
            label="SECURITY"
            value={
              settings.securityAssessment
                ? "ENABLED"
                : "DISABLED"
            }
          />

        </div>

      </section>

    </div>
  );
}

function Setting({
  icon,
  title,
  description,
  type,
  value,
  options,
  onChange,
}) {
  return (
    <div className="setting-row">

      <div className="setting-icon">
        {icon}
      </div>

      <div className="setting-content">
        <strong>{title}</strong>
        <span>{description}</span>
      </div>

      <div className="setting-control">

        {type === "toggle" ? (
          <button
            type="button"
            className={`setting-toggle ${
              value ? "active" : ""
            }`}
            aria-pressed={value}
            onClick={() =>
              onChange(!value)
            }
          >
            <span className="toggle-track">
              <span className="toggle-thumb" />
            </span>

            <span className="toggle-label">
              {value
                ? "ENABLED"
                : "DISABLED"}
            </span>
          </button>
        ) : (
          <select
            className="setting-select"
            value={value}
            onChange={(event) =>
              onChange(event.target.value)
            }
          >
            {options.map((option) => (
              <option
                key={option}
                value={option}
              >
                {option}
              </option>
            ))}
          </select>
        )}

      </div>

    </div>
  );
}

function Evidence({ label, value }) {
  return (
    <div className="evidence-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
