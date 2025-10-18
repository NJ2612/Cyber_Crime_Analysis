import React, { useState } from "react";
import "../App.css";

const Profile = () => {
  const [user, setUser] = useState({
    name: "Admin",
    email: "admin@sentinel.com",
    role: "Administrator",
    phone: "9876543210",
  });

  const handleChange = (e) => setUser({ ...user, [e.target.name]: e.target.value });

  return (
    <div>
      <h1>Profile</h1>
      <p>View and update your account information.</p>

      <div className="card">
        <div className="form-group">
          <label>Name</label>
          <input name="name" value={user.name} onChange={handleChange} />
        </div>

        <div className="form-group">
          <label>Email</label>
          <input name="email" value={user.email} onChange={handleChange} />
        </div>

        <div className="form-group">
          <label>Phone</label>
          <input name="phone" value={user.phone} onChange={handleChange} />
        </div>

        <div className="form-group">
          <label>Role</label>
          <input name="role" value={user.role} readOnly />
        </div>

        <button className="save-btn">Save Changes</button>
      </div>
    </div>
  );
};

export default Profile;
