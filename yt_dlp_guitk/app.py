import guitk as ui
from loguru import logger

from .gui.window import MainWindow
from .library import env, log


def main():
    try:
        log.configure()

        if env.get("DEBUG", "0") == "1":
            ui.set_debug(True)

        logger.trace("Launching main window")
        window = MainWindow()
        window.run()
    except Exception as ex:
        print(f"Unexpected exception: {str(ex)}")


if __name__ == "__main__":
    main()
