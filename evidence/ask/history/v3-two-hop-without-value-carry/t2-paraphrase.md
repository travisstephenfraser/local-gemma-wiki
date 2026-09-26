# Evidence card: t2-paraphrase

**Question:** In the contacts tracker, what stops one signed-in person from seeing somebody else's contacts?  
**Kind:** answerable, worded differently from the source  
**Mode:** ask · **Execution:** local (http://localhost:1234/v1) · **Network online during run:** True  
**Model:** `google/gemma-4-26b-a4b-qat` safetensors 4bit · embeddings `text-embedding-embeddinggemma-300m` · run 2026-09-25T21:55:44-0700

## Expected (written before the run)

- Behavior: `answer`
- Sources: `raw/assign1/README.md`
- Passage: Row Level Security policy: auth.user_id() = user_id; the JWT sub claim is read by auth.user_id() and compared to contacts.user_id

**Search queries:** `In the contacts tracker, what stops one signed-in person from seeing somebody else's contacts?` · `secure contacts tracker row level security policy` · `secure contacts tracker data isolation`  
**Two-hop:** not needed

## Retrieved passages (bm25+vector (RRF) · query planning (2 sub-queries), 1.11s)

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

**[S2]** `raw/assign1/Assignment 1_ Secure Networking Tracker.md:1-2 § Assignment 1: Secure Networking Tracker` · bm25 rank 1 · vector rank 7

```text
# Assignment 1: Secure Networking Tracker
```

**[S3]** `raw/assign1/README.md:557-568 § Strada > Grading evidence > User A cannot see or change User B's contacts` · bm25 rank 3 · vector rank 2

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

**[S4]** `raw/assign1/README.md:253-280 § Strada > Authentication and RLS ownership > The ownership rule` · bm25 rank 1 · vector rank 2

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

**[S5]** `raw/assign1/README.md:726-748 § Strada > Optional: wiki sync > Both visibility tags are included, and one field is not` · bm25 rank 10 · vector rank 1

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

**[S6]** `raw/assign1/Assignment 1_ Secure Networking Tracker.md:89-92 § Starter Prompt for Your Coding Agent` · bm25 rank 3 · vector rank 8

```text
# Starter Prompt for Your Coding Agent

Plan and build a secure networking tracker with separate frontend and backend logic, Neon Postgres, Managed Better Auth, the Neon Data API, and a Vercel deployment. Use @neondatabase/neon-js with its two-URL object form for authentication and data access. Create a contacts table with a text user\_id that defaults to auth.user\_id(). Enable RLS and create ownership policies for select, insert, update, and delete using auth.user\_id() \= user\_id, including WITH CHECK for inserts and updates. Build create, view, edit, delete, sort, and filter behavior. Validate required fields and priority values in trusted server or database code. Add at least one automated test. Create .env.example with only placeholder values, keep DATABASE\_URL and every other secret server-only, and write a complete README covering setup, architecture, schema, security, testing, …
```

## Gemma's answer

Row Level Security (RLS) is enabled on the contacts table [S1, S4, S6]. Separate select, insert, update, and delete policies apply to authenticated users [S1, S4, S6]. Every policy restricts access to rows where the `user_id` matches the signed-in user [S1, S4, S6]. Specifically, the `contacts_select_own` policy uses `auth.user_id() = user_id` to gate access [S4].

*1.18s generation, 1775 prompt tokens*

## Citation check: 4 supported

- **supported** (S1, S4, S6, overlap 1.0): Row Level Security (RLS) is enabled on the contacts table .
- **supported** (S1, S4, S6, overlap 1.0): Separate select, insert, update, and delete policies apply to authenticated users .
- **supported** (S1, S4, S6, overlap 1.0): Every policy restricts access to rows where the `user_id` matches the signed-in user .
- **supported** (S4, overlap 0.56): Specifically, the `contacts_select_own` policy uses `auth.user_id() = user_id` to gate access .

## Score

| retrieval hit | behavior | exact facts | citations | PASS |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ |

## Assessment

_Human review: see README evidence section._
