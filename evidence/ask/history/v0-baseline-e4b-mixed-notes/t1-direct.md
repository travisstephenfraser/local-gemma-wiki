# Evidence card: t1-direct

**Question:** What replay buffer capacity did the Ms. Pac-Man DQN use, and what was the notebook's default?  
**Kind:** direct, one source  
**Mode:** ask · **Execution:** local (http://localhost:1234/v1) · **Network online during run:** True  
**Model:** `google/gemma-4-e4b` safetensors 4bit · embeddings `text-embedding-embeddinggemma-300m` · run 2026-09-25T21:19:18-0700

## Expected (written before the run)

- Behavior: `answer`
- Sources: `raw/assign2/README.md`
- Passage: REPLAY_CAPACITY | 5,000 | 2,500,000 (section: ### `REPLAY_CAPACITY`, 5,000 to 2,500,000)

## Retrieved passages (bm25+vector (RRF), 0.05s)

**[S1]** `wiki/Concepts/Experience Replay.md:15-17 § Experience Replay > Where it appears > [[Ms Pac-Man DQN Agent]]` · bm25 rank 1 · vector rank 2

```text
### [[Ms Pac-Man DQN Agent]]
- The author increased the replay buffer capacity to 2,500,000 to reduce correlation and improve learning. ([raw/assign2/README.md](../../raw/assign2/README.md))
- Used alongside [[Deep Q-Network]], [[Fixed Evaluation Protocol]], [[Hyperparameters]], [[PyTorch]], [[Winner's Curse]] in this project.
```

**[S2]** `wiki/Projects/Ms Pac-Man DQN Agent.md:45-53 § Ms Pac-Man DQN Agent > Concepts and tools` · bm25 rank 2 · vector rank 3

```text
## Concepts and tools

- [[Deep Q-Network]]: The assignment requires using a provided notebook to train a Deep Q-Network on Ms. Pac-Man.
- [[Experience Replay]]: The author increased the replay buffer capacity to 2,500,000 to reduce correlation and improve learning.
- [[Fixed Evaluation Protocol]]: The brief requires the same five seeds, 5% exploration, and time limit before and after training, with an untrained network as the baseline.
- [[Hyperparameters]]: Students must choose and explain three specific hyperparameters: exploration, episodes, and learning rate.
- [[PyTorch]]: The project uses PyTorch 2.14.0 for the agent's implementation.
- [[Winner's Curse]]: The validation-best checkpoint scored 1,173.3 on validation seeds but 912.0 on the official five, so the author submitted the final network instead.
```

**[S3]** `wiki/Projects/Ms Pac-Man DQN Agent.md:13-16 § Ms Pac-Man DQN Agent` · bm25 rank 3 · vector rank 4

```text
# Ms Pac-Man DQN Agent

This project README describes a 5,000-episode Deep Q-Network training run for Ms. Pac-Man. The mean score over five evaluation games rose from 492 for the untrained network to 1,342 after training, and raising the replay buffer from 5,000 to 2,500,000 is what turned a flat training curve into a rising one.
```

**[S4]** `raw/assign2/README.md:82-91 § Training a Ms. Pac-Man agent with Deep Q-Learning > My three hyperparameters` · bm25 rank 4 · vector rank 8

```text
## My three hyperparameters

| Setting | My value | Notebook default | Why |
|---|---|---|---|
| Exploration | `0.20` | 0.20 | The notebook holds epsilon *constant* instead of annealing it, so one number has to serve the whole run. Standard DQN decays 1.0 to 0.1; 0.20 sits just above the end of that schedule. I also tested 0.05 directly, on the theory that matching training exploration to the 5% used at evaluation would help. It did not, and the experiment is reported in [How I got here](#how-i-got-here-four-experiments). |
| Episodes | `5000` | 100 | 3,557,262 agent decisions, about 28% of the original DQN paper's budget of 50 million frames, which is 12.5 million decisions at four frames each. This is the largest budget that fits a working session at 128 minutes. It is worth spending *only* because the buffer fix below gave the learning curve a slope; at the notebook's default buffer,  …
```

**[S5]** `wiki/Concepts/Deep Q-Network.md:16-19 § Deep Q-Network > Where it appears > [[Ms Pac-Man DQN Agent]]` · bm25 rank 5 · vector rank 7

```text
### [[Ms Pac-Man DQN Agent]]
- The assignment requires using a provided notebook to train a Deep Q-Network on Ms. Pac-Man. ([raw/assign2/Assignment 2_ Train a Ms. Pac-Man Agent.md](../../raw/assign2/Assignment%202_%20Train%20a%20Ms.%20Pac-Man%20Agent.md))
- The project uses a Deep Q-Network architecture with 3 convolutional layers and 2 dense layers. ([raw/assign2/README.md](../../raw/assign2/README.md))
- Used alongside [[Experience Replay]], [[Fixed Evaluation Protocol]], [[Hyperparameters]], [[PyTorch]], [[Winner's Curse]] in this project.
```

**[S6]** `raw/assign2/README.md:522-553 § Training a Ms. Pac-Man agent with Deep Q-Learning > Local setup` · bm25 rank 9 · vector rank 5

```text
## Local setup

Python 3.11 to 3.13. The notebook installs its own packages on first run.

```bash
git clone <REMOTE_URL>
cd pacman-dqn
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m ipykernel install --user --name pacman-dqn --display-name "pacman-dqn"
python -m jupyter lab pacman_dqn.ipynb
```

Select the `pacman-dqn` kernel and Run All. On Apple Silicon the notebook selects MPS
automatically; elsewhere it selects CUDA or CPU.

To run it headless instead:

```bash
python -m jupyter nbconvert --to notebook --execute --inplace pacman_dqn.ipynb \
  --ExecutePreprocessor.kernel_name=pacman-dqn --ExecutePreprocessor.timeout=-1
```

**Memory.** `REPLAY_CAPACITY = 2500000` needs about 82 GiB of RAM at 5,000 episodes, since each
transition stores five 84x84 frames at 35,280 bytes. On a smaller machine, reduce it. The
formula is `capacity x 5 x 84 x 84 …
```

## Gemma's answer

The Ms. Pac-Man DQN project used a replay buffer capacity of 2,500,000 [S1, S2, S3, S6]. This increase was made to reduce correlation and improve learning [S1, S2]. The capacity was raised from a notebook default of 5,000 [S3].

*6.49s generation, 1692 prompt tokens*

## Citation check: 2 supported, 1 weak

- **supported** (S1, S2, S3, S6, overlap 1.0): Pac-Man DQN project used a replay buffer capacity of 2,500,000 .
- **supported** (S1, S2, overlap 0.67): This increase was made to reduce correlation and improve learning .
- **weak** (S3, overlap 0.33): The capacity was raised from a notebook default of 5,000 .

## Score

| retrieval hit | behavior | exact facts | citations | PASS |
|---|---|---|---|---|
| ❌ | ✅ | ✅ | ❌ | ❌ |

## Assessment

_Human review: see README evidence section._
