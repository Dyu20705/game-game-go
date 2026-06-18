"""SquareXO HUD helpers."""


def status_line(state, blockchain_mode: str) -> str:
    mode = "TESTNET ONLY - NO REAL VALUE" if blockchain_mode == "OASIS_TESTNET" else blockchain_mode
    return f"Mode: local_1v1 | Blockchain: {mode} | Turn: {state.current_player.value}"

