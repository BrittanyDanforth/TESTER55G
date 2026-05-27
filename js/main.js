import { createGame, DIFFICULTIES } from "./game.js";
import { createUI } from "./ui.js";

const boardEl = document.getElementById("board");
const difficultyInputs = document.querySelectorAll('input[name="difficulty"]');

if (!boardEl) {
  throw new Error("Board element not found");
}

/** @type {ReturnType<typeof createGame>} */
let game = createGame(DIFFICULTIES.beginner);

const ui = createUI(boardEl, () => game);

function startDifficulty(difficulty) {
  const config =
    DIFFICULTIES[/** @type {keyof typeof DIFFICULTIES} */ (difficulty)];
  game = createGame(config);
  ui.reloadBoard();
}

ui.buildBoard();
ui.render();

difficultyInputs.forEach((input) => {
  input.addEventListener("change", (e) => {
    const target = /** @type {HTMLInputElement} */ (e.target);
    if (target.checked) startDifficulty(target.value);
  });
});
