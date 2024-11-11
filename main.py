import flet as ft
from app import gui
from app.utils import logger


async def main(page: ft.Page):
    logger.info("Приложение запущено")
    app = gui.MainWindow(page)
    await app.run()
    logger.info("Приложение закрыто")

if __name__ == '__main__':
    ft.app(main)
