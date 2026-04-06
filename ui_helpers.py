from tkinter import END, Text


def set_text(widget: Text, content: str) -> None:
    widget.config(state="normal")
    widget.delete("1.0", END)
    widget.insert("1.0", content)
    widget.config(state="disabled")


def clear_text(widget: Text) -> None:
    set_text(widget, "")
