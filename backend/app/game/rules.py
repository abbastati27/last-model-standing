import random
from collections import Counter


# -------------------------------------------------
# REPEATED TARGET PENALTY (ESCALATING)
# -------------------------------------------------
def apply_repeated_target_penalty(
    current_round: int,
    history: list,
    actor: str,
    target: str,
    steal_amount: int
) -> int:
    """
    Penalize repeatedly attacking the same target
    across consecutive rounds.

    Round 1: no penalty
    2nd consecutive hit: steal = 1
    3rd+ consecutive hit: steal = 0
    """
    if current_round <= 1:
        return steal_amount

    # Count how many consecutive rounds actor attacked target
    consecutive_hits = 0
    for r in range(current_round - 1, 0, -1):
        found = False
        for log in history:
            if (
                log["round"] == r
                and log["player"] == actor
                and log["take_from"] == target
            ):
                consecutive_hits += 1
                found = True
                break
        if not found:
            break

    if consecutive_hits >= 2:
        return 0
    if consecutive_hits == 1:
        return 1

    return steal_amount


# -------------------------------------------------
# MUTUAL ALLIANCE CAP (STRONGER)
# -------------------------------------------------
def apply_mutual_alliance_cap(
    history: list,
    actor: str,
    give_to: str,
    amount: int
) -> int:
    """
    Prevent strong mutual point farming.

    If actor and give_to exchanged points
    in the previous round → cap to 1.
    If they did it in TWO consecutive rounds → cap to 0.
    """
    if not history:
        return amount

    last_round = max(h["round"] for h in history)

    def helped(a, b, r):
        return any(
            h["round"] == r and h["player"] == a and h["give_to"] == b
            for h in history
        )

    mutual_last = helped(actor, give_to, last_round) and helped(give_to, actor, last_round)
    mutual_prev = helped(actor, give_to, last_round - 1) and helped(give_to, actor, last_round - 1)

    if mutual_last and mutual_prev:
        return 0
    if mutual_last:
        return min(1, amount)

    return amount


# -------------------------------------------------
# TARGET FATIGUE (ANTI DOG-PILE)
# -------------------------------------------------
def apply_target_fatigue(
    history: list,
    target: str,
    amount: int
) -> int:
    """
    Reduce steal amount if a target
    has been attacked by MANY players
    in the previous round.
    """
    if not history:
        return amount

    last_round = max(h["round"] for h in history)
    attackers = {
        h["player"]
        for h in history
        if h["round"] == last_round and h["take_from"] == target
    }

    if len(attackers) >= 3:
        return max(0, amount - 1)

    return amount


# -------------------------------------------------
# SANITIZE MOVE (STRICT)
# -------------------------------------------------
def sanitize_move(player, move, players):
    take_from = move.get("take_from")
    give_to = move.get("give_to")

    valid_targets = [p for p in players if p != player]

    # Fix invalid take
    if take_from not in valid_targets:
        take_from = random.choice(valid_targets)

    # Fix invalid give
    if give_to not in valid_targets:
        give_to = random.choice(valid_targets)

    # Fix take == give
    if take_from == give_to:
        give_to = random.choice([p for p in valid_targets if p != take_from])

    return take_from, give_to
