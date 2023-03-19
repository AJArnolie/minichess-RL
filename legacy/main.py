from MCTS import MonteCarloTreeSearch
from minichess.games.silverman45.board import Silverman45ChessBoard
from minichess.games.abstract.board import AbstractBoardStatus
from minichess.players.gardner import RandomPlayer

if __name__ == "__main__":
    m = MonteCarloTreeSearch()
    game = Silverman45ChessBoard()
    p = RandomPlayer()
    turn = 0

    while game.status == AbstractBoardStatus.ONGOING:
        print(game)
        print("---")
        actions = game.legal_actions()
        for a in actions:
            print(a)
        if turn == 0:
            _, proposed = p.propose_action(game, None, game.legal_action_mask())
        if turn == 1:
            proposed = m.run_sims(game)
        if turn == 0:
            print("MOVE (Random):", proposed)
        if turn == 1:
            print("MOVE (MCTS):", proposed)
        turn = 1 - turn
        game.push(proposed)
        input()

        print('+---------------+')

    print(game)
    print(game.status)



