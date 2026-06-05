"""Main application window."""

from __future__ import annotations

import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from src.converter import SUPPORTED_FORMATS, convert_batch, count_pages_to_convert, parse_page_range
from src.i18n import I18n, LANGUAGE_LABELS

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class PdfToPicApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self._i18n = I18n("zh")
        self._pdf_paths: list[Path] = []
        self._is_converting = False
        self._widgets: dict[str, object] = {}

        self._build_ui()
        self._apply_language()
        self._setup_drag_drop()

    def _t(self, key: str, **kwargs: object) -> str:
        return self._i18n.t(key, **kwargs)

    def _build_ui(self) -> None:
        self.geometry("900x700")
        self.minsize(800, 620)

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=24, pady=(16, 0), sticky="ew")
        top_bar.grid_columnconfigure(0, weight=1)

        self._widgets["header"] = ctk.CTkLabel(
            top_bar,
            text="",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self._widgets["header"].grid(row=0, column=0, sticky="w")

        lang_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        lang_frame.grid(row=0, column=1, sticky="e")
        self._widgets["language_label"] = ctk.CTkLabel(lang_frame, text="", font=ctk.CTkFont(weight="bold"))
        self._widgets["language_label"].pack(side="left", padx=(0, 8))
        self._lang_var = ctk.StringVar(value=LANGUAGE_LABELS["zh"])
        self._lang_menu = ctk.CTkOptionMenu(
            lang_frame,
            variable=self._lang_var,
            values=list(LANGUAGE_LABELS.values()),
            width=110,
            command=self._on_language_change,
        )
        self._lang_menu.pack(side="left")

        self._widgets["subtitle"] = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=("gray40", "gray70"),
        )
        self._widgets["subtitle"].grid(row=1, column=0, padx=24, pady=(4, 12), sticky="w")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        file_frame = ctk.CTkFrame(self)
        file_frame.grid(row=2, column=0, padx=24, pady=8, sticky="nsew")
        file_frame.grid_columnconfigure(0, weight=1)
        file_frame.grid_rowconfigure(2, weight=1)

        file_header = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_header.grid(row=0, column=0, padx=12, pady=(12, 4), sticky="ew")
        file_header.grid_columnconfigure(0, weight=1)

        self._widgets["files_label"] = ctk.CTkLabel(
            file_header,
            text="",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self._widgets["files_label"].grid(row=0, column=0, sticky="w")

        self._file_count_label = ctk.CTkLabel(
            file_header,
            text="",
            text_color=("gray40", "gray70"),
        )
        self._file_count_label.grid(row=0, column=1, sticky="e")

        self._widgets["drop_hint"] = ctk.CTkLabel(
            file_frame,
            text="",
            text_color=("gray50", "gray60"),
            font=ctk.CTkFont(size=12),
        )
        self._widgets["drop_hint"].grid(row=1, column=0, padx=12, pady=(0, 4), sticky="w")

        self._file_list = tk.Listbox(
            file_frame,
            selectmode=tk.EXTENDED,
            font=("Segoe UI", 11),
            activestyle="none",
            highlightthickness=1,
            relief=tk.FLAT,
            borderwidth=0,
        )
        self._file_list.grid(row=2, column=0, padx=12, pady=(0, 8), sticky="nsew")

        btn_row = ctk.CTkFrame(file_frame, fg_color="transparent")
        btn_row.grid(row=3, column=0, padx=12, pady=(0, 12), sticky="ew")

        self._widgets["add_btn"] = ctk.CTkButton(btn_row, text="", command=self._add_files)
        self._widgets["add_btn"].pack(side="left", padx=(0, 8))
        self._widgets["remove_btn"] = ctk.CTkButton(
            btn_row, text="", command=self._remove_selected, width=110
        )
        self._widgets["remove_btn"].pack(side="left", padx=(0, 8))
        self._widgets["clear_btn"] = ctk.CTkButton(
            btn_row, text="", command=self._clear_files, width=100
        )
        self._widgets["clear_btn"].pack(side="left")

        options_frame = ctk.CTkFrame(self)
        options_frame.grid(row=3, column=0, padx=24, pady=8, sticky="ew")
        options_frame.grid_columnconfigure(1, weight=1)
        options_frame.grid_columnconfigure(3, weight=1)

        self._widgets["format_label"] = ctk.CTkLabel(
            options_frame, text="", font=ctk.CTkFont(weight="bold")
        )
        self._widgets["format_label"].grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")
        self._format_var = ctk.StringVar(value="PNG")
        format_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self._format_var,
            values=list(SUPPORTED_FORMATS.keys()),
            width=120,
        )
        format_menu.grid(row=0, column=1, padx=8, pady=(16, 8), sticky="w")

        self._widgets["dpi_label"] = ctk.CTkLabel(
            options_frame, text="", font=ctk.CTkFont(weight="bold")
        )
        self._widgets["dpi_label"].grid(row=0, column=2, padx=(16, 8), pady=(16, 8), sticky="w")
        self._dpi_var = ctk.StringVar(value="150")
        dpi_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self._dpi_var,
            values=["96", "150", "200", "300", "600"],
            width=90,
        )
        dpi_menu.grid(row=0, column=3, padx=8, pady=(16, 8), sticky="w")

        self._widgets["page_range_label"] = ctk.CTkLabel(
            options_frame, text="", font=ctk.CTkFont(weight="bold")
        )
        self._widgets["page_range_label"].grid(row=1, column=0, padx=16, pady=(8, 8), sticky="w")
        self._page_range_var = ctk.StringVar(value="")
        page_range_entry = ctk.CTkEntry(
            options_frame,
            textvariable=self._page_range_var,
            placeholder_text="",
        )
        page_range_entry.grid(row=1, column=1, columnspan=3, padx=8, pady=(8, 8), sticky="ew")
        self._widgets["page_range_entry"] = page_range_entry

        self._widgets["output_label"] = ctk.CTkLabel(
            options_frame, text="", font=ctk.CTkFont(weight="bold")
        )
        self._widgets["output_label"].grid(row=2, column=0, padx=16, pady=(8, 16), sticky="w")
        self._output_dir_var = ctk.StringVar()
        output_entry = ctk.CTkEntry(options_frame, textvariable=self._output_dir_var)
        output_entry.grid(row=2, column=1, columnspan=2, padx=8, pady=(8, 16), sticky="ew")
        self._widgets["browse_btn"] = ctk.CTkButton(
            options_frame, text="", command=self._browse_output, width=90
        )
        self._widgets["browse_btn"].grid(row=2, column=3, padx=8, pady=(8, 16), sticky="w")

        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.grid(row=4, column=0, padx=24, pady=(4, 8), sticky="ew")
        progress_frame.grid_columnconfigure(0, weight=1)

        self._status_label = ctk.CTkLabel(
            progress_frame,
            text="",
            text_color=("gray40", "gray70"),
            anchor="w",
        )
        self._status_label.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        self._progress = ctk.CTkProgressBar(progress_frame)
        self._progress.grid(row=1, column=0, sticky="ew")
        self._progress.set(0)

        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=5, column=0, padx=24, pady=(8, 20), sticky="ew")
        action_frame.grid_columnconfigure(0, weight=1)

        self._open_output_btn = ctk.CTkButton(
            action_frame,
            text="",
            height=42,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            command=self._open_output_dir,
        )
        self._open_output_btn.grid(row=0, column=0, sticky="w")

        self._convert_btn = ctk.CTkButton(
            action_frame,
            text="",
            height=42,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._start_conversion,
        )
        self._convert_btn.grid(row=0, column=1, sticky="e")

    def _apply_language(self) -> None:
        i18n = self._i18n
        self.title(i18n.t("app_title"))
        self._widgets["header"].configure(text=i18n.t("header"))
        self._widgets["subtitle"].configure(text=i18n.t("subtitle"))
        self._widgets["files_label"].configure(text=i18n.t("files_label"))
        self._widgets["drop_hint"].configure(text=i18n.t("drop_hint"))
        self._widgets["add_btn"].configure(text=i18n.t("add_files"))
        self._widgets["remove_btn"].configure(text=i18n.t("remove_selected"))
        self._widgets["clear_btn"].configure(text=i18n.t("clear_list"))
        self._widgets["format_label"].configure(text=i18n.t("output_format"))
        self._widgets["dpi_label"].configure(text=i18n.t("dpi"))
        self._widgets["page_range_label"].configure(text=i18n.t("page_range"))
        self._widgets["page_range_entry"].configure(placeholder_text=i18n.t("page_range_hint"))
        self._widgets["output_label"].configure(text=i18n.t("output_dir"))
        self._widgets["browse_btn"].configure(text=i18n.t("browse"))
        self._widgets["language_label"].configure(text=i18n.t("language"))
        self._open_output_btn.configure(text=i18n.t("open_output"))
        if not self._is_converting:
            self._convert_btn.configure(text=i18n.t("start_convert"))
            self._status_label.configure(text=i18n.t("ready"))

        if not self._output_dir_var.get():
            self._output_dir_var.set(
                str(Path.home() / "Documents" / i18n.t("default_output_dir"))
            )

        self._update_file_count()

    def _on_language_change(self, label: str) -> None:
        for code, name in LANGUAGE_LABELS.items():
            if name == label:
                self._i18n.set_lang(code)
                break
        self._apply_language()

    def _setup_drag_drop(self) -> None:
        if sys.platform != "win32":
            return
        try:
            import windnd

            windnd.hook_dropfiles(self, func=self._on_drop_files)
            windnd.hook_dropfiles(self._file_list, func=self._on_drop_files)
        except ImportError:
            pass

    def _on_drop_files(self, files: list[bytes] | tuple[bytes, ...]) -> None:
        paths: list[str] = []
        for item in files:
            if isinstance(item, bytes):
                try:
                    paths.append(item.decode("utf-8"))
                except UnicodeDecodeError:
                    paths.append(item.decode("gbk"))
            else:
                paths.append(str(item))
        self._add_paths(paths)

    def _add_paths(self, raw_paths: list[str]) -> None:
        existing = {p.resolve() for p in self._pdf_paths}
        added = 0
        for raw in raw_paths:
            path = Path(raw.strip().strip('"'))
            if path.suffix.lower() != ".pdf" or not path.is_file():
                continue
            resolved = path.resolve()
            if resolved in existing:
                continue
            self._pdf_paths.append(path)
            self._file_list.insert(tk.END, str(path))
            existing.add(resolved)
            added += 1

        self._update_file_count()

        if added == 0 and raw_paths:
            messagebox.showinfo(self._t("info"), self._t("no_new_files"))

    def _add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title=self._t("dialog_select_pdf"),
            filetypes=[
                (self._t("pdf_files"), "*.pdf"),
                (self._t("all_files"), "*.*"),
            ],
        )
        if paths:
            self._add_paths(list(paths))

    def _remove_selected(self) -> None:
        selected = list(self._file_list.curselection())
        if not selected:
            return
        for index in reversed(selected):
            self._file_list.delete(index)
            del self._pdf_paths[index]
        self._update_file_count()

    def _clear_files(self) -> None:
        self._pdf_paths.clear()
        self._file_list.delete(0, tk.END)
        self._update_file_count()

    def _update_file_count(self) -> None:
        self._file_count_label.configure(
            text=self._t("files_selected", count=len(self._pdf_paths))
        )

    def _browse_output(self) -> None:
        directory = filedialog.askdirectory(title=self._t("dialog_select_output"))
        if directory:
            self._output_dir_var.set(directory)

    def _open_output_dir(self) -> None:
        output_dir = Path(self._output_dir_var.get())
        if not output_dir.exists():
            messagebox.showwarning(self._t("info"), self._t("output_not_exist"))
            return
        import os
        import subprocess

        if sys.platform == "win32":
            os.startfile(output_dir)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.run(["open", str(output_dir)], check=False)
        else:
            subprocess.run(["xdg-open", str(output_dir)], check=False)

    def _set_converting(self, converting: bool) -> None:
        self._is_converting = converting
        state = "disabled" if converting else "normal"
        self._convert_btn.configure(
            state=state,
            text=self._t("converting") if converting else self._t("start_convert"),
        )

    def _get_page_range(self) -> str | None:
        spec = self._page_range_var.get().strip()
        if not spec:
            return None

        try:
            import fitz

            for path in self._pdf_paths:
                with fitz.open(path) as doc:
                    parse_page_range(spec, doc.page_count)
        except Exception as exc:
            messagebox.showerror(
                self._t("error"),
                self._t("invalid_page_range", detail=str(exc)),
            )
            raise ValueError(str(exc)) from exc

        return spec

    def _start_conversion(self) -> None:
        if self._is_converting:
            return
        if not self._pdf_paths:
            messagebox.showwarning(self._t("info"), self._t("no_files"))
            return

        output_dir = Path(self._output_dir_var.get().strip())
        if not output_dir:
            messagebox.showwarning(self._t("info"), self._t("no_output_dir"))
            return

        try:
            dpi = int(self._dpi_var.get())
            if dpi < 72 or dpi > 600:
                raise ValueError
        except ValueError:
            messagebox.showerror(self._t("error"), self._t("invalid_dpi"))
            return

        try:
            page_range = self._get_page_range()
        except ValueError:
            return

        image_format = self._format_var.get()
        self._set_converting(True)
        self._progress.set(0)
        self._status_label.configure(text=self._t("preparing"))

        thread = threading.Thread(
            target=self._run_conversion,
            args=(list(self._pdf_paths), output_dir, image_format, dpi, page_range),
            daemon=True,
        )
        thread.start()

    def _run_conversion(
        self,
        pdf_paths: list[Path],
        output_dir: Path,
        image_format: str,
        dpi: int,
        page_range: str | None,
    ) -> None:
        completed_pages = 0

        def on_file_start(_path: Path, file_index: int, total_files: int) -> None:
            self.after(
                0,
                lambda: self._status_label.configure(
                    text=self._t("processing_file", current=file_index, total=total_files)
                ),
            )

        def on_page(filename: str, page_num: int, page_total: int) -> None:
            nonlocal completed_pages
            if total_pages == 0:
                return
            completed_pages += 1
            progress = completed_pages / total_pages
            self.after(
                0,
                lambda p=progress, f=filename, n=page_num, t=page_total: (
                    self._progress.set(p),
                    self._status_label.configure(
                        text=self._t("processing_page", name=f, current=n, total=t)
                    ),
                ),
            )

        try:
            total_pages = count_pages_to_convert(pdf_paths, page_range)

            results = convert_batch(
                pdf_paths=pdf_paths,
                output_dir=output_dir,
                image_format=image_format,
                dpi=dpi,
                page_range=page_range,
                on_file_start=on_file_start,
                on_page=on_page,
            )

            total_images = sum(len(r.output_files) for r in results)
            self.after(
                0,
                lambda: self._on_conversion_done(
                    True,
                    self._t(
                        "convert_success",
                        files=len(results),
                        images=total_images,
                    ),
                    output_dir,
                ),
            )
        except Exception as exc:
            self.after(
                0,
                lambda: self._on_conversion_done(
                    False,
                    self._t("convert_failed", error=str(exc)),
                    output_dir,
                ),
            )

    def _on_conversion_done(self, success: bool, message: str, output_dir: Path) -> None:
        self._set_converting(False)
        self._progress.set(1 if success else 0)
        self._status_label.configure(text=message)

        if success:
            if messagebox.askyesno(self._t("done"), f"{message}\n\n{self._t('open_output_prompt')}"):
                self._output_dir_var.set(str(output_dir))
                self._open_output_dir()
        else:
            messagebox.showerror(self._t("error"), message)


def run() -> None:
    app = PdfToPicApp()
    app.mainloop()
