from collections import defaultdict


class WordRepository:
    def __init__(self, size, words):
        self.size = size
        self.words = words
        self.pos_index = self._build_pos_index(words)

    @classmethod
    def from_file(cls, path, size):
        words = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                w = line.strip().lower()
                if len(w) == size and w.isalpha():
                    words.append(w)
        return cls(size=size, words=sorted(set(words)))

    def _build_pos_index(self, words):
        pos_index = [defaultdict(set) for _ in range(self.size)]
        for idx, w in enumerate(words):
            for i, ch in enumerate(w):
                pos_index[i][ch].add(idx)
        return pos_index

    def pattern_candidates(self, pattern):
        candidates = None
        for i, ch in enumerate(pattern):
            if ch == ".":
                continue
            matched = self.pos_index[i].get(ch, set())
            candidates = matched if candidates is None else (candidates & matched)
            if not candidates:
                return []
        if candidates is None:
            return list(range(len(self.words)))
        return list(candidates)
