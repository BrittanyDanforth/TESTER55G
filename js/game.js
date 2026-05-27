/** @typedef {'hidden' | 'revealed' | 'flagged'} CellState */

/** @typedef {{ mine: boolean, adjacent: number, state: CellState }} Cell */

/** @typedef {'idle' | 'playing' | 'won' | 'lost'} GameStatus */

/** @typedef {{ rows: number, cols: number, mines: number }} BoardConfig */

export const DIFFICULTIES = {
  beginner: { rows: 9, cols: 9, mines: 10 },
  intermediate: { rows: 16, cols: 16, mines: 40 },
  expert: { rows: 16, cols: 30, mines: 99 },
};

/**
 * @param {BoardConfig} config
 */
export function createGame(config) {
  const { rows, cols, mines } = config;
  /** @type {Cell[][]} */
  let grid = [];
  /** @type {GameStatus} */
  let status = "idle";
  let flagsPlaced = 0;
  let cellsRevealed = 0;
  let minesPlaced = false;
  let firstClick = true;

  function initGrid() {
    grid = Array.from({ length: rows }, () =>
      Array.from({ length: cols }, () => ({
        mine: false,
        adjacent: 0,
        state: /** @type {CellState} */ ("hidden"),
      }))
    );
    status = "idle";
    flagsPlaced = 0;
    cellsRevealed = 0;
    minesPlaced = false;
    firstClick = true;
  }

  initGrid();

  function inBounds(row, col) {
    return row >= 0 && row < rows && col >= 0 && col < cols;
  }

  function neighbors(row, col) {
    /** @type {{ row: number, col: number }[]} */
    const list = [];
    for (let dr = -1; dr <= 1; dr++) {
      for (let dc = -1; dc <= 1; dc++) {
        if (dr === 0 && dc === 0) continue;
        const nr = row + dr;
        const nc = col + dc;
        if (inBounds(nr, nc)) list.push({ row: nr, col: nc });
      }
    }
    return list;
  }

  function placeMines(safeRow, safeCol) {
    const forbidden = new Set([`${safeRow},${safeCol}`]);
    for (const { row, col } of neighbors(safeRow, safeCol)) {
      forbidden.add(`${row},${col}`);
    }

    const candidates = [];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        if (!forbidden.has(`${r},${c}`)) candidates.push({ row: r, col: c });
      }
    }

    const mineCount = Math.min(mines, candidates.length);
    shuffle(candidates);
    for (let i = 0; i < mineCount; i++) {
      const { row, col } = candidates[i];
      grid[row][col].mine = true;
    }

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        if (grid[r][c].mine) continue;
        grid[r][c].adjacent = neighbors(r, c).filter(
          ({ row, col }) => grid[row][col].mine
        ).length;
      }
    }

    minesPlaced = true;
  }

  function reveal(row, col) {
    if (status === "won" || status === "lost") return { changed: false };
    const cell = grid[row][col];
    if (cell.state === "flagged" || cell.state === "revealed") {
      return { changed: false };
    }

    if (firstClick) {
      placeMines(row, col);
      firstClick = false;
      status = "playing";
    }

    if (cell.mine) {
      cell.state = "revealed";
      status = "lost";
      return { changed: true, exploded: true };
    }

    floodReveal(row, col);
    checkWin();
    return { changed: true, exploded: false };
  }

  function floodReveal(row, col) {
    const stack = [{ row, col }];
    while (stack.length > 0) {
      const { row: r, col: c } = stack.pop();
      const cell = grid[r][c];
      if (cell.state !== "hidden" || cell.mine) continue;

      cell.state = "revealed";
      cellsRevealed++;

      if (cell.adjacent === 0) {
        for (const n of neighbors(r, c)) {
          if (grid[n.row][n.col].state === "hidden") {
            stack.push(n);
          }
        }
      }
    }
  }

  function toggleFlag(row, col) {
    if (status === "won" || status === "lost" || status === "idle") {
      return { changed: false };
    }
    const cell = grid[row][col];
    if (cell.state === "revealed") return { changed: false };

    if (cell.state === "flagged") {
      cell.state = "hidden";
      flagsPlaced--;
    } else {
      cell.state = "flagged";
      flagsPlaced++;
    }
    return { changed: true };
  }

  function checkWin() {
    const totalSafe = rows * cols - mines;
    if (cellsRevealed >= totalSafe) {
      status = "won";
      flagAllMines();
    }
  }

  function flagAllMines() {
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        if (grid[r][c].mine) grid[r][c].state = "flagged";
      }
    }
  }

  function revealAllMines() {
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        if (grid[r][c].mine) grid[r][c].state = "revealed";
      }
    }
  }

  function reset() {
    initGrid();
  }

  function getSnapshot() {
    return {
      rows,
      cols,
      mines,
      grid: grid.map((row) => row.map((cell) => ({ ...cell }))),
      status,
      flagsPlaced,
      cellsRevealed,
      minesRemaining: Math.max(0, mines - flagsPlaced),
    };
  }

  return {
    get rows() {
      return rows;
    },
    get cols() {
      return cols;
    },
    get mines() {
      return mines;
    },
    reveal,
    toggleFlag,
    revealAllMines,
    reset,
    getSnapshot,
  };
}

function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
}
