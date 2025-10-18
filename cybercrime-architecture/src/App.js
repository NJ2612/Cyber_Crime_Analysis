import React, { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Crimes from "./pages/Crimes";
import Suspects from "./pages/Suspects";
import Victims from "./pages/Victims";
import Evidence from "./pages/Evidence";
import Reports from "./pages/Reports";
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";
import Login from "./pages/Login";
import "./App.css";

const App = () => {
  const [page, setPage] = useState("Dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("isLoggedIn");
    if (saved) setLoggedIn(true);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("isLoggedIn");
    setLoggedIn(false);
  };

  const renderPage = () => {
    switch (page) {
      case "Dashboard":
        return <Dashboard />;
      case "Crimes":
        return <Crimes />;
      case "Suspects":
        return <Suspects />;
      case "Victims":
        return <Victims />;
      case "Evidence":
        return <Evidence />;
      case "Reports":
        return <Reports />;
      case "Profile":
        return <Profile />;
      case "Settings":
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  if (!loggedIn) {
    return <Login onLogin={() => setLoggedIn(true)} />;
  }

  return (
    <div className="app-container">
      <Sidebar
        onNavigate={(p) => {
          setPage(p);
          setSidebarOpen(false);
        }}
        className={sidebarOpen ? "sidebar active" : "sidebar"}
      />

      <Header
        title={page}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        onNavigate={setPage}
        onLogout={handleLogout}
      />

      {/* Page Transition Wrapper */}
      <main className="main-content">
        <AnimatePresence mode="wait">
          <motion.div
            key={page}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            transition={{ duration: 0.35, ease: "easeInOut" }}
          >
            {renderPage()}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
};

export default App;
