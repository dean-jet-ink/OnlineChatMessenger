from typing import Tuple
from threading import Thread

from my_socket.inet_dgram_socket import InetDgramSocket

class ChatClient:
    def __init__(self, socket: InetDgramSocket, room_address: Tuple[str, int], name: str):
        self.__socket = socket
        self.__room_address = room_address
        self.__name = name
        self.__exit_flag = False

    def __recv_data(self):
        while not self.__exit_flag:
            try:
                message, _ = self.__socket.recvfrom()
                print(message.decode())
            except Exception as e:
                print(e)

    def __send_data(self):
        while True:
            message = input("")

            if(message == "exit"):
                self.__exit_flag = True
                self.__socket.sendto(f"{self.__name} has exited", self.__room_address)
                break
            else:
                self.__socket.sendto(f"{self.__name}: {message}", self.__room_address)

    def start(self):
        self.__socket._create_socket()
        self.__socket._bind()

        thread = Thread(target=self.__recv_data)
        thread.start()

        self.__socket.sendto(f"SIGN UP:{self.__name}", self.__room_address)

        self.__send_data()