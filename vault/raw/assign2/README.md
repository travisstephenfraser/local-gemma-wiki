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
the notebook's 5,000-transition replay buffer, which holds about *eight games*, was the thing
holding the agent back. Raising it is what turned a flat training curve into a rising one.

Two of the three hypotheses were wrong, and both are written up below rather than quietly
dropped.

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

The notebook itself is the course's work ([pepealonso95/pacman-dqn](https://github.com/pepealonso95/pacman-dqn));
my contribution is the hyperparameter choices, the executed runs, the validation harness, the
experiments, and this write-up. It was written with the help of Claude Code, which ran the
notebook and drafted this README from the run's output files.

**Status: complete.** The run finished all 5,000 episodes without interruption.

---

```
Task        ALE/MsPacman-v5 (Atari 2600, via Gymnasium + ale-py)
Agent       Deep Q-Network: 3 conv layers + 2 dense, experience replay, target network
Input       4 stacked grayscale 84x84 frames
Hardware    Apple Silicon MPS, macOS 26.6.2 arm64, Python 3.12.14, PyTorch 2.14.0
Run         5,000 episodes | 3,557,262 decisions | 889,066 updates | 127.7 minutes
Result      492 -> 1,342 mean score over 5 fixed seeds (+850, 2.73x, all 5 seeds up)
```

**Runs locally or in Colab. There is no deployed service.**
[Open the notebook in Google Colab](https://colab.research.google.com/github/travisstephenfraser/pacman-dqn/blob/main/pacman_dqn.ipynb)

---

## Contents

- [My three hyperparameters](#my-three-hyperparameters)
- [What I changed and why](#what-i-changed-and-why)
- [What I expected, and what happened](#what-i-expected-and-what-happened)
- [Results](#results)
- [Gameplay](#gameplay)
- [Is the improvement real?](#is-the-improvement-real)
- [How I got here: four experiments](#how-i-got-here-four-experiments)
- [What the agent actually sees, does, and is paid for](#what-the-agent-actually-sees-does-and-is-paid-for)
- [Architecture](#architecture)
- [Technology stack and why](#technology-stack-and-why)
- [What a run produces](#what-a-run-produces)
- [Local setup](#local-setup)
- [Tests](#tests)
- [Grading evidence](#grading-evidence)
- [Reproducing this run](#reproducing-this-run)
- [Known limitations and what I would do next](#known-limitations-and-what-i-would-do-next)
- [Not applicable to this project](#not-applicable-to-this-project)
- [License](#license)
- [Contributing](#contributing)

---

## My three hyperparameters

| Setting | My value | Notebook default | Why |
|---|---|---|---|
| Exploration | `0.20` | 0.20 | The notebook holds epsilon *constant* instead of annealing it, so one number has to serve the whole run. Standard DQN decays 1.0 to 0.1; 0.20 sits just above the end of that schedule. I also tested 0.05 directly, on the theory that matching training exploration to the 5% used at evaluation would help. It did not, and the experiment is reported in [How I got here](#how-i-got-here-four-experiments). |
| Episodes | `5000` | 100 | 3,557,262 agent decisions, about 28% of the original DQN paper's budget of 50 million frames, which is 12.5 million decisions at four frames each. This is the largest budget that fits a working session at 128 minutes. It is worth spending *only* because the buffer fix below gave the learning curve a slope; at the notebook's default buffer, more episodes bought more flat trajectory. |
| Learning rate | `0.0001` | 0.0001 | The standard Adam rate for DQN. I left it alone deliberately: the instability I measured pointed at the replay buffer and the target network rather than the step size, so changing the learning rate would have confounded the one experiment that mattered. |

---

## What I changed and why

Three changes fall outside the three assigned hyperparameters. The brief permits this with an
explanation, and the replay buffer is the substantive one.

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
| 30-seed mean of the last five checkpoints | 694.3 | **990.2** |
| Trend correlation across 40 checkpoints | 0.40 | **0.72** |
| Best checkpoint | episode 825 | **episode 1,000** |

The gain is +295.9 with a standard error near 48, about **6.2 sigma**. For the first time the
*final* checkpoint was also the best one, meaning the curve rises rather than oscillating.

The cost is memory and nothing else: sampling 32 items from 2.5 million costs the same as from
5,000, so wall-clock per episode is unchanged. At 5,000 episodes this run peaked at 86 GiB with
zero swap.

### `DEMO_EVERY`, 25 to 125

Bookkeeping. At 5,000 episodes the original value would write 200 checkpoints and 200 GIFs.
125 keeps the run at 40 periodic samples, the same number every earlier run produced, so the
checkpoint sweeps stay directly comparable.

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

**This changes speed, not behaviour.** `random.sample` depends only on the population size, so
for the same RNG state it selects the same indices; while the buffer has not wrapped, the two
implementations return *identical* draws. I verified three things before using it: identical
draws over 200 consecutive samples on an unwrapped buffer, identical retained contents after
wrapping, and 1.680 ms falling to 0.006 ms at 611,000 items.

Without this fix the 5,000-episode run would have spent more time copying lists than learning.

---

## What I expected, and what happened

**What I expected.** After the 1,000-episode run I expected the replay buffer to be the binding
constraint, and I wrote that prediction down before testing it, including the statistic it
would move: the spread across sampled checkpoints should fall well below 630 points.

**What happened.** The mechanism was right and my chosen statistic was wrong. Raising the buffer
did fix the learning curve, at 6.2 sigma, but raw spread *rose* from 794.7 to 876.3 rather than
falling. Raw max-minus-min conflates trend with churn, and the fixed run has a trend the
original did not, so a rising curve inflates it legitimately. On the statistics that separate
the two, residual scatter about the fitted line and the spread across late checkpoints, churn
did fall. I am recording the miss rather than restating the prediction to match the result.

I also expected matching training exploration to evaluation exploration to help. It did not,
and that is written up below.

Watching the GIFs, the trained agent commits to directions and clears pellet corridors instead
of oscillating in place, and it now survives long enough to clear most of a maze. I still see
no evidence it treats ghosts as anything but scenery. It survives **53% longer** than the
untrained network, which is consistent with "moves with purpose" rather than "evades".

---

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

**Survival.** The trained agent also lasts far longer, which is a second signal that does not
depend on the score: mean survival rose from 589 to 901 decisions per game, about 39 to 60
seconds of game time, a 1.53x increase.

### The training run

| Measure | Value |
|---|---|
| Episodes requested / completed | 5,000 / 5,000 (status `completed`) |
| Agent decisions | 3,557,262 |
| Learning updates | 889,066 |
| Elapsed (training plus periodic evaluations) | 7,665 s = 127.7 minutes |
| Device | Apple Silicon MPS |
| Peak memory | 86 GiB, zero swap |
| Best single training game | 4,210 at episode 2,770 |
| Mean of first 25 / last 25 training games | 522.0 / 1,386.0 |

Source: [`results/training_summary.json`](results/training_summary.json),
[`results/config.json`](results/config.json), [`results/training.csv`](results/training.csv).

![Training dashboard](results/training_dashboard.png)

The three panels are raw training score, mean update loss, and exploration. Exploration is a
flat line at 0.20 by design. **The score panel is the one that changed.** In my 1,000-episode
run at the default buffer it wandered between 600 and 900 with no visible climb. Here it rises
monotonically across every 1,000-episode block:

| Episodes | 1-1000 | 1001-2000 | 2001-3000 | 3001-4000 | 4001-5000 |
|---|---|---|---|---|---|
| Mean training score | 757.7 | 970.7 | 1,137.6 | 1,203.3 | **1,309.0** |

Training games are played at 20% exploration, so one move in five is random no matter how good
the policy is. The curve rises anyway.

---

## Gameplay

Every GIF plays at 4x speed and shows the first 20 seconds of a game. The score in each caption
is the full-game score, not the excerpt's.

**Before training.** The untrained network scored 350 on this seed. It reverses direction
constantly and dies in a small area of the maze.

![Untrained agent](results/demos/episode_0000.gif)

**Best trained game.** 1,700 points, the best of the five final evaluation games. This is the
GIF the notebook selects by full-game score.

![Best trained game](results/demos/final_best.gif)

**Across training**, sampled every 250 episodes over the first fifth of the run. These are
single-game evaluations on one seed, which is why they bounce around so much.

| Episode 250 (900) | Episode 500 (790) | Episode 750 (1,050) | Episode 1000 (380) |
|---|---|---|---|
| ![250](results/demos/episode_0250.gif) | ![500](results/demos/episode_0500.gif) | ![750](results/demos/episode_0750.gif) | ![1000](results/demos/episode_1000.gif) |

That row is a fair picture of why single-game samples cannot be trusted: those four numbers span
670 points and come from the *same* training run a few hundred episodes apart. It is the reason
every judgement in this README rests on 30-seed means rather than on demonstration scores.

My run produced **42 GIFs** in total, one every 125 episodes plus the untrained and final
samples. All of them are committed in [`results/demos/`](results/demos); the ones above are a
readable subset. Per-sample scores: [`results/demo_scores.json`](results/demo_scores.json).

---

## Is the improvement real?

**Yes.** This is a stronger answer than my 1,000-episode submission could give, and the reason
is that I built a better measurement before running more experiments.

### The measurement's own noise floor

Training scores in this run have a standard deviation of about 512 points per game. A five-game
mean therefore carries a standard error near 512/sqrt(5), about 229 points, and the difference
between two such means carries about 324. So a before/after gap needs to clear roughly ±650
points before five games alone can call it.

The observed **+850 clears it.** The paired form of the test is stronger still, because the same
five seeds are used on both sides: the mean paired difference is +850 with a standard deviation
of 263, giving **t(4) = 7.21**, well past the conventional threshold. For comparison, my
1,000-episode run gave t(4) = 2.60, which was suggestive and not conclusive. That is the
difference between this submission and the last one.

### A known-answer anchor

The assignment notes the baseline is an untrained network, not a random-action agent, so I
measured a uniform-random policy on the identical seeds and settings as an outside reference
point. This is a check the notebook does not perform.

| Policy | Five-game scores | Mean |
|---|---|---|
| Uniform random actions | 220, 260, 340, 180, 310 | **262** |
| Untrained network (the baseline) | 350, 500, 320, 800, 490 | **492** |
| Trained network, 5,000 episodes | 1,220, 1,700, 1,000, 1,320, 1,470 | **1,342** |

The ladder is ordered correctly, which is the point of running it. The untrained network is
already 1.9x random, so beating it is a real but modest bar; the trained agent is **5.1x
random**. My re-evaluation reproduces the notebook's own 492.0 and 1,342.0 exactly from the
saved checkpoints using an independent script, so the two harnesses agree.
Data: [`results/anchor_scores.json`](results/anchor_scores.json).

### The 30-seed validation harness

Five games cannot resolve most of the questions this project raises, and the five official seeds
are the leaderboard's, so tuning against them would be fitting the test set. I therefore built a
second evaluation on **30 seeds (9001 to 9030), asserted disjoint from the official five**, used
for every decision and never for reporting. At 30 seeds the standard error of a mean falls from
about 229 to about 79, which makes ~220-point differences detectable instead of ~650-point ones.

Evaluation is cheap, so this costs little: 40 checkpoints on 30 seeds is 1,200 games in roughly
ten minutes.

The harness carries two guards, because a measurement that can read its own inputs will report
success either way:

- **A known-answer anchor.** Before any sweep it re-derives two committed score lists on the
  official seeds and *raises* if they have drifted. Because seed 42 fixes the initial weights,
  the untrained network must score 492.0 on the official five and 374.33 on the validation
  seeds in every run. It does, in all five runs below.
- **A degeneracy check.** If fewer than a quarter of the 40 checkpoints produce distinct means,
  or if the random policy ties the untrained network, it raises. Unrelated policies scoring
  identically means the harness is evaluating one thing repeatedly, not many things once.

Both raise rather than warn. The legacy checks still reproduce their committed JSON byte for
byte, so adding the harness provably did not change what is being measured.

### The checkpoint sweep, and why the final number is not the best one

Evaluating all 40 checkpoints on the 30 validation seeds gives the trajectory the five-game
protocol cannot:

| Measure | Value |
|---|---|
| Mean of the last five checkpoints | 1,297.9 |
| Mean across all 40 checkpoints | 1,022.9 |
| Trend correlation, r | 0.76 |
| Final checkpoint (episode 5,000) | 1,171.0 |
| Best checkpoint (episode 4,750) | **1,560.7** |

The best checkpoint beats the final one by 390 points on the validation seeds, which raises an
obvious temptation. **I tested selecting it and rejected it**, on evidence rather than on
principle. In the 1,000-episode run the validation-best checkpoint scored 1,173.3 on the
validation seeds and then **912.0** on the official five, against 918.0 for simply taking the
final network. The 261-point collapse is the *winner's curse*: taking the maximum of 40 noisy
estimates inflates that estimate by roughly two standard errors, and the inflation does not
survive contact with a fresh seed set. The submitted network is the final one.

Data: [`results/checkpoint_sweep.json`](results/checkpoint_sweep.json) (official five),
[`results/validation_sweep.json`](results/validation_sweep.json) (30 seeds),
[`results/selected_checkpoint.json`](results/selected_checkpoint.json) (the rejected selection).

---

## How I got here: four experiments

Each run changed one thing and was judged on the 30-seed sweep rather than on its final score.
Two hypotheses were wrong.

| | buffer 5k, 1k ep | **eps 0.05** | buffer 700k, 1k ep | buffer 2M, 3k ep | buffer 2.5M, 5k ep |
|---|---|---|---|---|---|
| 30-seed tail-5 mean | 694.3 | 751.6 | 990.2 | 1,226.8 | **1,297.9** |
| 30-seed all-40 mean | 650.1 | 637.5 | 676.3 | 908.0 | **1,022.9** |
| Trend r | 0.40 | 0.25 | 0.72 | 0.79 | 0.76 |
| Residual scatter | 171.3 | 192.1 | 164.3 | **160.6** | 189.1 |
| **Official five** | 918.0 | 670.0 | 738.0 | 1,072.0 | **1,342.0** |

**1. Exploration 0.20 to 0.05. Refuted.** Training runs at 20% random moves while evaluation
runs at 5%, so the policy is optimised for conditions it is not scored under. Matching them was
the cheapest available explanation for the instability. It changed nothing: the all-40 mean,
the spread and the residual scatter were all flat or slightly worse, and the trend correlation
*fell* to 0.25. Exploration noise is not what was wrong.

**2. Replay buffer 5,000 to 700,000. Confirmed at 6.2 sigma.** Covered
[above](#replay_capacity-5000-to-2500000).

**3. Scale to 3,000 episodes.** Worth doing only once the curve had a slope, which it now did.
This produced the steadiest run of the five, with residual scatter of 160.6 and only 1.8% of its
experience evicted.

**4. Scale to 5,000 episodes.** The submitted run. Highest on every headline measure.

**One result cuts against the submission and belongs here.** Notice that residual scatter rises
to 189.1 in the final run, the worst of the three fixed-buffer runs. The 3,000-episode run
evicted 1.8% of its experience; this one evicted 30%, because 5,000 episodes produce ~3.56M
transitions and retaining all of them needs 118 GiB, which does not fit alongside other work on
a 128 GB machine. Capacity was therefore set by the memory budget rather than by the experiment.
Forgetting and instability move together across all five runs, so **the memory ceiling probably
cost this run some stability**, and a machine with more RAM would likely do better at this scale.

**A measurement lesson worth recording.** Twice, the official five and the 30 validation seeds
disagreed in *sign*. The 700k-buffer run scored 738.0 on the official five against the
baseline's 918.0, reading as a large regression, while scoring 1,102.3 against 826.7 on 30
seeds, reading as a clear gain. Neither five-game difference was significant. Judged on the
official five alone I would have discarded the single most important change in this project.

---

## What the agent actually sees, does, and is paid for

**Observations: four game screens.** Each Atari frame is cropped and shrunk to an 84x84
grayscale image, and the four most recent are stacked. Four, rather than one, because a single
still frame cannot show which way a ghost is travelling. The stack encodes motion, so the
network can tell a ghost approaching from a ghost retreating. One agent decision covers four
emulator frames, so the agent acts about 15 times a second.

**Actions: joystick moves.** Nine of them, the Atari's centre position plus four directions and
four diagonals. The network outputs one number per action, its estimate of the total future
points that action is worth from the current screen, and the agent normally picks the highest.
With probability 0.20 during training it ignores that and picks at random, which is how it
discovers routes its current estimates would never try.

**Rewards: the game's own points.** Pellets, power pills, eaten ghosts, and fruit, exactly as
the arcade machine awards them. One thing is worth knowing here: during training the reward is
clipped to the range [-1, 1], so a 200-point ghost and a 10-point pellet both become +1 in the
learning signal. That keeps the gradients stable across games with wildly different scales, at
the cost of the agent never learning that ghosts are worth twenty pellets. **Every score
reported in this README is the raw, unclipped game score.** The clipping only shapes learning.

**How it learns.** Each decision is stored as an experience. Every four decisions, the agent
samples a random batch of 32 past experiences and nudges the network so its prediction for the
action it took moves toward the reward it actually received plus its estimate of the next
screen's value, discounted by 0.99. Sampling randomly from memory instead of learning from
consecutive frames breaks the correlation between one moment and the next. That mechanism only
works if memory is large enough to hold experience worth sampling, which is the whole subject of
[What I changed and why](#what-i-changed-and-why). A second frozen copy of the network supplies
the "next screen's value" term and is refreshed every 1,000 decisions, so the target does not
move while the network chases it.

---

## Architecture

```
  pacman_dqn.ipynb  (the course's notebook, executed)
        |
        |  section 1   three hyperparameter choices
        |  section 3   DQN, ReplayMemory, training loop
        |  section 4   evaluate()  <-- fixed seeds, 5% exploration, never writes weights
        |  section 5   training loop, periodic checkpoints + GIFs
        |  section 6   before/after comparison
        v
  pacman_runs/<timestamp>/        gitignored, 42 checkpoints + ZIP
        |
        |  scripts/build_results.py      copies evidence into results/
        |  scripts/evaluate_extra.py     random anchor, checkpoint sweep, 30-seed validation
        v
  results/                        committed evidence, every README number reads from here
```

### The design decision worth explaining

**The separation between training and evaluation is the load-bearing idea, and nothing in this
project touched it.** Evaluation builds its own environment, runs at a fixed 5% exploration,
uses five fixed seeds, and never writes to replay or updates a weight. Training never sees the
evaluation seeds. That separation is what makes a before/after number mean anything, and it is
why every experiment above changed training settings only.

The 30-seed validation harness extends the same principle one level up. Selection pressure has
to land somewhere, and if it lands on the official five then the leaderboard number stops
measuring the agent and starts measuring how hard I tuned against those five games. Putting
selection on a disjoint seed set keeps the reported number honest.

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

## Technology stack and why

| Layer | Choice | Why |
|---|---|---|
| Environment | Gymnasium + ale-py, `ALE/MsPacman-v5` | The course's choice. Sticky actions at 0.25 are on, which is the standard modern Atari protocol and makes memorised action sequences useless. |
| Agent | PyTorch DQN, 3 conv + 2 dense | The course's architecture, unchanged. Nothing in the evidence pointed at capacity as the limit, so changing it would have added a variable without a reason. |
| Compute | Apple Silicon MPS | A 128-minute local run beats the Colab CPU tier and cannot time out mid-session. The one cost is a test assertion that hardcodes Python 3.13. |
| Replay memory | List-backed ring buffer | Replaces a `deque` whose `sample()` was O(n) per update. Identical draws, O(1) indexing. See [the fix](#replaymemorysample-a-performance-fix). |
| Optimiser | Adam, Huber loss | Huber is less sensitive to the occasional large target error than mean squared error, which matters when a single ghost capture produces an outlier. |
| Verification | Plain Python scripts, no framework | The checks need to reproduce their committed output byte for byte; a test runner would add ceremony without adding confidence. |
| Rendering | Pillow, Matplotlib | GIF samples and the dashboard. Pillow rather than a video encoder because a GIF renders inline on GitHub with no plugin. |

---

## What a run produces

Each execution writes `pacman_runs/<timestamp>/` and a matching ZIP. The folder is gitignored
because the checkpoints are large; the evidence subset lives in `results/`.

| Path | Contents |
|---|---|
| `config.json` | Every setting, plus hardware and package versions |
| `training.csv` | One row per episode: score, steps, exploration, mean loss, elapsed |
| `training_summary.json` | Status, completed episodes, decisions, updates, elapsed |
| `comparison.json` | All five before and after scores, seeds, step counts |
| `baseline.json` | The untrained evaluation on its own |
| `demo_scores.json` | Score for each periodic demonstration |
| `demos/*.gif` | Untrained sample, one every 125 episodes, and the best final game |
| `*.pt` | 42 checkpoints: untrained, 40 periodic, final |
| `training_dashboard.png` | Score, loss, and exploration panels |

**Where the checkpoints are.** The 42 `.pt` files total about 271 MB and are deliberately not
committed. They stay in the run folder and its ZIP, which the assignment permits. Only replaying
a mid-training network needs one.

---

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
formula is `capacity x 5 x 84 x 84` bytes, and `capacity = 700000` (23 GiB) is enough to make a
1,000-episode run evict nothing at all. Even 50,000 is ten times the notebook's default and
captures most of the benefit.

---

## Tests

```bash
python tests/verify_notebook.py --kernel pacman-dqn --no-popups
```

This is the course's own end-to-end check. It executes the notebook in order through a real
Jupyter kernel with `EPISODES` rewritten to 5, then asserts on the artifacts that run produced.

**It fails on this machine, and the failure is an environment mismatch rather than a defect.**
Line 59 asserts `config["python"].startswith("3.13.")` while this project runs 3.12.14, and the
project supports 3.11 to 3.13. Assertions after line 59 never execute.

This submission introduces a *second* mismatch with the same file, which I am recording rather
than patching. Line 42 rewrites the literal string `DEMO_EVERY = 25` to `2` so that a 5-episode
run still produces periodic samples. This submission uses `DEMO_EVERY = 125`, which that literal
does not match, so line 74's assertion that demos appear at episodes 2 and 4 would fail on
Python 3.13. Line 59 fires first, so the observed failure is unchanged. `tests/verify_notebook.py`
belongs to the course author and patching it locally would diverge from upstream for no benefit.

Full output, including the traceback:
[`results/test-output-verify.txt`](results/test-output-verify.txt).

### Verification I added

Because the course's test stops at line 59, I re-ran the checks it blocks directly against the
5,000-episode run:

```console
--- checks re-run directly against the 5,000-episode run (the ones line 59 blocks) ---
tensors in model: 10  changed by training: 10  all finite: True
episodes with a post-warmup loss: 4999  all finite: True
GIFs: 42  loop values: {1} (1 == plays twice)
periodic checkpoints: 40  first episode_0125.pt last episode_5000.pt
ALL CHECKS PASSED
```

Beyond that, three checks exist because a measurement that can read its own inputs will report
success either way:

| Check | What it catches | Where |
|---|---|---|
| Known-answer anchor | An evaluation path that has silently changed what it measures | `evaluate_extra.py`, raises |
| Degeneracy guard | One policy being evaluated N times and reported as N policies | `evaluate_extra.py`, raises |
| Byte-for-byte replay | A refactor that quietly altered results | legacy JSON reproduced exactly |

**Falsification.** The checkpoint sweep is the falsification attempt that mattered, and I ran it
against my own claims three times. It broke the first submission's "training steadily improved
the network", it refuted my exploration hypothesis, and it refuted the raw-spread prediction I
made for the buffer fix. The claim that survives, that the final network is far better than the
untrained one, survives at t(4) = 7.21 on the official five and 30-seed confirmation behind it.

---

## Grading evidence

Every item the assignment brief lists, with a link to the committed file behind it.

**Executed notebook with outputs.** [`pacman_dqn.ipynb`](pacman_dqn.ipynb), saved after the final
run. All 28 code cells carry execution counts and outputs, and none raised an error.
`EPISODES = 5000` is visible in section 1. At 4.0 MB it may exceed GitHub's inline notebook
renderer; if the page does not render, use
[nbviewer](https://nbviewer.org/github/travisstephenfraser/pacman-dqn/blob/main/pacman_dqn.ipynb).

**Untrained and best trained GIFs.** [`results/demos/episode_0000.gif`](results/demos/episode_0000.gif)
and [`results/demos/final_best.gif`](results/demos/final_best.gif), both embedded in
[Gameplay](#gameplay).

**Intermediate GIFs and checkpoints.** The run passed 25 episodes, so it produced 40 periodic
samples. All 42 GIFs are in [`results/demos/`](results/demos). The 42 matching checkpoints are
kept locally and in the run ZIP, as described in [What a run produces](#what-a-run-produces).

**Training plot.** [`results/training_dashboard.png`](results/training_dashboard.png), embedded
above with the score, loss, and exploration panels.

**All five before and after scores.** The table in [Results](#results), backed by
[`results/comparison.json`](results/comparison.json).

**Observations, actions, rewards, and one limitation.**
[What the agent actually sees, does, and is paid for](#what-the-agent-actually-sees-does-and-is-paid-for)
and [Known limitations](#known-limitations-and-what-i-would-do-next).

**Actual training budget and hardware.** The table in [Results](#results): 5,000 episodes,
3,557,262 decisions, 889,066 learning updates, 127.7 minutes, Apple Silicon MPS. Status
`completed`, not interrupted, and the learning-update count is non-zero.
Source: [`results/training_summary.json`](results/training_summary.json) and
[`results/config.json`](results/config.json).

**Other hyperparameters tuned, with reasons.** [What I changed and why](#what-i-changed-and-why)
covers `REPLAY_CAPACITY`, `DEMO_EVERY`, and the `ReplayMemory.sample()` fix.
[How I got here](#how-i-got-here-four-experiments) reports every run, including the two that
failed.

**Runs that did not improve, reported honestly.** The exploration experiment scored 670.0 and the
700k-buffer run scored 738.0 on the official five, both below the 918.0 I had already submitted.
Both are in [How I got here](#how-i-got-here-four-experiments) with their sweep data committed as
`results/validation_sweep_eps005.json` and `results/validation_sweep_buf700k.json`.

**Supporting data.** [`results/config.json`](results/config.json),
[`results/training.csv`](results/training.csv),
[`results/training_summary.json`](results/training_summary.json),
[`results/baseline.json`](results/baseline.json),
[`results/demo_scores.json`](results/demo_scores.json),
[`results/anchor_scores.json`](results/anchor_scores.json),
[`results/checkpoint_sweep.json`](results/checkpoint_sweep.json),
[`results/validation_sweep.json`](results/validation_sweep.json),
[`results/selected_checkpoint.json`](results/selected_checkpoint.json),
[`results/run_facts.json`](results/run_facts.json).

**Leaderboard number.** Mean of the five trained evaluation games: **1,342.0**, produced by the
notebook's unchanged evaluation protocol on `trained.pt` after episode 5,000.

**No committed secrets.** This project uses no credentials, API keys, or environment variables. A
scan of the working tree and the full commit history for AWS keys, GitHub and npm tokens, Slack
and OpenAI-style keys, private key blocks, JWTs, and connection strings returns nothing, and no
`.env` file is tracked.

---

## Reproducing this run

The run is seeded, so it reproduces. Because seed 42 fixes the initial weights, every run in this
project evaluates its untrained network at exactly 492.0 on the official five and 374.33 on the
30 validation seeds, which is the anchor the harness asserts.

1. Follow [Local setup](#local-setup), and read the memory note.
2. Set `EXPLORATION = 0.20`, `EPISODES = 5000`, `LEARNING_RATE = 0.0001` in section 1.
3. Confirm `REPLAY_CAPACITY = 2500000` and `DEMO_EVERY = 125` in section 3.
4. Run All. Expect about 128 minutes on Apple Silicon MPS, longer on CPU.
5. Read the five before and after scores printed by section 6b, and the ZIP link in section 7.

**The step that is easy to miss.** The training cell refuses to run twice in one kernel, by
design, so re-running only the training cell after a completed run raises
`RuntimeError: Start a new experiment by rerunning from section 5a`. Restart from section 5a, or
Run All. If you interrupt training, interrupt once and then continue to section 6; the saved
model includes the partial episode but the episode log does not.

### Reproducing the extra checks

The two scripts behind this README's verification are committed and deterministic.

```bash
python scripts/evaluate_extra.py pacman_runs/<your-run>              # random-policy anchor
python scripts/evaluate_extra.py pacman_runs/<your-run> --sweep      # five-checkpoint sweep, official seeds
python scripts/evaluate_extra.py pacman_runs/<your-run> --validate   # 40 checkpoints x 30 validation seeds
python scripts/build_results.py pacman_runs/<your-run>               # rebuild results/
```

`--validate` takes about ten minutes and refuses to run if the known-answer anchor has drifted.
`build_results.py` copies a run folder into `results/` and writes `run_facts.json`, the file every
number in this README is read from. Note that it deletes `results/` before rebuilding it, so the
sweep files must be preserved separately.

---

## Known limitations and what I would do next

- **Capacity was set by my hardware, not by the experiment, and it probably cost stability.**
  Retaining all 3.56M transitions from a 5,000-episode run needs 118 GiB. I capped at 2.5M (82
  GiB), so 30% of the run's experience was evicted. Residual scatter rose to 189.1 from the
  3,000-episode run's 160.6, and forgetting tracks instability across all five runs.
- **The best checkpoint is not the submitted one.** Episode 4,750 scores 1,560.7 on the
  validation seeds against the final network's 1,171.0. I am submitting the final network because
  selecting on the maximum of 40 noisy estimates cost 261 points to the winner's curse when I
  measured it directly.
- **The evaluation is five games.** With a per-game standard deviation near 512, a five-game mean
  carries a standard error of about 229. This run's +850 clears that comfortably at t(4) = 7.21,
  but every *smaller* comparison in this README rests on the 30-seed harness for a reason.
- **The agent shows no evidence of understanding ghosts.** Reward clipping to [-1, 1] makes a
  200-point ghost worth the same as a 10-point pellet in the learning signal, so there is no
  gradient pointing toward chasing a blue ghost.
- **The GIFs show 20 seconds of games that now last 60.** The visible excerpt is the easy opening,
  not the deaths, so gameplay judgements from the GIFs alone are biased toward the agent. This got
  worse as the agent improved, because the games got longer while the excerpt did not.
- **One test assertion is environment-specific, and I introduced a second mismatch.** Covered in
  [Tests](#tests).
- **Not a benchmark reproduction.** Published DQN results on this game use a 1,000,000-transition
  buffer and 50 million frames. This run used 2.5M transitions and 14.2 million frames.

### The next experiment: slow the target network from 1,000 decisions to 5,000

If I could change one setting, it would be `TARGET_EVERY`, from 1,000 to 5,000.

With `TRAIN_EVERY = 4`, the notebook refreshes its target network every **250 gradient updates**.
The original DQN paper refreshes every 10,000. The notebook is therefore bootstrapping off a
target that moves roughly 40x faster than standard, and a fast-moving target is the textbook
cause of the value churn that is still visible in this run's checkpoint sweep.

It is free. No extra memory, no extra wall-clock, one constant.

The prediction is falsifiable and the harness already measures it: **residual scatter about the
fitted trend should fall below this run's 189.1**, back toward or under the 3,000-episode run's
160.6, without the trend correlation dropping. If scatter does not move, the remaining
instability is the 30% eviction rather than the target network, and the answer is more RAM rather
than a different constant.

I would keep all five other settings fixed so the comparison isolates one variable, and I would
judge it on the 30-seed sweep rather than the final score, because this project has now produced
two cases where the official five and the validation seeds disagreed in sign.

---

## Not applicable to this project

The course README rubric includes items this project has no counterpart for. Listed so it is
clear each was considered rather than skipped.

- **Live URL and deployment.** Not applicable: this is a notebook experiment with no service. The
  Colab link and [Reproducing this run](#reproducing-this-run) stand in for both.
- **Database schema.** Not applicable: no database. The run folder format is documented in
  [What a run produces](#what-a-run-produces).
- **Authentication and ownership.** Not applicable: no users, no accounts, no stored personal
  data. Nothing in a run folder identifies anyone.
- **Environment variables.** Not applicable: the notebook reads none, and no `.env` file exists.
- **Secrets, publishable versus server-only.** Not applicable: the project holds no credentials.
  The scan result is recorded under [Grading evidence](#grading-evidence).
- **Vulnerability disclosure path.** Not applicable: nothing is deployed and no user data is held.

---

## License

No license chosen yet; all rights reserved by default. The underlying notebook comes from
[pepealonso95/pacman-dqn](https://github.com/pepealonso95/pacman-dqn) and its terms govern that
portion of this repository.

---

## Contributing

Not accepting outside contributions. This is a course submission and a record of one experiment.
