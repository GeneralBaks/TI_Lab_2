from __future__ import annotations

from tkinter import (
    Button,
    Entry,
    Frame,
    Label,
    LabelFrame,
    Menu,
    Scrollbar,
    StringVar,
    Text,
    Tk,
)
from typing import Final

from config import POLYNOMIAL_TAPS, REGISTER_SIZE


class App:
    MAX_KEY_LEN: Final[int] = REGISTER_SIZE

    def __init__(self) -> None:
        self._source_path: str | None = None
        self._result_path: str | None = None

        self._init_main_form()

        polynomial_str = " + ".join(f"x^{t}" for t in POLYNOMIAL_TAPS) + " + 1"
        self.key_counter_var = StringVar(value=f"Символов: 0 / {self.MAX_KEY_LEN}")

        self._init_menu()
        self._init_key_frame(polynomial_str)
        self._init_content_frame()
        self._init_button_frame()

    def _init_main_form(self) -> None:
        self.main_form = Tk()
        self.main_form.title("LFSR Шифрование")
        self.main_form.geometry("1200x760")
        self.main_form.minsize(980, 620)
        self.main_form.columnconfigure(0, weight=1)
        self.main_form.rowconfigure(2, weight=1)

    def _init_menu(self) -> None:
        self.file_menu = Menu(self.main_form, tearoff=0)
        self.file_menu.add_command(label="Открыть файл")
        self.file_menu.add_command(label="Сохранить результат")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Выйти")

        self.main_menu = Menu(self.main_form)
        self.main_menu.add_cascade(label="Файл", menu=self.file_menu)
        self.main_form.config(menu=self.main_menu)

    def _init_key_frame(self, polynomial_str: str) -> None:
        input_frame = Frame(self.main_form, padx=10, pady=6)
        input_frame.grid(row=0, column=0, sticky="ew")
        input_frame.columnconfigure(1, weight=1)

        Label(
            input_frame,
            text=f"Начальное состояние регистра ({self.MAX_KEY_LEN} бит, {polynomial_str}:",
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        self._vcmd = (self.main_form.register(self._validate_key_input), "%P")
        self.entry_key = Entry(
            input_frame,
            validate="key",
            validatecommand=self._vcmd,
            font=("Courier New", 11),
        )
        self.entry_key.grid(row=0, column=1, sticky="ew")

        Label(
            input_frame,
            textvariable=self.key_counter_var,
            font=("Courier New", 10),
            fg="#555555",
        ).grid(row=0, column=2, sticky="e", padx=(10, 0))

        key_frame = LabelFrame(
            self.main_form,
            text="Сгенерированный ключ (первые 32 + последние 16 байт)",
            padx=5,
            pady=4,
        )
        key_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 4))
        key_frame.rowconfigure(0, weight=1)
        key_frame.columnconfigure(0, weight=1)

        self.text_key = Text(
            key_frame,
            height=4,
            state="disabled",
            font=("Courier New", 9),
            bg="#f5f5f5",
            wrap="word",
        )
        self.text_key.grid(row=0, column=0, sticky="nsew")

        self.scroll_key = Scrollbar(
            key_frame, orient="vertical", command=self.text_key.yview
        )
        self.scroll_key.grid(row=0, column=1, sticky="ns")
        self.text_key.config(yscrollcommand=self.scroll_key.set)

    def _validate_key_input(self, value_after: str) -> bool:
        if len(value_after) > self.MAX_KEY_LEN:
            return False
        if not all(ch in ("0", "1") for ch in value_after):
            return False
        self.key_counter_var.set(f"Символов: {len(value_after)} / {self.MAX_KEY_LEN}")
        return True

    def _init_content_frame(self) -> None:
        outer_frame = Frame(self.main_form, padx=10)
        outer_frame.grid(row=2, column=0, sticky="nsew")
        outer_frame.columnconfigure(0, weight=1)
        outer_frame.columnconfigure(1, weight=1)
        outer_frame.rowconfigure(0, weight=1)

        self.text_source = self._make_text_panel(
            parent=outer_frame,
            title="Исходный файл (двоичный вид)",
            grid_column=0,
            padx=(0, 5),
        )

        self.text_result = self._make_text_panel(
            parent=outer_frame,
            title="Результат шифрования / дешифрования (двоичный вид)",
            grid_column=1,
            padx=(5, 0),
        )

    def _make_text_panel(
        self,
        parent: Frame,
        title: str,
        grid_column: int,
        padx: tuple[int, int],
    ) -> Text:
        frame = LabelFrame(parent, text=title, padx=5, pady=4)
        frame.grid(row=0, column=grid_column, sticky="nsew", padx=padx)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        text_widget = Text(
            frame,
            state="disabled",
            font=("Courier New", 9),
            bg="#f5f5f5",
            wrap="word",
        )
        text_widget.grid(row=0, column=0, sticky="nsew")

        scrollbar = Scrollbar(frame, orient="vertical", command=text_widget.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        text_widget.config(yscrollcommand=scrollbar.set)

        return text_widget

    def _init_button_frame(self) -> None:
        buttons_frame = Frame(self.main_form, pady=10)
        buttons_frame.grid(row=3, column=0)

        self.btn_open_file = Button(buttons_frame, text="Открыть файл", width=18)
        self.btn_open_file.pack(side="left", padx=10)

        self.btn_encrypt = Button(buttons_frame, text="Зашифровать", width=18)
        self.btn_encrypt.pack(side="left", padx=10)

        self.btn_decrypt = Button(buttons_frame, text="Дешифровать", width=18)
        self.btn_decrypt.pack(side="left", padx=10)

        self.btn_save_result = Button(
            buttons_frame, text="Сохранить результат", width=18
        )
        self.btn_save_result.pack(side="left", padx=10)

    def run(self) -> None:
        self.main_form.mainloop()
