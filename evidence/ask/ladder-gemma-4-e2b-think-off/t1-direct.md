# Evidence card: t1-direct

**Question:** What replay buffer capacity did the Ms. Pac-Man DQN use, and what was the notebook's default?  
**Kind:** direct, one source  
**Mode:** ask · **Execution:** local (http://localhost:1234/v1) · **Network online during run:** True  
**Model:** `google/gemma-4-e2b` safetensors 4bit · embeddings `text-embedding-embeddinggemma-300m` · run 2026-09-25T21:49:38-0700

## Expected (written before the run)

- Behavior: `answer`
- Sources: `raw/assign2/README.md`
- Passage: REPLAY_CAPACITY | 5,000 | 2,500,000 (section: ### `REPLAY_CAPACITY`, 5,000 to 2,500,000)

## Retrieved passages (bm25+vector (RRF) · query planning (0 sub-queries), 1.69s)

**[S1]** `raw/assign2/README.md:82-91 § Training a Ms. Pac-Man agent with Deep Q-Learning > My three hyperparameters` · bm25 rank 1 · vector rank 3

```text
## My three hyperparameters

| Setting | My value | Notebook default | Why |
|---|---|---|---|
| Exploration | `0.20` | 0.20 | The notebook holds epsilon *constant* instead of annealing it, so one number has to serve the whole run. Standard DQN decays 1.0 to 0.1; 0.20 sits just above the end of that schedule. I also tested 0.05 directly, on the theory that matching training exploration to the 5% used at evaluation would help. It did not, and the experiment is reported in [How I got here](#how-i-got-here-four-experiments). |
| Episodes | `5000` | 100 | 3,557,262 agent decisions, about 28% of the original DQN paper's budget of 50 million frames, which is 12.5 million decisions at four frames each. This is the largest budget that fits a working session at 128 minutes. It is worth spending *only* because the buffer fix below gave the learning curve a slope; at the notebook's default buffer,  …
```

**[S2]** `raw/assign2/README.md:522-553 § Training a Ms. Pac-Man agent with Deep Q-Learning > Local setup` · bm25 rank 3 · vector rank 2

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

**[S3]** `raw/assign2/README.md:97-121 § Training a Ms. Pac-Man agent with Deep Q-Learning > What I changed and why > `REPLAY_CAPACITY`, 5,000 to 2,500,000` · bm25 rank 7 · vector rank 1

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

**[S4]** `raw/assign2/Assignment 2_ Train a Ms. Pac-Man Agent.md:5-8 § Overview` · bm25 rank 4 · vector rank 8

```text
# Overview

Use the ready-made notebook to train a Deep Q-Network (DQN) on Ms. Pac-Man. Choose exploration, episodes, and learning rate. Submit one public GitHub repository URL with the notebook and your evidence in its README.
```

**[S5]** `raw/assign2/README.md:20-47 § Training a Ms. Pac-Man agent with Deep Q-Learning` · bm25 rank 9 · vector rank 5

```text
**What I changed beyond the three assigned hyperparameters, stated up front.** The brief allows
tuning other settings if you explain what you did and why, and I did:

| Change | From | To | Kind |
|---|---|---|---|
| `EPISODES` | 1,000 | 5,000 | one of my three choices |
| `REPLAY_CAPACITY` | 5,000 | 2,500,000 | a *fixed classroom setting* in section 3 |
| `DEMO_EVERY` | 25 | 125 | a fixed classroom setting, bookkeeping only |
| `ReplayMemory.sample()` | `deque` scan | ring buffer | *source code*, not a hyperparameter |

`EXPLORATION` stays at 0.20 and `LEARNING_RATE` stays at 1e-4. **Every evaluation setting is
untouched**: the same five seeds, 5% exploration, and the same 3,000-decision cap, before and
after, exactly as the brief requires. Each change is justified in
[What I changed and why](#what-i-changed-and-why).

The notebook itself is the course's work ([pepealonso95/pacman-dqn]( …
```

**[S6]** `raw/assign2/README.md:485-495 § Training a Ms. Pac-Man agent with Deep Q-Learning > Technology stack and why` · bm25 rank 8 · vector rank 7

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

## Gemma's answer

The replay memory capacity used was 5,000 [S3]. The notebook's default for the replay capacity is not explicitly stated in the provided passages.

*0.4s generation, 2434 prompt tokens*

## Citation check: 1 supported, 1 uncited

- **supported** (S3, overlap 0.83): The replay memory capacity used was 5,000 .
- **uncited** (no citation, overlap 0.0): The notebook's default for the replay capacity is not explicitly stated in the provided passages.

## Score

| retrieval hit | behavior | exact facts | citations | PASS |
|---|---|---|---|---|
| ✅ | ✅ | ❌ | ❌ | ❌ |

## Assessment

_Human review: see README evidence section._
