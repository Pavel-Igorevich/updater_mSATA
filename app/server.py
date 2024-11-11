import time

import paramiko
from app import utils
import re
from io import BytesIO


class ServerConnection:
    def __init__(self, serial_number, file):
        self.user = 'root'
        self.password = 'toor'
        self.port = 22
        self.serial_number = int(serial_number)
        self.ip = None
        self.client = None
        self.file_content = file
        self.result = None
        self.device = None
        self.all_devices = None
        self.fw_path = '/mnt/video/L23B03.bin'
        self.logger = utils.logger

    def settings(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def create_ip_server(self):
        if 1 <= self.serial_number <= 50175:
            self.ip = f"10.8.{60 + (self.serial_number // 256)}.{self.serial_number % 256}"
            return True
        else:
            self.logger.error(f'Не корректный номер сервера, {self.serial_number}')
            self.result = 'Не корректный номер сервера'
            return False

    def ssh(self, command, timeout=3):
        error, result = None, None
        try:
            self.client.connect(
                self.ip,
                self.port,
                self.user,
                self.password,
                look_for_keys=False,
                allow_agent=False,
                timeout=timeout
            )
            if command:
                self.logger.info(f'Команда ssh: {command}')
                _, client_stdout, client_stderr = self.client.exec_command(command + '\n')
                error, result = map(lambda p: p.read().decode('utf-8').rstrip(), (client_stderr, client_stdout))
        except Exception as exc:
            self.logger.error(f'Ошибка ssh-подключения к серверу, IP = {self.ip}, exception: {exc}')
            self.result = f'Ошибка подключения к серверу, IP = {self.ip}'
            error = exc
        finally:
            self.client.close()
        return error, result

    def search_devices(self):
        error, result = self.ssh('parted -l')
        if result:
            device_pattern = re.compile(r"Disk\s(/dev/\S+):\s*\S+")
            devices = []
            for match in device_pattern.finditer(result):
                devices.append(match.group(1))
            if devices:
                self.all_devices = devices
                self.logger.info(f'Найдены следующие устройства: {self.all_devices}')
                return True
            else:
                self.logger.error(f"Устройств не найдено. error: {error}, result: {result}")
                self.result = "Устройств на сервере не найдено"
                return False
        else:
            self.logger.error(f"Ошибка с выполнением команды «parted -l». error: {error}, result: {result}")
            self.result = "Ошибка с выполнением команды «parted -l»"
            return False

    def find_msata(self, devices):
        for device in devices:
            error, result = self.ssh(f"hdparm -i {device}")
            if result:
                model, firmware_version = self.check_msata(result)
                if 'mSATA' in model and '3SE4' in model:
                    if firmware_version == 'L23B03':
                        self.logger.info(f'Обновление ПО устройства {model} не требуется. Версия ПО L23B03')
                        self.result = 'Обновление ПО не требуется. Версия на устройстве актуальна'
                        return True
                    self.logger.info(f'Устройство {model} с версией ПО {firmware_version} найдено')
                    self.device = device
                    return True
            self.logger.error(f'Ошибка выполнения команды «hdparm -i {device}». error: {error}, result: {result}')
        self.logger.error('Устройства mSATA 3SE4 не найдено!')
        self.result = "Устройства mSATA 3SE4 не найдено!"
        return False

    @staticmethod
    def check_msata(result):
        model_pattern = re.search(r"Model=([^,]+)", result)
        fwrev_pattern = re.search(r"FwRev=([^\s,]+)", result)
        if model_pattern and fwrev_pattern:
            model = model_pattern.group(1)
            firmware_version = fwrev_pattern.group(1)
            return model, firmware_version
        else:
            return None, None

    def upload_bytes_to_server(self):
        self.ssh('mkdir -p /mnt/video')
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.ip,
                self.port,
                self.user,
                self.password,
                look_for_keys=False,
                allow_agent=False,
                timeout=20
            )
            sftp = ssh.open_sftp()
            byte_stream = BytesIO(self.file_content)
            with sftp.open(self.fw_path, 'wb') as remote_file:
                remote_file.write(byte_stream.read())
            sftp.close()
            ssh.close()
            self.logger.info(f'Файл ПО успешно загружен по пути: {self.fw_path}')

        except Exception as exc:
            self.logger.error(f'Ошибка в передаче файла ПО. Exception: {exc}')
            self.result = 'Ошибка в передаче файла ПО'
            return False
        return True

    def update_msata(self):
        command = f"hdparm --yes-i-know-what-i-am-doing --please-destroy-my-drive --fwdownload {self.fw_path} {self.device}"
        error, result = self.ssh(
            command,
            timeout=20
        )
        if result and "Done" in result:
            self.logger.info(f'Обновление ПО выполнено. result: {result}')
            return True
        self.logger.error(f'Обновление ПО не произошло. error: {error}, result: {result}')
        self.result = 'Обновление ПО не произошло'
        return False

    def check_update_fw(self):
        error, result = self.ssh(f"hdparm -i {self.device}")
        if result:
            fwrev_pattern = re.search(r"FwRev=([^\s,]+)", result)
            if fwrev_pattern:
                firmware_version = fwrev_pattern.group(1)
                if firmware_version == 'L23B03':
                    self.logger.info(f'Актуальное ПО mSATA: {firmware_version}')
                    self.result = f'Обновление прошло успешно! Актуальное ПО mSATA: {firmware_version}'
                    return True
        self.logger.error(f'Проверка обновленной версии ПО не удалась. error: {error}, result: {result}')
        self.result = "Проверка обновленной версии ПО не удалась"
        return False

    def old_act(self, result_queue):
        self.settings()
        if not self.create_ip_server():
            result_queue.put({'Error': self.result})
            return
        error, _ = self.ssh('')
        if error:
            result_queue.put({'Error': f"Сервер № {self.serial_number} - не отвечает"})
            return
        if not self.search_devices():
            result_queue.put({'Error': self.result})
            return
        if not self.find_msata(self.all_devices):
            result_queue.put({'Error': self.result})
            return
        elif self.result:
            result_queue.put({'Success': self.result})
            return

        if not self.upload_bytes_to_server():
            result_queue.put({'Error': self.result})
            return
        if not self.update_msata():
            result_queue.put({'Error': self.result})
        if self.check_update_fw():
            result_queue.put({'Success': self.result})
        else:
            result_queue.put({'Error': self.result})

    def act(self, result_queue):
        time.sleep(3)
        return result_queue.put({'Error': f"Сервер № {self.serial_number} - не отвечает"})
