const FACE = {
  idle: "🙂",
  playing: "😮",
  won: "😎",
  lost: "😵",
};

/**
 * @param {HTMLElement} boardEl
 * @param {() => import('./game.js').ReturnType<typeof import('./game.js').createGame>} getGame
 */
export function createUI(boardEl, getGame) {
  const mineCountEl = document.getElementById("mine-count");
  const timerEl = document.getElementById("timer");
  const resetBtn = document.getElementById("reset-btn");
  const faceIcon = document.getElementById("face-icon");
  const statusEl = document.getElementById("status");

  /** @type {HTMLButtonElement[][]} */
  let cellButtons = [];
  let timerInterval = null;
  let seconds = 0;

  function pad3(n) {
    return String(Math.min(999, Math.max(0, n))).padStart(3, "0");
  }

  function stopTimer() {
    if (timerInterval !== null) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  }

  function startTimer() {
    if (timerInterval !== null) return;
    timerInterval = setInterval(() => {
      seconds++;
      if (timerEl) timerEl.textContent = pad3(seconds);
    }, 1000);
  }

  function resetTimer() {
    stopTimer();
    seconds = 0;
    if (timerEl) timerEl.textContent = pad3(0);
  }

  function buildBoard() {
    const game = getGame();
    boardEl.innerHTML = "";
    boardEl.style.gridTemplateColumns = `repeat(${game.cols}, var(--cell-size))`;
    boardEl.style.gridTemplateRows = `repeat(${game.rows}, var(--cell-size))`;

    cellButtons = [];
    for (let r = 0; r < game.rows; r++) {
      const rowBtns = [];
      for (let c = 0; c < game.cols; c++) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "cell";
        btn.dataset.row = String(r);
        btn.dataset.col = String(c);
        btn.setAttribute("role", "gridcell");
        btn.setAttribute("aria-label", `Cell row ${r + 1} column ${c + 1}, hidden`);

        btn.addEventListener("click", (e) => {
          e.preventDefault();
          onReveal(r, c);
        });

        btn.addEventListener("contextmenu", (e) => {
          e.preventDefault();
          onFlag(r, c);
        });

        boardEl.appendChild(btn);
        rowBtns.push(btn);
      }
      cellButtons.push(rowBtns);
    }
  }

  function onReveal(row, col) {
    const game = getGame();
    const before = game.getSnapshot().status;
    const result = game.reveal(row, col);
    if (!result.changed) return;

    if (before === "idle" && game.getSnapshot().status === "playing") {
      startTimer();
    }

    if (result.exploded) {
      game.revealAllMines();
      stopTimer();
    }

    render();
  }

  function onFlag(row, col) {
    const changed = getGame().toggleFlag(row, col).changed;
    if (changed) render();
  }

  function cellLabel(cell) {
    if (cell.state === "flagged") return "flagged";
    if (cell.state === "hidden") return "hidden";
    if (cell.mine) return "mine";
    if (cell.adjacent > 0) return `number ${cell.adjacent}`;
    return "empty";
  }

  function render() {
    const game = getGame();
    const snap = game.getSnapshot();

    if (mineCountEl) mineCountEl.textContent = pad3(snap.minesRemaining);

    const face = FACE[snap.status] ?? FACE.idle;
    if (faceIcon) faceIcon.textContent = face;
    resetBtn?.classList.toggle("win", snap.status === "won");
    resetBtn?.classList.toggle("lose", snap.status === "lost");

    if (statusEl) {
      statusEl.className = "status";
      if (snap.status === "won") {
        statusEl.textContent = "You cleared the field!";
        statusEl.classList.add("win");
      } else if (snap.status === "lost") {
        statusEl.textContent = "BOOM! Hit a mine. Click 🙂 to try again.";
        statusEl.classList.add("lose");
      } else if (snap.status === "playing") {
        statusEl.textContent = "Left-click to reveal, right-click to flag.";
      } else {
        statusEl.textContent = "Click any cell to start.";
      }
    }

    for (let r = 0; r < game.rows; r++) {
      for (let c = 0; c < game.cols; c++) {
        const cell = snap.grid[r][c];
        const btn = cellButtons[r]?.[c];
        if (!btn) continue;

        btn.disabled = snap.status === "won" || snap.status === "lost";
        btn.className = "cell";
        btn.textContent = "";

        btn.setAttribute(
          "aria-label",
          `Cell row ${r + 1} column ${c + 1}, ${cellLabel(cell)}`
        );

        if (cell.state === "hidden") continue;

        btn.classList.add("revealed");

        if (cell.state === "flagged") {
          btn.classList.add("flagged");
          btn.textContent = "🚩";
          continue;
        }

        if (cell.mine) {
          btn.classList.add(snap.status === "lost" ? "mine-hit" : "revealed");
          btn.textContent = "💣";
          continue;
        }

        if (cell.adjacent > 0) {
          btn.textContent = String(cell.adjacent);
          btn.classList.add(`num-${cell.adjacent}`);
        }
      }
    }

    if (snap.status === "won" || snap.status === "lost") {
      stopTimer();
    }
  }

  function reloadBoard({ resetGame = false } = {}) {
    resetTimer();
    if (resetGame) getGame().reset();
    buildBoard();
    render();
  }

  function fullReset() {
    reloadBoard({ resetGame: true });
  }

  resetBtn?.addEventListener("click", fullReset);

  return {
    buildBoard,
    render,
    fullReset,
    reloadBoard,
    stopTimer,
  };
}
