import React from "react";
import "./ConfirmDialog.css";

const ConfirmDialog = ({ 
  title = "Confirm Action", 
  message, 
  type = "default", 
  onConfirm, 
  onCancel 
}) => {
  const getColor = () => {
    switch (type) {
      case "delete":
        return "#e63946";
      case "block":
        return "#f59e0b";
      case "archive":
        return "#3b82f6";
      case "approve":
        return "#10b981";
      default:
        return "#6366f1";
    }
  };

  return (
    <div className="confirm-overlay">
      <div className="confirm-box" style={{ borderTop: `6px solid ${getColor()}` }}>
        <h3 style={{ color: getColor() }}>{title}</h3>
        <p>{message}</p>
        <div className="confirm-buttons">
          <button className="btn cancel" onClick={onCancel}>
            Cancel
          </button>
          <button className="btn confirm" style={{ background: getColor() }} onClick={onConfirm}>
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDialog;
