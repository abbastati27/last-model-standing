import random
from copy import deepcopy
from shutil import move
from app.game.state import initial_game_state, PLAYERS
from app.game.rules import (
    apply_repeated_target_penalty,
    apply_mutual_alliance_cap,
    sanitize_move
)
from app.llm.client import get_player_move
from app.logs.move_logger import log_move


class GameEngine:
    def __init__(self):
        self.state = None

    def start_new_game(self, predicted_winner: str):
        self.state = initial_game_state(predicted_winner)

    def get_state(self):
        return self.state

    def reset(self):
        self.state = None

    # ---------------------------
    # Realtime round start
    # ---------------------------
    def start_round(self, round_number: int):
        if round_number != self.state.round + 1:
            return {"error": "Invalid round order"}

        self.state.round = round_number
        self.state.turn_index = 0

        self.state.round_order = sorted(
            self.state.players.keys(),
            key=lambda p: self.state.players[p].points
        )

        return {
            "round": round_number,
            "order": self.state.round_order,
            "starting_player": self.state.round_order[0]
        }

    # ---------------------------
    # Realtime single move
    # ---------------------------
    def play_next_move(self):
        if self.state.turn_index >= len(self.state.round_order):
            return {"round_complete": True}

        player = self.state.round_order[self.state.turn_index]

        before_points = {
            p: self.state.players[p].points
            for p in self.state.players
        }

        ai_input_state = deepcopy(self.state.dict())
        move = get_player_move(player, ai_input_state)

        raw_take = move.get("take_from")
        raw_give = move.get("give_to")
        reason = move.get("reason", "")

        take_from, give_to = sanitize_move(player, move, PLAYERS)

        corrected = {
            "take_from_corrected": take_from != raw_take,
            "give_to_corrected": give_to != raw_give
        }

        # ---- RULE RESOLUTION ----
        transfer_requested = 2

        # repeated target penalty
        transfer_after_repeat = apply_repeated_target_penalty(
            self.state.round,
            self.state.history,
            player,
            take_from,
            transfer_requested
        )

        # mutual alliance cap (must pass THIS round actions)
        transfer_final = apply_mutual_alliance_cap(
            self.state.history,
            player,
            give_to,
            transfer_after_repeat
        )

        transfer_final = max(0, min(2, transfer_final))

    # ---- APPLY TRANSFER (NO SELF TAX) ----
        self.state.players[take_from].points -= transfer_final
        self.state.players[give_to].points += transfer_final

        after_points = {
            p: self.state.players[p].points
            for p in self.state.players
        }

        deltas = {
            p: after_points[p] - before_points[p]
            for p in before_points
            if after_points[p] != before_points[p]
        }

        log = {
            "round": self.state.round,
            "turn_index": self.state.turn_index,
            "player": player,
            "turn_order": self.state.round_order,

            "ai_input": {
                "visible_state": ai_input_state
            },

            "ai_output": {
                "raw_take_from": raw_take,
                "raw_give_to": raw_give,
                "reason": reason
            },

            "engine_resolution": {
                "final_take_from": take_from,
                "final_give_to": give_to,
                **corrected
            },

            "rule_effects": {
                "transfer_requested": 2,
                "transfer_applied": transfer_final
            },

            "points_before": before_points,
            "points_after": after_points,
            "deltas": deltas
        }

        self.state.history.append({
            "round": self.state.round,
            "player": player,
            "take_from": take_from,
            "give_to": give_to,
            "amount": transfer_final,
            "reason": reason
        })

        log_move(log)

        self.state.turn_index += 1

        next_player = (
            self.state.round_order[self.state.turn_index]
            if self.state.turn_index < len(self.state.round_order)
            else None
        )

        return {
            "round_complete": False,
            "move": {
                "player": player,
                "take_from": take_from,
                "give_to": give_to,
                "amount": transfer_final,
                "reason": reason
            },
            "next_player": next_player,
            "points": after_points
        }    

