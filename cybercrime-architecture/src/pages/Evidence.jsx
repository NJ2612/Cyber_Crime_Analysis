import React from "react";
import "./Evidence.css";

const Evidence = () => {
  return (
    <div className="evidence-page">
      <div className="evidence-header">
        <h2>Evidence</h2>
        <p>Upload, review, and manage digital evidence for ongoing investigations.</p>
      </div>

      <div className="evidence-table-container">
        <table className="evidence-table">
          <thead>
            <tr>
              <th>Evidence ID</th>
              <th>Case No.</th>
              <th>Type</th>
              <th>Status</th>
              <th>Uploaded On</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>EV1023</td>
              <td>C-120</td>
              <td>Digital</td>
              <td className="status review">Under Review</td>
              <td>2025-09-29</td>
            </tr>
            <tr>
              <td>EV1047</td>
              <td>C-122</td>
              <td>Image</td>
              <td className="status verified">Verified</td>
              <td>2025-10-03</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Evidence;
