import React, { useEffect, useState } from "react";
import { getGameState, resetGame } from "../api/gameApi";
import { useNavigate } from "react-router-dom";
import { PLAYERS } from "../constants/players";

function Result() {
  const [state, setState] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    load();
  }, []);

  async function load() {
    const data = await getGameState();
    setState(data);
  }

  async function restart() {
    await resetGame();
    navigate("/");
  }

  if (!state || !state.players) {
    return <p style={{ textAlign: "center" }}>Loading…</p>;
  }

  // 🏆 Determine winner safely
  const winnerEntry = Object.entries(state.players).sort(
    (a, b) => b[1].points - a[1].points
  )[0];

  const winner = winnerEntry?.[0];

  if (!winner || !PLAYERS[winner]) {
    return (
      <p style={{ textAlign: "center", color: "red" }}>
        Error determining winner.
      </p>
    );
  }

  // 🧠 Prediction may or may not exist
  const hasPrediction = Boolean(state.predicted_winner);
  const guessedCorrectly =
    hasPrediction && state.predicted_winner === winner;

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0f1220",
        color: "#fff",
        textAlign: "center",
        padding: "50px 20px",
      }}
    >
      {/* Title */}
      <h1 style={{ fontSize: "3rem", marginBottom: "10px" }}>
        🏁 Game Over
      </h1>

      {/* Winner */}
      <h2 style={{ color: PLAYERS[winner].color, marginTop: "20px" }}>
        🏆 {PLAYERS[winner].name} WINS
      </h2>

      {/* Scores */}
      <h3 style={{ marginTop: "30px" }}>Final Scores</h3>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {Object.entries(state.players).map(([id, p]) => (
          <li key={id} style={{ margin: "6px 0" }}>
            {PLAYERS[id].name}: <strong>{p.points}</strong> pts
          </li>
        ))}
      </ul>

      {/* Prediction (ONLY if available) */}
      {hasPrediction && PLAYERS[state.predicted_winner] && (
        <div
          style={{
            marginTop: "30px",
            padding: "20px",
            borderRadius: "12px",
            background: guessedCorrectly
              ? "rgba(25,135,84,0.25)"
              : "rgba(220,53,69,0.25)",
          }}
        >
          <h3>Your Prediction</h3>
          <p>
            You predicted{" "}
            <strong>{PLAYERS[state.predicted_winner].name}</strong>
          </p>
          <p style={{ fontSize: "1.1rem" }}>
            {guessedCorrectly
              ? "✅ Spot on. You read the game well."
              : "❌ The game played out differently."}
          </p>
        </div>
      )}

      {/* CTA */}
      <button
        className="game-button"
        style={{ marginTop: "40px" }}
        onClick={restart}
      >
        Play Again
      </button>
    </div>
  );
}

export default Result;
