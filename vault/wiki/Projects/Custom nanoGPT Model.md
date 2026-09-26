---
type: project
project_folder: assign3
sources:
  - raw/assign3/Assignment 3_ Building a Custom LLM.md
  - raw/assign3/README.md
  - raw/assign3/evals/README.md
  - raw/assign3/experiments/summary.md
generated_by:
  - google/gemma-4-26b-a4b-qat
tags:
  - project
---

# Custom nanoGPT Model

This document describes experiments training a nanoGPT model on different corpora to test its ability to learn negation and spatial relations. The results show that expanding the corpus with targeted teaching stories allows the model to learn multi-sentence patterns, though negation remains a fragile skill compared to spatial relations.

## The assignment brief: `Assignment 3_ Building a Custom LLM.md`

This document outlines an assignment to build, train, and evaluate a custom tiny language model using nanoGPT and PyTorch. Students must perform two experiments: one with a starter corpus and another with an expanded corpus, and then interact with the model via a chat interface.

- Use Andrej Karpathy's nanoGPT model with PyTorch.
- The model uses a small word-token transformer with 64-number embeddings and a 48-token context window.
- Students must perform two experiments: a starter-corpus experiment and a corpus-extension experiment.
- Submit a public GitHub repository containing the executed notebook, results, and a working chat interface.
- The assignment is graded out of 10 based on deliverable quality, testing & evaluation, and working result.
- The 48-case synthetic language eval suite must be run before and after training for both experiments.
- The chat interface can be a terminal or notebook loop, but must produce actual replies from the trained model.
- Use only corpus material you have permission to use and share.

Source: [raw/assign3/Assignment 3_ Building a Custom LLM.md](../../raw/assign3/Assignment%203_%20Building%20a%20Custom%20LLM.md)

## My write-up: `README.md`

- Trained Karpathy's nanoGPT (2 blocks, 4 heads, 64-number embeddings, 48-token context, word tokens) from scratch on CPU.
- Experiment A used the supplied classroom corpus.
- Experiment B used the classroom corpus plus added teaching stories for negation and spatial relations.
- Experiment C used the same words as B but with sentences split apart.
- Experiment B achieved 100% accuracy on 6 targeted scorable cases.
- A 1-layer model passed negation evals via a recency shortcut but failed probes designed to catch it.
- Training for 10,000 steps or using a learning rate of 0.01 improved negation performance.
- The model's performance on untargeted cases remained zero because their words never appeared in the training text.

Source: [raw/assign3/README.md](../../raw/assign3/README.md)

## Course material: `README.md`

This guide describes the supplied 48-case synthetic language eval suite: what it covers, how it is scored, and how to run it.

- 48 fixed, synthetic language evals authored for this assignment.
- The suite includes starter_patterns (16 cases), starter_transfer (8 cases), and extend_corpus (24 cases).
- Scoring is based on the highest next-token probability among four candidate words.
- A separate, unconstrained continuation is generated at temperature 0.8 with a 24-token limit.
- If a prompt or answer choice contains a word outside the learned vocabulary, the case is marked as out_of_vocabulary.
- The assignment uses a deliverable quality 4 + testing & evaluation 3 + working result 3 = 10 points grading structure.
- The tokenizer keeps only the 509 most frequent training token types.
- The terminal chat is launched with python chat.py --model llm_runs/YOUR_RUN/model.pt --transcript results/my-chat.json; run_evals.py reruns the evals separately.

Source: [raw/assign3/evals/README.md](../../raw/assign3/evals/README.md)

## Supporting data: `summary.md`

This document presents a table of experimental results across different model conditions and seeds. It compares performance metrics such as correct answers, transfer, negation, spatial, and various probe scores alongside validation loss.

- Per-seed values for seeds 42, 1, 2, and 3.
- Margin is calculated as p(correct) - p(best wrong choice), averaged over 3 cases.
- Condition A shows a validation loss ranging from 0.68 to 0.71.
- Condition B shows a spatial margin of 0.85 to 0.95.
- Condition B_layers1 shows a correct/48 score of 28 to 29 for all seeds.
- Condition B_lr0.0001 shows a validation loss between 1.40 and 1.83.
- Condition B_lr0.01 shows a spatial margin between 0.50 and 0.85 (negation margin 0.96 to 0.98).
- Condition B_steps10000 shows a correct/48 score of 28 to 30 and a validation loss between 0.80 and 0.92.

Source: [raw/assign3/experiments/summary.md](../../raw/assign3/experiments/summary.md)

## Concepts and tools

- [[Ablation]]: Experiment C trains on the same words as B with the sentences split apart, which separates vocabulary coverage from pattern learning.
- [[Corpus]]: The assignment requires students to choose a corpus and expand it for a second experiment.
- [[Eval Leakage]]: The brief threatens a substantial grade penalty if eval prompts, answer keys, or eval outputs are included in the training corpus.
- [[Hyperparameters]]: The assignment requires students to choose training steps and a learning rate as hyperparameters.
- [[Margin]]: Margin = p(correct) - p(best wrong choice), averaged over the 3 cases, reported per seed for negation and spatial.
- [[nanoGPT]]: The document specifies using a trained nanoGPT model to feed prefixes into for evaluation.
- [[Next-Token Scoring]]: Each case feeds a prefix to the trained nanoGPT and scores it correct if the right word has the highest probability among four candidates.
- [[Out-of-Vocabulary Cases]]: A case whose prompt or answer choice has a word outside the learned vocabulary is marked out_of_vocabulary and scores zero in the all-case rate.
- [[PyTorch]]: The assignment uses PyTorch for training the model and running the notebook.
- [[Transformer]]: The assignment uses a nanoGPT model which is a word-token transformer.

## Related projects

- [[Ms Pac-Man DQN Agent]]: also uses [[Hyperparameters]], [[PyTorch]]

---
See [[Source Catalog]] for file hashes and ingest details.
