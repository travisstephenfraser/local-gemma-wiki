# Evidence card: t4-unsupported

**Question:** What grade did I receive on the Ms. Pac-Man assignment?  
**Kind:** plausible but not in the wiki  
**Mode:** ask · **Execution:** local (http://localhost:1234/v1) · **Network online during run:** True  
**Model:** `google/gemma-4-26b-a4b-qat` safetensors 4bit · embeddings `text-embedding-embeddinggemma-300m` · run 2026-09-25T22:00:35-0700

## Expected (written before the run)

- Behavior: `insufficient_evidence`
- Sources: none
- Passage: none: no source records a grade

**Search queries:** `What grade did I receive on the Ms. Pac-Man assignment?` · `Ms. Pac-Man DQN agent grade`  
**Two-hop:** not needed

## Retrieved passages (bm25+vector (RRF) · query planning (1 sub-queries), 0.34s)

**[S1]** `raw/assign2/Assignment 2_ Train a Ms. Pac-Man Agent.md:1-2 § Class 3 Assignment: Train a Ms. Pac-Man Agent` · bm25 rank 1 · vector rank 2

```text
# Class 3 Assignment: Train a Ms. Pac-Man Agent
```

**[S2]** `raw/assign2/README.md:1-21 § Training a Ms. Pac-Man agent with Deep Q-Learning` · bm25 rank 3 · vector rank 1

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

**[S3]** `raw/assign2/Assignment 2_ Train a Ms. Pac-Man Agent.md:3-4 § Class 3 Assignment: Train a Ms. Pac-Man Agent > Choose three hyperparameters, train the agent, and explain what it actually learned.` · bm25 rank 2 · vector rank 3

```text
## Choose three hyperparameters, train the agent, and explain what it actually learned.
```

**[S4]** `raw/assign2/README.md:724-732 § Training a Ms. Pac-Man agent with Deep Q-Learning > Known limitations and what I would do next` · bm25 rank 9 · vector rank 9

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

**[S5]** `raw/assign2/README.md:46-57 § Training a Ms. Pac-Man agent with Deep Q-Learning` · bm25 rank 15 · vector rank 4

```text
Agent       Deep Q-Network: 3 conv layers + 2 dense, experience replay, target network
Input       4 stacked grayscale 84x84 frames
Hardware    Apple Silicon MPS, macOS 26.6.2 arm64, Python 3.12.14, PyTorch 2.14.0
Run         5,000 episodes | 3,557,262 decisions | 889,066 updates | 127.7 minutes
Result      492 -> 1,342 mean score over 5 fixed seeds (+850, 2.73x, all 5 seeds up)
```

**Runs locally or in Colab. There is no deployed service.**
[Open the notebook in Google Colab](https://colab.research.google.com/github/travisstephenfraser/pacman-dqn/blob/main/pacman_dqn.ipynb)

---
```

**[S6]** `raw/assign2/README.md:782-784 § Training a Ms. Pac-Man agent with Deep Q-Learning > Contributing` · bm25 rank 3 · vector rank 22

```text
## Contributing

Not accepting outside contributions. This is a course submission and a record of one experiment.
```

## Gemma's answer

INSUFFICIENT EVIDENCE: The provided passages do not contain information regarding the grade received on the Ms. Pac-Man assignment.

*0.45s generation, 1241 prompt tokens*

## Citation check: model reported insufficient evidence


## Score

| retrieval hit | behavior | exact facts | citations | PASS |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ |

## Assessment

_Human review: see README evidence section._
