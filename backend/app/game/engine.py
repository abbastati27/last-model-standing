import random
from copy import deepcopy
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

    # -------------------------------------------------
    # Game lifecycle
    # -------------------------------------------------
    def start_new_game(self, predicted_winner: str | None = None):
        # predicted_winner is intentionally ignored for gameplay fairness
        self.state = initial_game_state(predicted_winner)

    def get_state(self):
        return self.state

    def reset(self):
        self.state = None

    # -------------------------------------------------
    # Round start (realtime)
    # -------------------------------------------------
    def start_round(self, round_number: int):
        if round_number != self.state.round + 1:
            return {"error": "Invalid round order"}

        self.state.round = round_number
        self.state.turn_index = 0

        # Lowest points start first
        self.state.round_order = sorted(
            self.state.players.keys(),
            key=lambda p: self.state.players[p].points
        )

        return {
            "round": round_number,
            "order": self.state.round_order,
            "starting_player": self.state.round_order[0]
        }

    # -------------------------------------------------
    # Single move execution (realtime)
    # -------------------------------------------------
    def play_next_move(self):
        if self.state.turn_index >= len(self.state.round_order):
            return {"round_complete": True}

        player = self.state.round_order[self.state.turn_index]

        # Snapshot BEFORE move (for deltas & logs)
        before_points = {
            p: self.state.players[p].points
            for p in self.state.players
        }

        # AI should NOT see predicted winner
        ai_input_state = deepcopy(self.state.dict())
        ai_input_state.pop("predicted_winner", None)

        move = get_player_move(player, ai_input_state)

        raw_take = move.get("take_from")
        raw_give = move.get("give_to")
        reason = move.get("reason", "")

        # Sanitize invalid/self targets
        take_from, give_to = sanitize_move(player, move, PLAYERS)

        corrected = {
            "take_from_corrected": raw_take != take_from,
            "give_to_corrected": raw_give != give_to
        }

        # -------------------------------------------------
        # RULE APPLICATION PIPELINE
        # -------------------------------------------------
        BASE_TRANSFER = 2

        # Repeated target penalty
        after_repeat = apply_repeated_target_penalty(
            self.state.round,
            self.state.history,
            player,
            take_from,
            BASE_TRANSFER
        )

        # Mutual alliance cap (round-local, not full history)
        final_transfer = apply_mutual_alliance_cap(
            [],
            player,
            give_to,
            after_repeat
        )

        final_transfer = max(0, min(BASE_TRANSFER, final_transfer))

        # -------------------------------------------------
        # APPLY POINTS (NO SELF TAX)
        # -------------------------------------------------
        self.state.players[take_from].points -= final_transfer
        self.state.players[give_to].points += final_transfer

        # Snapshot AFTER move
        after_points = {
            p: self.state.players[p].points
            for p in self.state.players
        }

        deltas = {
            p: after_points[p] - before_points[p]
            for p in before_points
            if after_points[p] != before_points[p]
        }

        # -------------------------------------------------
        # STRUCTURED LOGGING
        # -------------------------------------------------
        log = {
            "round": self.state.round,
            "turn_index": self.state.turn_index,
            "player": player,
            "turn_order": self.state.round_order,

            "ai_input": ai_input_state,

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
                "base_transfer": BASE_TRANSFER,
                "transfer_after_repeat": after_repeat,
                "final_transfer": final_transfer
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
            "amount": final_transfer,
            "reason": reason
        })

        log_move(log)

        # Advance turn
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
                "amount": final_transfer,
                "reason": reason
            },
            "next_player": next_player,
            "points": after_points
        }
