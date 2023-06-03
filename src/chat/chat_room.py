from queue import Queue
from typing import Tuple, List
from threading import Thread

from my_socket.inet_dgram_socket import InetDgramSocket

class ChatRoom:
    def __init__(self, socket: InetDgramSocket, room_name: str, address: Tuple[str, int]):
        self.__socket = socket
        self.__clients: List[Tuple[str, int]] = []
        self.__message_queue: Queue[Tuple[bytes, Tuple[str, int]]] = Queue()
        self.__room_name = room_name
        self.__address = address
        
    def __recv_data(self):
        while True:
            try:
                message, address = self.__socket.recvfrom()
                self.__message_queue.put((message, address))
            except Exception as e:
                print(e)

    def __broadcast(self):
        while True:
            while not self.__message_queue.empty():
                message, address = self.__message_queue.get()
                room_name = f"[{self.__room_name}]"

                if not address in self.__clients:
                    self.__clients.append(address)
                
                if message.decode().startswith("SIGN UP"):
                    print(f"{room_name}: {message.decode()}")
                    name = message.decode()[message.decode().index(":") + 1:]
                    message = f"{room_name}: Join {name}!!"
                elif message.decode().endswith("exited") and not ":" in message.decode():
                    message = message.decode()
                    print(message)
                else:
                    message = f"{room_name}:{message.decode()}"

                for client in self.__clients:
                    try:
                        self.__socket.sendto(message, client)
                    except Exception as e:
                        print(e)
                        self.__clients.remove(client)

    def start(self):
        self.__socket._create_socket()

        self.__socket._bind()

        recv_thread = Thread(target=self.__recv_data)
        broadcast_thread = Thread(target=self.__broadcast)
        
        recv_thread.start()
        broadcast_thread.start()

    def get_name(self) -> str:
        return self.__room_name
    
    def get_room_address(self) -> Tuple[str, int]:
        return self.__address