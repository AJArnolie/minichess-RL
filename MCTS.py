'''
Monte Carlo Tree Search
- Online Planning
- During sim, updates estimated Q-function and # of times (s,a) pair is selected
- After m sims, chooses action maximizing estimated Q-function
- Exploration Strategy UCB1: Maximize --> Q(s,a) + c * sqrt(log(N(s)) / N(s, a))
- As we take action, step into new sampled states using generative model
- At unexplored state, initialize N(s,a) and Q(s,a) to 0 for each a, then return value estimate (Commonly estimated using policy rollout for n steps)
'''

import math
import numpy as np

class MonteCarloTreeSearch:
    def __init__(self, board, m=100, d=5, c=0.5, gamma=0.9):
        self.m = m # number of simulations
        self.d = d # depth
        self.c = c # exploration constant
        self.gamma = gamma # discount factor

        self.board = board
        self.S = []  # How do we define states and actions here?
        
        self.U = [0 for _ in range(len(self.S))] # value function estimate
        self.Q = {} # action value estimates
        self.N = {} # visit counts

    # Performs m iterations of MCTS and returns set of actions with counts and Q-values
    def run_search(self, s):
        for _ in range(self.m):
            self.simulate(s, self.d)
        return {a: (self.Q[(s, a)], self.N[(s, a)])  for a in self.board.legal_moves}

    def simulate(self, s, d=5):
        if d <= 0:
            return self.U(s)
        if (s, self.board.legal_moves[0]) not in self.N:
            for a in self.board.legal_moves:
                self.N[(s, a)] = 0
                self.Q[(s, a)] = 0.0
            return self.U(s)
        
        a = self.explore(s)
        s_prime, r = self.TR(s, a)
        q = r + self.gamma * self.simulate(s_prime, d - 1)

        self.N[(s, a)] += 1
        self.Q[(s, a)] += (q - self.Q[(s, a)]) / self.N[(s, a)]
        return q

    # How do we get this?
    def TR(self, s, a):
        return 0, 0

    # UCB1 Exploration Policy
    # --------------------------------
    def bonus(self, nsa, ns):
        return float('inf') if nsa == 0 else math.sqrt(math.log(ns) / nsa)

    def explore(self, s):
        ns = sum(self.N[(s, a)] for a in self.board.legal_moves)
        return self.board.legal_moves[np.argmax([self.Q[(s, a)] + self.c * self.bonus(self.N[(s, a)], ns) for a in self.board.legal_moves])]
    # --------------------------------


def main():
    board = None # Insert board implementation here
    MCTS = MonteCarloTreeSearch(board)

if __name__ == "__main__":
    main()