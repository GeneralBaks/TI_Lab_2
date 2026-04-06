from ui_binder import bind_all
from ui_widgets import App


def main() -> None:
    app = App()
    bind_all(app)
    app.run()


if __name__ == "__main__":
    main()
