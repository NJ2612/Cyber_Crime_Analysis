import React, { useState } from "react";
import "./Header.css";

const Header = ({ title, onToggleSidebar, onNavigate, onLogout }) => {
  const [openDropdown, setOpenDropdown] = useState(false);

  return (
    <header className="header">
      <div className="header-left">
        <button className="menu-btn" onClick={onToggleSidebar}>
          ☰
        </button>
        <h1>{title}</h1>
      </div>

      <div
        className="user-section"
        onClick={() => setOpenDropdown(!openDropdown)}
      >
        <span className="user-name">Admin</span>
        <img
          src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
          alt="User Avatar"
          className="user-avatar"
        />

        {openDropdown && (
          <div className="dropdown">
            <button onClick={() => onNavigate("Profile")}>👤 Profile</button>
            <button onClick={() => onNavigate("Settings")}>⚙️ Settings</button>
            <button
              onClick={() => {
                setOpenDropdown(false);
                onLogout();
              }}
            >
              🚪 Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
