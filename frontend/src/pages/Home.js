import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { startGame } from "../api/gameApi";
import { PLAYERS } from "../constants/players";

function Home() {
  const [selected, setSelected] = useState(null);
  const navigate = useNavigate();

  async function handleStart() {
    if (!selected) return alert("Select a winner first");
    await startGame(selected);
    navigate("/play");
  }

  return (
    <div style={{ padding: "40px", textAlign: "center" }}>
      <h1>Last Model Standing</h1>
      <p>A strategic AI alliance game</p>

      <h2>Select your predicted winner</h2>

      <div style={{ display: "flex", justifyContent: "center", gap: "20px" }}>
        {Object.entries(PLAYERS).map(([id, p]) => (
          <div
            key={id}
            onClick={() => setSelected(id)}
            style={{
              border: selected === id ? `2px solid ${p.color}` : "1px solid gray",
              padding: "12px",
              cursor: "pointer"
            }}
          >
            <h3 style={{ color: p.color }}>{p.name}</h3>
            <p style={{ fontWeight: "bold" }}>{p.role}</p>
            <p style={{ fontSize: "13px", opacity: 0.8, maxWidth: "200px" }}>
              {p.description}
            </p>
          </div>
        ))}
      </div>

      <button className="game-button" onClick={handleStart}>
        Enter the Arena
      </button>
    </div>
  );
}

export default Home;
