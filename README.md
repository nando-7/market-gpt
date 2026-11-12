# market-gpt

Learning how LLMs work by building one from scratch — then using real LLMs like an engineer — with financial news and market data.

Background: I built an intraday trading system ([market-scanner-api](https://github.com/nando-7/market-scanner-api)). Its backtest said +1,677%; paper trading lost money. This project is what came next.

## Plan

**Part 1 — How LLMs work (built by hand)**
1. Tokenizers: characters, then byte-pair encoding from scratch
2. Bigram model: what "predict the next token" means
3. Self-attention, by hand
4. A tiny GPT trained on news headlines — watch random characters become headlines
5. Bonus: can GPT predict the stock market? (candles as tokens)

**Part 2 — Using real LLMs**
6. APIs and structured output: classify headline catalysts
7. Evals: measure accuracy, cost, latency against hand labels
8. Embeddings and retrieval
9. Fine-tuning with LoRA, and the contamination trap

**Part 3 — Agents**
10. Tool calling / MCP server over the trading database
11. An agent that writes a daily research report
12. Wrap-up

## Data

News headlines from Alpaca's news API (Benzinga, 2015–present). Candles come from the market-scanner database and serve as the answer key — what prices actually did after the news.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add Alpaca market-data keys
python scripts/download_news.py --from 2024-01 --to 2024-12
```

Data and model weights are not committed (`data/`, `checkpoints/`).

## Journal

Progress, decisions and surprises go in [JOURNAL.md](JOURNAL.md). A plain-language explanation of each concept so far is in [LEARNING.md](LEARNING.md).
