---
type: concept
sources:
  - raw/assign2/README.md
tags:
  - concept
---

# Experience Replay

A technique to break correlation between consecutive frames by sampling random batches of past experiences.

## Where it appears

### [[Ms Pac-Man DQN Agent]]
- The author increased the replay buffer capacity to 2,500,000 to reduce correlation and improve learning. ([raw/assign2/README.md](../../raw/assign2/README.md))
- Used alongside [[Deep Q-Network]], [[Fixed Evaluation Protocol]], [[Hyperparameters]], [[PyTorch]], [[Winner's Curse]] in this project.
