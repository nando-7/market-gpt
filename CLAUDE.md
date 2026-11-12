# market-gpt

## Purpose

Learning project and possible YouTube series: understand how LLMs work by building a tiny GPT from scratch, then use real LLMs like an engineer (APIs, evals, embeddings, fine-tuning, agents). It's also a portfolio piece for software engineering job applications. See README.md for the 12-episode plan.

The user is a software developer (PHP/Laravel background, newer to Python/ML). Explain concepts plainly and build things step by step so each episode is understandable on its own; the learning matters more than the result.

## Key ideas already settled

- The toy GPT is for **learning the mechanics**, not making a useful model. Readable-but-imperfect generated headlines are the expected outcome. Plan: character-level first, then byte-pair encoding (BPE) built from scratch.
- Real use of LLMs (Part 2+) is **prompting/fine-tuning pretrained models**, not training from zero.
- Candles from the sibling project `~/Projects/market-scanner-api` (PostgreSQL `stock_candles`, ~9.9M 1-minute bars, 2,688 stocks) are the **answer key**: what prices did after the news. A "candles as tokens" episode is a bonus experiment; expect no tradable prediction.
- Be honest about results; never present a model as predicting prices profitably. The trading project's backtest-vs-reality gap is the series' backstory.

## Data

- Alpaca news API (Benzinga, 2015–present) via `scripts/download_news.py` → `data/raw/news/YYYY-MM.jsonl` (read-only, resumable). One month ≈ 17k articles, 1.6 MB of headlines, ~4 min to download.
- Finnhub (current key) returned no history for 2024–25; not used for now.
- Data cleanup still to do: HTML entities in summaries (`&#39;`), boilerplate like "Trading Halt: …" and "12 … Stocks Moving In …" roundups.
- Small-cap catalyst coverage is thin (2 of 15 older movers had news), so "no news" is its own category in Part 2.

## Environment

- Apple M2, 16 GB. PyTorch with the `mps` device for training (to be added when Episode 1 starts).
- Python 3.12 virtualenv in `.venv/`; `.env` holds Alpaca market-data keys (git-ignored; never print or commit them).
- Long downloads/training runs: give the user the command to run rather than running hours-long jobs yourself.
- Remote: `git@github.com:nando-7/market-gpt.git` (private).

## Status (2026-11-12)

Skeleton, README, JOURNAL.md and downloader done; June 2024 downloaded. Next: user downloads 2024 in full, then Episode 1 — character-level tokenizer.
