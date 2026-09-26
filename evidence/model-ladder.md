# Model ladder: the same four ask-mode tests per Gemma size

Query planning on, citation judge on, embeddings `text-embedding-embeddinggemma-300m`, run 2026-09-25 21:52.

| Model | Thinking | Passed | Weights (GB) | LM Studio footprint (GB) | Avg ask, end to end (s) | Avg reasoning tokens | Failed |
|---|---|---|---|---|---|---|---|
| `google/gemma-4-e2b` | off | 1/4 | 4.37 | 10.07 | 1.1 | 0 | t1-direct, t2-paraphrase, t3-cross-source |
| `google/gemma-4-e2b` | on | 1/4 | 4.37 | 8.22 | 4.1 | 511 | t1-direct, t2-paraphrase, t3-cross-source |
| `google/gemma-4-e4b` | off | 2/4 | 6.86 | 12.14 | 1.9 | 0 | t1-direct, t3-cross-source |
| `google/gemma-4-e4b` | on | 2/4 | 6.86 | 12.16 | 9.4 | 677 | t2-paraphrase, t3-cross-source |
| `google/gemma-4-26b-a4b-qat` | off | 3/4 | 15.64 | 20.71 | 1.9 | 0 | t3-cross-source |
| `google/gemma-4-26b-a4b-qat` | on | 3/4 | 15.64 | 18.7 | 16.2 | 1284 | t3-cross-source |
