# Evidence card: t3-cross-source

**Question:** What learning rate did the Pac-Man DQN use, and how did the custom LLM do when it was trained at that same learning rate?  
**Kind:** connects two sources  
**Mode:** ask · **Execution:** local (http://localhost:1234/v1) · **Network online during run:** True  
**Model:** `google/gemma-4-e4b` safetensors 4bit · embeddings `text-embedding-embeddinggemma-300m` · run 2026-09-25T21:24:23-0700

## Expected (written before the run)

- Behavior: `answer`
- Sources: `raw/assign2/README.md`, `raw/assign3/README.md`
- Passage: Pac-Man: Learning rate 0.0001, standard Adam rate, left alone deliberately. Custom LLM: '0.0001 is too small. After 3,000 steps the model had barely learned: 4-8/48, with validation loss 1.40-1.83.'

## Retrieved passages (bm25+vector (RRF) · query planning (2 sub-queries), 0.4s)

**[S1]** `raw/assign2/README.md:82-91 § Training a Ms. Pac-Man agent with Deep Q-Learning > My three hyperparameters` · bm25 rank 2 · vector rank 1

```text
## My three hyperparameters

| Setting | My value | Notebook default | Why |
|---|---|---|---|
| Exploration | `0.20` | 0.20 | The notebook holds epsilon *constant* instead of annealing it, so one number has to serve the whole run. Standard DQN decays 1.0 to 0.1; 0.20 sits just above the end of that schedule. I also tested 0.05 directly, on the theory that matching training exploration to the 5% used at evaluation would help. It did not, and the experiment is reported in [How I got here](#how-i-got-here-four-experiments). |
| Episodes | `5000` | 100 | 3,557,262 agent decisions, about 28% of the original DQN paper's budget of 50 million frames, which is 12.5 million decisions at four frames each. This is the largest budget that fits a working session at 128 minutes. It is worth spending *only* because the buffer fix below gave the learning curve a slope; at the notebook's default buffer,  …
```

**[S2]** `raw/assign3/Assignment 3_ Building a Custom LLM.md:5-8 § Overview` · bm25 rank 2 · vector rank 9

```text
# Overview

Use the ready-made notebook to understand the basics of a language model: corpus, tokens, vectors, embeddings, neural networks, and learning. It uses Andrej Karpathy's actual nanoGPT model, using PyTorch and a small word-token transformer. Choose your corpus, training steps, and learning rate, then submit one public GitHub repository URL with your executed notebook and evidence. This miniature model generates short sentences from a narrow corpus, not general chat answers.
```

**[S3]** `raw/assign2/README.md:724-732 § Training a Ms. Pac-Man agent with Deep Q-Learning > Known limitations and what I would do next` · bm25 rank 4 · vector rank 3

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

**[S4]** `raw/assign2/README.md:1-21 § Training a Ms. Pac-Man agent with Deep Q-Learning` · bm25 rank 5 · vector rank 6

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

**[S5]** `raw/assign3/Assignment 3_ Building a Custom LLM.md:31-37 § Open the Notebook` · bm25 rank 8 · vector rank 4

```text
# Open the Notebook

* [Custom LLM sample project on GitHub](https://github.com/pepealonso95/custom-llm)  
* Local Jupyter or VS Code: install requirements.txt and open custom\_llm.ipynb with that Python 3 environment. Colab generally includes PyTorch; notebook setup installs the PDF reader if absent. The pinned nanoGPT model source is provided.  
* [Open custom\_llm.ipynb in Google Colab. The default CPU runtime is enough.](https://colab.research.google.com/github/pepealonso95/custom-llm/blob/main/custom_llm.ipynb)  
* Read [Karpathy's nanoGPT explanation](https://github.com/karpathy/nanoGPT) alongside the notebook. The model uses two blocks, four heads, 64-number embeddings, a 48-token context, PyTorch backpropagation, and AdamW. Whole-word tokenization is a classroom choice, not intrinsic to nanoGPT. Classroom additions make data, evaluation, and learning visible.
```

**[S6]** `raw/assign2/README.md:120-123 § Training a Ms. Pac-Man agent with Deep Q-Learning > What I changed and why > `REPLAY_CAPACITY`, 5,000 to 2,500,000` · bm25 rank 9 · vector rank 10

```text
The cost is memory and nothing else: sampling 32 items from 2.5 million costs the same as from
5,000, so wall-clock per episode is unchanged. At 5,000 episodes this run peaked at 86 GiB with
zero swap.
```

## Gemma's answer

The Pac-Man DQN used a learning rate of `0.0001` [S1]. The passages do not contain information regarding how the custom LLM performed when trained at that same learning rate.

*7.49s generation, 1705 prompt tokens*

## Citation check: 1 supported, 1 uncited

- **supported** (S1, overlap 0.7): The Pac-Man DQN used a learning rate of `0.0001` .
- **uncited** (no citation, overlap 0.0): The passages do not contain information regarding how the custom LLM performed when trained at that same learning rate.

## Score

| retrieval hit | behavior | exact facts | citations | PASS |
|---|---|---|---|---|
| ❌ | ✅ | ❌ | ❌ | ❌ |

## Assessment

_Human review: see README evidence section._
