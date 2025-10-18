import React, { useState } from "react";
import ConfirmDialog from "../components/ConfirmDialog";
import Toast from "../components/Toast";

const Suspects = () => {
  const [showDialog, setShowDialog] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastType, setToastType] = useState("success");
  const [toastMsg, setToastMsg] = useState("");

  const handleDeleteClick = () => setShowDialog(true);

  const confirmDelete = () => {
    setToastType("success");
    setToastMsg("Suspect deleted successfully.");
    setShowToast(true);
    setShowDialog(false);
  };

  const cancelDelete = () => {
    setToastType("info");
    setToastMsg("Action cancelled.");
    setShowToast(true);
    setShowDialog(false);
  };

  return (
    <div style={{ padding: "90px 40px 40px 280px" }}>
      <h2>Suspect Management</h2>
      <p>Manage suspect details, records, and actions.</p>
      <button
        style={{
          background: "#ef4444",
          color: "white",
          padding: "10px 16px",
          borderRadius: "8px",
          border: "none",
          marginTop: "20px",
          cursor: "pointer",
        }}
        onClick={handleDeleteClick}
      >
        Delete Suspect
      </button>

      {showDialog && (
        <ConfirmDialog
          title="Delete Suspect"
          message="Are you sure you want to permanently delete this suspect?"
          type="delete"
          onConfirm={confirmDelete}
          onCancel={cancelDelete}
        />
      )}

      {showToast && (
        <Toast
          message={toastMsg}
          type={toastType}
          onClose={() => setShowToast(false)}
        />
      )}
    </div>
  );
};

export default Suspects;
