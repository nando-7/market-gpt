# How LLMs work: what we've learned so far

A plain-language explanation of each step in this project, in the order we built it. It's updated after every episode. For dates, numbers and decisions, see [JOURNAL.md](JOURNAL.md).

## The big picture

Every LLM, including ChatGPT and Claude, is built on one idea: **read some text, predict the next piece of text**. Do that billions of times with a big enough model and it starts to look like understanding.

The pipeline we're building, piece by piece:

```
raw text ──► cleaning ──► tokenizer ──► numbers ──► model ──► probabilities for the next token
(headlines)  (Ep 1)       (Ep 1)                    (Ep 2–4)          │
                                                                      ▼
                                                     pick one, append it, repeat = generated text
```

- ✅ **Episode 1: data and tokenizer.** No learning yet. We prepared the text and a way to turn it into numbers.
- ⏳ **Episode 2: the first model** (bigram).

---

## Episode 1: the data and the tokenizer

### 1. The training data (the "corpus")

An LLM learns **only** from examples, so what you feed it decides what it can learn. Our corpus is financial news headlines from Alpaca/Benzinga.

That's why we cleaned them:
- **Duplicates** would teach the model to memorise those exact strings.
- **Templates** like "Trading Halt: Halt status updated at…" are trivially predictable. A model could look smart just by copying them. We **labelled** them (each headline has a `kind`) instead of deleting them, so each episode can choose whether to leave them out. Decision: the toy GPT trains **without** the machine-made families (halts, "whale" options posts, "$1000 invested" calculators, and so on). It **keeps** analyst ratings: they follow a template, but each one is a real event that can move a stock.

### 2. The tokenizer: text ↔ numbers

A neural network can only do arithmetic, so it never sees letters, only numbers. A **tokenizer** translates in both directions:

- `encode("Nvidia")` → `[47, 86, 73, 68, 73, 65]`
- `decode([47, 86, 73, 68, 73, 65])` → `"Nvidia"`

Key words:
- **Token:** the unit the model reads and predicts. Ours is **one character**. That's the simplest choice.
- **Vocabulary:** the list of all possible tokens. Ours has 187 characters (letters, digits, punctuation, accented letters, even a few invisible ones). A token's id is just its position in that list, like a primary key. `'a'` being 65 means nothing in itself.
- **Vocabulary size** decides the shape of the model. In Episode 2 the model's job is literally: given the current token, output a probability for each of the 187 possible next tokens.
- **The newline is a token too.** We put one headline per line, so newline means "headline over". That's how the model can learn when to stop.

The cost of the character approach: a headline becomes about **82 tokens**. Real LLMs use chunks ("Nvidia", " Shares"), so the same headline is about 15 tokens. Fewer tokens means the model can "see" more text at once and generates faster. That's the BPE tokenizer later in the series. Character-level also can't encode a character it has never seen (🚀 fails). Real tokenizers work on bytes to avoid that.

### 3. Training data vs validation data

We hide the last part of the data from the model and test it on that later.

- If the model does well on **training** data but badly on **validation** data, it **memorised** instead of learning patterns. This is called **overfitting**.
- We split **by date** (train on the past, validate on the future), because that's how the model will be used. A random split lets near-copies of validation headlines (the same story re-posted minutes later) sneak into training, and the score looks better than it really is. It's the same trap as a backtest that looks brilliant and then loses money live.

### 4. Where the data lives

No database, just plain files in `data/` (git-ignored, because they're big and can be rebuilt):

```
data/raw/news/2024-01.jsonl …   what the downloader saved (never edited)
data/processed/headlines.jsonl  cleaned headlines + kind + split (built by the Episode 1 notebook)
data/processed/char_tokenizer.json   the 187-character vocabulary
```

**JSONL** = one JSON object per line. Why files instead of MySQL/PostgreSQL? The data is small enough to fit in memory, and training reads *everything* over and over rather than looking things up. Databases are good at lookups; for "read it all", a file is simpler. Raw and processed are kept separate, so changing a cleaning rule means re-running the notebook, not re-downloading.

The price candles are different: they're already in PostgreSQL (market-scanner's `stock_candles`). Millions of rows, and questions like "what did this stock do in the hour after this headline?" are exactly what databases are for. We'll query them in Part 2.

### What we haven't done yet

**Any learning.** No model exists yet. Episode 2 builds the first one: count which character tends to follow which, and use those counts to predict and generate text.
