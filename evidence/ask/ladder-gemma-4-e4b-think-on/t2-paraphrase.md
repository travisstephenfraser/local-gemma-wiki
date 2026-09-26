# Evidence card: t2-paraphrase

**Question:** In the contacts tracker, what stops one signed-in person from seeing somebody else's contacts?  
**Kind:** answerable, worded differently from the source  
**Mode:** ask · **Execution:** local (http://localhost:1234/v1) · **Network online during run:** True  
**Model:** `google/gemma-4-e4b` safetensors 4bit · embeddings `text-embedding-embeddinggemma-300m` · run 2026-09-25T21:50:21-0700

## Expected (written before the run)

- Behavior: `answer`
- Sources: `raw/assign1/README.md`
- Passage: Row Level Security policy: auth.user_id() = user_id; the JWT sub claim is read by auth.user_id() and compared to contacts.user_id

## Retrieved passages (bm25+vector (RRF) · query planning (0 sub-queries), 0.42s)

**[S1]** `raw/assign1/Assignment 1_ Secure Networking Tracker.md:39-49 § Security Requirements` · bm25 rank 1 · vector rank 3

```text
# Security Requirements

* The contacts table includes a text user\_id that defaults to auth.user\_id() and cannot be null  
* Row Level Security is enabled on the contacts table  
* Separate select, insert, update, and delete policies apply to authenticated users  
* Every policy restricts access to rows where user\_id matches the signed-in user  
* Update policies prevent a user from changing a row so it belongs to someone else  
* Two test accounts prove that User A cannot read or change User B's contacts  
* The frontend may use the public Neon Auth and Data API URLs; RLS must protect every exposed contacts row  
* The Postgres connection string, cookie secret, and all other secrets stay server-only and are never committed to Git
```

**[S2]** `raw/assign1/README.md:557-568 § Strada > Grading evidence > User A cannot see or change User B's contacts` · bm25 rank 3 · vector rank 2

```text
✓ everything else still works > allows the operator's own layer to change freely 30ms
 ✓ everything else still works > leaves a hand-made contact fully editable 29ms
 ✓ the limit of this guarantee, stated rather than hidden > lets a caller who sets wiki_synced_at through: this is not a security boundary 61ms
 ✓ User A's row, as seen by User A (positive control) > A can read the row A created 32ms
 ✓ User B cannot SEE User A's contacts > B's unfiltered read of the whole table does not contain A's row 32ms
 ✓ User B cannot SEE User A's contacts > B cannot read A's row even when asking for it by id 30ms
 ✓ User B cannot CHANGE User A's contacts > B's update of A's row affects nothing 61ms
 ✓ User B cannot CHANGE User A's contacts > B's delete of A's row removes nothing 126ms
 ✓ User B cannot CHANGE User A's contacts > B's unfiltered delete cannot reach A's rows 87ms
 ✓ Ownership cannot be h …
```

**[S3]** `raw/assign1/README.md:726-748 § Strada > Optional: wiki sync > Both visibility tags are included, and one field is not` · bm25 rank 10 · vector rank 1

```text
### Both visibility tags are included, and one field is not

Neither tag means "keep this person out of my own private, row-level-secured list".
`visibility/internal` means do not publish. `visibility/pii` marks a page whose **body**
is sensitive: compensation, routing, things said in confidence.

Sync never transmits page text, so what a `pii` page contributes is a business card:
name, company, role, where you met. The one field that could carry the page's substance
is `bio`, because it is the model's summary *of* that prose, so **`bio` is dropped for a
`pii` source**. The person becomes reachable; the sensitive material stays on the machine.

Excluding those people outright was the earlier default and it made the tracker
arbitrarily incomplete: eleven real people were already synced to the same hosted
database while one relationship was held out on a tag describing prose that never lea …
```

**[S4]** `raw/assign1/README.md:239-246 § Strada > Database schema > `contacts`` · bm25 rank 2 · vector rank 12

```text
The migration ledger deliberately lives in a separate `strada_meta` schema. Enabling the
Data API installs `ALTER DEFAULT PRIVILEGES ... GRANT ... TO authenticated`, so **every**
table created in `public` is fully writable by every signed-in user unless RLS says
otherwise. A bookkeeping table should not be defended with policies; it should be
unreachable, and only `public` is exposed.

---
```

**[S5]** `raw/assign1/README.md:540-558 § Strada > Grading evidence > User A cannot see or change User B's contacts` · bm25 rank 6 · vector rank 10

```text
### User A cannot see or change User B's contacts

Two live suites run here. `two-account.test.ts` is the privacy proof below;
`wiki-layer.test.ts` proves the wiki layer is locked in the database rather than only in
`apps/api`, and ends by demonstrating the limit of that lock rather than implying it has
none.

```console
$ npm run test:rls

 ✓ the wiki layer is read-only to an ordinary write > refuses a change to name on a wiki-linked row 29ms
 ✓ the wiki layer is read-only to an ordinary write > refuses a change to company on a wiki-linked row 29ms
 ✓ the wiki layer is read-only to an ordinary write > refuses a change to role on a wiki-linked row 31ms
 ✓ the wiki layer is read-only to an ordinary write > refuses a change to met_where on a wiki-linked row 30ms
 ✓ the wiki layer is read-only to an ordinary write > refuses a change to bio on a wiki-linked row 98ms
 ✓ the wiki layer is read …
```

**[S6]** `raw/assign1/Assignment 1_ Secure Networking Tracker.md:93-102 § Evidence Required in the README` · bm25 rank 7 · vector rank 9

```text
# Evidence Required in the README

* Automated test output showing at least one passing validation test  
* A screenshot or recording of sign-in and sign-out  
* A screenshot or recording of creating, editing, deleting, and refreshing a contact  
* A two-account test showing that one user cannot access the other user's contacts  
* A screenshot of one invalid input failing safely  
* A brief explanation of the contacts schema and RLS ownership rule  
* A GitHub repository with no committed secret values
```

## Gemma's answer

Row Level Security is enabled on the `contacts table` [S1]. This security relies on separate select, insert, update, and delete policies that apply to authenticated users [S1]. Specifically, every policy restricts access to rows where the `user_id` matches the signed-in user [S1]. This setup ensures that User A cannot read or change User B's contacts [S1], and an unfiltered read of the whole table by one user will not contain the other user's rows [S2].

*9.52s generation, 1779 prompt tokens*

## Citation check: 4 supported

- **supported** (S1, overlap 1.0): Row Level Security is enabled on the `contacts table` .
- **supported** (S1, overlap 0.91): This security relies on separate select, insert, update, and delete policies that apply to authenticated users .
- **supported** (S1, overlap 0.82): Specifically, every policy restricts access to rows where the `user_id` matches the signed-in user .
- **supported** (S1, S2, overlap 0.82): This setup ensures that User A cannot read or change User B's contacts , and an unfiltered read of the whole table by one user will not contain the other user's rows .

## Score

| retrieval hit | behavior | exact facts | citations | PASS |
|---|---|---|---|---|
| ❌ | ✅ | ❌ | ✅ | ❌ |

## Assessment

_Human review: see README evidence section._
