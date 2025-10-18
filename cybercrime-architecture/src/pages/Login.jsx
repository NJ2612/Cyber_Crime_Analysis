import React, { useState } from "react";
import "./Login.css";

const Login = ({ onLogin }) => {
  const [form, setForm] = useState({ username: "", password: "" });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (form.username === "admin" && form.password === "admin123") {
      localStorage.setItem("isLoggedIn", true);
      onLogin();
    } else {
      alert("Invalid username or password");
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">
          CyberCrime<span>DB</span>
        </h1>
        <p className="subtitle">Secure Access Portal</p>

        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            required
          />
          <button type="submit">Login</button>
        </form>

        <p className="hint">
          Use <b>admin / admin123</b> to access the dashboard
        </p>
      </div>
    </div>
  );
};

export default Login;
