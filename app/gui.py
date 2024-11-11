import asyncio
import queue
from concurrent.futures import ThreadPoolExecutor
import aiofiles
import flet as ft
from .utils import search_fw_file, ip_check
from .server import ServerConnection

STYLE_BTN = ft.ButtonStyle(
    shape=ft.RoundedRectangleBorder(radius=5),
    bgcolor=ft.colors.BLUE,
    color=ft.colors.WHITE,
)

STYLE_BTN_BLOCK = ft.ButtonStyle(
    shape=ft.RoundedRectangleBorder(radius=5),
    bgcolor=ft.colors.GREY,
    color=ft.colors.WHITE,
)


class MainWindow:
    def __init__(self, page: ft.Page):
        self.page = page
        self.enable_user_control = ft.Container(expand=True, bgcolor=ft.colors.GREY)
        self.appbar_field = ft.Text('Программа обновление mSATA')

        self.progress = ft.ProgressBar(color=ft.colors.GREEN_ACCENT, value=0, height=10)

        self.list_start_btn_values = ['Обновить', 'Остановить']
        self.server_num_field = None
        self.start_btn = None
        self.load_btn = None
        self.file_content = None
        self.file_picker = ft.FilePicker(on_result=self.load_file)
        self.snack_bar_text = ft.Text(
                "Ваше устройство не настроено на работу в подсети 10.8.X.X",
                color=ft.colors.BLACK
            )
        self.snackbar_content = ft.Container(
            alignment=ft.alignment.center,
            content=self.snack_bar_text,
            expand=True
        )

    async def load_file(self, e: ft.FilePickerResultEvent):
        if e.files:
            path = e.files[0].path
            async with aiofiles.open(path, 'rb') as file:
                contents = await file.read()
            self.file_content = contents
            self.load_btn.visible = False
            self.start_btn.visible = True
            await self.page.update_async()

    async def show_drawer(self, _event: ft.ControlEvent):
        self.page.drawer.open = True
        await self.page.update_async()
        await self.page.drawer.update_async()

    async def check_server_num(self):
        if not self.server_num_field.value:
            self.server_num_field.error_text = "Обязательное поле для ввода"
        await self.page.update_async()

    async def change_server_num(self, _: ft.ControlEvent):
        if not self.server_num_field.value:
            self.server_num_field.error_text = "Обязательное поле для ввода"
        elif not str(self.server_num_field.value).isdigit():
            self.server_num_field.error_text = "Номер вводится числом"
        else:
            self.server_num_field.error_text = ''
        await self.page.update_async()

    async def block_start_btn(self):
        self.page.snack_bar.show_close_icon = False
        self.page.snack_bar.duration = 1500
        self.page.snack_bar.bgcolor = ft.colors.RED_ACCENT
        self.start_btn.disabled = True
        self.start_btn.style = STYLE_BTN_BLOCK
        await self.page.update_async()

    async def unblock_start_btn(self):
        self.start_btn.disabled = False
        self.start_btn.style = STYLE_BTN
        await self.page.update_async()

    async def check_params(self) -> bool:
        await self.check_server_num()
        if not ip_check():
            self.snack_bar_text.value = "Ваше устройство не настроено на работу в подсети 10.8.X.X"
            self.page.snack_bar.open = True
            await self.unblock_start_btn()
            return False
        elif self.server_num_field.error_text:
            self.snack_bar_text.value = "Введите верный серийный номер"
            self.page.snack_bar.open = True
            await self.unblock_start_btn()
            return False
        return True

    async def on_off_progress(self, on):
        self.progress.value = None if on else 0
        await self.page.update_async()

    async def start(self, _e: ft.ControlEvent):
        await self.block_start_btn()
        check = await self.check_params()
        if check:
            await self.on_off_progress(on=True)
            result_queue = queue.Queue()
            server = ServerConnection(self.server_num_field.value, self.file_content)

            with ThreadPoolExecutor() as executor:
                await asyncio.get_running_loop().run_in_executor(
                    executor, server.act, result_queue
                )

            result = result_queue.get()
            if result:
                error_msg = result.get('Error')
                success_msg = result.get('Success')

                if error_msg:
                    self.snack_bar_text.value = error_msg
                    self.page.snack_bar.duration = 10000

                if success_msg:
                    self.snack_bar_text.value = success_msg
                    self.page.snack_bar.duration = 10000
                    self.page.snack_bar.bgcolor = ft.colors.GREEN_ACCENT

                self.page.snack_bar.show_close_icon = True
                self.page.snack_bar.open = True

            await self.on_off_progress(on=False)
            await self.unblock_start_btn()

    async def create_main_window(self):
        self.file_content = await search_fw_file()
        self.server_num_field = ft.TextField(
            label='Выберите серийный номер сервера',
            expand=True,
            height=60,
            on_change=self.change_server_num
        )
        self.start_btn = ft.ElevatedButton(
            text=self.list_start_btn_values[0],
            expand=True,
            visible=False,
            on_click=self.start,
            style=STYLE_BTN,
            height=40
        )
        self.load_btn = ft.ElevatedButton(
            text='Выбрать файл обновления',
            expand=True,
            visible=True,
            on_click=lambda _: self.file_picker.pick_files(
                allowed_extensions=['bin'],
                dialog_title='Выберите файл обновления *.bin'
            ),
            style=STYLE_BTN
        )
        if self.file_content:
            self.load_btn.visible = False
            self.start_btn.visible = True
        main_column = ft.Column(
            [
                ft.Container(
                    ft.Row([self.server_num_field]),
                    expand=True
                ),
                self.progress,
                ft.Row(
                    [
                        self.start_btn,
                        self.load_btn
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            expand=True,
        )
        await self.page.add_async(main_column)

    async def settings(self):
        self.page.title = 'Программа обновление mSATA'
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.overlay.append(self.file_picker)
        self.page.window_min_width = self.page.window_width = self.page.window_max_width = 400
        self.page.window_min_height = self.page.window_height = self.page.window_max_height = 200
        self.page.snack_bar = ft.SnackBar(
            content=self.snackbar_content,
            bgcolor=ft.colors.RED_ACCENT,
            duration=1500
        )

    async def run(self):
        await self.create_main_window()
        await self.settings()
        await self.page.add_async()
