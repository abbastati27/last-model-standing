from typing import Dict, List, Optional
from pydantic import BaseModel

PLAYERS = ["A", "B", "C", "D", "E"]


class PlayerState(BaseModel):
    points: int = 20


class GameState(BaseModel):
    round: int = 0

    # Core game data
    players: Dict[str, PlayerState]
    history: List[dict] = []

    # Turn mechanics
    round_order: List[str] = []
    turn_index: int = 0

    # 🔑 User-only meta (NOT shown to AI)
    predicted_winner: Optional[str] = None

    # 🔒 Private perceptions (AI-visible, but no meta)
    perceptions: Dict[str, dict] = {}


def build_perceptions(players: Dict[str, PlayerState]) -> Dict[str, dict]:
    """
    Build player-relative threat perceptions.
    No global winner. No shared labels.
    """
    perceptions = {}

    for me, my_state in players.items():
        ahead = []
        close = []
        safe = []

        for other, other_state in players.items():
            if other == me:
                continue

            diff = other_state.points - my_state.points

            if diff >= 3:
                ahead.append(other)
            elif -2 <= diff <= 2:
                close.append(other)
            else:
                safe.append(other)

        perceptions[me] = {
            "ahead_of_me": ahead,
            "close_to_me": close,
            "safe_for_now": safe
        }

    return perceptions


def initial_game_state(predicted_winner: Optional[str] = None) -> GameState:
    players = {p: PlayerState() for p in PLAYERS}

    return GameState(
        round=0,
        players=players,
        history=[],
        round_order=[],
        turn_index=0,
        predicted_winner=predicted_winner,
        perceptions=build_perceptions(players)
    )
