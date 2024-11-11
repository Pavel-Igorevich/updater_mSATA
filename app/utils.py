import os
import aiofiles
import ifaddr
import logging
from datetime import datetime


async def search_fw_file():
    current_dir = os.getcwd()

    filename = 'L23B03.bin'

    if filename in os.listdir(current_dir):
        file_path = os.path.join(current_dir, filename)
        async with aiofiles.open(file_path, "rb") as file:
            file_content = await file.read()
        return file_content
    else:
        return False


def ip_check() -> bool:
    config = ifaddr.get_adapters(include_unconfigured=True)
    if any(
            True if isinstance(data.ip, str) and '10.8.' in data.ip
            else False for adapter in config for data in adapter.ips
    ):
        logger.info("Машина пользователя настроена на работу в подсети 10.8.X.X")
        return True
    else:
        logger.warning("Машина пользователя не настроена работу в подсети 10.8.X.X")
        return False


def search_fw_file_noasync():
    current_dir = os.getcwd()

    filename = '3SE4 DEMSR-08GM41SWADB/L23B03.bin'

    if filename in os.listdir(current_dir):
        file_path = os.path.join(current_dir, filename)
        with open(file_path, "rb") as file:
            file_content = file.read()
        return file_content
    else:
        return False


def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    current_date = datetime.now().strftime("%Y-%m-%d")
    log_filename = os.path.join(log_dir, f"updater_msata_{current_date}.log")

    main_logger = logging.getLogger("app_logger")
    main_logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    main_logger.addHandler(file_handler)

    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger("flet_core").setLevel(logging.WARNING)
    logging.getLogger("flet_runtime").setLevel(logging.WARNING)

    return main_logger


logger = setup_logging()
