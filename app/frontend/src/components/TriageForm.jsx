import { useState } from "react";

export default function TriageForm({ onSubmit, loading }) {
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [symptoms, setSymptoms] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name || !age || !symptoms) return;
    onSubmit({ name, age: parseInt(age, 10), symptoms });
    setName("");
    setAge("");
    setSymptoms("");
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="field">
        <label htmlFor="name">Patient Name</label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Jane Doe"
          required
        />
      </div>

      <div className="field">
        <label htmlFor="age">Age</label>
        <input
          id="age"
          type="number"
          min="0"
          max="150"
          value={age}
          onChange={(e) => setAge(e.target.value)}
          placeholder="e.g. 45"
          required
        />
      </div>

      <div className="field">
        <label htmlFor="symptoms">Symptoms</label>
        <textarea
          id="symptoms"
          rows="4"
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
          placeholder="Describe the patient's symptoms..."
          required
        />
      </div>

      <button type="submit" className="btn-primary" disabled={loading}>
        {loading ? "Classifying…" : "Triage Patient"}
      </button>
    </form>
  );
}
