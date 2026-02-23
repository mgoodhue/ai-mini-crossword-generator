const gridEl = document.getElementById("grid");
const acrossEl = document.getElementById("across");
const downEl = document.getElementById("down");
const sizeEl = document.getElementById("size");
const difficultyEl = document.getElementById("difficulty");
const statusEl = document.getElementById("status");
const themeToggleBtn = document.getElementById("theme-toggle");
const generateBtn = document.getElementById("generate");
const checkBtn = document.getElementById("check");
const clearBtn = document.getElementById("clear");
const revealBtn = document.getElementById("reveal");

let solution = [];
let revealed = false;

function updateThemeButton(theme) {
  themeToggleBtn.textContent = theme === "dark" ? "Light mode" : "Dark mode";
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem("theme", theme);
  updateThemeButton(theme);
}

function initializeTheme() {
  const saved = localStorage.getItem("theme");
  if (saved === "light" || saved === "dark") {
    applyTheme(saved);
    return;
  }
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(prefersDark ? "dark" : "light");
}

function toggleTheme() {
  const current = document.documentElement.dataset.theme === "dark" ? "dark" : "light";
  applyTheme(current === "dark" ? "light" : "dark");
}

function setStatus(text, isError = false) {
  statusEl.textContent = text;
  statusEl.classList.toggle("error", isError);
}

function clearLists() {
  acrossEl.innerHTML = "";
  downEl.innerHTML = "";
}

function renderGrid(size) {
  gridEl.innerHTML = "";
  gridEl.style.setProperty("--size", String(size));
  for (let row = 0; row < size; row += 1) {
    for (let col = 0; col < size; col += 1) {
      const cell = document.createElement("input");
      cell.type = "text";
      cell.maxLength = 1;
      cell.autocomplete = "off";
      cell.spellcheck = false;
      cell.className = "cell";
      cell.dataset.row = String(row);
      cell.dataset.col = String(col);
      cell.disabled = revealed;

      cell.addEventListener("input", (event) => {
        const input = event.target;
        const value = (input.value || "").toUpperCase().replace(/[^A-Z]/g, "");
        input.value = value.slice(0, 1);
        input.classList.remove("correct", "incorrect");
        if (input.value) {
          focusCell(row, col + 1);
        }
      });

      cell.addEventListener("keydown", (event) => {
        if (event.key === "ArrowUp") {
          event.preventDefault();
          focusCell(row - 1, col);
        } else if (event.key === "ArrowDown") {
          event.preventDefault();
          focusCell(row + 1, col);
        } else if (event.key === "ArrowLeft") {
          event.preventDefault();
          focusCell(row, col - 1);
        } else if (event.key === "ArrowRight") {
          event.preventDefault();
          focusCell(row, col + 1);
        } else if (event.key === "Backspace" && !cell.value) {
          event.preventDefault();
          focusCell(row, col - 1);
        }
      });

      gridEl.appendChild(cell);
    }
  }
}

function renderClues(target, clues) {
  target.innerHTML = "";
  for (const item of clues) {
    const li = document.createElement("li");
    li.textContent = item.clue;
    target.appendChild(li);
  }
}

function getCell(row, col) {
  return gridEl.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
}

function focusCell(row, col) {
  if (!solution.length) {
    return;
  }
  const size = solution.length;
  if (row < 0 || col < 0 || row >= size || col >= size) {
    return;
  }
  const target = getCell(row, col);
  if (target) {
    target.focus();
    target.select();
  }
}

function allCells() {
  return Array.from(gridEl.querySelectorAll(".cell"));
}

function clearGrid() {
  for (const cell of allCells()) {
    cell.value = "";
    cell.classList.remove("correct", "incorrect");
    cell.disabled = false;
  }
  revealed = false;
  setStatus("Grid cleared.");
  focusCell(0, 0);
}

function checkGrid() {
  if (!solution.length) {
    return;
  }

  let filled = 0;
  let correct = 0;
  const size = solution.length;

  for (let row = 0; row < size; row += 1) {
    for (let col = 0; col < size; col += 1) {
      const cell = getCell(row, col);
      if (!cell) {
        continue;
      }
      const guess = (cell.value || "").toUpperCase();
      const actual = solution[row][col];
      cell.classList.remove("correct", "incorrect");
      if (guess) {
        filled += 1;
        if (guess === actual) {
          cell.classList.add("correct");
          correct += 1;
        } else {
          cell.classList.add("incorrect");
        }
      }
    }
  }

  const total = size * size;
  if (correct === total) {
    setStatus(`Solved! ${correct}/${total} correct.`);
    return;
  }
  if (filled < total) {
    setStatus(`Progress: ${correct}/${total} correct, ${total - filled} empty.`);
    return;
  }
  setStatus(`Checked: ${correct}/${total} correct.`);
}

function revealGrid() {
  if (!solution.length) {
    return;
  }
  const size = solution.length;
  for (let row = 0; row < size; row += 1) {
    for (let col = 0; col < size; col += 1) {
      const cell = getCell(row, col);
      if (!cell) {
        continue;
      }
      cell.value = solution[row][col];
      cell.classList.remove("incorrect");
      cell.classList.add("correct");
      cell.disabled = true;
    }
  }
  revealed = true;
  setStatus("Solution revealed.");
}

async function generate() {
  const size = Number(sizeEl.value);
  const difficulty = difficultyEl.value;
  setStatus("Generating...");
  clearLists();
  gridEl.innerHTML = "";

  try {
    const params = new URLSearchParams({
      size: String(size),
      difficulty,
    });
    const res = await fetch(`/api/generate?${params.toString()}`);
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Failed to generate puzzle.");
    }
    const data = await res.json();
    solution = data.solution;
    revealed = false;
    renderGrid(data.size);
    renderClues(acrossEl, data.across);
    renderClues(downEl, data.down);
    setStatus(`Puzzle ready (${data.difficulty}). Fill the grid, then press Check.`);
    focusCell(0, 0);
  } catch (err) {
    setStatus(err.message, true);
  }
}

generateBtn.addEventListener("click", generate);
checkBtn.addEventListener("click", checkGrid);
clearBtn.addEventListener("click", clearGrid);
revealBtn.addEventListener("click", revealGrid);
themeToggleBtn.addEventListener("click", toggleTheme);
initializeTheme();
generate();
