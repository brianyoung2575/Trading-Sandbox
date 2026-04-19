def create_position(direction, entry_price, size=1):
    return {
        "direction": direction,  # "long" or "short"
        "entry_price": entry_price,
        "size": size,
        "pnl": 0.0
    }


def update_position(pos, S):
    if pos["direction"] == "long":
        pos["pnl"] = (S - pos["entry_price"]) * pos["size"]
    else:
        pos["pnl"] = (pos["entry_price"] - S) * pos["size"]

    return pos