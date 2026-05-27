"""Tkinter GUI for Stake-style Mines prediction / detection."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from mines_predictor.provably_fair import (
    PredictionResult,
    format_tile_list,
    hash_server_seed,
    predict_mines,
    verify_server_seed_hash,
)


COLS = 5
ROWS = 5
GRID_SIZE = COLS * ROWS

COLORS = {
    "bg": "#0f1923",
    "panel": "#1a2c38",
    "panel_border": "#2f4553",
    "text": "#e8f0f6",
    "muted": "#8fa3b0",
    "accent": "#00e701",
    "danger": "#ff4d4d",
    "safe": "#1e3a2f",
    "safe_border": "#00e701",
    "mine": "#3d1515",
    "mine_border": "#ff4d4d",
    "hidden": "#213743",
    "hidden_border": "#3d5564",
    "input_bg": "#0f212e",
}


class MinesPredictorApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Stake Mines Detector / Predictor")
        self.root.configure(bg=COLORS["bg"])
        self.root.minsize(720, 680)

        self._cell_buttons: list[list[tk.Label]] = []
        self._last_result: PredictionResult | None = None

        self._build_style()
        self._build_layout()

    def _build_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TFrame",
            background=COLORS["bg"],
        )
        style.configure(
            "Panel.TLabelframe",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            bordercolor=COLORS["panel_border"],
        )
        style.configure(
            "Panel.TLabelframe.Label",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "TLabel",
            background=COLORS["panel"],
            foreground=COLORS["text"],
        )
        style.configure(
            "Bg.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["muted"],
        )
        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 11, "bold"),
        )

    def _build_layout(self) -> None:
        header = ttk.Label(
            self.root,
            text="Mines Detector — Stake-style provably fair predictor",
            style="Bg.TLabel",
            font=("Segoe UI", 14, "bold"),
            foreground=COLORS["text"],
            background=COLORS["bg"],
        )
        header.pack(pady=(12, 4))

        subtitle = ttk.Label(
            self.root,
            text="Enter seeds to detect mine positions before you click (offline / after seed reveal).",
            style="Bg.TLabel",
        )
        subtitle.pack(pady=(0, 12))

        body = ttk.Frame(self.root, style="TFrame")
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        left = ttk.Frame(body, style="TFrame")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))

        right = ttk.Frame(body, style="TFrame")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_seed_panel(left)
        self._build_grid_panel(right)
        self._build_output_panel(left)

    def _build_seed_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Seeds & bet", style="Panel.TLabelframe")
        frame.pack(fill=tk.X, pady=(0, 10))

        self.server_seed_var = tk.StringVar()
        self.client_seed_var = tk.StringVar()
        self.server_hash_var = tk.StringVar()
        self.nonce_var = tk.StringVar(value="0")
        self.mine_count_var = tk.IntVar(value=3)

        self._labeled_entry(frame, "Server seed (unhashed)", self.server_seed_var, 0)
        self._labeled_entry(frame, "Client seed", self.client_seed_var, 1)
        self._labeled_entry(frame, "Server seed hash (optional)", self.server_hash_var, 2)
        self._labeled_entry(frame, "Nonce", self.nonce_var, 3)

        mine_row = ttk.Frame(frame, style="TFrame")
        mine_row.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=8)
        ttk.Label(mine_row, text="Mines on board").pack(side=tk.LEFT)
        mine_spin = ttk.Spinbox(
            mine_row,
            from_=1,
            to=24,
            textvariable=self.mine_count_var,
            width=6,
        )
        mine_spin.pack(side=tk.RIGHT)

        btn_row = ttk.Frame(frame, style="TFrame")
        btn_row.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(4, 10))

        ttk.Button(
            btn_row,
            text="Detect mines",
            style="Accent.TButton",
            command=self._on_predict,
        ).pack(fill=tk.X, pady=(0, 6))

        ttk.Button(
            btn_row,
            text="Verify server seed hash",
            command=self._on_verify_hash,
        ).pack(fill=tk.X, pady=(0, 6))

        ttk.Button(
            btn_row,
            text="Scan next 5 nonces",
            command=self._on_scan_nonces,
        ).pack(fill=tk.X)

        frame.columnconfigure(1, weight=1)

    def _labeled_entry(
        self,
        parent: ttk.LabelFrame,
        label: str,
        variable: tk.StringVar,
        row: int,
    ) -> None:
        ttk.Label(parent, text=label).grid(
            row=row, column=0, sticky="w", padx=10, pady=(8, 2)
        )
        entry = tk.Entry(
            parent,
            textvariable=variable,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            font=("Consolas", 9),
        )
        entry.grid(row=row, column=1, sticky="ew", padx=10, pady=(8, 2), ipady=4)

    def _build_grid_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="5×5 detection grid", style="Panel.TLabelframe")
        frame.pack(fill=tk.BOTH, expand=True)

        grid_wrap = tk.Frame(frame, bg=COLORS["panel"])
        grid_wrap.pack(padx=16, pady=16)

        for row in range(ROWS):
            row_buttons: list[tk.Label] = []
            for col in range(COLS):
                tile = row * COLS + col
                cell = tk.Label(
                    grid_wrap,
                    text="?",
                    width=4,
                    height=2,
                    font=("Segoe UI", 14, "bold"),
                    bg=COLORS["hidden"],
                    fg=COLORS["muted"],
                    relief=tk.RAISED,
                    bd=2,
                )
                cell.grid(row=row, column=col, padx=3, pady=3)
                row_buttons.append(cell)
            self._cell_buttons.append(row_buttons)

        legend = tk.Frame(frame, bg=COLORS["panel"])
        legend.pack(fill=tk.X, padx=12, pady=(0, 12))
        for text, color in [
            ("💣 Predicted mine", COLORS["mine_border"]),
            ("💎 Predicted safe", COLORS["safe_border"]),
        ]:
            tk.Label(
                legend,
                text=text,
                fg=color,
                bg=COLORS["panel"],
                font=("Segoe UI", 9),
            ).pack(side=tk.LEFT, padx=8)

    def _build_output_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Detection result", style="Panel.TLabelframe")
        frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(
            frame,
            height=14,
            wrap=tk.WORD,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            font=("Consolas", 9),
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.result_text.insert(
            tk.END,
            "Paste server seed + client seed + nonce, then click Detect mines.\n\n"
            "Note: Live Stake hides the server seed until you rotate. This tool "
            "predicts positions once you have the unhashed seed (or for your offline clone).\n",
        )
        self.result_text.configure(state=tk.DISABLED)

    def _read_inputs(self) -> tuple[str, str, int, int]:
        try:
            nonce = int(self.nonce_var.get().strip())
        except ValueError as exc:
            raise ValueError("Nonce must be a whole number") from exc
        return (
            self.server_seed_var.get(),
            self.client_seed_var.get(),
            nonce,
            int(self.mine_count_var.get()),
        )

    def _on_predict(self) -> None:
        try:
            server_seed, client_seed, nonce, mine_count = self._read_inputs()
            result = predict_mines(server_seed, client_seed, nonce, mine_count)
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))
            return

        self._last_result = result
        self._render_grid(result)
        self._write_result(result, nonce)

    def _on_verify_hash(self) -> None:
        server_seed = self.server_seed_var.get().strip()
        expected = self.server_hash_var.get().strip()
        if not server_seed or not expected:
            messagebox.showwarning(
                "Missing data",
                "Enter both the unhashed server seed and the hash from Stake fairness settings.",
            )
            return
        ok = verify_server_seed_hash(server_seed, expected)
        computed = hash_server_seed(server_seed)
        if ok:
            messagebox.showinfo("Hash verified", "Server seed matches the committed hash.")
        else:
            messagebox.showerror(
                "Hash mismatch",
                f"Hash does not match.\n\nComputed:\n{computed}",
            )

    def _on_scan_nonces(self) -> None:
        try:
            server_seed, client_seed, start_nonce, mine_count = self._read_inputs()
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))
            return

        lines = [f"Scan for {mine_count} mine(s), client seed unchanged:\n"]
        for offset in range(5):
            nonce = start_nonce + offset
            result = predict_mines(server_seed, client_seed, nonce, mine_count)
            lines.append(
                f"Nonce {nonce}: mines at {format_tile_list(result.mine_tiles)}"
            )

        self._set_result_text("\n".join(lines))

    def _render_grid(self, result: PredictionResult) -> None:
        mines = set(result.mine_tiles)
        for row in range(ROWS):
            for col in range(COLS):
                tile = row * COLS + col
                cell = self._cell_buttons[row][col]
                if tile in mines:
                    cell.configure(
                        text="💣",
                        bg=COLORS["mine"],
                        fg=COLORS["danger"],
                        highlightbackground=COLORS["mine_border"],
                        highlightthickness=2,
                    )
                else:
                    cell.configure(
                        text="💎",
                        bg=COLORS["safe"],
                        fg=COLORS["accent"],
                        highlightbackground=COLORS["safe_border"],
                        highlightthickness=2,
                    )

    def _write_result(self, result: PredictionResult, nonce: int) -> None:
        text = (
            f"Detection complete (nonce {nonce})\n"
            f"{'=' * 40}\n"
            f"Mines ({result.mine_count}): {format_tile_list(result.mine_tiles)}\n"
            f"Safe tiles ({len(result.safe_tiles)}): {format_tile_list(result.safe_tiles)}\n\n"
            f"Tile indices (0–24, left→right, top→bottom):\n"
            f"  Mines: {list(result.mine_tiles)}\n\n"
            f"Shuffle order (first {result.mine_count} = mines):\n"
            f"  {list(result.shuffle_order)}\n"
        )
        self._set_result_text(text)

    def _set_result_text(self, text: str) -> None:
        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.configure(state=tk.DISABLED)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    MinesPredictorApp().run()
