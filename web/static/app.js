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
let activeDirection = "across";
let activeCell = null;
let clueNumberByStartCell = new Map();
const clueItemByDirection = {
  across: new Map(),
  down: new Map(),
};

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

function isStartOfAcross(row, col, size) {
  if (solution[row][col] === "#") {
    return false;
  }
  if (col > 0 && solution[row][col - 1] !== "#") {
    return false;
  }
  return col + 1 < size && solution[row][col + 1] !== "#";
}

function isStartOfDown(row, col, size) {
  if (solution[row][col] === "#") {
    return false;
  }
  if (row > 0 && solution[row - 1][col] !== "#") {
    return false;
  }
  return row + 1 < size && solution[row + 1][col] !== "#";
}

function collectClueNumbers(size) {
  const numbers = [];
  let clueNumber = 1;
  for (let row = 0; row < size; row += 1) {
    for (let col = 0; col < size; col += 1) {
      const startsAcross = isStartOfAcross(row, col, size);
      const startsDown = isStartOfDown(row, col, size);
      if (!startsAcross && !startsDown) {
        continue;
      }
      numbers.push({ row, col, number: clueNumber });
      clueNumber += 1;
    }
  }
  return numbers;
}

function cellSupportsDirection(row, col, direction, size = solution.length) {
  if (!solution.length || row < 0 || col < 0 || row >= size || col >= size) {
    return false;
  }
  if (solution[row][col] === "#") {
    return false;
  }
  if (direction === "across") {
    return (
      (col > 0 && solution[row][col - 1] !== "#") || (col + 1 < size && solution[row][col + 1] !== "#")
    );
  }
  return (
    (row > 0 && solution[row - 1][col] !== "#") || (row + 1 < size && solution[row + 1][col] !== "#")
  );
}

function chooseDirectionForCell(row, col, preferredDirection) {
  const supportsAcross = cellSupportsDirection(row, col, "across");
  const supportsDown = cellSupportsDirection(row, col, "down");
  if (preferredDirection === "down") {
    if (supportsDown) {
      return "down";
    }
    if (supportsAcross) {
      return "across";
    }
    return "down";
  }
  if (supportsAcross) {
    return "across";
  }
  if (supportsDown) {
    return "down";
  }
  return "across";
}

function getEntryStart(row, col, direction) {
  if (direction === "across") {
    let startCol = col;
    while (startCol > 0 && solution[row][startCol - 1] !== "#") {
      startCol -= 1;
    }
    return { row, col: startCol };
  }
  let startRow = row;
  while (startRow > 0 && solution[startRow - 1][col] !== "#") {
    startRow -= 1;
  }
  return { row: startRow, col };
}

function updateActiveHighlights() {
  for (const cell of gridEl.querySelectorAll(".cell.active-word, .cell.active-cell")) {
    cell.classList.remove("active-word", "active-cell");
  }
  for (const li of acrossEl.querySelectorAll(".active-clue")) {
    li.classList.remove("active-clue");
  }
  for (const li of downEl.querySelectorAll(".active-clue")) {
    li.classList.remove("active-clue");
  }
  acrossEl.classList.toggle("active-direction", activeDirection === "across");
  downEl.classList.toggle("active-direction", activeDirection === "down");

  if (!activeCell || !solution.length) {
    return;
  }

  const { row, col } = activeCell;
  const active = getCell(row, col);
  if (active) {
    active.classList.add("active-cell");
  }

  if (!cellSupportsDirection(row, col, activeDirection)) {
    return;
  }

  const start = getEntryStart(row, col, activeDirection);
  let cursorRow = start.row;
  let cursorCol = start.col;
  while (
    cursorRow >= 0 &&
    cursorCol >= 0 &&
    cursorRow < solution.length &&
    cursorCol < solution.length &&
    solution[cursorRow][cursorCol] !== "#"
  ) {
    const cell = getCell(cursorRow, cursorCol);
    if (cell) {
      cell.classList.add("active-word");
    }
    if (activeDirection === "across") {
      cursorCol += 1;
    } else {
      cursorRow += 1;
    }
  }

  const clueNumber = clueNumberByStartCell.get(`${start.row},${start.col}`);
  const clue = clueItemByDirection[activeDirection].get(clueNumber);
  if (clue) {
    clue.classList.add("active-clue");
  }
}

function setActiveCell(row, col, preferredDirection = null) {
  if (!solution.length) {
    return;
  }
  activeCell = { row, col };
  const preferred = preferredDirection || activeDirection || "across";
  activeDirection = chooseDirectionForCell(row, col, preferred);
  updateActiveHighlights();
}

function renderGrid(size) {
  gridEl.innerHTML = "";
  gridEl.style.setProperty("--size", String(size));
  clueNumberByStartCell = new Map(
    collectClueNumbers(size).map((item) => [`${item.row},${item.col}`, item.number]),
  );
  for (let row = 0; row < size; row += 1) {
    for (let col = 0; col < size; col += 1) {
      const isBlock = solution[row]?.[col] === "#";
      const cell = document.createElement(isBlock ? "div" : "input");
      cell.className = "cell";
      cell.dataset.row = String(row);
      cell.dataset.col = String(col);

      if (isBlock) {
        cell.classList.add("block");
        cell.setAttribute("aria-label", "Blocked cell");
        gridEl.appendChild(cell);
        continue;
      }

      const slot = document.createElement("div");
      slot.className = "cell-slot";

      cell.type = "text";
      cell.maxLength = 1;
      cell.autocomplete = "off";
      cell.spellcheck = false;
      cell.disabled = revealed;

      cell.addEventListener("input", (event) => {
        const input = event.target;
        const value = (input.value || "").toUpperCase().replace(/[^A-Z]/g, "");
        input.value = value.slice(0, 1);
        input.classList.remove("correct", "incorrect");
        if (input.value) {
          if (activeDirection === "down") {
            focusCell(row + 1, col, "down");
          } else {
            focusCell(row, col + 1, "across");
          }
        }
      });

      cell.addEventListener("keydown", (event) => {
        if (event.key === "ArrowUp") {
          event.preventDefault();
          if (!focusCell(row - 1, col, "down")) {
            setActiveCell(row, col, "down");
          }
        } else if (event.key === "ArrowDown") {
          event.preventDefault();
          if (!focusCell(row + 1, col, "down")) {
            setActiveCell(row, col, "down");
          }
        } else if (event.key === "ArrowLeft") {
          event.preventDefault();
          if (!focusCell(row, col - 1, "across")) {
            setActiveCell(row, col, "across");
          }
        } else if (event.key === "ArrowRight") {
          event.preventDefault();
          if (!focusCell(row, col + 1, "across")) {
            setActiveCell(row, col, "across");
          }
        } else if (event.key === "Backspace" && !cell.value) {
          event.preventDefault();
          if (activeDirection === "down") {
            focusCell(row - 1, col, "down");
          } else {
            focusCell(row, col - 1, "across");
          }
        }
      });

      cell.addEventListener("focus", () => {
        setActiveCell(row, col);
      });

      const clueNumber = clueNumberByStartCell.get(`${row},${col}`);
      if (clueNumber !== undefined) {
        const label = document.createElement("span");
        label.className = "cell-number";
        label.textContent = String(clueNumber);
        slot.appendChild(label);
      }

      slot.appendChild(cell);
      gridEl.appendChild(slot);
    }
  }
}

function renderClues(target, clues) {
  target.innerHTML = "";
  const direction = target === acrossEl ? "across" : "down";
  clueItemByDirection[direction].clear();
  for (const item of clues) {
    const li = document.createElement("li");
    li.value = Number(item.number);
    li.textContent = item.clue;
    clueItemByDirection[direction].set(Number(item.number), li);
    target.appendChild(li);
  }
}

function getCell(row, col) {
  return gridEl.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
}

function focusCell(row, col, preferredDirection = null) {
  if (!solution.length) {
    return false;
  }
  const size = solution.length;
  if (row < 0 || col < 0 || row >= size || col >= size) {
    return false;
  }
  if (solution[row][col] === "#") {
    return false;
  }
  const target = getCell(row, col);
  if (target) {
    setActiveCell(row, col, preferredDirection);
    target.focus();
    target.select();
    return true;
  }
  return false;
}

function allCells() {
  return Array.from(gridEl.querySelectorAll(".cell"));
}

function clearGrid() {
  for (const cell of allCells()) {
    if (cell.classList.contains("block")) {
      continue;
    }
    cell.value = "";
    cell.classList.remove("correct", "incorrect");
    cell.disabled = false;
  }
  revealed = false;
  activeDirection = "across";
  activeCell = null;
  updateActiveHighlights();
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
  let total = 0;

  for (let row = 0; row < size; row += 1) {
    for (let col = 0; col < size; col += 1) {
      if (solution[row][col] === "#") {
        continue;
      }
      total += 1;
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
      if (solution[row][col] === "#") {
        continue;
      }
      const cell = getCell(row, col);
      if (!cell) {
        continue;
      }
      if (!(cell instanceof HTMLInputElement)) {
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
    activeDirection = "across";
    activeCell = null;
    renderGrid(data.size);
    renderClues(acrossEl, data.across);
    renderClues(downEl, data.down);
    updateActiveHighlights();
    setStatus(`Puzzle ready (${data.difficulty}). Fill the grid, then press Check.`);
    outer:
    for (let row = 0; row < data.size; row += 1) {
      for (let col = 0; col < data.size; col += 1) {
        if (solution[row][col] !== "#") {
          focusCell(row, col);
          break outer;
        }
      }
    }
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
