"""Local SquareXO Pygame session."""

from dataclasses import dataclass, field

from src.platform.blockchain.domain.result import ReplayVerificationRequest
from src.platform.games import GameExitAction, GameExitResult, GameLaunchOptions

from src.games.square_xo.domain.board import create_game
from src.games.square_xo.domain.move import ClaimEdge
from src.games.square_xo.domain.replay import envelope_for_replay
from src.games.square_xo.domain.rules import apply_move
from src.games.square_xo.view.gameplay_scene import draw_gameplay, edge_from_mouse
from src.games.square_xo.view.hud import status_line


@dataclass
class SquareXOLocalSession:
    context: object
    launch_options: GameLaunchOptions
    moves: list[ClaimEdge] = field(default_factory=list)

    def run(self) -> GameExitResult:
        import pygame

        rows = int(self.launch_options.custom.get("rows", 4))
        cols = int(self.launch_options.custom.get("cols", 4))
        blockchain_mode = str(self.launch_options.custom.get("blockchain_mode", "LOCAL_MOCK"))
        state = create_game(rows, cols)
        hover = None

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return GameExitResult(GameExitAction.QUIT)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return self._exit_result(state)
                    if event.key == pygame.K_r:
                        state = create_game(rows, cols)
                        self.moves.clear()
                if event.type == pygame.MOUSEMOTION and not state.is_terminal:
                    hover = edge_from_mouse(pygame, self.context.screen, state, event.pos)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not state.is_terminal:
                    edge = edge_from_mouse(pygame, self.context.screen, state, event.pos)
                    if edge is not None:
                        move = ClaimEdge(edge=edge, player=state.current_player)
                        try:
                            state = apply_move(state, move)
                            self.moves.append(move)
                        except ValueError:
                            continue

            draw_gameplay(pygame, self.context.screen, state, hover, status_line(state, blockchain_mode))
            pygame.display.flip()
            self.context.clock.tick(60)

    def _exit_result(self, state):
        if not self.moves:
            return GameExitResult(GameExitAction.GAME_LIBRARY, {"game_id": "square_xo"})
        initial = create_game(state.rows, state.cols)
        envelope = envelope_for_replay("local-square-xo", initial, tuple(self.moves))
        verification = None
        if self.context.blockchain is not None:
            verification = self.context.blockchain.result_verifier.verify_replay(ReplayVerificationRequest(envelope))
            if verification.accepted:
                self.context.blockchain.match_registry.submit_result(envelope)
        return GameExitResult(
            GameExitAction.GAME_LIBRARY,
            {
                "game_id": "square_xo",
                "result_hash": envelope.digest(),
                "verified": bool(verification.accepted) if verification else False,
            },
        )
