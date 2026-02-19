from crossword import CrosswordGenerator
from crossword.clues import ClueGenerator

def generate():
    generator = CrosswordGenerator(size=5, words_path="words.txt")
    result = generator.generate()
    if result is None:
        print("No solution found. Try a bigger/better word list.")
        return

    clue_generator = ClueGenerator(provider="ollama", model="llama3.2")
    across_clues = clue_generator.generate_clues(result.across, "across")
    down_clues = clue_generator.generate_clues(result.down, "down")

    print("GRID:")
    for line in result.grid_lines:
        print(line)

    print("\nACROSS:")
    for i, (word, clue) in enumerate(zip(result.across, across_clues), start=1):
        print(f"{i}. {word} - {clue}")

    print("\nDOWN:")
    for i, (word, clue) in enumerate(zip(result.down, down_clues), start=1):
        print(f"{i}. {word} - {clue}")

if __name__ == "__main__":
    generate()
