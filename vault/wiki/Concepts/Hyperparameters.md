---
type: concept
sources:
  - raw/assign2/Assignment 2_ Train a Ms. Pac-Man Agent.md
  - raw/assign2/README.md
  - raw/assign3/Assignment 3_ Building a Custom LLM.md
  - raw/assign3/README.md
  - raw/assign3/experiments/summary.md
tags:
  - concept
---

# Hyperparameters

Parameters set before the beginning of a training process that control the learning behavior of the model.

## Where it appears

### [[Custom nanoGPT Model]]
- The assignment requires students to choose training steps and a learning rate as hyperparameters. ([raw/assign3/Assignment 3_ Building a Custom LLM.md](../../raw/assign3/Assignment%203_%20Building%20a%20Custom%20LLM.md))
- The document discusses adjusting training steps, learning rate, and model depth (layers). ([raw/assign3/README.md](../../raw/assign3/README.md))
- Conditions vary learning rate (0.0001, 0.01, 0.03), step count (10000), and layer count (1, 4) against baseline B. ([raw/assign3/experiments/summary.md](../../raw/assign3/experiments/summary.md))
- Used alongside [[Ablation]], [[Corpus]], [[Eval Leakage]], [[Margin]], [[nanoGPT]], [[Next-Token Scoring]], [[Out-of-Vocabulary Cases]], [[PyTorch]], [[Transformer]] in this project.

### [[Ms Pac-Man DQN Agent]]
- Students must choose and explain three specific hyperparameters: exploration, episodes, and learning rate. ([raw/assign2/Assignment 2_ Train a Ms. Pac-Man Agent.md](../../raw/assign2/Assignment%202_%20Train%20a%20Ms.%20Pac-Man%20Agent.md))
- The author set exploration 0.20, episodes 5,000, and learning rate 0.0001, and separately changed the fixed classroom settings REPLAY_CAPACITY (5,000 to 2,500,000) and DEMO_EVERY (25 to 125). ([raw/assign2/README.md](../../raw/assign2/README.md))
- Used alongside [[Deep Q-Network]], [[Experience Replay]], [[Fixed Evaluation Protocol]], [[PyTorch]], [[Winner's Curse]] in this project.
