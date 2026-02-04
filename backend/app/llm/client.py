import requests
import json
import random
import re
from app.llm.prompts import BASE_RULES, PLAYER_PROMPTS

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"

JSON_REGEX = re.compile(r"\{[\s\S]*\}")


def extract_json(text: str) -> dict | None:
    match = JSON_REGEX.search(text)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


def get_player_move(player_id: str, game_state: dict) -> dict:
    try:
        prompt = f"""
{BASE_RULES}

{PLAYER_PROMPTS[player_id]}

CURRENT GAME STATE:
{json.dumps(game_state, indent=2)}

FINAL INSTRUCTION (MOST IMPORTANT):
- Respond with ONE valid JSON object
- No text before or after JSON
- No markdown
- No explanation outside JSON

JSON ONLY:
{{
  "take_from": "A",
  "give_to": "B",
  "reason": "short explanation focused on my advantage"
}}
"""

        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            # 🔑 key change: reduce randomness, increase obedience
            "options": {
                "temperature": 0.4,
                "top_p": 0.9,
                "num_predict": 120
            }
        }

        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()

        raw_text = response.json().get("response", "")
        move = extract_json(raw_text)

        if not move:
            raise ValueError("No valid JSON returned")

        if not all(k in move for k in ("take_from", "give_to", "reason")):
            raise ValueError("Missing required keys")

        return {
            "take_from": move["take_from"],
            "give_to": move["give_to"],
            "reason": move["reason"]
        }

    except Exception:
        # SAFE FALLBACK (RULE COMPLIANT)
        players = list(game_state["players"].keys())
        others = [p for p in players if p != player_id]

        take_from = random.choice(others)
        give_to = random.choice([p for p in others if p != take_from])

        return {
            "take_from": take_from,
            "give_to": give_to,
            "reason": "Fallback move due to invalid LLM output."
        }
