from __future__ import annotations

from typing import TYPE_CHECKING

from ui_event_handlers import (
    on_decrypt,
    on_encrypt,
    on_exit,
    on_open_file,
    on_save_result,
)

if TYPE_CHECKING:
    from ui_widgets import App


def bind_all(app: App) -> None:

    app.file_menu.entryconfig(0, command=lambda: on_open_file(app))
    app.file_menu.entryconfig(1, command=lambda: on_save_result(app))
    app.file_menu.entryconfig(3, command=lambda: on_exit(app))

    app.btn_open_file.config(command=lambda: on_open_file(app))
    app.btn_encrypt.config(command=lambda: on_encrypt(app))
    app.btn_decrypt.config(command=lambda: on_decrypt(app))
    app.btn_save_result.config(command=lambda: on_save_result(app))

    app.main_form.protocol("WM_DELETE_WINDOW", lambda: on_exit(app))
