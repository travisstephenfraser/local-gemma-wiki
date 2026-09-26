# Evidence card: t3-cross-source

**Question:** What learning rate did the Pac-Man DQN use, and how did the custom LLM do when it was trained at that same learning rate?  
**Kind:** connects two sources  
**Mode:** ask · **Execution:** local (http://localhost:1234/v1) · **Network online during run:** True  
**Model:** `google/gemma-4-26b-a4b-qat` safetensors 4bit · embeddings `text-embedding-embeddinggemma-300m` · run 2026-09-25T22:00:43-0700

## Expected (written before the run)

- Behavior: `answer`
- Sources: `raw/assign2/README.md`, `raw/assign3/README.md`
- Passage: Pac-Man: Learning rate 0.0001, standard Adam rate, left alone deliberately. Custom LLM: '0.0001 is too small. After 3,000 steps the model had barely learned: 4-8/48, with validation loss 1.40-1.83.'

**Search queries:** `What learning rate did the Pac-Man DQN use, and how did the custom LLM do when it was trained at that same learning rate?` · `Ms. Pac-Man DQN learning rate` · `custom nanoGPT learning rate` · `custom LLM learning rate assignment 3 0.0001`  
**Two-hop:** missing 'learning rate for the custom LLM' -> searched `custom LLM learning rate assignment 3 0.0001`

## Retrieved passages (bm25+vector (RRF) · query planning (2 sub-queries) · two-hop, 1.15s)

**[S1]** `raw/assign3/README.md:609-625 § Custom nanoGPT: starter corpus vs. a negation + spatial extension > Follow-up experiments (optional): seeds, training length, learning rate, depth` · bm25 rank 2 · vector rank 4

```text
overconfident on those, while the answer token that the evals measure is a tiny share of the total. Loss alone would
have told me to stop early.

**3. Learning rate: this puts real evidence behind the "too small / too large" question.**
- **0.0001 is too small.** After 3,000 steps the model had barely learned: 4–8/48, with validation loss 1.40–1.83.
- **0.01 learned negation far better** than the default 0.001: 3/3 at every seed, with margins 0.96–0.98 instead
  of ≈0.1. Spatial was slightly weaker (2–3/3).
- **0.03 is too large, but it didn't crash.** Warmup and gradient clipping keep it stable, and the loss looks normal.
  Instead it does worse on spatial (1–3/3) and transfer (4–7/8).
- **Loss can't see these differences.** Validation loss at 0.01 and 0.001 is about the same, even though the negation
  behavior is completely different.

**4. Architecture: how many layers the copy needs …
```

**[S2]** `raw/assign2/README.md:82-91 § Training a Ms. Pac-Man agent with Deep Q-Learning > My three hyperparameters` · bm25 rank 2 · vector rank 1

```text
## My three hyperparameters

| Setting | My value | Notebook default | Why |
|---|---|---|---|
| Exploration | `0.20` | 0.20 | The notebook holds epsilon *constant* instead of annealing it, so one number has to serve the whole run. Standard DQN decays 1.0 to 0.1; 0.20 sits just above the end of that schedule. I also tested 0.05 directly, on the theory that matching training exploration to the 5% used at evaluation would help. It did not, and the experiment is reported in [How I got here](#how-i-got-here-four-experiments). |
| Episodes | `5000` | 100 | 3,557,262 agent decisions, about 28% of the original DQN paper's budget of 50 million frames, which is 12.5 million decisions at four frames each. This is the largest budget that fits a working session at 128 minutes. It is worth spending *only* because the buffer fix below gave the learning curve a slope; at the notebook's default buffer,  …
```

**[S3]** `raw/assign3/Assignment 3_ Building a Custom LLM.md:31-37 § Open the Notebook` · bm25 rank 4 · vector rank 8

```text
# Open the Notebook

* [Custom LLM sample project on GitHub](https://github.com/pepealonso95/custom-llm)  
* Local Jupyter or VS Code: install requirements.txt and open custom\_llm.ipynb with that Python 3 environment. Colab generally includes PyTorch; notebook setup installs the PDF reader if absent. The pinned nanoGPT model source is provided.  
* [Open custom\_llm.ipynb in Google Colab. The default CPU runtime is enough.](https://colab.research.google.com/github/pepealonso95/custom-llm/blob/main/custom_llm.ipynb)  
* Read [Karpathy's nanoGPT explanation](https://github.com/karpathy/nanoGPT) alongside the notebook. The model uses two blocks, four heads, 64-number embeddings, a 48-token context, PyTorch backpropagation, and AdamW. Whole-word tokenization is a classroom choice, not intrinsic to nanoGPT. Classroom additions make data, evaluation, and learning visible.
```

**[S4]** `raw/assign3/README.md:587-589 § Custom nanoGPT: starter corpus vs. a negation + spatial extension > Follow-up experiments (optional): seeds, training length, learning rate, depth` · bm25 rank 5 · vector rank 8

```text
| B_layers1 | 42, 1, 2, 3 | 28 / 29 / 29 / 29 | 8 / 8 / 8 / 8 | 2 / 2 / 3 / 2 | 2 / 3 / 2 / 3 | 0.17 / 0.13 / 0.14 / 0.11 | 0.30 / 0.36 / 0.51 / 0.44 | 6 / 5 / 5 / 4 | 6 / 5 / 5 / 5 | 3 / 3 / 3 / 4 | 0.75 / 0.79 / 0.85 / 0.84 |
| B_layers4 | 42, 1, 2, 3 | 30 / 28 / 30 / 30 | 8 / 8 / 8 / 8 | 3 / 1 / 3 / 3 | 3 / 3 / 3 / 3 | 0.28 / -0.02 / 0.13 / 0.13 | 0.85 / 0.95 / 0.96 / 0.91 | 6 / 4 / 6 / 5 | 6 / 5 / 6 / 6 | 5 / 4 / 6 / 5 | 0.72 / 0.79 / 0.82 / 0.81 |
| B_lr0.0001 | 42, 1, 2, 3 | 4 / 6 / 8 / 8 | 1 / 2 / 3 / 3 | 0 / 0 / 1 / 0 | 1 / 2 / 1 / 1 | -0.00 / -0.01 / -0.00 / -0.01 | -0.00 / 0.00 / -0.00 / -0.00 | 3 / 2 / 3 / 3 | 4 / 1 / 3 / 4 | 2 / 2 / 1 / 2 | 1.40 / 1.50 / 1.71 / 1.83 |
```

**[S5]** `raw/assign2/README.md:724-732 § Training a Ms. Pac-Man agent with Deep Q-Learning > Known limitations and what I would do next` · bm25 rank 5 · vector rank 3

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

**[S6]** `raw/assign2/README.md:1-21 § Training a Ms. Pac-Man agent with Deep Q-Learning` · bm25 rank 4 · vector rank 7

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

The Ms. Pac-Man DQN used a learning rate of 0.0001 [S2]. When the custom LLM was trained at that same learning rate (B_lr0.0001), it achieved a validation loss of 1.40–1.83 [S4].

*0.89s generation, 2520 prompt tokens*

## Citation check: 1 supported, 1 weak

- **supported** (S2, overlap 0.64): The Ms. Pac-Man DQN used a learning rate of 0.0001 .
- **weak** (S4, overlap 0.47): When the custom LLM was trained at that same learning rate (B_lr0.0001), it achieved a validation loss of 1.40–1.83 .

## Score

| retrieval hit | behavior | exact facts | citations | PASS |
|---|---|---|---|---|
| ✅ | ✅ | ❌ | ❌ | ❌ |

## Assessment

_Human review: see README evidence section._
