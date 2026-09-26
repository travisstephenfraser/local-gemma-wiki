# Evidence card: t1-direct

**Question:** What replay buffer capacity did the Ms. Pac-Man DQN use, and what was the notebook's default?  
**Kind:** direct, one source  
**Mode:** ask · **Execution:** local (http://localhost:1234/v1) · **Network online during run:** True  
**Model:** `google/gemma-4-e4b` safetensors 4bit · embeddings `text-embedding-embeddinggemma-300m` · run 2026-09-25T21:50:21-0700

## Expected (written before the run)

- Behavior: `answer`
- Sources: `raw/assign2/README.md`
- Passage: REPLAY_CAPACITY | 5,000 | 2,500,000 (section: ### `REPLAY_CAPACITY`, 5,000 to 2,500,000)

## Retrieved passages (bm25+vector (RRF) · query planning (2 sub-queries), 0.43s)

**[S1]** `raw/assign2/README.md:82-91 § Training a Ms. Pac-Man agent with Deep Q-Learning > My three hyperparameters` · bm25 rank 1 · vector rank 3

```text
## My three hyperparameters

| Setting | My value | Notebook default | Why |
|---|---|---|---|
| Exploration | `0.20` | 0.20 | The notebook holds epsilon *constant* instead of annealing it, so one number has to serve the whole run. Standard DQN decays 1.0 to 0.1; 0.20 sits just above the end of that schedule. I also tested 0.05 directly, on the theory that matching training exploration to the 5% used at evaluation would help. It did not, and the experiment is reported in [How I got here](#how-i-got-here-four-experiments). |
| Episodes | `5000` | 100 | 3,557,262 agent decisions, about 28% of the original DQN paper's budget of 50 million frames, which is 12.5 million decisions at four frames each. This is the largest budget that fits a working session at 128 minutes. It is worth spending *only* because the buffer fix below gave the learning curve a slope; at the notebook's default buffer,  …
```

**[S2]** `raw/assign2/README.md:97-121 § Training a Ms. Pac-Man agent with Deep Q-Learning > What I changed and why > `REPLAY_CAPACITY`, 5,000 to 2,500,000` · bm25 rank 3 · vector rank 1

```text
### `REPLAY_CAPACITY`, 5,000 to 2,500,000

**This is the change that made the difference, and it is not a close call.**

At 5,000 transitions and roughly 610 decisions per game, the notebook's buffer holds about
**eight games**. Every batch of 32 is drawn from that narrow, highly correlated window, so the
network is continuously refit to the last few games and forgets everything earlier. That is
precisely the correlation experience replay exists to break. Published DQN uses a buffer of
1,000,000; the notebook ships with 0.5% of that.

I tested it as a falsifiable prediction rather than assuming it. Holding everything else at the
original 1,000-episode settings and raising capacity to 700,000, which exceeds the 609,223
decisions such a run produces so that *nothing is ever evicted*:

| | buffer 5,000 | buffer 700,000 |
|---|---|---|
| 30-seed mean of the last five checkpoints | 694.3 | ** …
```

**[S3]** `raw/assign2/README.md:522-553 § Training a Ms. Pac-Man agent with Deep Q-Learning > Local setup` · bm25 rank 3 · vector rank 2

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

**[S4]** `raw/assign2/README.md:485-495 § Training a Ms. Pac-Man agent with Deep Q-Learning > Technology stack and why` · bm25 rank 5 · vector rank 8

```text
## Technology stack and why

| Layer | Choice | Why |
|---|---|---|
| Environment | Gymnasium + ale-py, `ALE/MsPacman-v5` | The course's choice. Sticky actions at 0.25 are on, which is the standard modern Atari protocol and makes memorised action sequences useless. |
| Agent | PyTorch DQN, 3 conv + 2 dense | The course's architecture, unchanged. Nothing in the evidence pointed at capacity as the limit, so changing it would have added a variable without a reason. |
| Compute | Apple Silicon MPS | A 128-minute local run beats the Colab CPU tier and cannot time out mid-session. The one cost is a test assertion that hardcodes Python 3.13. |
| Replay memory | List-backed ring buffer | Replaces a `deque` whose `sample()` was O(n) per update. Identical draws, O(1) indexing. See [the fix](#replaymemorysample-a-performance-fix). |
| Optimiser | Adam, Huber loss | Huber is less sensitive to the oc …
```

**[S5]** `raw/assign2/Assignment 2_ Train a Ms. Pac-Man Agent.md:5-8 § Overview` · bm25 rank 4 · vector rank 8

```text
# Overview

Use the ready-made notebook to train a Deep Q-Network (DQN) on Ms. Pac-Man. Choose exploration, episodes, and learning rate. Submit one public GitHub repository URL with the notebook and your evidence in its README.
```

**[S6]** `raw/assign2/README.md:130-161 § Training a Ms. Pac-Man agent with Deep Q-Learning > What I changed and why > `ReplayMemory.sample()`, a performance fix` · bm25 rank 14 · vector rank 2

```text
### `ReplayMemory.sample()`, a performance fix

This one is source code, not a hyperparameter, so it needs stating plainly. The shipped method
was:

```python
batch = rng.sample(list(self.items), size)   # list() copies the entire buffer, every update
```

That rebuilds the whole buffer as a list on *every one of the 889,066 updates*. It is invisible
at 5,000 items and quadratic after that:

| Buffer | Cost per update | Added over a run |
|---|---|---|
| 5,000 | 0.019 ms | negligible, which is why nobody notices |
| 611,000 | 1.680 ms | +4.4 minutes |
| 2,500,000 | ~6.9 ms | over an hour |

A `deque` is also O(n) for random indexing, so the obvious fix does not help. The replacement is
a list-backed ring buffer that indexes in O(1) and draws its sample by index:

```python
batch = [self.items[i] for i in rng.sample(range(len(self.items)), size)]
```

**This changes speed, not behaviour.* …
```

## Gemma's answer

The experiment discussed capacities of 5,000 and 2,500,000 transitions [S2], [S3]. The notebook's default buffer size was 0.5% of the published DQN's buffer, which uses a capacity of 1,000,000 [S2]. At the default setting of 5,000 transitions, the notebook's buffer held about eight games [S2].

*13.93s generation, 2425 prompt tokens*

## Citation check: 3 supported

- **supported** (S2, S3, overlap 0.62): The experiment discussed capacities of 5,000 and 2,500,000 transitions , .
- **supported** (S2, overlap 0.86): The notebook's default buffer size was 0.5% of the published DQN's buffer, which uses a capacity of 1,000,000 .
- **supported** (S2, overlap 0.75): At the default setting of 5,000 transitions, the notebook's buffer held about eight games .

## Score

| retrieval hit | behavior | exact facts | citations | PASS |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ |

## Assessment

_Human review: see README evidence section._
