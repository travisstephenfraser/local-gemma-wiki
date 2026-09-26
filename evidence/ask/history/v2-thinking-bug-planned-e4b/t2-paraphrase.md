# Evidence card: t2-paraphrase

**Question:** In the contacts tracker, what stops one signed-in person from seeing somebody else's contacts?  
**Kind:** answerable, worded differently from the source  
**Mode:** ask · **Execution:** local (http://localhost:1234/v1) · **Network online during run:** True  
**Model:** `google/gemma-4-e4b` safetensors 4bit · embeddings `text-embedding-embeddinggemma-300m` · run 2026-09-25T21:26:36-0700

## Expected (written before the run)

- Behavior: `answer`
- Sources: `raw/assign1/README.md`
- Passage: Row Level Security policy: auth.user_id() = user_id; the JWT sub claim is read by auth.user_id() and compared to contacts.user_id

## Retrieved passages (bm25+vector (RRF) · query planning (1 sub-queries), 0.41s)

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

**[S3]** `raw/assign1/README.md:253-280 § Strada > Authentication and RLS ownership > The ownership rule` · bm25 rank 5 · vector rank 2

```text
### The ownership rule

```sql
alter table contacts enable row level security;
alter table contacts force  row level security;   -- owners bypass RLS without this

create policy contacts_select_own on contacts for select to authenticated
  using (auth.user_id() = user_id);

create policy contacts_insert_own on contacts for insert to authenticated
  with check (auth.user_id() = user_id);

create policy contacts_update_own on contacts for update to authenticated
  using (auth.user_id() = user_id)          -- gates the row as it exists
  with check (auth.user_id() = user_id);    -- gates the row as it would become

create policy contacts_delete_own on contacts for delete to authenticated
  using (auth.user_id() = user_id);
```

Four separate per-verb policies, not `FOR ALL`. `USING` and `WITH CHECK` are both present
on UPDATE and that pairing is load-bearing: `USING` alone would let a user  …
```

**[S4]** `raw/assign1/README.md:726-748 § Strada > Optional: wiki sync > Both visibility tags are included, and one field is not` · bm25 rank 10 · vector rank 1

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

**[S5]** `raw/assign1/README.md:168-188 § Strada > Architecture > The design decision worth explaining` · bm25 rank 3 · vector rank 5

```text
### The design decision worth explaining

> **The database, not the API server, enforces ownership. No component in the request
> path holds a credential that bypasses RLS.**

The Express layer never connects to Postgres. It has no connection string and no Postgres
driver; `npm test` asserts both. It forwards the caller's own token, so every query it
makes is already scoped to that caller by RLS. A serious bug in the API (a missing
filter, a wrong id) still cannot return another user's row, because the credential
required to do that does not exist anywhere in the deployment.

Being precise about what that does **not** claim, since overclaiming here would be worse
than not claiming it at all:

- **The API is not the security boundary and is not meant to be.** The Data API is
  reachable by any signed-in user holding their own token. Every control in Express is
  fail-fast and UX; the enfo …
```

**[S6]** `raw/assign1/README.md:239-246 § Strada > Database schema > `contacts`` · bm25 rank 2 · vector rank 12

```text
The migration ledger deliberately lives in a separate `strada_meta` schema. Enabling the
Data API installs `ALTER DEFAULT PRIVILEGES ... GRANT ... TO authenticated`, so **every**
table created in `public` is fully writable by every signed-in user unless RLS says
otherwise. A bookkeeping table should not be defended with policies; it should be
unreachable, and only `public` is exposed.

---
```

## Gemma's answer

Row Level Security (RLS) is enabled on the `contacts` table [S1]. This security mechanism ensures that every policy restricts access to rows where the `user_id` matches the signed-in user [S1]. Specifically, the `contacts_select_own` policy uses the condition `(auth.user_id() = user_id)` to govern selection [S3]. This setup prevents a signed-in person from reading another user's contacts, even if they attempt to query the whole table or use a specific ID [S2]. The database, not the API server, enforces this ownership boundary [S5].

*8.36s generation, 1942 prompt tokens*

## Citation check: 4 supported, 1 weak

- **supported** (S1, overlap 1.0): Row Level Security (RLS) is enabled on the `contacts` table .
- **supported** (S1, overlap 0.77): This security mechanism ensures that every policy restricts access to rows where the `user_id` matches the signed-in user .
- **supported** (S3, overlap 0.5): Specifically, the `contacts_select_own` policy uses the condition `(auth.user_id() = user_id)` to govern selection .
- **weak** (S2, overlap 0.4): This setup prevents a signed-in person from reading another user's contacts, even if they attempt to query the whole table or use a specific ID .
- **supported** (S5, overlap 1.0): The database, not the API server, enforces this ownership boundary .

## Score

| retrieval hit | behavior | exact facts | citations | PASS |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ❌ | ❌ |

## Assessment

_Human review: see README evidence section._
