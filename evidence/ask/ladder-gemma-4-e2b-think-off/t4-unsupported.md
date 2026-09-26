# Evidence card: t4-unsupported

**Question:** What grade did I receive on the Ms. Pac-Man assignment?  
**Kind:** plausible but not in the wiki  
**Mode:** ask · **Execution:** local (http://localhost:1234/v1) · **Network online during run:** True  
**Model:** `google/gemma-4-e2b` safetensors 4bit · embeddings `text-embedding-embeddinggemma-300m` · run 2026-09-25T21:49:38-0700

## Expected (written before the run)

- Behavior: `insufficient_evidence`
- Sources: none
- Passage: none: no source records a grade

## Retrieved passages (bm25+vector (RRF) · query planning (0 sub-queries), 0.15s)

**[S1]** `raw/assign2/Assignment 2_ Train a Ms. Pac-Man Agent.md:1-2 § Class 3 Assignment: Train a Ms. Pac-Man Agent` · bm25 rank 1 · vector rank 2

```text
# Class 3 Assignment: Train a Ms. Pac-Man Agent
```

**[S2]** `raw/assign2/Assignment 2_ Train a Ms. Pac-Man Agent.md:3-4 § Class 3 Assignment: Train a Ms. Pac-Man Agent > Choose three hyperparameters, train the agent, and explain what it actually learned.` · bm25 rank 2 · vector rank 3

```text
## Choose three hyperparameters, train the agent, and explain what it actually learned.
```

**[S3]** `raw/assign2/README.md:1-21 § Training a Ms. Pac-Man agent with Deep Q-Learning` · bm25 rank 12 · vector rank 4

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

**[S4]** `raw/assign2/README.md:782-784 § Training a Ms. Pac-Man agent with Deep Q-Learning > Contributing` · bm25 rank 3 · vector rank 22

```text
## Contributing

Not accepting outside contributions. This is a course submission and a record of one experiment.
```

**[S5]** `raw/assign3/Assignment 3_ Building a Custom LLM.md:19-25 § How Evals Affect Your Assignment Grade` · bm25 rank 17 · vector rank 7

```text
# How Evals Affect Your Assignment Grade

This assignment is graded out of 10 using the course framework: deliverable quality (4 points), testing & evaluation (3 points), and working result (3 points). The 48-case eval percentage is a model measurement, not your assignment grade. The runner does not calculate your grade.

* Deliverable quality (4 points): submit both executed experiments, readable source code, corpus sources and choices, and a clear README. Explain the model's learning process using your actual token, embedding, gradient, and loss evidence. Explain why you chose at least two extension categories and how your new teaching material addresses their gaps.  
* Testing & evaluation (3 points): run all 48 unchanged cases before and after training in each experiment. That means four complete result sets: starter untrained, starter trained, expanded-corpus untrained, and expanded …
```

**[S6]** `raw/assign2/README.md:183-187 § Training a Ms. Pac-Man agent with Deep Q-Learning > What I expected, and what happened` · bm25 rank 6 · vector rank 21

```text
no evidence it treats ghosts as anything but scenery. It survives **53% longer** than the
untrained network, which is consistent with "moves with purpose" rather than "evades".

---
```

## Gemma's answer

INSUFFICIENT EVIDENCE: The provided passages do not state the grade received for the Ms. Pac-Man assignment.

*0.34s generation, 1229 prompt tokens*

## Citation check: model reported insufficient evidence


## Score

| retrieval hit | behavior | exact facts | citations | PASS |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ |

## Assessment

_Human review: see README evidence section._
