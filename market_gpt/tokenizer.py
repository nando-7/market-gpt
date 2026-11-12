"""Character-level tokenizer: every distinct character gets its own number.

Built in Episode 1. Episode 2 loads it with CharTokenizer.load(...).
"""

import json
from pathlib import Path


class CharTokenizer:
    def __init__(self, chars):
        # The vocabulary: position in this list = the character's token id.
        self.chars = list(chars)
        # Lookup table for encoding, e.g. {"A": 33, "B": 34, ...}
        self.char_to_id = {ch: i for i, ch in enumerate(self.chars)}

    @classmethod
    def from_text(cls, text):
        """Build a vocabulary from every distinct character in `text`, sorted."""
        return cls(sorted(set(text)))

    @property
    def vocab_size(self):
        return len(self.chars)

    def encode(self, text):
        """Text -> list of token ids."""
        try:
            return [self.char_to_id[ch] for ch in text]
        except KeyError as e:
            raise ValueError(f"Character {e.args[0]!r} is not in the vocabulary") from None

    def decode(self, ids):
        """List of token ids -> text."""
        return "".join(self.chars[i] for i in ids)

    def save(self, path):
        data = {"type": "char", "chars": self.chars}
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(data["chars"])
