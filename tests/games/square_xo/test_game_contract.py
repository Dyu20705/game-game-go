from src.games.square_xo.game import SquareXOGame
from src.games.square_xo.runtime.local_session import SquareXOLocalSession
from src.platform.games import GameCapability, GameLaunchOptions


def test_square_xo_descriptor_capabilities():
    game = SquareXOGame()

    assert game.descriptor.game_id == "square_xo"
    assert GameCapability.LOCAL_PLAY in game.descriptor.capabilities
    assert GameCapability.VERIFIED_RESULT in game.descriptor.capabilities


def test_square_xo_create_session_defaults_to_no_stake_local_mock():
    session = SquareXOGame().create_session(object(), GameLaunchOptions())

    assert isinstance(session, SquareXOLocalSession)
    assert session.launch_options.mode == "local_1v1"
    assert session.launch_options.custom["stake_mode"] == "NO_STAKE"
    assert session.launch_options.custom["blockchain_mode"] == "LOCAL_MOCK"

