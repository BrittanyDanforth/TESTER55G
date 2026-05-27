"""Tkinter GUI for Stake-style Mines prediction / detection."""

from __future__ import annotations

import hashlib
import time
import tkinter as tk
from tkinter import messagebox, ttk

from mines_predictor.demo import OFFLINE_DEMO, run_demo_detection
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
    "demo": "#f7b731",
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
        self.root.title("Mines Detector")
        self.root.configure(bg=COLORS["bg"])
        self.root.minsize(700, 660)

        self._detector = MinesDetector()
        self._cell_labels: list[list[tk.Label]] = []
        self._seed_entries: list[tk.Entry] = []

        self.demo_mode = tk.BooleanVar(value=True)
        self._saved_live_seeds: dict[str, str] = {}
        self._detect_count = 0
        self._last_input_key: str | None = None
        self._last_mine_tiles: tuple[int, ...] | None = None
        self._detect_after_id: str | None = None
        self._busy = False
        self._suppress_auto = False

        self.server_seed_var = tk.StringVar()
        self.client_seed_var = tk.StringVar()
        self.server_hash_var = tk.StringVar()
        self.mine_count_var = tk.StringVar(value="3")

        self._build_style()
        self._build_layout()
        self.root.bind("<Return>", self._on_return_key)

        self.root.after(100, self._apply_demo_mode)

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
        style.configure(
            "Demo.TCheckbutton",
            background=COLORS["bg"],
            foreground=COLORS["demo"],
            font=("Segoe UI", 10, "bold"),
        )

    def _build_layout(self) -> None:
        top = tk.Frame(self.root, bg=COLORS["bg"])
        top.pack(fill=tk.X, padx=16, pady=(10, 0))

        self.title_label = tk.Label(
            top,
            text="Mines Detector",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            font=("Segoe UI", 15, "bold"),
        )
        self.title_label.pack(side=tk.LEFT)

        self.demo_switch = ttk.Checkbutton(
            top,
            text="Offline demo mode",
            variable=self.demo_mode,
            command=self._on_demo_toggle,
            style="Demo.TCheckbutton",
        )
        self.demo_switch.pack(side=tk.RIGHT)

        self.subtitle_label = tk.Label(
            self.root,
            text="",
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10),
            wraplength=640,
            justify=tk.LEFT,
        )
        self.subtitle_label.pack(anchor=tk.W, padx=16, pady=(6, 4))

        self.demo_banner = tk.Label(
            self.root,
            text="",
            bg="#2a2208",
            fg=COLORS["demo"],
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=6,
        )
        self.demo_banner.pack(fill=tk.X, padx=16, pady=(0, 8))

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
        self.seed_frame = ttk.LabelFrame(parent, text="Seeds", style="Panel.TLabelframe")
        self.seed_frame.pack(fill=tk.X, pady=(0, 10))

        self._labeled_entry(
            self.seed_frame, "Server seed (unhashed)", self.server_seed_var, 0
        )
        self._labeled_entry(self.seed_frame, "Client seed", self.client_seed_var, 1)
        self._labeled_entry(
            self.seed_frame, "Server seed hash (optional)", self.server_hash_var, 2
        )

        mine_row = ttk.Frame(self.seed_frame, style="TFrame")
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
        self.mine_spinbox.bind("<FocusOut>", self._on_mine_count_changed)
        self.mine_spinbox.bind("<<Increment>>", self._on_mine_count_changed)
        self.mine_spinbox.bind("<<Decrement>>", self._on_mine_count_changed)

        btn_row = ttk.Frame(self.seed_frame, style="TFrame")
        btn_row.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=(4, 10))

        self.detect_btn = ttk.Button(
            btn_row,
            text="Detect mines",
            style="Accent.TButton",
            command=self._on_predict,
        )
        self.detect_btn.pack(fill=tk.X, pady=(0, 6))

        self.verify_btn = ttk.Button(
            btn_row,
            text="Verify server seed hash",
            command=self._on_verify_hash,
        )
        self.verify_btn.pack(fill=tk.X)

        self.seed_frame.columnconfigure(1, weight=1)

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
        entry.bind("<KeyRelease>", self._on_live_seed_edited)
        if row < 2:
            variable.trace_add("write", lambda *_a: self._on_live_seed_edited())
        self._seed_entries.append(entry)

    def _build_grid_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="5×5 detection grid", style="Panel.TLabelframe")
        frame.pack(fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(
            frame,
            text="Turn on demo mode or paste seeds, then detect.",
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
            height=11,
            wrap=tk.WORD,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            font=("Consolas", 9),
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._set_result_text(
            "Paste server + client seeds and mine count, then Detect.\n\n"
            "Same seeds + same mine count = same bombs every click (correct).\n"
            "Change a seed or mine count to move the bombs.\n"
            "Live mode auto-detects when you edit seeds.\n"
        )

    def _on_demo_toggle(self) -> None:
        self._apply_demo_mode()

    def _snapshot_fields_to_buffer(self) -> None:
        """Remember current seed fields (used before entering demo)."""
        self._saved_live_seeds = {
            "server": self.server_seed_var.get(),
            "client": self.client_seed_var.get(),
            "hash": self.server_hash_var.get(),
            "mines": self.mine_count_var.get(),
        }

    def _on_live_seed_edited(self, _event=None) -> None:
        if self.demo_mode.get() or self._suppress_auto:
            return
        self._snapshot_fields_to_buffer()
        if self._has_valid_live_seeds():
            self._schedule_live_detect()

    def _schedule_live_detect(self) -> None:
        if self._detect_after_id is not None:
            self.root.after_cancel(self._detect_after_id)
        self._detect_after_id = self.root.after(
            350, lambda: self._on_predict(show_errors=False)
        )

    def _get_entry_text(self, index: int, fallback: tk.StringVar) -> str:
        if index < len(self._seed_entries):
            try:
                value = self._seed_entries[index].get().strip()
                if value:
                    return value
            except tk.TclError:
                pass
        return fallback.get().strip()

    def _bundle_input_key(self, bundle: SeedBundle) -> str:
        raw = (
            f"{bundle.server_seed}|{bundle.client_seed}|"
            f"{bundle.mine_count}|{bundle.game_round}|{self.demo_mode.get()}"
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]

    def _apply_demo_mode(self) -> None:
        if self.demo_mode.get():
            current_server = self.server_seed_var.get().strip()
            if current_server and current_server != OFFLINE_DEMO.server_seed:
                self._snapshot_fields_to_buffer()
            self._load_demo_seeds()
            self._set_seed_inputs_enabled(False)
            self.subtitle_label.configure(
                text="Offline demo — real Stake-style math, no site needed. "
                "Turn off demo to use your own site seeds (fields stay editable)."
            )
            self.demo_banner.configure(
                text="  DEMO: verified seeds · mines at tiles 18, 15, 5 (with 3 mines)  "
            )
            self.root.title("Mines Detector — Offline demo")
            self._on_predict(show_errors=True)
            return

        # Leaving demo → live mode
        self._set_seed_inputs_enabled(True)
        if self._saved_live_seeds.get("server") or self._saved_live_seeds.get("client"):
            self._restore_live_seeds()
        # else: keep whatever is already in the fields (demo seeds stay for editing)

        self.subtitle_label.configure(
            text="Paste or edit seeds from YOUR site. Click Detect mines when ready."
        )
        self.demo_banner.configure(text="")
        self.root.title("Mines Detector — Your site")

        if self._has_valid_live_seeds():
            self._on_predict(show_errors=False)
        else:
            self._show_live_ready_state()

    def _has_valid_live_seeds(self) -> bool:
        return bool(
            self._get_entry_text(0, self.server_seed_var)
            and self._get_entry_text(1, self.client_seed_var)
        )

    def _load_demo_seeds(self) -> None:
        self._suppress_auto = True
        self.server_seed_var.set(OFFLINE_DEMO.server_seed)
        self.client_seed_var.set(OFFLINE_DEMO.client_seed)
        self.server_hash_var.set(OFFLINE_DEMO.server_hash)
        self.mine_count_var.set(str(OFFLINE_DEMO.mine_count))
        self._suppress_auto = False

    def _restore_live_seeds(self) -> None:
        self._suppress_auto = True
        self.server_seed_var.set(self._saved_live_seeds.get("server", ""))
        self.client_seed_var.set(self._saved_live_seeds.get("client", ""))
        self.server_hash_var.set(self._saved_live_seeds.get("hash", ""))
        self.mine_count_var.set(self._saved_live_seeds.get("mines", "3"))
        self._suppress_auto = False

    def _show_live_ready_state(self) -> None:
        self._reset_grid()
        self.status_label.configure(
            text="Ready — paste seeds, then click Detect mines",
            fg=COLORS["muted"],
        )
        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(
            tk.END,
            "Live mode\n"
            f"{'=' * 40}\n"
            "Paste server seed and client seed from your site's fairness page.\n"
            "Set mines on board to match your game, then click Detect mines.\n\n"
            "No error — waiting for your seeds.\n",
        )
        self.result_text.configure(state=tk.DISABLED)

    def _set_seed_inputs_enabled(self, enabled: bool) -> None:
        entry_state = tk.NORMAL if enabled else tk.DISABLED
        for entry in self._seed_entries:
            entry.configure(state=entry_state)
        self.mine_spinbox.configure(state=tk.NORMAL)
        self.verify_btn.configure(state=entry_state)

    def _on_mine_count_changed(self, _event=None) -> None:
        if self.demo_mode.get():
            self.root.after(80, lambda: self._on_predict(show_errors=True))
        elif self._has_valid_live_seeds():
            self.root.after(80, lambda: self._on_predict(show_errors=False))

    def _on_return_key(self, _event=None) -> None:
        self._on_predict(show_errors=True)

    def _parse_mine_count(self) -> int:
        self.root.update_idletasks()
        raw = str(self.mine_spinbox.get()).strip()
        if not raw:
            raw = self.mine_count_var.get().strip()
        try:
            count = int(raw)
        except ValueError as exc:
            raise ValueError("Mines on board must be a whole number from 1 to 24") from exc
        if count < 1 or count > 24:
            raise ValueError("Mines on board must be from 1 to 24")
        return count

    def _read_bundle(self) -> SeedBundle:
        mine_count = self._parse_mine_count()
        if self.demo_mode.get():
            return SeedBundle(
                server_seed=OFFLINE_DEMO.server_seed,
                client_seed=OFFLINE_DEMO.client_seed,
                mine_count=mine_count,
                game_round=OFFLINE_DEMO.game_round,
            )
        server = self._get_entry_text(0, self.server_seed_var)
        client = self._get_entry_text(1, self.client_seed_var)
        if not server:
            raise ValueError("Server seed is required (paste from your site fairness page)")
        if not client:
            raise ValueError("Client seed is required")
        return SeedBundle(
            server_seed=server,
            client_seed=client,
            mine_count=mine_count,
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

    def _on_predict(self, _event=None, *, show_errors: bool = True) -> None:
        if self._busy:
            return
        self._busy = True
        self.detect_btn.configure(state=tk.DISABLED)
        self.root.update_idletasks()

        try:
            if not self.demo_mode.get() and not self._has_valid_live_seeds():
                self._show_live_ready_state()
                if show_errors:
                    messagebox.showinfo(
                        "Seeds needed",
                        "Paste your server seed and client seed from your site's "
                        "fairness page, then click Detect mines.",
                    )
                return

            self._reset_grid()
            self.root.update()

            bundle = self._read_bundle()
            input_key = self._bundle_input_key(bundle)
            same_inputs = input_key == self._last_input_key

            result = self._detector.detect(bundle)
            self._detect_count += 1

            demo_note = ""
            if self.demo_mode.get():
                ok, msg = run_demo_detection(bundle.mine_count)
                demo_note = f"\n\n[{msg}]" if ok else f"\n\n[WARNING: {msg}]"
            else:
                ok = True

            pattern_note = self._pattern_change_note(result, same_inputs, input_key)
            self._flash_then_render(result)

            if self.demo_mode.get() and not ok:
                self.status_label.configure(text="Demo check failed", fg=COLORS["danger"])
            elif same_inputs:
                self.status_label.configure(
                    text=(
                        f"Run #{self._detect_count} — same seeds, same "
                        f"{result.mine_count} mine(s) (expected)"
                    ),
                    fg=COLORS["demo"] if self.demo_mode.get() else COLORS["muted"],
                )
            else:
                self.status_label.configure(
                    text=f"Run #{self._detect_count} — new pattern detected",
                    fg=COLORS["accent"],
                )

            self._write_result(result, demo_note + pattern_note)
            self._last_input_key = input_key
            self._last_mine_tiles = result.mine_tiles
        except ValueError as exc:
            self.status_label.configure(text="Detection failed", fg=COLORS["danger"])
            if show_errors:
                messagebox.showerror("Detection failed", str(exc))
            else:
                self._set_result_text(f"Could not detect:\n{exc}\n")
        finally:
            self._busy = False
            self.detect_btn.configure(state=tk.NORMAL)
            self.root.update_idletasks()

    def _pattern_change_note(
        self,
        result: PredictionResult,
        same_inputs: bool,
        input_key: str,
    ) -> str:
        lines = [
            f"\nDetection run #{self._detect_count} at {time.strftime('%H:%M:%S')}",
            f"Input id: {input_key}",
        ]
        if same_inputs:
            lines.append(
                "\nSame server + client + mine count → same bomb spots every time.\n"
                "That is correct (math is locked to your seeds).\n"
                "Change a seed or mine count to move the bombs."
            )
        elif (
            self._last_mine_tiles is not None
            and self._last_mine_tiles != result.mine_tiles
        ):
            lines.append(
                f"\nPattern changed: was {list(self._last_mine_tiles)} → "
                f"now {list(result.mine_tiles)}"
            )
        return "\n".join(lines)

    def _flash_then_render(self, result: PredictionResult) -> None:
        """Brief ? flash so each click visibly refreshes before showing mines."""
        self._reset_grid()
        self.root.update()
        self._render_grid(result)
        self.root.update()

    def _on_verify_hash(self) -> None:
        server_seed = self.server_seed_var.get().strip()
        expected = self.server_hash_var.get().strip()
        if not server_seed or not expected:
            messagebox.showwarning(
                "Missing data",
                "Enter the unhashed server seed and the hash from your site's fairness page.",
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

    def _set_result_text(self, text: str) -> None:
        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.configure(state=tk.DISABLED)

    def _write_result(self, result: PredictionResult, extra: str = "") -> None:
        mode = "OFFLINE DEMO" if self.demo_mode.get() else "YOUR SITE"
        self._set_result_text(
            f"Mode: {mode}\n"
            f"{'=' * 40}\n"
            f"Mines on board: {result.mine_count}\n"
            f"Mine tiles: {format_tile_list(result.mine_tiles)}\n"
            f"Indices: {list(result.mine_tiles_sorted)}\n\n"
            f"Safe ({len(result.safe_tiles)}): "
            f"{format_tile_list(result.safe_tiles)}"
            f"{extra}\n"
        )

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    MinesPredictorApp().run()
