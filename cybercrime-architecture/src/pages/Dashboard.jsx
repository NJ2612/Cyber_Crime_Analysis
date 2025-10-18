import React from "react";
import "./Dashboard.css";

const Dashboard = () => {
  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <div className="breadcrumb">Home / Dashboard</div>
          <h1>Dashboard Overview</h1>
        </div>
        <div className="actions">
          {/* buttons or filters here */}
        </div>
      </div>

      <p>Welcome to the Cybercrime Data Management Portal.</p>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Crimes</h3>
          <p>1,234</p>
        </div>
        <div className="stat-card">
          <h3>Active Cases</h3>
          <p>245</p>
        </div>
        <div className="stat-card">
          <h3>Suspects</h3>
          <p>521</p>
        </div>
        <div className="stat-card">
          <h3>Resolved Cases</h3>
          <p>988</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
