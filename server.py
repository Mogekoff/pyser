import socket
import os

ip = '127.0.0.1'
port = 80
workers = 128
html_404 = "html/error/404.html"
html_403 = "html/error/403.html"
html_root = "html"
html_index = "index.html"
log_error = "log/error.log"
log_access = "log/access.log"

hdr_http = 'HTTP/1.1 '
hdr_ok = '200 OK\r\n'
hdr_404 = '404 Not Found\r\n'
hdr_403 = '403 Forbidden\r\n'
hdr_contype = 'Content-Type: text/html; charset=utf-8\r\n\r\n'

server = ''
client_socket = ''


def start_server():
    global server
    global client_socket
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((ip, port))
        server.listen(workers)
    except:
        print(f'Неудалось запустить сервер по адресу {ip}:{port}')

    print(f'Сервер запущен по адресу {ip}:{port}...')
    while True:
        try:
            client_socket, address = server.accept()
            data = client_socket.recv(1024).decode('utf-8')

            print(f'Клиент {address[0]}:{address[1]} подключился')

            #print(data)

            content = load_page(data)

            client_socket.send(content)
            client_socket.shutdown(socket.SHUT_WR)
        except KeyboardInterrupt:
            server.close()
            print('Перехвачено Ctrl+C, сервер завершает работу...')
        except FileNotFoundError:
            send_error(404)
        except PermissionError:
            send_error(403)


def load_page(request):
    path = request.split(' ')[1]
    print(f'Запрос на получение удаленного файла {ip}:{port}{path}')
    print(f'Попытка открытия локального файла {html_root}{path}',end='')
    if os.path.isdir(html_root+path):
        if path[-1]!='/':
            path = path + '/'
        print(html_index, end='')
        with open(html_root+path+html_index, 'rb') as file:
            response = file.read()
    else:
        with open(html_root + path, 'rb') as file:
            response = file.read()
    print('\n[200]\tФайл успешно прочитан')

    headers = (hdr_http + hdr_ok + hdr_contype).encode('utf-8')
    return headers + response


def send_error(error):
    if error == 404:
        with open(html_404, 'rb') as file:
            response = file.read()
        headers = (hdr_http + hdr_404 + hdr_contype).encode('utf-8')
        print('\n[404]\tФайл не найден на сервере')
    elif error == 403:
        with open(html_403, 'rb') as file:
            response = file.read()
        headers = (hdr_http + hdr_404 + hdr_contype).encode('utf-8')
        print('\n[403]\tДоступ к файлу запрещен')
    client_socket.send(headers + response)
    client_socket.shutdown(socket.SHUT_WR)


start_server()
