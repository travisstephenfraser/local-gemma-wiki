---
type: concept
sources:
  - raw/assign3/evals/README.md
tags:
  - concept
---

# Out-of-Vocabulary Cases

Test cases containing words the model never learned, which it cannot score.

## Where it appears

### [[Custom nanoGPT Model]]
- A case whose prompt or answer choice has a word outside the learned vocabulary is marked out_of_vocabulary and scores zero in the all-case rate. ([raw/assign3/evals/README.md](../../raw/assign3/evals/README.md))
- Used alongside [[Ablation]], [[Corpus]], [[Eval Leakage]], [[Hyperparameters]], [[Margin]], [[nanoGPT]], [[Next-Token Scoring]], [[PyTorch]], [[Transformer]] in this project.
