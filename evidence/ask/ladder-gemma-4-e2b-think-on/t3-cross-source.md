# Evidence card: t3-cross-source

**Question:** What learning rate did the Pac-Man DQN use, and how did the custom LLM do when it was trained at that same learning rate?  
**Kind:** connects two sources  
**Mode:** ask · **Execution:** local (http://localhost:1234/v1) · **Network online during run:** True  
**Model:** `google/gemma-4-e2b` safetensors 4bit · embeddings `text-embedding-embeddinggemma-300m` · run 2026-09-25T21:49:46-0700

## Expected (written before the run)

- Behavior: `answer`
- Sources: `raw/assign2/README.md`, `raw/assign3/README.md`
- Passage: Pac-Man: Learning rate 0.0001, standard Adam rate, left alone deliberately. Custom LLM: '0.0001 is too small. After 3,000 steps the model had barely learned: 4-8/48, with validation loss 1.40-1.83.'

## Retrieved passages (bm25+vector (RRF) · query planning (0 sub-queries), 0.15s)

**[S1]** `raw/assign2/README.md:82-91 § Training a Ms. Pac-Man agent with Deep Q-Learning > My three hyperparameters` · bm25 rank 2 · vector rank 1

```text
## My three hyperparameters

| Setting | My value | Notebook default | Why |
|---|---|---|---|
| Exploration | `0.20` | 0.20 | The notebook holds epsilon *constant* instead of annealing it, so one number has to serve the whole run. Standard DQN decays 1.0 to 0.1; 0.20 sits just above the end of that schedule. I also tested 0.05 directly, on the theory that matching training exploration to the 5% used at evaluation would help. It did not, and the experiment is reported in [How I got here](#how-i-got-here-four-experiments). |
| Episodes | `5000` | 100 | 3,557,262 agent decisions, about 28% of the original DQN paper's budget of 50 million frames, which is 12.5 million decisions at four frames each. This is the largest budget that fits a working session at 128 minutes. It is worth spending *only* because the buffer fix below gave the learning curve a slope; at the notebook's default buffer,  …
```

**[S2]** `raw/assign2/README.md:724-732 § Training a Ms. Pac-Man agent with Deep Q-Learning > Known limitations and what I would do next` · bm25 rank 5 · vector rank 3

```text
gradient pointing toward chasing a blue ghost.
- **The GIFs show 20 seconds of games that now last 60.** The visible excerpt is the easy opening,
  not the deaths, so gameplay judgements from the GIFs alone are biased toward the agent. This got
  worse as the agent improved, because the games got longer while the excerpt did not.
- **One test assertion is environment-specific, and I introduced a second mismatch.** Covered in
  [Tests](#tests).
- **Not a benchmark reproduction.** Published DQN results on this game use a 1,000,000-transition
  buffer and 50 million frames. This run used 2.5M transitions and 14.2 million frames.
```

**[S3]** `raw/assign2/README.md:120-123 § Training a Ms. Pac-Man agent with Deep Q-Learning > What I changed and why > `REPLAY_CAPACITY`, 5,000 to 2,500,000` · bm25 rank 10 · vector rank 10

```text
The cost is memory and nothing else: sampling 32 items from 2.5 million costs the same as from
5,000, so wall-clock per episode is unchanged. At 5,000 episodes this run peaked at 86 GiB with
zero swap.
```

**[S4]** `raw/assign2/README.md:20-47 § Training a Ms. Pac-Man agent with Deep Q-Learning` · bm25 rank 24 · vector rank 2

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

**[S5]** `raw/assign2/README.md:188-210 § Training a Ms. Pac-Man agent with Deep Q-Learning > Results` · bm25 rank 8 · vector rank 16

```text
## Results

All ten games below use the notebook's unchanged evaluation protocol: the same five seeds, 5%
exploration, the same 3,000-decision cap, and a separate environment that never touches replay
or weights. The baseline is the **untrained network**, as the assignment specifies.

| Evaluation game | Seed | Before (untrained) | After (5,000 episodes) | Change |
|---|---|---|---|---|
| 1 | 101 | 350 | 1,220 | +870 |
| 2 | 202 | 500 | 1,700 | +1,200 |
| 3 | 303 | 320 | 1,000 | +680 |
| 4 | 404 | 800 | 1,320 | +520 |
| 5 | 505 | 490 | 1,470 | +980 |
| **Mean** | | **492.0** | **1,342.0** | **+850.0** |

**All five seeds improved**, and the weakest trained game (1,000) beats the strongest untrained
game (800). No game in either set hit the time limit, so every game ended in a real game over.
Full data: [`results/comparison.json`](results/comparison.json).

**Survival.** The trained agent …
```

**[S6]** `raw/assign2/README.md:1-21 § Training a Ms. Pac-Man agent with Deep Q-Learning` · bm25 rank 7 · vector rank 18

```text
# Training a Ms. Pac-Man agent with Deep Q-Learning

**A 5,000-episode DQN run that scores 2.73x its untrained baseline, the one setting change that
made the difference, and the measurements that say how much of it to believe.**

This repository is my submission for Class 3. It uses the course's ready-made Deep Q-Network
notebook, which learns to play Ms. Pac-Man from raw screen pixels. The agent's mean score over
the five evaluation games rose from **492 to 1,342**, and all five seeds improved.

The part worth reading is not that number. My first submission scored 918 from a 1,000-episode
run, and I could not tell whether that gain was learning or luck, because a five-game
evaluation has a noise floor of roughly ±530 points. So I built a 30-seed validation harness on
seeds the leaderboard never touches, used it to test three hypotheses in order, and found that
the notebook's 5,000-trans …
```

## Gemma's answer

The Pac-Man DQN used a learning rate of $0.0001$ or $1e-4$ [S1, S4]. Information regarding how a custom LLM performed when trained at that same learning rate is not present in the provided passages.

*4.17s generation, 2233 prompt tokens*

## Citation check: 1 supported, 1 uncited

- **supported** (S1, S4, overlap 0.77): The Pac-Man DQN used a learning rate of $0.0001$ or $1e-4$ .
- **uncited** (no citation, overlap 0.0): Information regarding how a custom LLM performed when trained at that same learning rate is not present in the provided passages.

## Score

| retrieval hit | behavior | exact facts | citations | PASS |
|---|---|---|---|---|
| ❌ | ✅ | ❌ | ❌ | ❌ |

## Assessment

_Human review: see README evidence section._
