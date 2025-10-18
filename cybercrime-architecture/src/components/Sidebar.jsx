import React from "react";
import "./Sidebar.css";

const Sidebar = ({ onNavigate, className }) => {
  return (
    <aside className={className}>
      <div className="logo">Sentinel</div>
      <ul>
        {["Dashboard", "Crimes", "Suspects", "Victims", "Evidence", "Reports"].map(
          (item) => (
            <li key={item} onClick={() => onNavigate(item)}>
              {item}
            </li>
          )
        )}
      </ul>
    </aside>
  );
};

export default Sidebar;
