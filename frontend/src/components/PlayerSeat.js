import React from "react";
import "../styles/game.css";

function PlayerSeat({
  player,
  points,
  active,
  lastAction,
  delta,
  reason // 🆕 NEW PROP
}) {
  return (
    <div
      className={`player-seat ${active ? "thinking" : ""}`}
      style={{ borderColor: player.color }}
    >
      <h3 style={{ color: player.color }}>{player.name}</h3>
      <p className="role">{player.role}</p>

      <div className="points-wrapper">
        <p className="points">{points} pts</p>

        {delta !== null && delta !== undefined && (
          <span
            className={`delta ${
              delta > 0 ? "delta-plus" : "delta-minus"
            }`}
          >
            {delta > 0 ? `+${delta}` : delta}
          </span>
        )}
      </div>

      {active && <p className="thinking-text">thinking…</p>}

      {/* Action summary */}
      {lastAction && (
        <div className="action-log">
          <p>{lastAction.text}</p>
        </div>
      )}

      {/* 🧠 Reason (temporary, dramatic) */}
      {reason && (
        <div className="action-reason">
          <span>🧠 {reason}</span>
        </div>
      )}
    </div>
  );
}

export default PlayerSeat;
