from __future__ import annotations

import os
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING

from cipher_logic import clean_seed_text
from file_logic import process_file_stream, read_file_binary_text, save_temporary_result
from ui_helpers import clear_text, set_text

if TYPE_CHECKING:
    from ui_widgets import App


def _get_validated_seed(app: App) -> str | None:
    seed_text = clean_seed_text(app.entry_key.get())

    if len(seed_text) != app.MAX_KEY_LEN:
        messagebox.showwarning(
            "Внимание",
            f"Начальное состояние регистра должно содержать ровно {app.MAX_KEY_LEN} бит.\n"
            f"Сейчас введено: {len(seed_text)}.",
        )
        return None

    return seed_text


def _cleanup_temp_file(app: App) -> None:
    if app._result_path and os.path.exists(app._result_path):
        try:
            os.remove(app._result_path)
        except OSError:
            pass
    app._result_path = None


def on_open_file(app: App) -> None:
    file_path = filedialog.askopenfilename(
        title="Открыть файл для шифрования / дешифрования",
        filetypes=[("Все файлы", "*.*")],
    )
    if not file_path:
        return

    try:
        source_binary_text = read_file_binary_text(file_path)
    except FileNotFoundError:
        messagebox.showerror("Ошибка", "Файл не найден.")
        return
    except PermissionError:
        messagebox.showerror("Ошибка", "Нет прав на чтение файла.")
        return
    except Exception as exc:
        messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{exc}")
        return

    app._source_path = file_path
    _cleanup_temp_file(app)

    set_text(app.text_source, source_binary_text)
    clear_text(app.text_result)
    clear_text(app.text_key)


def _run_cipher(app: App, operation_label: str) -> None:
    if app._source_path is None:
        messagebox.showwarning("Внимание", "Сначала откройте файл.")
        return

    seed_text = _get_validated_seed(app)
    if seed_text is None:
        return

    try:
        temp_path, source_view, key_view, result_view = process_file_stream(
            app._source_path,
            seed_text,
        )
    except PermissionError:
        messagebox.showerror("Ошибка", "Нет прав на чтение файла.")
        return
    except Exception as exc:
        messagebox.showerror("Ошибка", f"Ошибка обработки файла:\n{exc}")
        return

    _cleanup_temp_file(app)
    app._result_path = temp_path

    set_text(app.text_source, source_view)
    set_text(app.text_key, key_view)
    set_text(app.text_result, result_view)


def on_encrypt(app: App) -> None:
    _run_cipher(app, "Шифрование")


def on_decrypt(app: App) -> None:
    _run_cipher(app, "Дешифрование")


def on_save_result(app: App) -> None:
    if app._result_path is None:
        messagebox.showwarning(
            "Внимание",
            "Сначала выполните шифрование или дешифрование.",
        )
        return

    save_path = filedialog.asksaveasfilename(
        title="Сохранить результат",
        confirmoverwrite=True,
        filetypes=[("Все файлы", "*.*")],
    )
    if not save_path:
        return

    try:
        save_temporary_result(app._result_path, save_path)
    except PermissionError:
        messagebox.showerror("Ошибка", "Нет прав на запись файла.")
        return
    except Exception as exc:
        messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{exc}")
        return

    messagebox.showinfo("Сохранено", f"Файл успешно сохранён:\n{save_path}")


def on_exit(app: App) -> None:
    _cleanup_temp_file(app)
    app.main_form.destroy()
