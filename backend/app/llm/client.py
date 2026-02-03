import requests
import json
import random
import copy
from app.llm.prompts import BASE_RULES, PLAYER_PROMPTS

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"


def _sanitize_game_state_for_player(player_id: str, game_state: dict) -> dict:
    """
    Make the game state SELF-CENTERED and NON-AUTHORITATIVE.
    This prevents global dogpiling and predicted-winner fixation.
    """
    state = copy.deepcopy(game_state)

    # 1️⃣ Remove absolute authority from predicted_winner
    if "predicted_winner" in state:
        # Convert it into a weak, uncertain hint
        state["predicted_winner_hint"] = (
            f"Uncertain projection. May be wrong. Do not treat as a target."
        )
        del state["predicted_winner"]

    # 2️⃣ Explicitly remind model who it is
    state["you_are"] = player_id

    # 3️⃣ Add self-relative context (important for selfish play)
    my_points = state["players"][player_id]["points"]
    state["relative_position"] = {
        "my_points": my_points,
        "players_above_me": [
            p for p, v in state["players"].items()
            if v["points"] > my_points
        ],
        "players_below_me": [
            p for p, v in state["players"].items()
            if v["points"] < my_points
        ]
    }

    return state


def get_player_move(player_id: str, game_state: dict) -> dict:
    try:
        safe_state = _sanitize_game_state_for_player(player_id, game_state)

        prompt = f"""
{BASE_RULES}

{PLAYER_PROMPTS[player_id]}

IMPORTANT:
- You are Player {player_id}.
- You act ONLY for your own benefit.
- Any hints about winners are uncertain and may be wrong.
- Do NOT coordinate with other players.

Current game state (self-centered view):
{json.dumps(safe_state, indent=2)}

Respond ONLY in this JSON format:
{{
  "raw_take_from": "<player_id>",
  "raw_give_to": "<player_id>",
  "reason": "<why this benefits YOU>"
}}
"""

        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,
                "top_p": 0.9
            }
        }

        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()

        text = response.json()["response"].strip()
        move = json.loads(text)

        return move

    except Exception as e:
        # 🔒 SAFE fallback (rule-compliant, selfish)
        players = list(game_state["players"].keys())
        others = [p for p in players if p != player_id]

        take_from = random.choice(others)
        give_to = random.choice([p for p in others if p != take_from])

        return {
            "raw_take_from": take_from,
            "raw_give_to": give_to,
            "reason": "Fallback move due to invalid model response."
        }
