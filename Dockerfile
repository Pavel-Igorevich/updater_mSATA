# Dockerfile
FROM ubuntu:latest

# Установка необходимых пакетов
RUN apt-get update && \
    apt-get install -y openssh-server && \
    mkdir -p /var/run/sshd  # Используем -p, чтобы не создавать папку, если она уже существует

# Установка пароля root
RUN echo 'root:password' | chpasswd

# Разрешение подключения root по SSH
RUN sed -i 's/^#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config

# Открываем порт SSH
EXPOSE 22

# Запуск SSH-сервера
CMD ["/usr/sbin/sshd", "-D"]
