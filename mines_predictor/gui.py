"""Tkinter GUI for Stake-style Mines prediction / detection."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from mines_predictor.detector import MinesDetector, SeedBundle
from mines_predictor.provably_fair import (
    PredictionResult,
    format_tile_list,
    hash_server_seed,
)


COLS = 5
ROWS = 5

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
    "input_bg": "#0f212e",
}


class MinesPredictorApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Stake Mines Detector")
        self.root.configure(bg=COLORS["bg"])
        self.root.minsize(680, 640)

        self._detector = MinesDetector()
        self._cell_labels: list[list[tk.Label]] = []
        self._entry_widgets: list[tk.Entry] = []

        self._build_style()
        self._build_layout()
        self.root.bind("<Return>", self._on_return_key)

    def _build_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=COLORS["bg"])
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
        style.configure("TLabel", background=COLORS["panel"], foreground=COLORS["text"])
        style.configure("Bg.TLabel", background=COLORS["bg"], foreground=COLORS["muted"])
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))

    def _build_layout(self) -> None:
        header = ttk.Label(
            self.root,
            text="Mines Detector",
            style="Bg.TLabel",
            font=("Segoe UI", 14, "bold"),
            foreground=COLORS["text"],
            background=COLORS["bg"],
        )
        header.pack(pady=(12, 4))

        subtitle = ttk.Label(
            self.root,
            text="Paste server + client seeds and mine count, then detect.",
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
        frame = ttk.LabelFrame(parent, text="Seeds", style="Panel.TLabelframe")
        frame.pack(fill=tk.X, pady=(0, 10))

        self.server_seed_var = tk.StringVar()
        self.client_seed_var = tk.StringVar()
        self.server_hash_var = tk.StringVar()
        self.mine_count_var = tk.StringVar(value="3")

        self._labeled_entry(frame, "Server seed (unhashed)", self.server_seed_var, 0)
        self._labeled_entry(frame, "Client seed", self.client_seed_var, 1)
        self._labeled_entry(frame, "Server seed hash (optional)", self.server_hash_var, 2)

        mine_row = ttk.Frame(frame, style="TFrame")
        mine_row.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=8)
        ttk.Label(mine_row, text="Mines on board (1–24)").pack(side=tk.LEFT)
        self.mine_spinbox = ttk.Spinbox(
            mine_row,
            from_=1,
            to=24,
            textvariable=self.mine_count_var,
            width=6,
        )
        self.mine_spinbox.pack(side=tk.RIGHT)
        self.mine_spinbox.bind("<Return>", self._on_return_key)

        btn_row = ttk.Frame(frame, style="TFrame")
        btn_row.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=(4, 10))

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
        entry.bind("<Return>", self._on_return_key)
        self._entry_widgets.append(entry)

    def _build_grid_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="5×5 detection grid", style="Panel.TLabelframe")
        frame.pack(fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(
            frame,
            text="Waiting for detection…",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10),
        )
        self.status_label.pack(pady=(10, 4))

        grid_wrap = tk.Frame(frame, bg=COLORS["panel"])
        grid_wrap.pack(padx=16, pady=8)

        for row in range(ROWS):
            row_labels: list[tk.Label] = []
            for col in range(COLS):
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
                    highlightthickness=0,
                )
                cell.grid(row=row, column=col, padx=3, pady=3)
                row_labels.append(cell)
            self._cell_labels.append(row_labels)

        legend = tk.Frame(frame, bg=COLORS["panel"])
        legend.pack(fill=tk.X, padx=12, pady=(0, 12))
        for text, color in [
            ("💣 Mine", COLORS["mine_border"]),
            ("💎 Safe", COLORS["safe_border"]),
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
            height=12,
            wrap=tk.WORD,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            font=("Consolas", 9),
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._set_result_text(
            "Enter server seed, client seed, and how many mines are on the board.\n"
            "Click Detect mines (or press Enter).\n\n"
            "The grid updates every time you detect — change seeds or mine count "
            "and click again to see a new pattern.\n"
        )

    def _on_return_key(self, _event=None) -> None:
        self._on_predict()

    def _parse_mine_count(self) -> int:
        raw = self.mine_spinbox.get().strip()
        try:
            count = int(raw)
        except ValueError as exc:
            raise ValueError("Mines on board must be a whole number from 1 to 24") from exc
        if count < 1 or count > 24:
            raise ValueError("Mines on board must be from 1 to 24")
        return count

    def _read_bundle(self) -> SeedBundle:
        return SeedBundle(
            server_seed=self.server_seed_var.get().strip(),
            client_seed=self.client_seed_var.get().strip(),
            mine_count=self._parse_mine_count(),
            game_round=0,
        )

    def _reset_grid(self) -> None:
        for row in range(ROWS):
            for col in range(COLS):
                self._cell_labels[row][col].configure(
                    text="?",
                    bg=COLORS["hidden"],
                    fg=COLORS["muted"],
                    highlightthickness=0,
                )
        self.status_label.configure(text="Detecting…", fg=COLORS["muted"])
        self.root.update_idletasks()

    def _on_predict(self, _event=None) -> None:
        self._reset_grid()
        try:
            bundle = self._read_bundle()
            result = self._detector.detect(bundle)
        except ValueError as exc:
            self.status_label.configure(text="Detection failed", fg=COLORS["danger"])
            messagebox.showerror("Detection failed", str(exc))
            return

        self._render_grid(result)
        self._write_result(result)
        self.status_label.configure(
            text=f"Detected {result.mine_count} mine(s) on the grid",
            fg=COLORS["accent"],
        )
        self.root.update_idletasks()

    def _on_verify_hash(self) -> None:
        server_seed = self.server_seed_var.get().strip()
        expected = self.server_hash_var.get().strip()
        if not server_seed or not expected:
            messagebox.showwarning(
                "Missing data",
                "Enter the unhashed server seed and the hash from Fairness settings.",
            )
            return
        computed = hash_server_seed(server_seed)
        if computed.lower() == expected.lower():
            messagebox.showinfo("Hash verified", "Server seed matches the committed hash.")
        else:
            messagebox.showerror(
                "Hash mismatch",
                f"Hash does not match.\n\nComputed:\n{computed}",
            )

    def _render_grid(self, result: PredictionResult) -> None:
        mines = set(result.mine_tiles)
        for row in range(ROWS):
            for col in range(COLS):
                tile = row * COLS + col
                cell = self._cell_labels[row][col]
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

    def _write_result(self, result: PredictionResult) -> None:
        text = (
            "Detection complete\n"
            f"{'=' * 40}\n"
            f"Mines on board: {result.mine_count}\n"
            f"Mine tiles: {format_tile_list(result.mine_tiles)}\n"
            f"Indices: {list(result.mine_tiles_sorted)}\n\n"
            f"Safe tiles ({len(result.safe_tiles)}): "
            f"{format_tile_list(result.safe_tiles)}\n"
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
