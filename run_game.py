from minichess.games.silverman45.board import Silverman45ChessBoard
from minichess.games.abstract.board import AbstractBoardStatus
from minichess.players.gardner import RandomPlayer

# This needs to update 
def simulate(policy=None, game=None):
    game = Silverman45ChessBoard() if game == None else game
    p = RandomPlayer() if policy == None else policy

    while game.status == AbstractBoardStatus.ONGOING:
        print(game)
        print(game.state_representation())
        input()
        print("---")
        print(game.condensed_legal_actions())
        print("---")
        _, proposed = p.propose_action(game, None, game.legal_action_mask())
        print(type(proposed), proposed)
        print("MOVE:", proposed)
        game.push(proposed)

        print('+---------------+')

    print(game)
    print(game.status)


if __name__ == "__main__":
    simulate()

