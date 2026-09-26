---
type: concept
sources:
  - raw/assign2/README.md
tags:
  - concept
---

# Winner's Curse

Picking the best of many noisy measurements inflates its score, so the winner underperforms on fresh data.

## Where it appears

### [[Ms Pac-Man DQN Agent]]
- The validation-best checkpoint scored 1,173.3 on validation seeds but 912.0 on the official five, so the author submitted the final network instead. ([raw/assign2/README.md](../../raw/assign2/README.md))
- Used alongside [[Deep Q-Network]], [[Experience Replay]], [[Fixed Evaluation Protocol]], [[Hyperparameters]], [[PyTorch]] in this project.
