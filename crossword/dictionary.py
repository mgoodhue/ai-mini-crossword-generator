from collections import defaultdict


class WordRepository:
    def __init__(self, size: int, words: list[str]) -> None:
        self.size: int = size
        self.words: list[str] = words
        self.pos_index = self._build_pos_index(words)
        self.word_scores: list[int] = [self._difficulty_score(word) for word in words]

    @classmethod
    def from_file(cls, path: str, size: int) -> "WordRepository":
        words: list[str] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                w = line.strip().lower()
                if len(w) == size and w.isalpha():
                    words.append(w)
        return cls(size=size, words=sorted(set(words)))

    def _build_pos_index(self, words: list[str]) -> list[defaultdict[str, set[int]]]:
        pos_index: list[defaultdict[str, set[int]]] = [
            defaultdict(set) for _ in range(self.size)
        ]
        for idx, w in enumerate(words):
            for i, ch in enumerate(w):
                pos_index[i][ch].add(idx)
        return pos_index

    def pattern_candidates(self, pattern: str) -> list[int]:
        candidates: set[int] | None = None
        for i, ch in enumerate(pattern):
            if ch == ".":
                continue
            matched: set[int] = self.pos_index[i].get(ch, set())
            candidates = matched if candidates is None else (candidates & matched)
            if not candidates:
                return []
        if candidates is None:
            return list(range(len(self.words)))
        return list(candidates)

    def order_candidates(
        self, candidate_indices: list[int], difficulty: str = "standard"
    ) -> list[int]:
        if difficulty == "easy":
            return sorted(
                candidate_indices,
                key=lambda i: (self.word_scores[i], self.words[i]),
            )
        if difficulty == "hard":
            return sorted(
                candidate_indices,
                key=lambda i: (self.word_scores[i], self.words[i]),
                reverse=True,
            )
        return list(candidate_indices)

    def _difficulty_score(self, word: str) -> int:
        score = 0
        rare_letter_penalty: dict[str, int] = {
            "j": 6,
            "q": 7,
            "x": 6,
            "z": 6,
            "v": 3,
            "k": 3,
            "w": 2,
            "y": 2,
        }
        common_letters: set[str] = set("etaoinshrdlucm")
        vowels: set[str] = set("aeiou")

        vowel_count = 0
        for ch in word:
            score += rare_letter_penalty.get(ch, 0)
            if ch not in common_letters:
                score += 1
            if ch in vowels:
                vowel_count += 1

        if vowel_count < 2:
            score += 3
        if vowel_count > 3:
            score += 1

        for i in range(1, len(word)):
            if word[i] == word[i - 1]:
                score += 1

        return score
