from typing import Dict, List
from pydantic import BaseModel

PLAYERS = ["A", "B", "C", "D", "E"]

class PlayerState(BaseModel):
    points: int = 20

class GameState(BaseModel):
    round: int = 0
    players: Dict[str, PlayerState]
    history: List[dict] = []   # ✅ plain dicts
    predicted_winner: str | None = None

    round_order: list = []
    turn_index: int = 0


def initial_game_state(predicted_winner: str) -> GameState:
    return GameState(
        round=0,
        players={p: PlayerState() for p in PLAYERS},
        history=[],
        predicted_winner=predicted_winner
    )
