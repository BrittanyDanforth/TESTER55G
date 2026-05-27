"""Tkinter GUI for Stake-style Mines prediction / detection."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from mines_predictor.demo import OFFLINE_DEMO, run_demo_detection
from mines_predictor.detector import MinesDetector, SeedBundle
from mines_predictor.provably_fair import (
    PredictionResult,
    format_tile_list,
    hash_server_seed,
)
from mines_predictor.theme import (
    CELL_GAP,
    CELL_PAD,
    COLORS,
    FONTS,
    LEFT_PANEL_WIDTH,
    configure_styles,
)


COLS = 5
ROWS = 5


class MinesPredictorApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Mines Detector")
        self.root.configure(bg=COLORS["bg"])
        self.root.minsize(820, 720)

        self._detector = MinesDetector()
        self._cell_labels: list[list[tk.Label]] = []
        self._seed_entries: list[tk.Entry] = []

        self.demo_mode = tk.BooleanVar(value=True)
        self._saved_live_seeds: dict[str, str] = {}
        self._last_bundle_key: tuple[str, str, int, int, bool] | None = None
        self._last_rendered_mines: frozenset[int] | None = None

        self.server_seed_var = tk.StringVar()
        self.client_seed_var = tk.StringVar()
        self.server_hash_var = tk.StringVar()
        self.mine_count_var = tk.StringVar(value="3")

        configure_styles(self.root)
        self._build_layout()
        self.root.bind("<Return>", self._on_detect_click)
        self.root.after(100, self._apply_demo_mode)

    def _build_layout(self) -> None:
        outer = tk.Frame(self.root, bg=COLORS["bg"])
        outer.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        self._build_header(outer)

        body = tk.Frame(outer, bg=COLORS["bg"])
        body.pack(fill=tk.BOTH, expand=True, pady=(16, 0))

        left = tk.Frame(body, bg=COLORS["bg"], width=LEFT_PANEL_WIDTH)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 16))
        left.pack_propagate(False)

        right = tk.Frame(body, bg=COLORS["bg"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_seed_panel(left)
        self._build_output_panel(left)
        self._build_grid_panel(right)

    def _build_header(self, parent: tk.Frame) -> None:
        header = tk.Frame(parent, bg=COLORS["bg"])
        header.pack(fill=tk.X)

        title_block = tk.Frame(header, bg=COLORS["bg"])
        title_block.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            title_block,
            text="Mines Detector",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            font=FONTS["title"],
        ).pack(anchor=tk.W)

        self.subtitle_label = tk.Label(
            title_block,
            text="",
            bg=COLORS["bg"],
            fg=COLORS["text_secondary"],
            font=FONTS["subtitle"],
            wraplength=480,
            justify=tk.LEFT,
        )
        self.subtitle_label.pack(anchor=tk.W, pady=(4, 0))

        demo_wrap = tk.Frame(
            header,
            bg=COLORS["panel"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        demo_wrap.pack(side=tk.RIGHT, padx=(12, 0), pady=4)

        ttk.Checkbutton(
            demo_wrap,
            text="  Offline demo",
            variable=self.demo_mode,
            command=self._on_demo_toggle,
            style="Demo.TCheckbutton",
        ).pack(padx=12, pady=8)

        tk.Frame(parent, bg=COLORS["accent"], height=2).pack(fill=tk.X, pady=(14, 0))

        self.demo_banner_frame = tk.Frame(parent, bg=COLORS["demo_bg"])
        self.demo_banner_frame.pack_forget()

        banner_inner = tk.Frame(self.demo_banner_frame, bg=COLORS["demo_bg"])
        banner_inner.pack(fill=tk.X, padx=12, pady=10)
        tk.Frame(banner_inner, bg=COLORS["demo"], width=3).pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.demo_banner = tk.Label(
            banner_inner,
            text="",
            bg=COLORS["demo_bg"],
            fg=COLORS["demo"],
            font=("Segoe UI", 9, "bold"),
            anchor=tk.W,
        )
        self.demo_banner.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _build_seed_panel(self, parent: tk.Frame) -> None:
        card = ttk.LabelFrame(parent, text="  Seeds & settings", style="Card.TLabelframe")
        card.pack(fill=tk.X, pady=(0, 12))

        inner = tk.Frame(card, bg=COLORS["panel"])
        inner.pack(fill=tk.X, padx=12, pady=(4, 12))

        self._field(inner, "Server seed", self.server_seed_var, 0, mono=True)
        self._field(inner, "Client seed", self.client_seed_var, 1, mono=True)
        self._field(inner, "Seed hash (optional)", self.server_hash_var, 2, mono=True)

        mine_row = tk.Frame(inner, bg=COLORS["panel"])
        mine_row.pack(fill=tk.X, pady=(10, 4))
        tk.Label(
            mine_row,
            text="Mines on board",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=FONTS["label"],
        ).pack(side=tk.LEFT)
        tk.Label(
            mine_row,
            text="1 – 24",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=FONTS["label"],
        ).pack(side=tk.RIGHT)

        self._build_mine_stepper(inner)

        self.detect_btn = ttk.Button(
            inner,
            text="Detect mines",
            style="Primary.TButton",
            command=self._on_detect_click,
        )
        self.detect_btn.pack(fill=tk.X, pady=(0, 8))

        self.verify_btn = ttk.Button(
            inner,
            text="Verify seed hash",
            style="Ghost.TButton",
            command=self._on_verify_hash,
        )
        self.verify_btn.pack(fill=tk.X)

    def _build_mine_stepper(self, parent: tk.Frame) -> None:
        wrap = tk.Frame(
            parent,
            bg=COLORS["input_bg"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        wrap.pack(fill=tk.X, pady=(0, 12))

        row = tk.Frame(wrap, bg=COLORS["input_bg"])
        row.pack(fill=tk.X, padx=4, pady=4)
        row.columnconfigure(1, weight=1)

        self.mine_minus_btn = ttk.Button(
            row,
            text="−",
            style="Stepper.TButton",
            command=lambda: self._step_mines(-1),
        )
        self.mine_minus_btn.grid(row=0, column=0, sticky="ns", padx=(4, 0))

        center = tk.Frame(row, bg=COLORS["input_bg"])
        center.grid(row=0, column=1, sticky="ew", padx=8)

        self.mine_entry = tk.Entry(
            center,
            textvariable=self.mine_count_var,
            width=4,
            justify=tk.CENTER,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            relief=tk.FLAT,
            font=("Segoe UI", 20, "bold"),
            disabledbackground=COLORS["input_bg"],
            disabledforeground=COLORS["text"],
        )
        self.mine_entry.pack(ipady=4)
        self.mine_entry.bind("<KeyRelease>", self._on_mine_count_edited)
        self.mine_entry.bind("<Return>", self._on_detect_click)

        tk.Label(
            center,
            text="bombs",
            bg=COLORS["input_bg"],
            fg=COLORS["muted"],
            font=FONTS["label"],
        ).pack()

        self.mine_plus_btn = ttk.Button(
            row,
            text="+",
            style="Stepper.TButton",
            command=lambda: self._step_mines(1),
        )
        self.mine_plus_btn.grid(row=0, column=2, sticky="ns", padx=(0, 4))

    def _field(
        self,
        parent: tk.Frame,
        label: str,
        variable: tk.StringVar,
        index: int,
        *,
        mono: bool = False,
    ) -> None:
        tk.Label(
            parent,
            text=label,
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=FONTS["label"],
        ).pack(anchor=tk.W, pady=(8, 4) if index else (0, 4))

        border = tk.Frame(
            parent,
            bg=COLORS["input_bg"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        border.pack(fill=tk.X)

        entry = tk.Entry(
            border,
            textvariable=variable,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            relief=tk.FLAT,
            font=FONTS["mono"] if mono else FONTS["body"],
        )
        entry.pack(fill=tk.X, ipady=7, ipadx=6, padx=1, pady=1)
        entry.bind("<Return>", self._on_detect_click)

        def on_focus_in(_e: tk.Event, frame: tk.Frame = border) -> None:
            frame.configure(highlightbackground=COLORS["border_focus"])

        def on_focus_out(_e: tk.Event, frame: tk.Frame = border) -> None:
            frame.configure(highlightbackground=COLORS["border"])

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        self._seed_entries.append(entry)

    def _build_grid_panel(self, parent: tk.Frame) -> None:
        card = ttk.LabelFrame(parent, text="  Board", style="Card.TLabelframe")
        card.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(card, bg=COLORS["panel"])
        inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        self.status_pill = tk.Frame(
            inner,
            bg=COLORS["pill_bg"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        self.status_pill.pack(pady=(0, 12))

        self.status_label = tk.Label(
            self.status_pill,
            text="Ready",
            bg=COLORS["pill_bg"],
            fg=COLORS["text_secondary"],
            font=FONTS["body"],
            padx=16,
            pady=6,
        )
        self.status_label.pack()

        grid_outer = tk.Frame(
            inner,
            bg=COLORS["bg_deep"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        grid_outer.pack()

        grid_wrap = tk.Frame(grid_outer, bg=COLORS["bg_deep"])
        grid_wrap.pack(padx=CELL_PAD, pady=CELL_PAD)

        for row in range(ROWS):
            row_labels: list[tk.Label] = []
            for col in range(COLS):
                cell = tk.Label(
                    grid_wrap,
                    text="·",
                    width=3,
                    height=1,
                    font=FONTS["cell"],
                    bg=COLORS["cell_hidden"],
                    fg=COLORS["cell_hidden_fg"],
                    relief=tk.FLAT,
                    highlightthickness=2,
                    highlightbackground=COLORS["bg_deep"],
                )
                cell.grid(row=row, column=col, padx=CELL_GAP, pady=CELL_GAP, sticky="nsew")
                row_labels.append(cell)
            self._cell_labels.append(row_labels)

        legend = tk.Frame(inner, bg=COLORS["panel"])
        legend.pack(fill=tk.X, pady=(14, 0))
        for icon, label, color in (
            ("💣", "Bomb", COLORS["cell_mine_border"]),
            ("💎", "Safe", COLORS["cell_safe_border"]),
        ):
            item = tk.Frame(legend, bg=COLORS["panel"])
            item.pack(side=tk.LEFT, padx=(0, 20))
            tk.Label(item, text=icon, bg=COLORS["panel"], font=FONTS["body"]).pack(
                side=tk.LEFT, padx=(0, 6)
            )
            tk.Label(
                item, text=label, bg=COLORS["panel"], fg=color, font=FONTS["label"]
            ).pack(side=tk.LEFT)

    def _build_output_panel(self, parent: tk.Frame) -> None:
        card = ttk.LabelFrame(parent, text="  Results", style="Card.TLabelframe")
        card.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(card, bg=COLORS["panel"])
        inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.stat_mines = tk.Label(
            inner,
            text="—",
            bg=COLORS["panel"],
            fg=COLORS["accent"],
            font=FONTS["stat_big"],
        )
        self.stat_mines.pack(anchor=tk.W)

        tk.Label(
            inner,
            text="bombs found",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=FONTS["label"],
        ).pack(anchor=tk.W, pady=(0, 12))

        tk.Frame(inner, bg=COLORS["border"], height=1).pack(fill=tk.X, pady=(0, 10))

        self.result_bombs = tk.Label(
            inner,
            text="Tap Detect to scan the board",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=FONTS["body"],
            wraplength=LEFT_PANEL_WIDTH - 48,
            justify=tk.LEFT,
        )
        self.result_bombs.pack(anchor=tk.W, pady=4)

        self.result_safe = tk.Label(
            inner,
            text="",
            bg=COLORS["panel"],
            fg=COLORS["text_secondary"],
            font=FONTS["body"],
            wraplength=LEFT_PANEL_WIDTH - 48,
            justify=tk.LEFT,
        )
        self.result_safe.pack(anchor=tk.W, pady=4)

    def _on_detect_click(self, _event=None) -> None:
        """Only way to run detection — button or Enter."""
        self._run_detect(show_popup=True, force=True)

    def _step_mines(self, delta: int) -> None:
        try:
            value = int(self._read_mine_count_raw())
        except ValueError:
            value = 3
        value = max(1, min(24, value + delta))
        self._set_mine_count(value)

    def _on_mine_count_edited(self, _event=None) -> None:
        raw = self._read_mine_count_raw()
        if not raw:
            return
        if not raw.isdigit():
            cleaned = "".join(ch for ch in raw if ch.isdigit())
            if cleaned:
                self._set_mine_count(int(cleaned))
            return
        value = int(raw)
        if value > 24:
            value = 24
        if value < 1:
            return
        self._set_mine_count(value)

    def _set_mine_count(self, value: int) -> None:
        text = str(max(1, min(24, value)))
        if self._read_mine_count_raw() == text:
            return
        self.mine_count_var.set(text)

    def _on_demo_toggle(self) -> None:
        self._apply_demo_mode()

    def _snapshot_fields_to_buffer(self) -> None:
        self._saved_live_seeds = {
            "server": self._read_server(),
            "client": self._read_client(),
            "hash": self.server_hash_var.get().strip(),
            "mines": self._read_mine_count_raw(),
        }

    def _apply_demo_mode(self) -> None:
        self._last_bundle_key = None
        self._last_rendered_mines = None

        if self.demo_mode.get():
            if self._read_server() and self._read_server() != OFFLINE_DEMO.server_seed:
                self._snapshot_fields_to_buffer()
            self._load_demo_seeds()
            self._set_seed_inputs_enabled(False)
            self.subtitle_label.configure(
                text="Demo — fixed seeds. Set mine count, then press Detect mines."
            )
            self.demo_banner.configure(
                text="Verified demo · 3 mines land on (4,4), (4,1), (2,1)"
            )
            self.demo_banner_frame.pack(fill=tk.X, pady=(12, 0))
            self._show_waiting_state()
            self._set_status("Press Detect mines to scan", COLORS["muted"])
            return

        self._set_seed_inputs_enabled(True)
        if self._saved_live_seeds.get("server") or self._saved_live_seeds.get("client"):
            self._restore_live_seeds()
        self.subtitle_label.configure(
            text="Paste seeds, set mine count, then press Detect mines."
        )
        self.demo_banner_frame.pack_forget()
        self._show_waiting_state()

    def _has_valid_live_seeds(self) -> bool:
        return bool(self._read_server() and self._read_client())

    def _load_demo_seeds(self) -> None:
        self.server_seed_var.set(OFFLINE_DEMO.server_seed)
        self.client_seed_var.set(OFFLINE_DEMO.client_seed)
        self.server_hash_var.set(OFFLINE_DEMO.server_hash)
        self.mine_count_var.set(str(OFFLINE_DEMO.mine_count))

    def _restore_live_seeds(self) -> None:
        self.server_seed_var.set(self._saved_live_seeds.get("server", ""))
        self.client_seed_var.set(self._saved_live_seeds.get("client", ""))
        self.server_hash_var.set(self._saved_live_seeds.get("hash", ""))
        self.mine_count_var.set(self._saved_live_seeds.get("mines", "3"))

    def _set_seed_inputs_enabled(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        bg = COLORS["input_bg"] if enabled else COLORS["input_disabled"]
        fg = COLORS["text"] if enabled else COLORS["muted"]
        for entry in self._seed_entries:
            entry.configure(state=state, bg=bg, fg=fg)
        self.mine_entry.configure(state=tk.NORMAL)
        if enabled:
            self.mine_minus_btn.state(["!disabled"])
            self.mine_plus_btn.state(["!disabled"])
            self.detect_btn.state(["!disabled"])
            self.verify_btn.state(["!disabled"])
        else:
            self.mine_minus_btn.state(["!disabled"])
            self.mine_plus_btn.state(["!disabled"])
            self.detect_btn.state(["!disabled"])
            self.verify_btn.state(["disabled"])

    def _read_server(self) -> str:
        return self._get_entry_text(0, self.server_seed_var)

    def _read_client(self) -> str:
        return self._get_entry_text(1, self.client_seed_var)

    def _get_entry_text(self, index: int, fallback: tk.StringVar) -> str:
        if index < len(self._seed_entries):
            try:
                value = self._seed_entries[index].get().strip()
                if value:
                    return value
            except tk.TclError:
                pass
        return fallback.get().strip()

    def _read_mine_count_raw(self) -> str:
        self.root.update_idletasks()
        try:
            from_entry = self.mine_entry.get().strip()
            if from_entry:
                return from_entry
        except tk.TclError:
            pass
        return self.mine_count_var.get().strip()

    def _parse_mine_count(self) -> int:
        raw = self._read_mine_count_raw()
        if not raw:
            raise ValueError("Enter how many mines are on the board (1–24)")
        try:
            count = int(raw)
        except ValueError as exc:
            raise ValueError("Mines must be a whole number from 1 to 24") from exc
        if count < 1 or count > 24:
            raise ValueError("Mines must be from 1 to 24")
        self._set_mine_count(count)
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
        server = self._read_server()
        client = self._read_client()
        if not server:
            raise ValueError("Paste your server seed first")
        if not client:
            raise ValueError("Paste your client seed first")
        return SeedBundle(
            server_seed=server,
            client_seed=client,
            mine_count=mine_count,
            game_round=0,
        )

    def _show_waiting_state(self) -> None:
        self._reset_grid()
        self._set_status("Add your seeds, then press Detect", COLORS["muted"])
        self.stat_mines.configure(text="—", fg=COLORS["muted"])
        self.result_bombs.configure(text="Paste server + client seed")
        self.result_safe.configure(text="")

    def _set_status(self, text: str, color: str) -> None:
        self.status_label.configure(text=text, fg=color)

    def _reset_grid(self) -> None:
        self._last_rendered_mines = None
        for row in range(ROWS):
            for col in range(COLS):
                self._cell_labels[row][col].configure(
                    text="·",
                    bg=COLORS["cell_hidden"],
                    fg=COLORS["cell_hidden_fg"],
                    highlightbackground=COLORS["bg_deep"],
                    highlightthickness=2,
                )

    def _run_detect(self, *, show_popup: bool, force: bool) -> None:
        self.root.update_idletasks()
        self.detect_btn.state(["disabled"])

        try:
            if not self.demo_mode.get() and not self._has_valid_live_seeds():
                if show_popup:
                    messagebox.showinfo(
                        "Seeds needed",
                        "Paste your server seed and client seed, then press Detect mines.",
                    )
                else:
                    self._show_waiting_state()
                return

            try:
                bundle = self._read_bundle()
            except ValueError as exc:
                self._set_status(str(exc), COLORS["danger"])
                if show_popup:
                    messagebox.showerror("Cannot detect", str(exc))
                return

            bundle_key = self._bundle_key(bundle)
            if not force and bundle_key == self._last_bundle_key:
                self._set_status("Board already matches these settings", COLORS["muted"])
                return

            self._set_status("Scanning board…", COLORS["text_secondary"])

            result = self._detector.detect(bundle)
            self._render_grid(result, force=True)
            self._write_result(result)
            self._last_bundle_key = bundle_key

            if self.demo_mode.get():
                ok, _ = run_demo_detection(bundle.mine_count)
                color = COLORS["demo"] if ok else COLORS["danger"]
                label = "Detection complete"
            else:
                ok = True
                color = COLORS["accent"]
                label = "Detection complete"

            self._set_status(f"{label} · {result.mine_count} bombs", color)
        finally:
            if self.demo_mode.get() or self._has_valid_live_seeds():
                self.detect_btn.state(["!disabled"])
            else:
                self.detect_btn.state(["disabled"])

    def _bundle_key(self, bundle: SeedBundle) -> tuple[str, str, int, int, bool]:
        return (
            bundle.server_seed,
            bundle.client_seed,
            bundle.mine_count,
            bundle.game_round,
            self.demo_mode.get(),
        )

    def _on_verify_hash(self) -> None:
        server_seed = self._read_server()
        expected = self.server_hash_var.get().strip()
        if not server_seed or not expected:
            messagebox.showwarning("Need both", "Add server seed and hash.")
            return
        computed = hash_server_seed(server_seed)
        if computed.lower() == expected.lower():
            messagebox.showinfo("Verified", "Seed hash matches.")
        else:
            messagebox.showerror("Mismatch", f"Expected:\n{computed}")

    def _render_grid(self, result: PredictionResult, *, force: bool = False) -> None:
        mines = frozenset(result.mine_tiles)
        if not force and mines == self._last_rendered_mines:
            return
        self._last_rendered_mines = mines

        for row in range(ROWS):
            for col in range(COLS):
                tile = row * COLS + col
                cell = self._cell_labels[row][col]
                if tile in mines:
                    cell.configure(
                        text="💣",
                        bg=COLORS["cell_mine_bg"],
                        fg=COLORS["danger"],
                        highlightbackground=COLORS["cell_mine_border"],
                        highlightthickness=2,
                    )
                else:
                    cell.configure(
                        text="💎",
                        bg=COLORS["cell_safe_bg"],
                        fg=COLORS["accent"],
                        highlightbackground=COLORS["cell_safe_border"],
                        highlightthickness=2,
                    )

    def _write_result(self, result: PredictionResult) -> None:
        bombs = format_tile_list(result.mine_tiles)
        self.stat_mines.configure(text=str(result.mine_count), fg=COLORS["accent"])
        self.result_bombs.configure(text=f"Bomb positions:\n{bombs}")
        self.result_safe.configure(text=f"Safe tiles: {len(result.safe_tiles)} of 25")

    def _on_close(self) -> None:
        self.root.destroy()

    def run(self) -> None:
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()


def main() -> None:
    MinesPredictorApp().run()
