import React, { useEffect, useState } from "react";

const computeHotspots = (crimes) => {
  // count per city
  const map = {};
  crimes.forEach(c => {
    const city = (c.city || c.location || "Unknown").trim();
    map[city] = (map[city] || 0) + 1;
  });
  // normalize scores 0..1
  const max = Math.max(...Object.values(map), 1);
  const rows = Object.entries(map).map(([city, cnt]) => {
    const score = cnt / max;
    const label = score >= 0.6 ? "HIGH" : score >= 0.35 ? "MEDIUM" : "LOW";
    return { city, count: cnt, score: +(score.toFixed(3)), label };
  });
  // sort by score desc
  return rows.sort((a,b)=>b.score-a.score);
};

const Hotspots = () => {
  const [hotspots, setHotspots] = useState([]);

  useEffect(()=>{
    const crimes = JSON.parse(localStorage.getItem("crimes")) || [];
    setHotspots(computeHotspots(crimes));
  }, []);

  return (
    <div>
      <h1>Hotspot Predictions</h1>
      <p>Simple risk scores generated from historical crime counts (demo).</p>
      <table>
        <thead><tr><th>City</th><th>Count</th><th>Risk Score</th><th>Label</th></tr></thead>
        <tbody>
          {hotspots.length===0 ? <tr><td colSpan="4" style={{textAlign:"center"}}>No data</td></tr> :
            hotspots.map(h => (
              <tr key={h.city}>
                <td>{h.city}</td>
                <td>{h.count}</td>
                <td>{h.score}</td>
                <td><strong style={{color: h.label==="HIGH" ? "#b91c1c" : h.label==="MEDIUM" ? "#d97706" : "#047857"}}>{h.label}</strong></td>
              </tr>
            ))
          }
        </tbody>
      </table>
    </div>
  );
};

export default Hotspots;
