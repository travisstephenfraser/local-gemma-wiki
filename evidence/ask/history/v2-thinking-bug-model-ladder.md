# Model ladder: same four ask-mode tests per Gemma size

| Model | Passed | Weights (GB) | LM Studio footprint (GB) | Avg answer (s) | Failed |
|---|---|---|---|---|---|
| `google/gemma-4-e2b` | 1/4 | 4.37 | 8.22 | 3.8 | t1-direct, t2-paraphrase, t3-cross-source |
| `google/gemma-4-e4b` | 1/4 | 6.86 | 10.67 | 5.2 | t1-direct, t2-paraphrase, t3-cross-source |
| `google/gemma-4-26b-a4b-qat` | 1/4 | 15.64 | 18.7 | 1.5 | t1-direct, t2-paraphrase, t3-cross-source |
