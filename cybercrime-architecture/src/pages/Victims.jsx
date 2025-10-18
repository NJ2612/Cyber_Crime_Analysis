import React, { useEffect, useState } from "react";
import "./Victims.css";

const Victims = () => {
  const [list, setList] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editIndex, setEditIndex] = useState(null);
  const [form, setForm] = useState({ name: "", age: "", gender: "", address: "" });

  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem("victims")) || [
      { id: 1, name: "Victim 1", age: 29, gender: "F", address: "Unknown" },
    ];
    setList(stored);
  }, []);

  useEffect(() => localStorage.setItem("victims", JSON.stringify(list)), [list]);

  const openAdd = () => {
    setEditIndex(null);
    setForm({ name: "", age: "", gender: "", address: "" });
    setShowModal(true);
  };

  const save = () => {
    if (!form.name) return alert("Name required");
    if (editIndex !== null) {
      setList(list.map((v, i) => (i === editIndex ? { ...v, ...form } : v)));
    } else {
      const id = list.length ? list[list.length - 1].id + 1 : 1;
      setList([...list, { id, ...form }]);
    }
    setShowModal(false);
  };

  const edit = (i) => {
    setEditIndex(i);
    setForm(list[i]);
    setShowModal(true);
  };

  const remove = (i) => {
    if (window.confirm("Delete victim?")) setList(list.filter((_, idx) => idx !== i));
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <div className="breadcrumb">Home / Victims</div>
          <h1>Victims</h1>
        </div>
        <div className="actions">
          <button className="add-btn" onClick={openAdd}>
            + Add Victim
          </button>
        </div>
      </div>

      <table className="styled-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Age</th>
            <th>Gender</th>
            <th>Address</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {list.length === 0 ? (
            <tr>
              <td colSpan="6" style={{ textAlign: "center" }}>
                No victims
              </td>
            </tr>
          ) : (
            list.map((v, i) => (
              <tr key={v.id}>
                <td>{v.id}</td>
                <td>{v.name}</td>
                <td>{v.age}</td>
                <td>{v.gender}</td>
                <td>{v.address}</td>
                <td>
                  <button className="edit-btn" onClick={() => edit(i)}>
                    Edit
                  </button>
                  <button className="delete-btn" onClick={() => remove(i)}>
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
            <h2>{editIndex !== null ? "Edit Victim" : "Add Victim"}</h2>
            <input
              placeholder="Name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
            <input
              placeholder="Age"
              type="number"
              value={form.age}
              onChange={(e) => setForm({ ...form, age: e.target.value })}
            />
            <input
              placeholder="Gender"
              value={form.gender}
              onChange={(e) => setForm({ ...form, gender: e.target.value })}
            />
            <input
              placeholder="Address"
              value={form.address}
              onChange={(e) => setForm({ ...form, address: e.target.value })}
            />
            <div className="modal-buttons">
              <button className="save-btn" onClick={save}>
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

export default Victims;
