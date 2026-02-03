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

  if (!state) return <p>Loading…</p>;

  const winner = Object.entries(state.players)
    .sort((a, b) => b[1].points - a[1].points)[0][0];

  const guessedCorrectly = state.predicted_winner === winner;

  const mood = guessedCorrectly
    ? {
        bg: "#0f5132",
        title: "YOU WON 🎉",
        subtitle: "Your prediction was spot on!",
        feedback: "🔥 Nailed it. You read the game perfectly.",
      }
    : {
        bg: "#842029",
        title: "YOU LOST 💔",
        subtitle: "The game had other plans.",
        feedback: "😬 Oof. Happens to the best of us.",
      };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: mood.bg,
        color: "#fff",
        textAlign: "center",
        padding: "50px 20px",
        paddingBottom: "-100px",
        marginTop: "-60px",
        // marginBottom: "-550px",
      }}
    >
      {/* Main Emotion */}
      <h1 style={{ fontSize: "3rem", marginBottom: "10px" }}>
        {mood.title}
      </h1>

      <p style={{ fontSize: "1.2rem", opacity: 0.9 }}>
        {mood.subtitle}
      </p>

      <hr style={{ margin: "30px auto", width: "60%", opacity: 0.3 }} />

      {/* Actual Winner */}
      <h2 style={{ color: PLAYERS[winner].color }}>
        🏆 {PLAYERS[winner].name} WON THE GAME
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

      {/* Prediction Feedback */}
      <div
        style={{
          marginTop: "30px",
          padding: "20px",
          borderRadius: "12px",
          background: guessedCorrectly
            ? "rgba(25,135,84,0.2)"
            : "rgba(220,53,69,0.2)",
        }}
      >
        <h3>Your Prediction</h3>
        <p>
          You backed{" "}
          <strong>{PLAYERS[state.predicted_winner].name}</strong>
        </p>
        <p style={{ fontSize: "1.1rem" }}>{mood.feedback}</p>
      </div>

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
