import socket

from my_socket.inet_stream_socket import InetStreamClientSocket
from chat.chat_handler import ChatClientHandler

def main():
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)

    sock = InetStreamClientSocket(9000, timeout = 30)
    chat_handler = ChatClientHandler(sock, ip_address)
    chat_handler.start()

if __name__ == "__main__":
    main()