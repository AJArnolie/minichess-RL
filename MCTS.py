from minichess.games.silverman45.board import Silverman45ChessBoard
from minichess.games.abstract.board import AbstractBoardStatus
from minichess.games.abstract.action import AbstractActionFlags
from minichess.games.abstract.piece import PieceColor
from minichess.players.gardner import RandomPlayer
from minichess.utils import numpy_scaled_softmax

import os
import math
import copy
import random
import pickle
import numpy as np
from collections import defaultdict
# ------------------------------------------------------------------------------------------------

def reward(s, a):
    reward = int(s._is_checking_action(a, s.active_color)[0]) / 10.0
    reward += int(AbstractActionFlags.PROMOTE_QUEEN in a.modifier_flags) / 2.0 
    if AbstractActionFlags.CAPTURE in a.modifier_flags:
        reward += a.captured_piece.value / 3000.0 
    return reward

PAWN_REWARDS = np.array([[  0,  0,  0,  0],
                         [ .4, .4, .4, .4],
                         [ .8, .8, .8, .8],
                         [  0,  0,  0,  0],
                         [  0,  0,  0,  0],])                        
KING_REWARDS = np.array([[  0,  0,  0,  0],
                         [  0,  0,  0,  0],
                         [  0,  0,  0,  0],
                         [-.3,-.5,-.5,-.3],
                         [ .4, .1, .1, .4],])  

LATE_PAWN_REWARDS = np.array([[  0,  0,  0,  0],
                              [  1,  1,  1,  1],
                              [ .8, .8, .8, .8],
                              [-.5,-.5,-.5,-.5],
                              [  0,  0,  0,  0],])                        
LATE_KING_REWARDS = np.array([[  0,  0,  0,  0],
                              [ .5, .5, .5, .5],
                              [ .3, .3, .3, .3],
                              [-.5,-.5,-.5,-.5],
                              [-.8,-.8,-.8,-.8],])  
        

# Gets color dependent reward
def U_color(s, white=True):
    # Heuristics Used
    #  -  Reward having More Material
    #  -  Reward Rooks and Queen off the back rank (middle row)
    #  -  Reward Pawns taking middle squares
    #  -  Punish Doubled Pawns
    #  -  Reward King staying back
    material = (s.get_white_utility() if white else s.get_black_utility()) / 2
    activity = get_position_reward(s, white) - get_position_reward(s, not white)
    return material + activity

# Gets reward for color based on positions of pieces
def get_position_reward(s, white):
    activity = 0
    board = s.state_vector_color(white)
    late = bool(s.num_pieces(white) <= 3)
    for i in range(len(board)):
        for j in range(len(board[0])):
            c = board[i][j]
            if i > 0 and c[0] == 1 and board[i - 1][j][0] == 1:
                activity -= 0.1
            if late:
                if c[0] == 1 and LATE_PAWN_REWARDS[i][j] != 0: 
                    activity += LATE_KING_REWARDS[i][j] / 15.0
                elif c[5] == 1 and LATE_PAWN_REWARDS[i][j] != 0: 
                    activity += LATE_KING_REWARDS[i][j] / 10.0
            else:
                if c[0] == 1 and PAWN_REWARDS[i][j] != 0: 
                    activity += PAWN_REWARDS[i][j] / 15.0
                elif c[5] == 1 and KING_REWARDS[i][j] != 0: 
                    activity += KING_REWARDS[i][j] / 10.0
    return activity

# ------------------------------------------------------------------------------------------------
class MonteCarloTreeSearch:
    def __init__(self, m=500, d=20, c=2, gamma=0.95, num_candidates=3):
        self.m = m # number of simulations
        self.d = d # depth
        self.c = c # exploration constant
        self.gamma = gamma # discount factor
        self.num_candidates = num_candidates # Number of move candidates to consider for softmax

        self.Q = {} # action value estimates
        self.N = {} # (s-a) visit counts
        self.Ns = {} # s visit counts

        self.Q_file = "saved_MCTS_Q.pkl"
        self.N_file = "saved_MCTS_N.pkl"
        self.Ns_file = "saved_MCTS_Ns.pkl"

        if os.path.isfile(self.Q_file):
            print("Loading Q data from saved pickle...")
            with open(self.Q_file, 'rb') as f:
                self.Q = pickle.load(f)
        else:   
            self.Q = {} # action value estimates

        if os.path.isfile(self.N_file):
            print("Loading N data from saved pickle...")
            with open(self.N_file, 'rb') as f:
                self.N = pickle.load(f)
        else:   
            self.N = {} # action value estimates

        if os.path.isfile(self.Ns_file):
            print("Loading Ns data from saved pickle...")
            with open(self.Ns_file, 'rb') as f:
                self.Ns = pickle.load(f)
        else:   
            self.Ns = {} # action value estimates

    # Performs m iterations of MCTS
    def run_sims(self, state):
        turn = 0 if state.active_color == PieceColor.WHITE else 1
        for i in range(self.m):
            self.simulate(copy.deepcopy(state), turn=turn, d=self.d)
        return self.make_move(state, softmax=False)

    def dump_data(self):
        with open(self.Q_file, "wb") as f:
            pickle.dump(self.Q, f)
        with open(self.N_file, "wb") as f:
            pickle.dump(self.N, f)
        with open(self.Ns_file, "wb") as f:
            pickle.dump(self.Ns, f)

    def get_move_info(self, s):
        s_rep = s.state_representation() + ("0" if s.active_color == PieceColor.WHITE else "1")
        return [(self.Q.get((s_rep, a), 0), self.N.get((s_rep, a), 0)) for a in s.condensed_legal_actions()]
        
    def make_move(self, s, softmax = True, scale = 5): # scale controls exploration vs. exploitation, higher scale -> greedy
        s_rep = s.state_representation() + ("0" if s.active_color == PieceColor.WHITE else "1")
        # Detects states in which both kings are trapped
        if sum([self.Q.get((s_rep, a), 0) for a in s.condensed_legal_actions()]) == 0:
            return "DRAW"
        if softmax:
            condensed_legal_actions = s.condensed_legal_actions()
            legal_actions = s.legal_actions()
            a_q_pairs = [(legal_actions[i], self.Q.get((s_rep, condensed_legal_actions[i]), 0)) for i in range(len(condensed_legal_actions))]
            candidate_moves = sorted(a_q_pairs, key = lambda x: x[1], reverse=True)[:self.num_candidates]
            actions = np.array([c[0] for c in candidate_moves])
            q_vals = np.array([c[1] for c in candidate_moves])
            softmax_q = numpy_scaled_softmax(q_vals, scale)
            return np.random.choice(actions, p = softmax_q)
        else: 
            return s.legal_actions()[np.argmax([self.Q.get((s_rep, a), 0) for a in s.condensed_legal_actions()])]

    def simulate(self, s, turn=0, d=20):
        s_rep = s.state_representation() + str(turn)
        # End of game, return reward for winning
        if s.status != AbstractBoardStatus.ONGOING:
            if s.status == AbstractBoardStatus.DRAW:
                return -.1
            else:
                return 100
        # Reached max depth, return estimated utility for previous agent
        if d <= 0: return U_color(s, bool(turn))
        
        if s_rep not in self.Ns:
            self.Ns[s_rep] = 0
            for a in s.condensed_legal_actions():
                self.N[(s_rep, a)] = 0
                self.Q[(s_rep, a)] = 0.0
            return U_color(s, bool(turn))

        a = self.explore(s, turn)
        r = reward(s, a)
        s.push(a)
        q = r + self.gamma * self.simulate(s, 1 - turn, d - 1)

        a_rep = s.condensed_action(a)
        self.N[(s_rep, a_rep)] += 1
        self.Ns[s_rep] += 1
        self.Q[(s_rep, a_rep)] += (q - self.Q[(s_rep, a_rep)]) / self.N[(s_rep, a_rep)]
        return -q

# UCB1 Exploration Policy
# --------------------------------
    def bonus(self, nsa, ns):
        return float('inf') if nsa == 0 else math.sqrt(math.log(ns) / nsa) # Default UCB1# Default UCB1
        #return math.sqrt(ns) / (1 + nsa) # AlphaZero Exploration Policy

    def explore(self, s, turn):
        s_rep = s.state_representation() + str(turn)
        return s.legal_actions()[np.argmax([self.Q[(s_rep, a)] + self.c * self.bonus(self.N[(s_rep, a)], self.Ns[s_rep]) for a in s.condensed_legal_actions()])]
# ------------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------------
class ForwardSearch:
    def __init__(self, d=4, g=0.95):
        self.d = d # depth
        self.gamma = g # lookahead discount
        
    def make_move(self, s):
        white = bool(s.active_color == PieceColor.WHITE)
        return self.minimax_search(s, self.d, 0, -1000, 1000, white)[0]

    def minimax_search(self, s, d, turn, alpha, beta, white):
        if s.status != AbstractBoardStatus.ONGOING:
            if s.status == AbstractBoardStatus.DRAW:
                return (None, 0)
            else:
                return (None, 100 if turn == 1 else -100)
        if d <= 0:
            return (None, U_color(s, white))
        actions = s.legal_actions()
        if not actions:
            return (None, U_color(s, white))

        if turn == 0: # Maximizing
            best = (None, -1000)
            for a in actions:
                s2 = copy.deepcopy(s)
                s2.push(a)
                se = self.minimax_search(s2, d - 1, 1 - turn, alpha, beta, white)[1]
                u = reward(s, a) + se
                if d == 4:
                    print(d, a, u)
                if (u == best[1] and random.randint(0, 1) == 0) or u > best[1]:
                    best = (a, u)
                    alpha = max(alpha, best[1])
                    if beta <= alpha:
                        break  
            return best
    
        if turn == 1: # Minimizing
            best = (None, 1000)
            for a in actions:
                s2 = copy.deepcopy(s)
                s2.push(a)
                se = self.minimax_search(s2, d - 1, 1 - turn, alpha, beta, white)[1]
                u = reward(s, a) + se
                if d == 3:
                    print("      ", d, a, u)
                if (u == best[1] and random.randint(0, 1) == 0) or u < best[1]:
                    best = (a, u)
                    beta = min(beta, best[1])
                    if beta <= alpha:
                        break  
            return best
# ------------------------------------------------------------------------------------------------




















# class MonteCarloTreeSearchWithFunctionApprox:
#     def __init__(self, m=100, d=20, c=10, gamma=0.9):
#         self.m = m # number of simulations
#         self.d = d # depth
#         self.c = c # exploration constant
#         self.gamma = gamma # discount factor
#         self.approximator = GradientQLearning()

#         self.Q = defaultdict(lambda:0) # action value estimates
#         self.N = {} # (s-a) visit counts

#     # Performs m iterations of MCTS
#     def run_sims(self, state):
#         for i in range(self.m):
#             si = copy.deepcopy(state)    # This is slow, find a better way to do this
#             self.simulate(si, d=self.d)
#         return self.make_move(state)

#     def make_move(self, s):
#         s_rep = s.state_representation() + ("0" if s.active_color == PieceColor.WHITE else "1")
#         return s.legal_actions()[np.argmax([self.Q[(s_rep, a)] for a in s.condensed_legal_actions()])]

#     def simulate(self, s, turn=0, d=5):
#         s_rep = s.state_representation() + str(turn)
#         # End of game, return reward for winning
#         if s.status != AbstractBoardStatus.ONGOING:
#             if s.status == AbstractBoardStatus.DRAW:
#                 return -10
#             else:
#                 return 100
#         # Reached max depth, return estimated utility
#         if d <= 0: 
#             return s.get_white_utility() if turn == 1 else s.get_black_utility()
        
#         if (s_rep, s.condensed_legal_actions()[0]) not in self.N:
#             for a in s.condensed_legal_actions():
#                 self.N[(s_rep, a)] = 0
#                 self.Q[(s_rep, a)] = self.approximator.Q(s, a) #TODO: Should this be s or s_rep?
#             return s.get_white_utility() if turn == 1 else s.get_black_utility()
        
#         s_prev = copy.deepcopy(s) # this is slow, as noted earlier
#         a = self.explore(s, turn)
#         s.push(a)
            
#         reward = s.get_white_utility() if turn == 0 else s.get_black_utility()
#         self.approximator.update(d = {"s": s_prev, "a": a, "sp": s, "r": reward})
#         q = reward + self.gamma * self.simulate(s, 1 - turn, d - 1)

#         a_rep = s.condensed_action(a)
#         self.N[(s_rep, a_rep)] += 1
#         self.Q[(s_rep, a_rep)] += (q - self.Q[(s_rep, a_rep)]) / self.N[(s_rep, a_rep)]
#         return -q

#     # UCB1 Exploration Policy
#     # --------------------------------
#     def bonus(self, nsa, ns):
#         return float('inf') if nsa == 0 else math.sqrt(math.log(ns) / nsa)

#     def explore(self, s, turn):
#         s_rep = s.state_representation() + str(turn)
#         ns = sum(self.N[(s_rep, a)] for a in s.condensed_legal_actions())
#         return s.legal_actions()[np.argmax([self.Q[(s_rep, a)] + self.c * self.bonus(self.N[(s_rep, a)], ns) for a in s.condensed_legal_actions()])]
#     # --------------------------------
# # ------------------------------------------------------------------------------------------------



# # ------------------------------------------------------------------------------------------------
# class GradientQLearning:
#     def __init__(self, gamma=0.95, alpha=0.9):
#         self.B = 8
#         self.t = 0
#         self.T = np.zeros(self.B) + 0.1
#         self.gradQ = np.zeros(list(current) + [self.B])
#         for i in range(current[0]):
#             for j in range(current[1]):
#                 self.gradQ[i][j] = self.gradientQ(i + 1, j + 1)
#         self.gamma = gamma
#         self.alpha = alpha
    
#     def gradientQ(self, s, a):
#         return np.array([1, s, s**2, s*a, a, a**2, s**2*a, a**2*s])

#     def Q(self, s, a):
#         return self.gradQ[(s, a)] @ self.T

#     def scale_gradient(self, d):
#         return min(1 / np.linalg.norm(d), 1) * d

#     def update(self, d):
#         s, a, r, sp = d['s'], d['a'], d['r'], d['sp']
#         u = max(self.Q(sp, ap) for ap in range(current[1]))
#         diff = r + self.gamma * u - self.Q(s, a)
#         self.t += diff
#         self.T += self.alpha * self.scale_gradient(diff * self.gradQ[(s, a)])
                        
#     def return_policy(self):
#         Q = np.zeros(current)
#         for i in range(current[0]):
#             for j in range(current[1]):
#                 Q[i][j] = self.Q(i, j)
#         return [np.argmax(Q[i]) + 1 for i in range(len(Q))]