"""Minimal BM25 retrieval (no external dependencies)."""

from __future__ import annotations

import math
import re
from collections import Counter


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.docs: list[str] = []
        self.doc_freqs: list[Counter] = []
        self.doc_len: list[int] = []
        self.df: Counter = Counter()
        self.avgdl: float = 0.0
        self.n: int = 0

    def fit(self, docs: list[str]) -> None:
        self.docs = docs
        self.n = len(docs)
        self.doc_freqs = []
        self.doc_len = []
        self.df = Counter()
        for d in docs:
            tf = Counter(tokenize(d))
            self.doc_freqs.append(tf)
            self.doc_len.append(sum(tf.values()))
            for t in tf:
                self.df[t] += 1
        self.avgdl = sum(self.doc_len) / self.n if self.n else 0.0

    def search(self, query: str, top_k: int = 5) -> list[tuple[str, float]]:
        if self.n == 0:
            return []
        qt = Counter(tokenize(query))
        scores: list[tuple[float, int]] = []
        for i, tf in enumerate(self.doc_freqs):
            dl = self.doc_len[i]
            score = 0.0
            for t, qf in qt.items():
                f = tf.get(t, 0)
                if f == 0:
                    continue
                idf = math.log((self.n - self.df[t] + 0.5) / (self.df[t] + 0.5) + 1.0)
                denom = f + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
                score += idf * (f * (self.k1 + 1)) / denom
            if score > 0:
                scores.append((score, i))
        scores.sort(reverse=True)
        return [(self.docs[i], s) for s, i in scores[:top_k]]
