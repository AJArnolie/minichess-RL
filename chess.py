import time
import random
from PIL import Image, ImageTk
from MCTS import MonteCarloTreeSearch, ForwardSearch
from minichess.games.abstract.piece import PieceColor
from minichess.games.silverman45.board import Silverman45ChessBoard
from minichess.games.abstract.board import AbstractBoardStatus
from minichess.players.gardner import RandomPlayer

# Currently running MCTS vs. MCTS
m = MonteCarloTreeSearch(m=50, c=2)
f = ForwardSearch()
game = Silverman45ChessBoard()
p = RandomPlayer()
wld = [0, 0, 0]
turn = random.randint(0, 1)

def update_board():
    global game
    if game.status == AbstractBoardStatus.ONGOING:
        proposed = m.run_sims(game)
        game.push(proposed)
        print(game, proposed, game.active_color)
    return None

def run_game():
    global wld, game, turn
    st = time.time()
    restart_game()
    turn = random.randint(0, 1)
    val = None
    while game.status == AbstractBoardStatus.ONGOING and val == None:
        val = update_board()
    if game.status == AbstractBoardStatus.BLACK_WIN: wld[turn] += 1
    elif game.status == AbstractBoardStatus.WHITE_WIN: wld[1 - turn] += 1
    else: wld[2] += 1
    print("Game Time Length: ", time.time() - st)
    
def run_100_games():
    for i in range(100):
        print("Game", i+1)
        print(game)
        run_game()
        restart_game()

def restart_game():
    global game, turn
    game = Silverman45ChessBoard()
    turn = random.randint(0, 1)

if __name__ == "__main__":
    run_100_games()
