# Evidence card: t3-cross-source

**Question:** What learning rate did the Pac-Man DQN use, and how did the custom LLM do when it was trained at that same learning rate?  
**Kind:** connects two sources  
**Mode:** ask · **Execution:** local (http://localhost:1234/v1) · **Network online during run:** True  
**Model:** `google/gemma-4-26b-a4b-qat` safetensors 4bit · embeddings `text-embedding-embeddinggemma-300m` · run 2026-09-25T21:55:44-0700

## Expected (written before the run)

- Behavior: `answer`
- Sources: `raw/assign2/README.md`, `raw/assign3/README.md`
- Passage: Pac-Man: Learning rate 0.0001, standard Adam rate, left alone deliberately. Custom LLM: '0.0001 is too small. After 3,000 steps the model had barely learned: 4-8/48, with validation loss 1.40-1.83.'

**Search queries:** `What learning rate did the Pac-Man DQN use, and how did the custom LLM do when it was trained at that same learning rate?` · `Ms. Pac-Man DQN learning rate` · `custom nanoGPT learning rate` · `custom LLM learning rate`  
**Two-hop:** missing 'custom LLM learning rate' -> searched `custom LLM learning rate`

## Retrieved passages (bm25+vector (RRF) · query planning (2 sub-queries) · two-hop, 1.23s)

**[S1]** `raw/assign3/Assignment 3_ Building a Custom LLM.md:65-71 § Run the Provided Language Evals` · bm25 rank 5 · vector rank 11

```text
# Run the Provided Language Evals

An eval is a fixed test: a prompt, a rule for judging the response, and the model's actual result. The corpus is study material; the eval suite is the exam. Training on the exam can make memorization look like learning.

* Use the 48 synthetic language tests already provided in evals/language\_evals.json: 16 reserved prompts for starter-corpus patterns, 8 new phrasings using familiar words, and 24 extension challenges. The extension skills are grammar, opposites, negation, references, sequence, spatial relations, everyday knowledge, and categories/analogies. You do not need to invent the eval suite.  
* Read [all 48 language eval cases](https://github.com/pepealonso95/custom-llm/blob/main/evals/language_evals.json) and the [runnable eval guide](https://github.com/pepealonso95/custom-llm/blob/main/evals/README.md) in the sample repository. Keep the cases …
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

**[S4]** `raw/assign3/README.md:272-288 § Custom nanoGPT: starter corpus vs. a negation + spatial extension > Token → ID → vector → gradient → update` · bm25 rank 15 · vector rank 2

```text
After: 0.0366, -0.0182, 0.1330, 0.1059, 0.0630, 0.0189, 0.1523, 0.0929, -0.0632, -0.0173, 0.0341, -0.0474, -0.0646, -0.0866, -0.1450, -0.0359, -0.1569, -0.1503, -0.0076, -0.0707, -0.0930, 0.0091, -0.0648, 0.0175, 0.0039, -0.0625, 0.1125, -0.0643, 0.0520, -0.1567, -0.0706, 0.0617, -0.0318, 0.1414, 0.0913, 0.0565, 0.0196, -0.1348, 0.1223, -0.0338, 0.1187, 0.0046, -0.1344, 0.0529, -0.0376, -0.1031, 0.0203, 0.0381, -0.0198, -0.1507, 0.0303, -0.1206, 0.0166, 0.0778, 0.1181, 0.0557, 0.0934, 0.0026, 0.0371, 0.0756, 0.1185, 0.0144, 0.0913, -0.0746
</details>

The trained vector is almost 4× longer, and its cosine similarity with the starting vector is only 0.20, so training
rewrote it rather than nudging it. The ID never changed. Only the numbers stored at that row did.

**One real gradient and update** (the first training step, coordinate 0 of `customer`'s vector):

| before | gradient | learni …
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

INSUFFICIENT EVIDENCE: The provided passages do not contain information regarding how the custom LLM performed when trained at the Pac-Man DQN's learning rate.

*1.07s generation, 2712 prompt tokens*

## Citation check: model reported insufficient evidence


## Score

| retrieval hit | behavior | exact facts | citations | PASS |
|---|---|---|---|---|
| ❌ | ❌ | ❌ | ✅ | ❌ |

## Assessment

_Human review: see README evidence section._
