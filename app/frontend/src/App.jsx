import { useState, useEffect } from "react";
import TriageForm from "./components/TriageForm.jsx";
import PatientList from "./components/PatientList.jsx";

export default function App() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchPatients = async () => {
    try {
      const res = await fetch("/api/patients");
      if (!res.ok) throw new Error("Failed to fetch patients");
      setPatients(await res.json());
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  const handleSubmit = async (data) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/triage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        const text = await res.text();
        let detail = "Triage failed";
        try { detail = JSON.parse(text).detail || detail; } catch {}
        throw new Error(detail);
      }
      await fetchPatients();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    await fetch("/api/patients", { method: "DELETE" });
    setPatients([]);
  };

  return (
    <div className="container">
      <header>
        <h1>🏥 Patient Triage Assistant</h1>
        <p className="subtitle">AI-powered urgency classification for healthcare</p>
      </header>

      {error && <div className="error">{error}</div>}

      <div className="layout">
        <section className="form-section">
          <h2>New Patient</h2>
          <TriageForm onSubmit={handleSubmit} loading={loading} />
        </section>

        <section className="list-section">
          <div className="list-header">
            <h2>Triage Queue ({patients.length})</h2>
            {patients.length > 0 && (
              <button className="btn-clear" onClick={handleClear}>
                Clear All
              </button>
            )}
          </div>
          <PatientList patients={patients} />
        </section>
      </div>
    </div>
  );
}
