import tkinter
import time
from tkinter import *
from PIL import Image, ImageTk
from MCTS import MonteCarloTreeSearch
from minichess.games.silverman45.board import Silverman45ChessBoard
from minichess.games.abstract.board import AbstractBoardStatus
from minichess.players.gardner import RandomPlayer

DARK_COLOR = "#ebecd0"
LIGHT_COLOR = "#779556"
IMAGE_PREFIX = "./images/"
IMAGE_TYPE = ".png"

image_names = ["white_pawn", "white_rook", "white_queen", "white_king", "black_pawn", "black_rook", "black_queen", "black_king"]

m = MonteCarloTreeSearch()
game = Silverman45ChessBoard()
p = RandomPlayer()
turn = 0
# ----------------------------------------

def possible_actions_string():
    global m
    global game
    s = "Possible Actions:\n"
    actions = game.legal_actions()
    info = m.get_move_info(game)
    for i in range(len(actions)):
        s += str(i+1) + ". " + str(actions[i]) + " --- Q(s, a) = " + str(info[i][0]) + ",  N(s, a) = " + str(info[i][1]) + "\n"
    return s

root = Tk()
root.geometry("1000x700")
root.resizable(False, False)
images = [PhotoImage(file = IMAGE_PREFIX + i + IMAGE_TYPE) for i in image_names]

game_status_var = StringVar(root, "Game Status: AbstractBoardStatus.ONGOING\n")
white_utility_var = StringVar(root, "White Utility: 0.0")
black_utility_var = StringVar(root, "Black Utility: -0.0\n")
possible_actions_var = StringVar(root, possible_actions_string())

# Establish Main Frames
top_frame = Frame(root, width=1000, height=50, pady=3)
center = Frame(root, bg='gray2', width=1000, height=40, padx=3, pady=3)
btm_frame = Frame(root, bg='white', width=1000, height=45, pady=3)

# layout all of the main containers
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

top_frame.grid(row=0, sticky="ew")
center.grid(row=1, sticky="nsew")
btm_frame.grid(row=3, sticky="ew")

# create the widgets for the top frame
title_label = Label(root, text='Silverman 4X5 Minichess Simulator', font=('Modern', 18, 'bold'))
title_label.grid(row=0, columnspan=3)

# create the center widgets
center.grid_rowconfigure(0, weight=1)
center.grid_columnconfigure(1, weight=1)

board = Frame(center, width=480, height=600)
board_tiles = [[None for _ in range(4)] for _ in range(5)]
board_images = [[None for _ in range(4)] for _ in range(5)]

img = PhotoImage(file = "./images/black_king.png")

l = game.populate_board()
for i in range(5):
    for j in range(4):
        board_tiles[i][j] = Canvas(board, bg=(DARK_COLOR if (i+j) % 2 == 0 else LIGHT_COLOR), 
                                        width=120, height=120, highlightthickness=0)
        if l[i*4+j] != None:
            board_tiles[i][j].create_image(60, 60, image=images[l[i*4+j]])
        board_tiles[i][j].grid(column=j, row=i)

ctr_mid = Frame(center, width=250, height=600, padx=3, pady=3)
game_status = Label(ctr_mid, textvariable=game_status_var, font=('Modern', 16, 'bold'), justify=LEFT, anchor="w")
white_utility = Label(ctr_mid, textvariable=white_utility_var, font=('Modern', 16, 'bold'), justify=LEFT, anchor="w")
black_utility = Label(ctr_mid, textvariable=black_utility_var, font=('Modern', 16, 'bold'), justify=LEFT, anchor="w")
possible_actions = Label(ctr_mid, textvariable=possible_actions_var, font=('Modern', 16, 'bold'), justify=LEFT, anchor="w")

game_status.grid(sticky = W, column=0, row=0)
white_utility.grid(sticky = W, column=0, row=1)
black_utility.grid(sticky = W, column=0, row=2)
possible_actions.grid(sticky = W, column=0, row=3)

ctr_right = Frame(center, width=100, height=600, padx=3, pady=3)

board.grid(row=0, column=0, sticky="ns", pady=10)
ctr_mid.grid(row=0, column=1, sticky="nsew")
ctr_right.grid(row=0, column=2, sticky="ns")


def update_board():
    global game, turn, board_tiles
    global game_status_var, white_utility_var, black_utility_var

    possible_actions_var.set(possible_actions_string())
    if game.status == AbstractBoardStatus.ONGOING:
        if turn == 0:
            _, proposed = p.propose_action(game, None, game.legal_action_mask())
            print("MOVE (Random):", proposed)
        if turn == 1:
            proposed = m.run_sims(game)
            print("MOVE (MCTS):", proposed)
        turn = 1 - turn
        game.push(proposed)
    l = game.populate_board()
    for i in range(len(l)):
        board_tiles[i // 4][i % 4].delete('all')
        if l[i] != None: board_tiles[i // 4][i % 4].create_image(60, 60, image=images[l[i]])
    game_status_var.set('Game Status: ' + str(game.status) + "\n")
    white_utility_var.set('White Utility: ' + str(game.get_white_utility()))
    black_utility_var.set('Black Utility: ' + str(game.get_black_utility()) + "\n")

def run_game():
    global root
    global game, turn, board_tiles
    global game_status_var, white_utility_var, black_utility_var

    while game.status == AbstractBoardStatus.ONGOING:
        if turn == 0:
            _, proposed = p.propose_action(game, None, game.legal_action_mask())
            print("MOVE (Random):", proposed)
        if turn == 1:
            proposed = m.run_sims(game)
            print("MOVE (MCTS):", proposed)
        turn = 1 - turn
        game.push(proposed)
        l = game.populate_board()
        for i in range(len(l)):
            board_tiles[i // 4][i % 4].delete('all')
            if l[i] != None: board_tiles[i // 4][i % 4].create_image(60, 60, image=images[l[i]])
        game_status_var.set('Game Status: ' + str(game.status) + "\n")
        white_utility_var.set('White Utility: ' + str(game.get_white_utility()))
        black_utility_var.set('Black Utility: ' + str(game.get_black_utility()) + "\n")
        possible_actions_var.set(possible_actions_string())
        root.update()
        time.sleep(0.1)

def restart_game():
    global root
    global game, turn, board_tiles
    global game_status_var, white_utility_var, black_utility_var

    game = Silverman45ChessBoard()
    turn = 0
    l = game.populate_board()
    for i in range(len(l)):
        board_tiles[i // 4][i % 4].delete('all')
        if l[i] != None: board_tiles[i // 4][i % 4].create_image(60, 60, image=images[l[i]])
    game_status_var.set('Game Status: ' + str(game.status) + "\n")
    white_utility_var.set('White Utility: ' + str(game.get_white_utility()))
    black_utility_var.set('Black Utility: ' + str(game.get_black_utility()) + "\n")
    possible_actions_var.set(possible_actions_string())
    root.update()

# Handle Bottom Frame
update = Button(btm_frame, text="Step Game", command=update_board)
run = Button(btm_frame, text="Run Full Game", command=run_game)
restart = Button(btm_frame, text="Restart Game", command=restart_game)
update.grid(column=0, row=0)
run.grid(column=1, row=0)
restart.grid(column=2, row=0)

root.mainloop()