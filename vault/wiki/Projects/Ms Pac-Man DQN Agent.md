---
type: project
project_folder: assign2
sources:
  - raw/assign2/Assignment 2_ Train a Ms. Pac-Man Agent.md
  - raw/assign2/README.md
generated_by:
  - google/gemma-4-26b-a4b-qat
tags:
  - project
---

# Ms Pac-Man DQN Agent

This project README describes a 5,000-episode Deep Q-Network training run for Ms. Pac-Man. The mean score over five evaluation games rose from 492 for the untrained network to 1,342 after training, and raising the replay buffer from 5,000 to 2,500,000 is what turned a flat training curve into a rising one.

## The assignment brief: `Assignment 2_ Train a Ms. Pac-Man Agent.md`

This document outlines the requirements for training a Deep Q-Network (DQN) agent to play Ms. Pac-Man. Students must select three hyperparameters, train the agent, and provide evidence of learning through a README containing GIFs, plots, and evaluation scores.

- Choose three hyperparameters: exploration, episodes, and learning rate.
- Submit one public GitHub repository URL containing the notebook and evidence in its README.
- The notebook requires a Python 3.11–3.13 kernel.
- Exploration stays constant after 1,000 random warm-up decisions.
- An episode ends at game over or the notebook's fixed time limit.
- Keep the notebook's evaluation settings unchanged: the same five seeds, 5% exploration, and time limit.
- The baseline for comparison is an untrained network, not a random-action agent.
- The best GIF is selected from five games and shows at most their first 20 seconds.

Source: [raw/assign2/Assignment 2_ Train a Ms. Pac-Man Agent.md](../../raw/assign2/Assignment%202_%20Train%20a%20Ms.%20Pac-Man%20Agent.md)

## My write-up: `README.md`

- The agent's mean score over five evaluation games rose from 492 to 1,342.
- A 5,000-episode run was conducted using 3,557,262 decisions and 889,066 updates.
- The replay buffer capacity was increased from 5,000 to 2,500,000 transitions.
- The training run took 127.7 minutes on Apple Silicon MPS.
- A 30-seed validation harness was used to measure performance more reliably than the official five-game evaluation.
- The agent's mean survival increased from 589 to 901 decisions per game.
- The training run reached a peak memory usage of 86 GiB.
- The agent's performance was evaluated using a fixed 5% exploration rate during evaluation.

Source: [raw/assign2/README.md](../../raw/assign2/README.md)

## Concepts and tools

- [[Deep Q-Network]]: The assignment requires using a provided notebook to train a Deep Q-Network on Ms. Pac-Man.
- [[Experience Replay]]: The author increased the replay buffer capacity to 2,500,000 to reduce correlation and improve learning.
- [[Fixed Evaluation Protocol]]: The brief requires the same five seeds, 5% exploration, and time limit before and after training, with an untrained network as the baseline.
- [[Hyperparameters]]: Students must choose and explain three specific hyperparameters: exploration, episodes, and learning rate.
- [[PyTorch]]: The project uses PyTorch 2.14.0 for the agent's implementation.
- [[Winner's Curse]]: The validation-best checkpoint scored 1,173.3 on validation seeds but 912.0 on the official five, so the author submitted the final network instead.

## Related projects

- [[Custom nanoGPT Model]]: also uses [[Hyperparameters]], [[PyTorch]]

---
See [[Source Catalog]] for file hashes and ingest details.
