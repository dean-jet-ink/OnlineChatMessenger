import socket

from my_socket.inet_stream_socket import InetStreamServerSocket
from chat.chat_handler import ChatServerHandler

def main():
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    print(f"address: {ip_address}")

    sock = InetStreamServerSocket(ip_address, 9000)
    chat_handler = ChatServerHandler(sock, ip_address)
    chat_handler.start()

if __name__ == "__main__":
    main()