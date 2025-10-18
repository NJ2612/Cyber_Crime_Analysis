import React from "react";
import "./Reports.css";

const toCSV = (arr, columns) => {
  const header = columns.join(",");
  const lines = arr.map((row) =>
    columns.map((c) => `"${(row[c] ?? "").toString().replace(/"/g, '""')}"`).join(",")
  );
  return [header, ...lines].join("\n");
};

const download = (filename, content) => {
  const blob = new Blob([content], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
};

const Reports = () => {
  const exportCrimes = () => {
    const crimes = JSON.parse(localStorage.getItem("crimes")) || [];
    if (!crimes.length) return alert("No crime data");
    const cols = ["id", "type", "location", "date", "severity", "description", "ip_address"];
    const csv = toCSV(crimes, cols);
    download("crimes_export.csv", csv);
  };

  const exportForecasts = () => {
    const forecasts = JSON.parse(localStorage.getItem("forecasts")) || [];
    if (!forecasts.length) return alert("No forecasts found");
    const cols = ["id", "city", "state", "month", "risk_score", "label", "created_at"];
    const csv = toCSV(forecasts, cols);
    download("forecasts_export.csv", csv);
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <div className="breadcrumb">Home / Reports</div>
          <h1>Reports & Export</h1>
        </div>
        <div className="actions">
          <button className="export-btn" onClick={exportCrimes}>
            Export Crimes (CSV)
          </button>
          <button className="export-btn" onClick={exportForecasts}>
            Export Forecasts (CSV)
          </button>
        </div>
      </div>
      <p>Download CSV exports of stored data.</p>
    </div>
  );
};

export default Reports;
