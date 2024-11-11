import flet as ft
from app import gui
from app.utils import logger


async def main(page: ft.Page):
    app = gui.MainWindow(page)
    await app.run()


if __name__ == '__main__':
    logger.info("Приложение запущено")
    ft.app(main)
    logger.info("Приложение закрыто")
