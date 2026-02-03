import React from "react";
import PlayerSeat from "./PlayerSeat";
import { PLAYERS } from "../constants/players";
import "../styles/game.css";

function TableLayout({
  players,
  activePlayer,
  lastActions,
  pointDeltas,
  visibleReason   // 🆕 NEW
}) {
  return (
    <div className="table">
      {Object.entries(PLAYERS).map(([id, meta], index) => (
        <div key={id} className={`seat seat-${index}`}>
          <PlayerSeat
            player={meta}
            points={players[id]?.points ?? 0}
            active={activePlayer === id}
            lastAction={lastActions[id] || null}
            delta={pointDeltas[id] || null}
            reason={
              visibleReason && visibleReason.player === id
                ? visibleReason.text
                : null
            }   // 🆕 only show for acting player
          />
        </div>
      ))}

      <div className="table-center">
        <p>
          ALLIANCE
          <br />
          TABLE
        </p>
      </div>
    </div>
  );
}

export default TableLayout;
