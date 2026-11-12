# Journal

## 2026-11-12 — Choosing the data

Compared news sources on 25 scanner movers (15 from 2024–25, 10 from Oct–Nov 2026) plus one full day of volume.

- **Alpaca (Pro plan):** history back to 2015; ~890 articles on 2024-06-12 (~90 KB of headlines); full article text available. Recent movers 7/10 with news, older movers 2/15.
- **Finnhub (current key):** nothing returned for any 2024–25 date; recent movers 7/10.

Decision: Alpaca headlines across all stocks for the toy GPT (plenty of text). Small-cap catalyst coverage is thin and often "12 stocks moving" roundups, so Part 2 will have fewer real catalyst examples than the raw volume suggests — "no news" is its own category.

## 2026-11-12 — Episode 1: character-level tokenizer

Notebook: `notebooks/01_char_tokenizer.ipynb`. Reusable code: `market_gpt/tokenizer.py` (`CharTokenizer`) and `market_gpt/data.py` (`load_headlines`). Output in `data/processed/` (`headlines.jsonl`, `char_tokenizer.json`). Data: June 2024 only.

- 16,983 articles → 16,468 headlines after dropping 515 exact duplicates (mostly trading halts and "whale" alerts). No empty headlines; 34 had HTML entities (`&amp;`).
- **121 distinct characters**, 99.985% plain ASCII. 1.58M characters in total; the median headline is 82 characters, so 82 tokens per headline at character level.
- **Templates are ~28% of headlines.** Analyst ratings alone are 20% (17% of characters). Machine-made families (halts, movers roundups, options/"whale" posts, "$1000 invested" calculators, "How is the market feeling", peer and P/E comparisons) are 7%. The tail of templates is long ("Analyst Scoreboard…", "What's Going On With…"), so the rules only catch the main families.
- Decision so far: **label, don't delete.** Each headline has a `kind`; `load_headlines(exclude_kinds=...)` applies the choice per episode. Which kinds to drop for the toy GPT is still open.
- Surprise: Alpaca files articles by `updated_at`, so the June file has 18 older articles (one from 2022). The split uses `created_at`.
- Split by date: train up to 2024-06-26 (14,786 headlines), validation 2024-06-27 to 06-30 (1,682, 10%). A random split leaks ~10× more same-day near-copies into validation (2.1% vs 0.2% of validation headlines, e.g. GameStop circuit-breaker updates minutes apart). That's real but small for headlines; for minute candles it would be huge.
- É, à and ø appear only in validation, so the vocabulary is built from all headlines. The vocabulary is only the alphabet and leaks nothing.

Next, Episode 2: the bigram model.

## 2026-11-12 — Full 2024 news, and how it lines up with the candles

- 2024 downloaded: 261,904 articles (116 MB), news for all stocks, not only scanner candidates.
- market-scanner candles exist only for "live candidates" (priced $1–$20, closed up ≥10% the previous trading day): 13,773 stock-days in 2024, 17,741 in 2025, 14,886 in 2026.
- 23% of 2024 articles mention a symbol that was a candidate at some point in 2024. Of the 2024 candidate days, 22% have news on that symbol the same day, 38% the same day or the day before, and 47% within 3 days. The day-before jump makes sense: the candidate trades the day *after* the ≥10% move, so the catalyst usually came out on the move day. Dates here are UTC, a rough match only.
- Decision: 2024 is enough text for the toy GPT (Part 1). Download 2025–2026 news when Part 2 needs to match candles from those years.

## 2026-11-12 — Episode 1 re-run on all of 2024

- 261,904 articles → 239,501 headlines (22,403 exact duplicates dropped). 22.6M characters. **Vocabulary grew from 121 to 187 characters**, including invisible ones (zero-width space, soft hyphen, text-direction marks) and combining accents. 99.98% of characters are still plain ASCII; the median headline is still 82 characters.
- Templates: analyst ratings are 26% of headlines (22% of characters). Machine-made families are only ~3%, because deduplication had already removed most trading halts and whale alerts, which repeat word for word.
- 270 articles were published before 2024 (back to 2011) but updated in 2024.
- Split: train up to 2024-11-12 (214,864 headlines), validation 2024-11-13 to 12-31 (24,637). Same-day near-copies leaking into validation: 2 with the date split vs 345 (1.4%) with a random split.
- Five characters appear only in validation (Ú, Ō, ε, ․, ﬃ).
- Fixed a bug in the notebook's leak examples: each validation headline was paired with the wrong training twin. The leak counts were already correct.

## 2026-11-13 — Boilerplate decision

The toy GPT trains without the machine-made families (`market_gpt.data.MACHINE_MADE_KINDS`: halts, movers roundups, options/whale posts, returns calculators, market sentiment, peer and P/E comparisons). That leaves 207,604 of 214,864 training headlines. Analyst ratings stay: they're templated but carry real information and are catalysts for Part 2. The labels remain in `headlines.jsonl`, so this is easy to revisit.
