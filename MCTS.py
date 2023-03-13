from minichess.games.silverman45.board import Silverman45ChessBoard
from minichess.games.abstract.board import AbstractBoardStatus
from minichess.games.abstract.action import AbstractActionFlags
from minichess.games.abstract.piece import PieceColor
from minichess.players.gardner import RandomPlayer
from minichess.utils import numpy_scaled_softmax

import math
import time
import random
import numpy as np
import copy
from collections import defaultdict
import pickle
import os

class MonteCarloTreeSearch:
    def __init__(self, m=100, d=30, c=5, gamma=0.9):
        self.m = m # number of simulations
        self.d = d # depth
        self.c = c # exploration constant
        self.gamma = gamma # discount factor

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
        s = time.time()
        turn = 0 if state.active_color == PieceColor.WHITE else 1
        for i in range(self.m):
            si = copy.deepcopy(state)
            self.simulate(si, turn=turn, d=self.d)
        print(time.time() - s)
        with open(self.Q_file, "wb") as f:
            pickle.dump(self.Q, f)
        with open(self.N_file, "wb") as f:
            pickle.dump(self.N, f)
        with open(self.Ns_file, "wb") as f:
            pickle.dump(self.Ns, f)
        return self.make_move(state)

    def get_move_info(self, s):
        s_rep = s.state_representation() + ("0" if s.active_color == PieceColor.WHITE else "1")
        return [(self.Q.get((s_rep, a), 0), self.N.get((s_rep, a), 0)) for a in s.condensed_legal_actions()]

    def make_move(self, s, softmax = True, scale = 10): # scale controls exploration vs. exploitation, higher scale -> gredy
        s_rep = s.state_representation() + ("0" if s.active_color == PieceColor.WHITE else "1")
        q_vals = np.array([self.Q.get((s_rep, a), 0) for a in s.condensed_legal_actions()])
        if softmax:
            softmax_q = numpy_scaled_softmax(q_vals, scale)
            # print(softmax_q)
            print(softmax_q)
            return np.random.choice(s.legal_actions(), p = softmax_q)
        else:
            return s.legal_actions()[np.argmax(q_vals)]

    def simulate(self, s, turn=0, d=20):
        s_rep = s.state_representation() + str(turn)
        # End of game, return reward for winning
        if s.status != AbstractBoardStatus.ONGOING:
            if s.status == AbstractBoardStatus.DRAW:
                return -30
            else:
                return 100
        # Reached max depth, return estimated utility
        if d <= 0: 
            return s.get_white_utility() if turn == 1 else s.get_black_utility()
        
        if s_rep not in self.Ns:
            self.Ns[s_rep] = 0
            for a in s.condensed_legal_actions():
                self.N[(s_rep, a)] = 0
                self.Q[(s_rep, a)] = 0.0
            return s.get_white_utility() if turn == 1 else s.get_black_utility()

        a = self.explore(s, turn)

        check, checkmate = s._is_checking_action(a, s.active_color)
        reward = int(check) / 10.0 + int(checkmate) * 5
        #print("Check Term: " + str(int(check) / 10.0 + int(checkmate) * 5))
        reward += int(AbstractActionFlags.CAPTURE in a.modifier_flags) / 10.0 + int(AbstractActionFlags.PROMOTE_QUEEN in a.modifier_flags) / 10.0
        # print("Capture Term: " + str(int(AbstractActionFlags.CAPTURE in a.modifier_flags) / 10.0))
        # print("Promote Term: " + str(int(AbstractActionFlags.PROMOTE_QUEEN in a.modifier_flags) / 10.0))
        reward += (s.get_white_utility() if turn == 0 else s.get_black_utility()) / 5.0
        # print("Utility Term: " + str((s.get_white_utility() if turn == 0 else s.get_black_utility()) / 5.0))
        
        s.push(a)

        q = reward + self.gamma * self.simulate(s, 1 - turn, d - 1)

        a_rep = s.condensed_action(a)
        self.N[(s_rep, a_rep)] += 1
        self.Ns[s_rep] += 1
        self.Q[(s_rep, a_rep)] += (q - self.Q[(s_rep, a_rep)]) / self.N[(s_rep, a_rep)]
        return -q

    # UCB1 Exploration Policy
    # --------------------------------
    def bonus(self, nsa, ns):
        return float('inf') if nsa == 0 else math.sqrt(math.log(ns) / nsa)

    def explore(self, s, turn):
        s_rep = s.state_representation() + str(turn)
        return s.legal_actions()[np.argmax([self.Q[(s_rep, a)] + self.c * self.bonus(self.N[(s_rep, a)], self.Ns[s_rep]) for a in s.condensed_legal_actions()])]
    # --------------------------------
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