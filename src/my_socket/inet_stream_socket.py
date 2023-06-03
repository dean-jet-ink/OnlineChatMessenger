import sys
import socket
from abc import ABC
from typing import Callable
from threading import Thread

from my_socket.socket_base import SocketBase

class InetStreamSocketBase(SocketBase, ABC):
    def __init__(self, recv_buffer: int, data_length_bytes: int):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM, recv_buffer, data_length_bytes)

    def _add_header(self, data: bytes) -> bytes:
        data_length = len(data)
        header = data_length.to_bytes(self._data_length_bytes, "big")
        return header + data

    def _get_data_length(self, connection: socket.socket) -> int:
        data_length_bytes = connection.recv(self._data_length_bytes)
        data_length = int.from_bytes(data_length_bytes, "big")
        return data_length

    def _get_data(self, connection: socket.socket) -> str:
        data_length = self._get_data_length(connection)
        message_bytes = b""
        while data_length > 0:
            chunk = connection.recv(self._recv_buffer)
            if not chunk:
                raise socket.error("Connection was closed unexpectedly")
            message_bytes += chunk
            data_length -= len(chunk)
        
        return message_bytes.decode()


class InetStreamServerSocket(InetStreamSocketBase):
    def __init__(self, address: str, port: int, recv_buffer: int = 4096, data_length_bytes: int = 4):
        super().__init__(recv_buffer, data_length_bytes)
        self.__address = address
        self.__port = port

    def __listen(self, backlog: int):
        print(f"Starting up on {self.__address}:{self.__port}")
        self._socket.bind((self.__address, self.__port))
        self._socket.listen(backlog)
    
    def __recv_data(self, connection: socket.socket, callback: Callable[[str], str]):
        try:
            data = self._get_data(connection)
            response = callback(data)
            self.__send_data(response, connection)

        except ConnectionResetError as e:
            raise Exception(e)
        except BrokenPipeError as e:
            raise Exception(e)
        finally:
            connection.close()

    def __send_data(self, response: str, connection: socket.socket):
        data = self._add_header(response.encode())
        connection.send(data)
    
    def communicate(self, backlog: int, callback: Callable[[str], str] = lambda x: x):
        self._create_socket()
        self.__listen(backlog)

        while True:
            connection, _ = self._socket.accept()
            thread = Thread(target = self.__recv_data, args = (connection, callback))
            thread.start()


class InetStreamClientSocket(InetStreamSocketBase):
    def __init__(self, server_port: int, recv_buffer: int = 4096, data_length_bytes: int = 4, timeout: int = 60):
        server_address = input("Please enter the server address\n")
        super().__init__(recv_buffer, data_length_bytes)
        self.__server_address = server_address
        self.__server_port = server_port
        self.__timeout = timeout

    def __connect(self):
        try:
            print(f"Connecting to {self.__server_address}:{self.__server_port}")
            self._socket.connect((self.__server_address, self.__server_port))
        except socket.error as e:
            print(e)
            sys.exit(1)
    
    def __send_data(self, message: str):
        data = self._add_header(message.encode())
        self._socket.send(data)

    def __recv_data(self) -> str:
        try:
            self._socket.settimeout(self.__timeout)
            data = self._get_data(self._socket)
            return data
        
        except ConnectionResetError as e:
            raise Exception(e)
        except BrokenPipeError as e:
            raise Exception(e)
        except TimeoutError as e:
            raise Exception(e)
        finally:
            self._close()

    def communicate(self, message: str) -> str:
        self._create_socket()
        self.__connect()
        self.__send_data(message)
        data = self.__recv_data()

        return data