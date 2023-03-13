from minichess.games.silverman45.board import Silverman45ChessBoard
from minichess.games.abstract.board import AbstractBoardStatus
from minichess.games.abstract.piece import PieceColor
from minichess.players.gardner import RandomPlayer
import math
import random
import numpy as np
import copy
from collections import defaultdict

class MonteCarloTreeSearch:
    def __init__(self, m=100, d=20, c=10, gamma=0.9):
        self.m = m # number of simulations
        self.d = d # depth
        self.c = c # exploration constant
        self.gamma = gamma # discount factor

        self.Q = defaultdict(lambda:0) # action value estimates
        self.N = {} # (s-a) visit counts

    # Performs m iterations of MCTS
    def run_sims(self, state):
        for i in range(self.m):
            si = copy.deepcopy(state)    # This is slow, find a better way to do this
            self.simulate(si, d=self.d)
        return self.make_move(state)

    def make_move(self, s):
        s_rep = s.state_representation() + ("0" if s.active_color == PieceColor.WHITE else "1")
        return s.legal_actions()[np.argmax([self.Q[(s_rep, a)] for a in s.condensed_legal_actions()])]

    def simulate(self, s, turn=0, d=5):
        s_rep = s.state_representation() + str(turn)
        # End of game, return reward for winning
        if s.status != AbstractBoardStatus.ONGOING:
            return 100
        # Reached max depth, return estimated utility
        if d <= 0: 
            return s.get_white_utility() if turn == 1 else s.get_black_utility()
        
        if (s_rep, s.condensed_legal_actions()[0]) not in self.N:
            for a in s.condensed_legal_actions():
                self.N[(s_rep, a)] = 0
                self.Q[(s_rep, a)] = s.get_white_utility() if turn == 1 else s.get_black_utility()
            return s.get_white_utility() if turn == 1 else s.get_black_utility()
        
        a = self.explore(s, turn)
        s.push(a)
            
        reward = s.get_white_utility() if turn == 0 else s.get_black_utility()
        q = reward + self.gamma * self.simulate(s, 1 - turn, d - 1)

        a_rep = s.condensed_action(a)
        self.N[(s_rep, a_rep)] += 1
        self.Q[(s_rep, a_rep)] += (q - self.Q[(s_rep, a_rep)]) / self.N[(s_rep, a_rep)]
        return -q

    # UCB1 Exploration Policy
    # --------------------------------
    def bonus(self, nsa, ns):
        return float('inf') if nsa == 0 else math.sqrt(math.log(ns) / nsa)

    def explore(self, s, turn):
        s_rep = s.state_representation() + str(turn)
        ns = sum(self.N[(s_rep, a)] for a in s.condensed_legal_actions())
        return s.legal_actions()[np.argmax([self.Q[(s_rep, a)] + self.c * self.bonus(self.N[(s_rep, a)], ns) for a in s.condensed_legal_actions()])]
    # --------------------------------
# ------------------------------------------------------------------------------------------------


class MonteCarloTreeSearchWithFunctionApprox:
    def __init__(self, m=100, d=20, c=10, gamma=0.9):
        self.m = m # number of simulations
        self.d = d # depth
        self.c = c # exploration constant
        self.gamma = gamma # discount factor
        self.approximator = GradientQLearning()

        self.Q = defaultdict(lambda:0) # action value estimates
        self.N = {} # (s-a) visit counts

    # Performs m iterations of MCTS
    def run_sims(self, state):
        for i in range(self.m):
            si = copy.deepcopy(state)    # This is slow, find a better way to do this
            self.simulate(si, d=self.d)
        return self.make_move(state)

    def make_move(self, s):
        s_rep = s.state_representation() + ("0" if s.active_color == PieceColor.WHITE else "1")
        return s.legal_actions()[np.argmax([self.Q[(s_rep, a)] for a in s.condensed_legal_actions()])]

    def simulate(self, s, turn=0, d=5):
        s_rep = s.state_representation() + str(turn)
        # End of game, return reward for winning
        if s.status != AbstractBoardStatus.ONGOING:
            return 100
        # Reached max depth, return estimated utility
        if d <= 0: 
            return s.get_white_utility() if turn == 1 else s.get_black_utility()
        
        if (s_rep, s.condensed_legal_actions()[0]) not in self.N:
            for a in s.condensed_legal_actions():
                self.N[(s_rep, a)] = 0
                self.Q[(s_rep, a)] = self.approximator.Q(s, a) #TODO: Should this be s or s_rep?
            return s.get_white_utility() if turn == 1 else s.get_black_utility()
        
        s_prev = copy.deepcopy(s) # this is slow, as noted earlier
        a = self.explore(s, turn)
        s.push(a)
            
        reward = s.get_white_utility() if turn == 0 else s.get_black_utility()
        self.approximator.update(d = {"s": s_prev, "a": a, "sp": s, "r": reward})
        q = reward + self.gamma * self.simulate(s, 1 - turn, d - 1)

        a_rep = s.condensed_action(a)
        self.N[(s_rep, a_rep)] += 1
        self.Q[(s_rep, a_rep)] += (q - self.Q[(s_rep, a_rep)]) / self.N[(s_rep, a_rep)]
        return -q

    # UCB1 Exploration Policy
    # --------------------------------
    def bonus(self, nsa, ns):
        return float('inf') if nsa == 0 else math.sqrt(math.log(ns) / nsa)

    def explore(self, s, turn):
        s_rep = s.state_representation() + str(turn)
        ns = sum(self.N[(s_rep, a)] for a in s.condensed_legal_actions())
        return s.legal_actions()[np.argmax([self.Q[(s_rep, a)] + self.c * self.bonus(self.N[(s_rep, a)], ns) for a in s.condensed_legal_actions()])]
    # --------------------------------
# ------------------------------------------------------------------------------------------------



# ------------------------------------------------------------------------------------------------
class GradientQLearning:
    def __init__(self, gamma=0.95, alpha=0.9):
        self.B = 8
        self.t = 0
        self.T = np.zeros(self.B) + 0.1
        self.gradQ = np.zeros(list(current) + [self.B])
        for i in range(current[0]):
            for j in range(current[1]):
                self.gradQ[i][j] = self.gradientQ(i + 1, j + 1)
        self.gamma = gamma
        self.alpha = alpha
    
    def gradientQ(self, s, a):
        return np.array([1, s, s**2, s*a, a, a**2, s**2*a, a**2*s])

    def Q(self, s, a):
        return self.gradQ[(s, a)] @ self.T

    def scale_gradient(self, d):
        return min(1 / np.linalg.norm(d), 1) * d

    def update(self, d):
        s, a, r, sp = d['s'], d['a'], d['r'], d['sp']
        u = max(self.Q(sp, ap) for ap in range(current[1]))
        diff = r + self.gamma * u - self.Q(s, a)
        self.t += diff
        self.T += self.alpha * self.scale_gradient(diff * self.gradQ[(s, a)])
                        
    def return_policy(self):
        Q = np.zeros(current)
        for i in range(current[0]):
            for j in range(current[1]):
                Q[i][j] = self.Q(i, j)
        return [np.argmax(Q[i]) + 1 for i in range(len(Q))]