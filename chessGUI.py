import time
import random
from tkinter import *
from PIL import Image, ImageTk
from MCTS import MonteCarloTreeSearch, ForwardSearch
from minichess.games.abstract.piece import PieceColor
from minichess.games.silverman45.board import Silverman45ChessBoard
from minichess.games.abstract.board import AbstractBoardStatus
from minichess.players.gardner import RandomPlayer

DARK_COLOR = "#ebecd0"
LIGHT_COLOR = "#779556"
BG_COLOR = "#ececec"
IMAGE_PREFIX = "./images/"
IMAGE_TYPE = ".png"
IMAGE_NAMES = ["white_pawn", "white_rook", "white_queen", "white_king", "black_pawn", "black_rook", "black_queen", "black_king"]
ROWS = ["5", "4", "3", "2", "1"]
COLUMNS = ["A", "B", "C", "D"]

m = MonteCarloTreeSearch(m=50, c=2)
f = ForwardSearch(d=2)
game = Silverman45ChessBoard()
p = RandomPlayer()
wld = [0, 0, 0]
turn = random.randint(0, 1)
average_moves = [0,0]
average_avg_times = [0,0]
average_game_time = 0

root = Tk()
root.geometry("1000x710")
root.resizable(False, False)
root.title("Minichess Simulator")

images = [PhotoImage(file = IMAGE_PREFIX + i + IMAGE_TYPE) for i in IMAGE_NAMES]

# Define GUI Variables
game_status_var = StringVar(root, "Game Status: ONGOING\n")
white_utility_var = StringVar(root, "White Utility: 0.0")
black_utility_var = StringVar(root, "Black Utility: -0.0\n")
wld_var = StringVar(root, "0 - 0 - 0 (Wins, Losses, Draws)\n\n")
white_player_name = StringVar(root, "White Player: ")
black_player_name = StringVar(root, "Black Player: \n\n")
update_Qvalues = StringVar(root, "Update Q")
player1 = StringVar(root, "MCTS")
player2 = StringVar(root, "MCTS")
selected = StringVar(root, "")

def action_str(a):
    return "(" + COLUMNS[a.from_pos[1]] + ROWS[a.from_pos[0]] + "  ->  " + COLUMNS[a.to_pos[1]] + ROWS[a.to_pos[0]] + ")"

def possible_actions_string():
    print(turn)
    s = "Possible Actions:\n"
    actions = game.legal_actions()
    info = m.get_move_info(game)
    for i in range(len(actions))[:10]:
        s += str(i+1) + ". " + action_str(actions[i]) + "      Q(s, a) = " + str(round(info[i][0], 3)) + ",  N(s, a) = " + str(info[i][1]) + "\n"
    if len(actions) > 10: s += "...\n"
    s += "\nAction Selected: " + selected.get() + " by " + ("Black" if game.active_color == PieceColor.BLACK else "White")
    return s

possible_actions_var = StringVar(root, possible_actions_string())

# Establish Main Frames
top_frame = Frame(root, width=1000, height=50, pady=3)
center = Frame(root, bg="black", width=1000, height=600, padx=3, pady=3)
btm_frame = Frame(root, bg=BG_COLOR, width=1000, height=45, pady=3)

# layout all of the main containers
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

top_frame.grid(row=0, sticky="ew")
center.grid(row=1, sticky="nsew")
btm_frame.grid(row=2, sticky="ew")

# create the widgets for the top frame
title_label = Label(root, text='Silverman 4X5 Minichess Simulator', font=('Modern', 18, 'bold'))
title_label.grid(row=0, columnspan=2)

# create the center widgets
center.grid_rowconfigure(0, weight=1)
center.grid_columnconfigure(1, weight=1)

board = Frame(center, width=480, height=600)
board_tiles = [[None for _ in range(4)] for _ in range(5)]

def redraw_labels():
    global board_tiles
    board_tiles[0][0].create_text(60, 10, text="A", fill="black", font=('Modern', 12, 'bold'))
    board_tiles[0][1].create_text(60, 10, text="B", fill="black", font=('Modern', 12, 'bold'))
    board_tiles[0][2].create_text(60, 10, text="C", fill="black", font=('Modern', 12, 'bold'))
    board_tiles[0][3].create_text(60, 10, text="D", fill="black", font=('Modern', 12, 'bold'))

    board_tiles[0][0].create_text(10, 60, text="5", fill="black", font=('Modern', 12, 'bold'))
    board_tiles[1][0].create_text(10, 60, text="4", fill="black", font=('Modern', 12, 'bold'))
    board_tiles[2][0].create_text(10, 60, text="3", fill="black", font=('Modern', 12, 'bold'))
    board_tiles[3][0].create_text(10, 60, text="2", fill="black", font=('Modern', 12, 'bold'))
    board_tiles[4][0].create_text(10, 60, text="1", fill="black", font=('Modern', 12, 'bold'))

l = game.populate_board()
for i in range(5):
    for j in range(4):
        board_tiles[i][j] = Canvas(board, bg=(DARK_COLOR if (i+j) % 2 == 1 else LIGHT_COLOR), 
                                        width=120, height=120, highlightthickness=0)
        if l[i*4+j] != None: board_tiles[i][j].create_image(60, 60, image=images[l[i*4+j]])
        board_tiles[i][j].grid(column=j, row=i)
redraw_labels()


ctr_mid = Frame(center, width=500, height=600, padx=3, pady=3, bg=BG_COLOR)
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

board.grid(row=0, column=0, sticky="ns", pady=10)
ctr_mid.grid(row=0, column=1, sticky="nsew")

def update_board():
    global root, game, turn, board_tiles
    white_player_name.set('White Player: ' + (player1.get() if turn else player2.get()))
    black_player_name.set('Black Player: ' + (player2.get() if turn else player1.get()) + "\n\n")
    if game.status == AbstractBoardStatus.ONGOING:
        if (player1.get() if turn == bool(game.active_color == PieceColor.WHITE) else player2.get()) == "MCTS":
            proposed = m.run_sims(game) if update_Qvalues.get() == "Update Q" else m.make_move(game)
            if proposed == "DRAW": return "DRAW"
        elif (player1.get() if turn == bool(game.active_color == PieceColor.WHITE) else player2.get()) == "Forward":
            proposed = f.make_move(game)
        else:
            _, proposed = p.propose_action(game, None, game.legal_action_mask()) 
        selected.set(action_str(proposed))  
        possible_actions_var.set(possible_actions_string())
        game.push(proposed)
 
    l = game.populate_board()
    for i in range(len(l)):
        board_tiles[i // 4][i % 4].delete('all')
        if l[i] != None: board_tiles[i // 4][i % 4].create_image(60, 60, image=images[l[i]])
    redraw_labels()
    game_status_var.set('Game Status: ' + str(game.status).split('.')[1] + "\n")
    white_utility_var.set('White Utility: ' + str(round(game.get_white_utility() * 10, 3)))
    black_utility_var.set('Black Utility: ' + str(round(game.get_black_utility() * 10, 3)) + "\n")
    root.update()
    return None

def run_game():
    st = time.time()
    global wld, game, turn, board_tiles
    global average_moves, average_avg_times
    restart_game()
    turn = random.randint(0, 1)
    white_player_name.set('White Player: ' + (player1.get() if turn else player2.get()))
    black_player_name.set('Black Player: ' + (player2.get() if turn else player1.get()) + "\n\n")
    val = None
    num_moves = [0, 0]
    tot_move_length = [0, 0]
    while game.status == AbstractBoardStatus.ONGOING and val == None:
        n = time.time()
        val = update_board()
        e = time.time()
        tot_move_length[1] += e - n
        num_moves[1] += 1
        if turn != bool(game.active_color == PieceColor.WHITE):
            tot_move_length[0] += e - n
            num_moves[0] += 1
    if game.status == AbstractBoardStatus.BLACK_WIN: wld[turn] += 1
    elif game.status == AbstractBoardStatus.WHITE_WIN: wld[1 - turn] += 1
    else: wld[2] += 1
    #m.dump_data()
    wld_var.set(str(wld[0]) + " - " + str(wld[1]) + " - "  + str(wld[2]) + " (Wins, Losses, Draws)\n\n")
    root.update()

    average_moves[0] += num_moves[0]
    average_moves[1] += num_moves[1]
    average_avg_times[0] += tot_move_length[0] / num_moves[0]
    average_avg_times[1] += tot_move_length[1] / num_moves[1]

    print("Game Time Length: ", time.time() - st)
    print("Num Moves: ", num_moves)
    print("Average Move Length: ", (tot_move_length[0] / num_moves[0], tot_move_length[1] / num_moves[1]))
    print("(Wins, Losses, Draws): ", wld)
    
def run_100_games():
    global average_game_time
    for i in range(100):
        print("|||||| Game", i+1, "||||||")
        st = time.time()
        run_game()
        e = time.time()
        average_game_time += e - st
        restart_game()
        print()
        print("AVERAGE MOVES: ", (average_moves[0] / (i+1.0), average_moves[1] / (i+1.0)))
        print("AVERAGE MOVE LENGTH: ", (average_avg_times[0] / (i+1.0), average_avg_times[1] / (i+1.0)))
        print("AVERAGE GAME TIME: ", average_game_time / (i+1.0))
        print("-----------------------------")

def restart_game():
    global root
    global game, turn, board_tiles
    global game_status_var, white_utility_var, black_utility_var

    game = Silverman45ChessBoard()
    turn = random.randint(0, 1)
    white_player_name.set('White Player: ' + (player1.get() if turn else player2.get()))
    black_player_name.set('Black Player: ' + (player2.get() if turn else player1.get()) + "\n\n")

    l = game.populate_board()
    for i in range(len(l)):
        board_tiles[i // 4][i % 4].delete('all')
        if l[i] != None: board_tiles[i // 4][i % 4].create_image(60, 60, image=images[l[i]])
    redraw_labels()
    game_status_var.set('Game Status: ' + str(game.status).split('.')[1] + "\n")
    white_utility_var.set('White Utility: 0.0')
    black_utility_var.set('Black Utility: -0.0\n')
    selected.set("")
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

players = ["MCTS", "Forward", "Random"]
p1 = OptionMenu(btm_frame, player1, *players)
p2 = OptionMenu(btm_frame, player2, *players)
p1_text = Label(btm_frame, text='  Player 1:', font=('Modern', 12, 'bold'))
p2_text = Label(btm_frame, text=' Player 2:', font=('Modern', 12, 'bold'))
p1_text.grid(column=7, row=0)
p1.grid(column=8, row=0)
p2_text.grid(column=9, row=0)
p2.grid(column=10, row=0)

exit_button = Button(btm_frame, text="Exit", command=root.destroy, fg="red")
exit_button.grid(column=11, row=0)

root.mainloop()