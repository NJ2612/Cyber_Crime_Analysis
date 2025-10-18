import React, { useState } from "react";
import "../App.css";

const Settings = () => {
  const [theme, setTheme] = useState("Light");
  const [notifications, setNotifications] = useState(true);

  return (
    <div>
      <h1>Settings</h1>
      <p>Customize your preferences and system settings.</p>

      <div className="card">
        <div className="form-group">
          <label>Theme</label>
          <select value={theme} onChange={(e) => setTheme(e.target.value)}>
            <option>🌞 Light</option>
            <option>🌙 Dark</option>
            <option>🌈 System Default</option>
          </select>
        </div>

        <div className="form-group" style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <label>Enable Notifications</label>
          <input
            type="checkbox"
            checked={notifications}
            onChange={() => setNotifications(!notifications)}
            style={{ width: "22px", height: "22px", cursor: "pointer" }}
          />
        </div>

        <button className="save-btn">Save Settings</button>
      </div>
    </div>
  );
};

export default Settings;
