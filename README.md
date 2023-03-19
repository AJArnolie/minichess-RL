# CS238 Final Project: Reinforcement Learning for Minichess Variants


<p align="center">
  <img src="https://user-images.githubusercontent.com/57520931/226214457-e86d4a12-346d-4516-8f23-a42b9d7f19c4.gif" alt="animated" />
</p>

## Abstract

In our project, we apply reinforcement learning to chess variants, with a particular emphasis on so-called "minichess" rulesets. Chess is an oft-studied and widely popular game that is commonly framed as a sequential decision-making problem. Although the rules of chess are relatively simple, substantial uncertainty is generated by the sheer number of possible moves in any given chess position. Contemporary approaches to chess engine development have traditionally combined search algorithms with position evaluation heuristics. More recent engines, such as AlphaZero, have applied self-play reinforcement learning (trained using massive computational resources) to achieve equivalent and occasionally superior results. Minichess variants, such Silverman 4×5, reduce the computational intractability of chess by shrinking the board and reducing the number of pieces. In our project, we apply reinforcement learning techniques in an attempt to produce human-level results in Silverman 4×5, a minichess variant. To this end, we tune a minichess playing agent using **Monte Carlo Tree Search** and evaluate this agent against basic Random and MiniMax agents.

## Minichess Variant: Silverman 4×5
<p align="center">
<img width="160" alt="Screen Shot 2023-02-18 at 4 55 16 PM" src="https://user-images.githubusercontent.com/57520931/219906266-023cf050-3194-4faa-bb24-a1c5f4378d9c.png">
</p>

**Silverman 4×5** is a simplified chess variant which reduces the board to 4 columns and 5 rows. Each player has four pawns, two rooks, one queen, and one king as can be seen in the image above. The rules of this variant are the same as traditional chess in terms of piece movement and promotion. However, castling or en-passant are not allowed in this variant. Additionally, we removed the ability of the pawn to move two squares from the starting row for the sake of simplifying the state space.

## Usage

### Clone this repo
```
git clone https://github.com/AJArnolie/minichess-RL.git
cd minichess-RL
```

### Modify agent parameters at top of chessGUI.py
```
vim chessGUI.py
```

### Run GUI
```
python3 chessGUI.py
```

### Non-GUI option available as well (though not recommended)
```
python3 chess.py
```
