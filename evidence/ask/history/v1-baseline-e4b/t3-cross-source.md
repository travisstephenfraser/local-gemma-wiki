# Evidence card: t3-cross-source

**Question:** What learning rate did the Pac-Man DQN use, and how did the custom LLM do when it was trained at that same learning rate?  
**Kind:** connects two sources  
**Mode:** ask · **Execution:** local (http://localhost:1234/v1) · **Network online during run:** True  
**Model:** `google/gemma-4-e4b` safetensors 4bit · embeddings `text-embedding-embeddinggemma-300m` · run 2026-09-25T21:23:33-0700

## Expected (written before the run)

- Behavior: `answer`
- Sources: `raw/assign2/README.md`, `raw/assign3/README.md`
- Passage: Pac-Man: Learning rate 0.0001, standard Adam rate, left alone deliberately. Custom LLM: '0.0001 is too small. After 3,000 steps the model had barely learned: 4-8/48, with validation loss 1.40-1.83.'

## Retrieved passages (bm25+vector (RRF), 0.05s)

**[S1]** `raw/assign2/README.md:82-91 § Training a Ms. Pac-Man agent with Deep Q-Learning > My three hyperparameters` · bm25 rank 2 · vector rank 1

```text
## My three hyperparameters

| Setting | My value | Notebook default | Why |
|---|---|---|---|
| Exploration | `0.20` | 0.20 | The notebook holds epsilon *constant* instead of annealing it, so one number has to serve the whole run. Standard DQN decays 1.0 to 0.1; 0.20 sits just above the end of that schedule. I also tested 0.05 directly, on the theory that matching training exploration to the 5% used at evaluation would help. It did not, and the experiment is reported in [How I got here](#how-i-got-here-four-experiments). |
| Episodes | `5000` | 100 | 3,557,262 agent decisions, about 28% of the original DQN paper's budget of 50 million frames, which is 12.5 million decisions at four frames each. This is the largest budget that fits a working session at 128 minutes. It is worth spending *only* because the buffer fix below gave the learning curve a slope; at the notebook's default buffer,  …
```

**[S2]** `raw/assign2/README.md:724-732 § Training a Ms. Pac-Man agent with Deep Q-Learning > Known limitations and what I would do next` · bm25 rank 4 · vector rank 3

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

**[S3]** `raw/assign2/README.md:120-123 § Training a Ms. Pac-Man agent with Deep Q-Learning > What I changed and why > `REPLAY_CAPACITY`, 5,000 to 2,500,000` · bm25 rank 9 · vector rank 10

```text
The cost is memory and nothing else: sampling 32 items from 2.5 million costs the same as from
5,000, so wall-clock per episode is unchanged. At 5,000 episodes this run peaked at 86 GiB with
zero swap.
```

**[S4]** `raw/assign2/README.md:188-210 § Training a Ms. Pac-Man agent with Deep Q-Learning > Results` · bm25 rank 6 · vector rank 16

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

**[S5]** `raw/assign2/README.md:20-47 § Training a Ms. Pac-Man agent with Deep Q-Learning` · bm25 rank 23 · vector rank 2

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

**[S6]** `raw/assign2/README.md:472-484 § Training a Ms. Pac-Man agent with Deep Q-Learning > Architecture > What this design does not claim` · bm25 rank 16 · vector rank 8

```text
### What this design does not claim

- It does not claim the agent understands ghosts. Reward clipping removes the gradient that
  would teach it.
- It does not claim these hyperparameters are optimal. Three of the many available settings were
  explored, and the search was guided by a measured failure mode rather than by a sweep.
- It does not claim a benchmark reproduction. Published DQN on this game uses 50 million frames;
  this run used 14.2 million.
- It does not claim the 30-seed harness is a substitute for the official protocol. It is a
  decision-making instrument; the reported number is always the official one.

---
```

## Gemma's answer

The learning rate used for the Pac-Man DQN was `0.0001` [S1, S5].

When trained, the agent underwent evaluation after 5,000 episodes [S1, S5]. The results showed that all five evaluation seeds improved [S4]. Specifically, the mean score increased from 492.0 (untrained) to 1,342.0 (after training) [S4]. Furthermore, the mean survival rate increased from 589 to 901 decisions per game [S4].

*8.75s generation, 2059 prompt tokens*

## Citation check: 5 supported

- **supported** (S1, S5, overlap 0.7): The learning rate used for the Pac-Man DQN was `0.0001` .
- **supported** (S1, S5, overlap 0.75): When trained, the agent underwent evaluation after 5,000 episodes .
- **supported** (S4, overlap 0.86): The results showed that all five evaluation seeds improved .
- **supported** (S4, overlap 0.77): Specifically, the mean score increased from 492.0 (untrained) to 1,342.0 (after training) .
- **supported** (S4, overlap 0.7): Furthermore, the mean survival rate increased from 589 to 901 decisions per game .

## Score

| retrieval hit | behavior | exact facts | citations | PASS |
|---|---|---|---|---|
| ❌ | ✅ | ❌ | ✅ | ❌ |

## Assessment

_Human review: see README evidence section._
