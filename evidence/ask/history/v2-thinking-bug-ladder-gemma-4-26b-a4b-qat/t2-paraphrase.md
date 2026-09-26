# Evidence card: t2-paraphrase

**Question:** In the contacts tracker, what stops one signed-in person from seeing somebody else's contacts?  
**Kind:** answerable, worded differently from the source  
**Mode:** ask · **Execution:** local (http://localhost:1234/v1) · **Network online during run:** True  
**Model:** `google/gemma-4-26b-a4b-qat` safetensors 4bit · embeddings `text-embedding-embeddinggemma-300m` · run 2026-09-25T21:30:49-0700

## Expected (written before the run)

- Behavior: `answer`
- Sources: `raw/assign1/README.md`
- Passage: Row Level Security policy: auth.user_id() = user_id; the JWT sub claim is read by auth.user_id() and compared to contacts.user_id

## Retrieved passages (error, 0.0s)

## Gemma's answer

ERROR: model output hit max_tokens=1000 and was cut off; raise the limit

*0.0s generation, 0 prompt tokens*

## Citation check: no claims


## Score

| retrieval hit | behavior | exact facts | citations | PASS |
|---|---|---|---|---|
| ❌ | ✅ | ❌ | ❌ | ❌ |

## Assessment

_Human review: see README evidence section._
