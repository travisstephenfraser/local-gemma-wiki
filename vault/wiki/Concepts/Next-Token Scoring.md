---
type: concept
sources:
  - raw/assign3/evals/README.md
tags:
  - concept
---

# Next-Token Scoring

Grading a language model by which candidate word it assigns the highest next-token probability.

## Where it appears

### [[Custom nanoGPT Model]]
- Each case feeds a prefix to the trained nanoGPT and scores it correct if the right word has the highest probability among four candidates. ([raw/assign3/evals/README.md](../../raw/assign3/evals/README.md))
- Used alongside [[Ablation]], [[Corpus]], [[Eval Leakage]], [[Hyperparameters]], [[Margin]], [[nanoGPT]], [[Out-of-Vocabulary Cases]], [[PyTorch]], [[Transformer]] in this project.
