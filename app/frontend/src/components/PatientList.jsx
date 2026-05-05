const URGENCY_COLORS = {
  Critical: "#dc2626",
  High: "#ea580c",
  Medium: "#ca8a04",
  Low: "#16a34a",
};

export default function PatientList({ patients }) {
  if (patients.length === 0) {
    return <p className="empty">No patients triaged yet. Submit a case above.</p>;
  }

  return (
    <ul className="patient-list">
      {patients.map((p) => (
        <li key={p.id} className="patient-card">
          <span
            className="urgency-badge"
            style={{ backgroundColor: URGENCY_COLORS[p.urgency] || "#6b7280" }}
          >
            {p.urgency}
          </span>
          <div className="patient-info">
            <strong>{p.name}</strong> — Age {p.age}
            <p className="symptoms">{p.symptoms}</p>
            <p className="reasoning">💡 {p.reasoning}</p>
            <time>{new Date(p.timestamp).toLocaleString()}</time>
          </div>
        </li>
      ))}
    </ul>
  );
}
