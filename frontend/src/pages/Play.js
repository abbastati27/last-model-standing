import React, { useEffect, useState } from "react";
import { getGameState } from "../api/gameApi";
import { useNavigate } from "react-router-dom";
import TableLayout from "../components/TableLayout";
import { PLAYERS } from "../constants/players";

const API_BASE = "http://localhost:8000";

function Play() {
  const navigate = useNavigate();

  const [state, setState] = useState({
    round: 0,
    players: null,
    history: []
  });

  const [activePlayer, setActivePlayer] = useState(null);
  const [lastActions, setLastActions] = useState({});
  const [pointDeltas, setPointDeltas] = useState({});
  const [visibleReason, setVisibleReason] = useState(null);
  const [loading, setLoading] = useState(false);

  // ---------------------------
  // Load game state
  // ---------------------------
  useEffect(() => {
    loadState();
  }, []);

  async function loadState() {
    const data = await getGameState();
    setState(data);
  }

  // ---------------------------
  // Start round
  // ---------------------------
  async function startRound() {
    if (loading) return;

    setLastActions({});
    setPointDeltas({});
    setVisibleReason(null);
    setLoading(true);

    const nextRound = state.round + 1;

    const res = await fetch(
      `${API_BASE}/game/round/${nextRound}/start`,
      { method: "POST" }
    );

    const data = await res.json();
    setActivePlayer(data.starting_player);

    runNextMove();
  }

  // ---------------------------
  // Step-by-step moves
  // ---------------------------
  async function runNextMove() {
    const res = await fetch(`${API_BASE}/game/round/next-move`, {
      method: "POST"
    });

    const data = await res.json();

    // round finished
    if (data.round_complete) {
      setActivePlayer(null);
      setLoading(false);
      await loadState();

      if (state.round + 1 >= 5) {
        navigate("/result");
      }
      return;
    }

    // thinking indicator
    setActivePlayer(data.next_player || null);

    // ---------------------------
    // Store action + reason
    // ---------------------------
    if (data.move && PLAYERS[data.move.player]) {
      const actionText = `${PLAYERS[data.move.player].name} took from ${PLAYERS[data.move.take_from].name} and gave to ${PLAYERS[data.move.give_to].name}`;

      setLastActions(prev => ({
        ...prev,
        [data.move.player]: {
          text: actionText,
          reason: data.move.reason
        }
      }));

      // show reason synced with delta animation
      setVisibleReason({
        player: data.move.player,
        text: data.move.reason
      });

      // auto-hide reason after animation window
      setTimeout(() => setVisibleReason(null), 8000);
    }

    // ---------------------------
    // Update players (authoritative)
    // ---------------------------
    const newPlayers = Object.fromEntries(
      Object.entries(data.points).map(([id, pts]) => [
        id,
        { points: pts }
      ])
    );

    setState(prev => ({
      ...prev,
      players: newPlayers
    }));

    // ---------------------------
    // PER-MOVE DELTAS
    // ---------------------------
    if (data.move && typeof data.move.amount === "number") {
      setPointDeltas({
        [data.move.take_from]: -data.move.amount,
        [data.move.give_to]: data.move.amount
      });

      // clear deltas after animation
      setTimeout(() => setPointDeltas({}), 1400);
    }

    // next move
    setTimeout(runNextMove, 1200);
  }

  // ---------------------------
  // Guard
  // ---------------------------
  if (!state.players) {
    return (
      <p style={{ color: "white", textAlign: "center" }}>
        Loading game…
      </p>
    );
  }

  // ---------------------------
  // Render
  // ---------------------------
  return (
    <div>
      <h2 style={{ textAlign: "center" }}>
        Round {state.round + 1}
      </h2>

      <TableLayout
        players={state.players}
        activePlayer={activePlayer}
        lastActions={lastActions}
        pointDeltas={pointDeltas}
        visibleReason={visibleReason}
      />

      <div style={{ textAlign: "center", marginTop: "-100px" }}>
        <button
          className="game-button"
          onClick={startRound}
          disabled={loading}
        >
          {state.round === 0
            ? "Begin Round 1"
            : `Begin Round ${state.round + 1}`}
        </button>
      </div>
    </div>
  );
}

export default Play;
