import React from "react";

// Box component for each stage of the architecture
const Stage = ({ color, title, subtitle }) => (
  <div
    style={{
      backgroundColor: color,
      color: "#fff",
      padding: "20px",
      borderRadius: "10px",
      textAlign: "center",
      width: "250px",
      boxShadow: "0 4px 8px rgba(0,0,0,0.2)",
    }}
  >
    <h3 style={{ margin: "5px 0" }}>{title}</h3>
    <p style={{ fontSize: "14px" }}>{subtitle}</p>
  </div>
);

// Connector line between stages
const Connector = () => (
  <div
    style={{
      width: "4px",
      height: "50px",
      backgroundColor: "#666",
      margin: "10px auto",
    }}
  ></div>
);

const SystemArchitecture = () => {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #f0f4f8, #d9e4ec)",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h2 style={{ marginBottom: "30px", color: "#333" }}>
        Cybercrime Data Management System - Architecture
      </h2>

      <Stage
        color="#22c55e"
        title="Frontend"
        subtitle="React Interface (Visualization, Reports)"
      />
      <Connector />
      <Stage
        color="#f59e0b"
        title="API Layer"
        subtitle="Express Backend, JWT Auth, CRUD APIs"
      />
      <Connector />
      <Stage
        color="#3b82f6"
        title="Database"
        subtitle="PostgreSQL / MySQL (Structured Storage)"
      />
      <Connector />
      <Stage
        color="#9333ea"
        title="ML Engine"
        subtitle="Hotspot Prediction, Risk Analysis"
      />
    </div>
  );
};

export default SystemArchitecture;
