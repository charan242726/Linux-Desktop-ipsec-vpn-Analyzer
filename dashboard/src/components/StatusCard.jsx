import { ArrowUpRight } from "lucide-react";

export default function StatusCard({
  label,
  value,
  detail,
  icon,
  tone = "normal",
}) {
  return (
    <div className={`status-card ${tone}`}>

      <div className="status-card-top">
        <span>{label}</span>

        <div className="status-card-icon">
          {icon}
        </div>
      </div>

      <strong>{value}</strong>

      <div className="status-card-bottom">
        <span>{detail}</span>
        <ArrowUpRight size={13} />
      </div>

    </div>
  );
}
