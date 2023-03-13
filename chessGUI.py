import tkinter
import time
import random
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
wld = [0, 0, 0]
turn = random.randint(0, 1)
# ----------------------------------------

def possible_actions_string():
    global m
    global game
    s = "Possible Actions:\n"
    actions = game.legal_actions()
    info = m.get_move_info(game)
    for i in range(len(actions)):
        s += str(i+1) + ". " + str(actions[i]) + " Q(s, a) = " + str(round(info[i][0], 3)) + ",  N(s, a) = " + str(info[i][1]) + "\n"
    return s

root = Tk()
root.geometry("1000x700")
root.resizable(False, False)
images = [PhotoImage(file = IMAGE_PREFIX + i + IMAGE_TYPE) for i in image_names]

game_status_var = StringVar(root, "Game Status: AbstractBoardStatus.ONGOING\n")
white_utility_var = StringVar(root, "White Utility: 0.0")
black_utility_var = StringVar(root, "Black Utility: -0.0\n")
possible_actions_var = StringVar(root, possible_actions_string())
wld_var = StringVar(root, "0 - 0 - 0 (Wins, Losses, Draws)\n\n")
white_player_name = StringVar(root, "White Player: ")
black_player_name = StringVar(root, "Black Player: \n\n")
update_Qvalues = StringVar(root, "Update Q")
player1 = StringVar(root, "MCTS")
player2 = StringVar(root, "Random")

if turn == 0:
    white_player_name.set('White Player: ' + player2.get())
    black_player_name.set('Black Player: ' + player1.get() + "\n\n")
else:
    white_player_name.set('White Player: ' + player1.get())
    black_player_name.set('Black Player: ' + player2.get() + "\n\n")

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

l = game.populate_board()
for i in range(5):
    for j in range(4):
        board_tiles[i][j] = Canvas(board, bg=(DARK_COLOR if (i+j) % 2 == 0 else LIGHT_COLOR), 
                                        width=120, height=120, highlightthickness=0)
        if l[i*4+j] != None:
            board_tiles[i][j].create_image(60, 60, image=images[l[i*4+j]])
        board_tiles[i][j].grid(column=j, row=i)

ctr_mid = Frame(center, width=250, height=600, padx=3, pady=3)
white_player = Label(ctr_mid, textvariable=white_player_name, font=('Modern', 16, 'bold'), justify=LEFT, anchor="w")
black_player = Label(ctr_mid, textvariable=black_player_name, font=('Modern', 16, 'bold'), justify=LEFT, anchor="w")
game_status = Label(ctr_mid, textvariable=game_status_var, font=('Modern', 16, 'bold'), justify=LEFT, anchor="w")
white_utility = Label(ctr_mid, textvariable=white_utility_var, font=('Modern', 16, 'bold'), justify=LEFT, anchor="w")
black_utility = Label(ctr_mid, textvariable=black_utility_var, font=('Modern', 16, 'bold'), justify=LEFT, anchor="w")
possible_actions = Label(ctr_mid, textvariable=possible_actions_var, font=('Modern', 16, 'bold'), justify=LEFT, anchor="w")
wld_label = Label(ctr_mid, textvariable=wld_var, font=('Modern', 16, 'bold'), justify=LEFT, anchor="w")

white_player.grid(sticky = W, column=0, row=0)
black_player.grid(sticky = W, column=0, row=1)
wld_label.grid(sticky = W, column=0, row=2)
game_status.grid(sticky = W, column=0, row=3)
white_utility.grid(sticky = W, column=0, row=4)
black_utility.grid(sticky = W, column=0, row=5)
possible_actions.grid(sticky = W, column=0, row=6)


ctr_right = Frame(center, width=100, height=600, padx=3, pady=3)

board.grid(row=0, column=0, sticky="ns", pady=10)
ctr_mid.grid(row=0, column=1, sticky="nsew")
ctr_right.grid(row=0, column=2, sticky="ns")


def update_board():
    global game, turn, board_tiles
    global game_status_var, white_utility_var, black_utility_var

    if game.status == AbstractBoardStatus.ONGOING:
        if turn == 0:
            if player2.get() == "MCTS":
                proposed = m.run_sims(game) if update_Qvalues.get() == "Update Q" else m.make_move(game)
            else:
                _, proposed = p.propose_action(game, None, game.legal_action_mask())
        if turn == 1:
            if player1.get() == "MCTS":
                proposed = m.run_sims(game) if update_Qvalues.get() == "Update Q" else m.make_move(game)
            else:
                _, proposed = p.propose_action(game, None, game.legal_action_mask())
        turn = 1 - turn
        game.push(proposed)
    l = game.populate_board()
    for i in range(len(l)):
        board_tiles[i // 4][i % 4].delete('all')
        if l[i] != None: board_tiles[i // 4][i % 4].create_image(60, 60, image=images[l[i]])
    possible_actions_var.set(possible_actions_string())
    game_status_var.set('Game Status: ' + str(game.status) + "\n")
    white_utility_var.set('White Utility: ' + str(game.get_white_utility()))
    black_utility_var.set('Black Utility: ' + str(game.get_black_utility()) + "\n")

def run_game():
    global root, wld
    global game, turn, board_tiles
    global game_status_var, white_utility_var, black_utility_var

    turn = random.randint(0, 1)
    init_turn = turn
    if turn == 0:
        white_player_name.set('White Player: ' + player2.get())
        black_player_name.set('Black Player: ' + player1.get() + "\n\n")
    else:
        white_player_name.set('White Player: ' + player1.get())
        black_player_name.set('Black Player: ' + player2.get() + "\n\n")

    while game.status == AbstractBoardStatus.ONGOING:
        if turn == 0:
            if player2.get() == "MCTS":
                proposed = m.run_sims(game) if update_Qvalues.get() == "Update Q" else m.make_move(game)
            else:
                _, proposed = p.propose_action(game, None, game.legal_action_mask())
        if turn == 1:
            if player1.get() == "MCTS":
                proposed = m.run_sims(game) if update_Qvalues.get() == "Update Q" else m.make_move(game)
            else:
                _, proposed = p.propose_action(game, None, game.legal_action_mask())
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
        wld_var.set(str(wld[0]) + " - " + str(wld[1]) + " - "  + str(wld[2]) + " (Wins, Losses, Draws)\n\n")
        root.update()
    if game.status == AbstractBoardStatus.BLACK_WIN:
        return 0 if init_turn == 0 else 1
    elif game.status == AbstractBoardStatus.WHITE_WIN:
        return 1 if init_turn == 0 else 0
    return 2
    
def run_100_games():
    global wld
    for i in range(100):
        wld[run_game()] += 1
        restart_game()

def restart_game():
    global root
    global game, turn, board_tiles
    global game_status_var, white_utility_var, black_utility_var

    game = Silverman45ChessBoard()
    turn = random.randint(0, 1)
    if turn == 0:
        white_player_name.set('White Player: ' + player2.get())
        black_player_name.set('Black Player: ' + player1.get() + "\n\n")
    else:
        white_player_name.set('White Player: ' + player1.get())
        black_player_name.set('Black Player: ' + player2.get() + "\n\n")
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
run100 = Button(btm_frame, text="Run 100 Games", command=run_100_games)
restart = Button(btm_frame, text="Restart Game", command=restart_game)
update.grid(column=0, row=0)
run.grid(column=1, row=0)
restart.grid(column=2, row=0)
run100.grid(column=3, row=0)

options = ["Update Q", "Exploit Q"]
drop = OptionMenu(btm_frame, update_Qvalues, *options)
drop.grid(column=6, row=0)

players = ["MCTS", "Random"]
p1 = OptionMenu(btm_frame, player1, *players)
p2 = OptionMenu(btm_frame, player2, *players)
p1_text = Label(btm_frame, text='  Player 1:', font=('Modern', 12, 'bold'))
p2_text = Label(btm_frame, text=' Player 2:', font=('Modern', 12, 'bold'))
p1_text.grid(column=7, row=0)
p1.grid(column=8, row=0)
p2_text.grid(column=9, row=0)
p2.grid(column=10, row=0)

exit_button = Button(btm_frame, text="Exit", command=root.destroy)
exit_button.grid(column=11, row=0)

root.mainloop()