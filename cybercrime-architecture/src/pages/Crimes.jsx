import React, { useState, useEffect } from "react";
import "./Crimes.css";

const Crimes = () => {
  const [crimes, setCrimes] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editIndex, setEditIndex] = useState(null);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("date");
  const [newCrime, setNewCrime] = useState({ type: "", location: "", date: "" });

  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem("crimes")) || [
      { id: 1, type: "Cyber Fraud", location: "Delhi", date: "2025-09-14" },
      { id: 2, type: "Data Theft", location: "Mumbai", date: "2025-09-20" },
    ];
    setCrimes(stored);
    setFiltered(stored);
  }, []);

  useEffect(() => localStorage.setItem("crimes", JSON.stringify(crimes)), [crimes]);

  useEffect(() => {
    let data = crimes.filter(
      (c) =>
        c.type.toLowerCase().includes(search.toLowerCase()) ||
        c.location.toLowerCase().includes(search.toLowerCase())
    );

    if (sortBy === "date") {
      data.sort((a, b) => new Date(b.date) - new Date(a.date));
    } else if (sortBy === "location") {
      data.sort((a, b) => a.location.localeCompare(b.location));
    }

    setFiltered(data);
  }, [search, sortBy, crimes]);

  const handleSaveCrime = () => {
    if (!newCrime.type || !newCrime.location || !newCrime.date) {
      alert("Please fill all fields");
      return;
    }

    let updated;
    if (editIndex !== null) {
      updated = crimes.map((crime, i) => (i === editIndex ? { ...crime, ...newCrime } : crime));
      setEditIndex(null);
    } else {
      const newId = crimes.length ? crimes[crimes.length - 1].id + 1 : 1;
      updated = [...crimes, { id: newId, ...newCrime }];
    }

    setCrimes(updated);
    setShowModal(false);
    setNewCrime({ type: "", location: "", date: "" });
  };

  const handleEdit = (index) => {
    setNewCrime(crimes[index]);
    setEditIndex(index);
    setShowModal(true);
  };

  const handleDelete = (index) => {
    if (window.confirm("Are you sure you want to delete this record?")) {
      const updated = crimes.filter((_, i) => i !== index);
      setCrimes(updated);
    }
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <div className="breadcrumb">Home / Crimes</div>
          <h1>Crimes</h1>
        </div>
        <div className="actions">
          <input
            type="text"
            placeholder="Search by type or location..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-box"
          />
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="sort-select">
            <option value="date">Sort by Date</option>
            <option value="location">Sort by Location</option>
          </select>
          <button className="add-btn" onClick={() => setShowModal(true)}>
            + Add New
          </button>
        </div>
      </div>

      <table className="styled-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Location</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filtered.length === 0 ? (
            <tr>
              <td colSpan="5" style={{ textAlign: "center" }}>
                No records found.
              </td>
            </tr>
          ) : (
            filtered.map((crime, index) => (
              <tr key={crime.id}>
                <td>{crime.id}</td>
                <td>{crime.type}</td>
                <td>{crime.location}</td>
                <td>{crime.date}</td>
                <td>
                  <button className="edit-btn" onClick={() => handleEdit(index)}>
                    Edit
                  </button>
                  <button className="delete-btn" onClick={() => handleDelete(index)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>{editIndex !== null ? "Edit Crime" : "Add New Crime"}</h2>
            <input
              type="text"
              placeholder="Crime Type"
              value={newCrime.type}
              onChange={(e) => setNewCrime({ ...newCrime, type: e.target.value })}
            />
            <input
              type="text"
              placeholder="Location"
              value={newCrime.location}
              onChange={(e) => setNewCrime({ ...newCrime, location: e.target.value })}
            />
            <input
              type="date"
              value={newCrime.date}
              onChange={(e) => setNewCrime({ ...newCrime, date: e.target.value })}
            />
            <div className="modal-buttons">
              <button className="save-btn" onClick={handleSaveCrime}>
                {editIndex !== null ? "Update" : "Save"}
              </button>
              <button className="cancel-btn" onClick={() => setShowModal(false)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Crimes;
