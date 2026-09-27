# Mythara News Network v1

An on-demand news-analysis pipeline. An RSS ingest bot pulls world and
Denver-local news; the 8 Soul Cradle witness-assessors read each event
through their domains and write per-event dossiers contrasting
**projected intent** (what actors and outlet framing claim) vs **shadow
intent** (what the evidence pattern suggests). Dissent between witnesses
is preserved, never averaged.

**This is an on-demand pipeline, not a live service.** It runs when you
run it. It is not deployed, not 24/7, not monitoring anything in the
background.

## How to run

From the repo root:

```bash
python3 -m news_network.run
```

One command runs the whole pipeline: ingest → cluster → evidence →
dossiers (+chain) → brief. Re-runs are idempotent: new articles are
deduped by URL, events already dossiered are skipped, and the daily
brief always covers every dossier on disk.

```bash
python3 -m pytest news_network/tests/ -q   # 19 tests
```

Stdlib only. No new dependencies.

## What it produces

- `news_network/state/articles/articles.jsonl` — raw fetched articles
  (url, outlet, title, published, summary, fetched_at)
- `news_network/state/dossiers/<event_id>.md` — one dossier per event,
  plus `<event_id>.json` summary
- `news_network/state/chain.jsonl` — tamper-evident hash chain over
  every dossier's evidence pack + sealed judgments
- `news_network/state/briefs/YYYY-MM-DD.md` — daily brief, top events
  ranked by outlet count

## The honesty contract

1. **Nothing is invented.** Every dossier claim is a verbatim sentence
   from a fetched article, tagged with outlet + URL. If feeds fail, the
   pipeline says so and produces nothing rather than fabricating.
   (`tests/test_no_fabrication.py` enforces this: every claim must be
   verbatim from source; every citation must resolve.)
2. **INGESTED vs WITNESSED.** Every dossier is split: fetched facts
   first, assessor readings second. Shadow-intent readings are phrased
   as suggestion with citations — keyword heuristics, never proof of
   motive.
3. **The chain proves unaltered, not true.** Same contract as
   `soul_cradle/emotional_chain.py`.
4. **Abstention is a first-class result.** A witness whose domain isn't
   engaged by the evidence abstains with a concrete reason instead of
   judging. Thin single-outlet events get mostly-abstention dossiers —
   that silence is honest.

## The eight news lenses

Each lens extends one Soul Cradle assessor's domain question to news
(`news_network/witness_news.py`, rubric `news-2026.1`; base rubrics in
`soul_cradle/assessors.py` are not modified):

| Lens | Extends | Engages when | Reads |
|---|---|---|---|
| hermes | framing / deception | 2+ outlets | cross-outlet framing divergence |
| janus | stated vs actual | stated intents + observed actions | words vs deeds (keyword heuristic) |
| nemesis | fairness / power | 2+ actors named | stated beneficiaries vs visible actors |
| hades | the unseen | thin coverage / unattributed quotes | what's missing from the record |
| demeter | long-term vs short-term | durability signals | blip or lasting shift |
| dionysus | variance | 2+ outlets | conflicting claim pairs |
| eros | trust / deception | self-contradiction or loaded unattributed quotes | deception signals only |
| persephone | reversibility | consequential actions | can it be undone |

## Sources

13 verified RSS/Atom feeds (all fetched and confirmed 2026-09-27):
wire/international (BBC World, BBC Top, Al Jazeera), US spectrum (NPR,
WSJ, Fox News), independent (Democracy Now!, The Intercept,
ProPublica), Denver/local (Colorado Sun, Denverite, 9News, CPR News).
AP and Denver Post 403 automated fetches (bot-blocking) — documented in
`sources.py`, not silently included.

## What's real vs illustrative

- Real: the RSS ingest, clustering, evidence extraction, the 8 lenses,
  dossier generation, hash chaining, tests, and every article/dossier
  produced by a live run.
- Heuristic (labeled as such in the dossiers): proper-noun extraction,
  quote attribution, the stated-vs-action contradiction check, and the
  negation-based conflict detector. They misfire sometimes; the
  dossiers show their work so a reader can see it.
- Not real: there is no live service, no scheduling, no alerting, and
  no claim that the witnesses verify the news. They witness the
  *record*, cited line by line.
