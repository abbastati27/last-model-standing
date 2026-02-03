import random



def apply_repeated_target_penalty(
    current_round: int,
    history: list,
    actor: str,
    target: str,
    steal_amount: int
) -> int:
    if current_round <= 1:
        return steal_amount

    last_round = current_round - 1
    for log in history:
        if (
            log["round"] == last_round
            and log["player"] == actor
            and log["take_from"] == target
        ):
            return 1


    return steal_amount


def apply_mutual_alliance_cap(
    history: list,
    actor: str,
    give_to: str,
    amount: int
) -> int:
    """
    If actor and give_to supported each other
    in the previous round, cap transfer to 1.
    """
    if not history:
        return amount

    last_round = max(h["round"] for h in history)

    actor_helped = any(
        h["round"] == last_round
        and h["player"] == actor
        and h["give_to"] == give_to
        for h in history
    )

    give_to_helped = any(
        h["round"] == last_round
        and h["player"] == give_to
        and h["give_to"] == actor
        for h in history
    )

    if actor_helped and give_to_helped:
        return min(1, amount)

    return amount




def sanitize_move(player, move, players):
    take_from = move.get("take_from")
    give_to = move.get("give_to")

    valid_targets = [p for p in players if p != player]

    # Fix self-steal
    if take_from == player or take_from not in players:
        take_from = random.choice(valid_targets)

    # Fix self-give
    if give_to == player or give_to not in players:
        give_to = random.choice(valid_targets)

    # Fix take == give
    if take_from == give_to:
        give_to = random.choice([p for p in valid_targets if p != take_from])

    return take_from, give_to