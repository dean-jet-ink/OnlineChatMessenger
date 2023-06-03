import socket
from typing import Tuple

from my_socket.socket_base import SocketBase

class InetDgramSocket(SocketBase):
  def __init__(self, address: str, port: int, recv_buffer: int = 4096, data_length_bytes: int = 4):
    super().__init__(socket.AF_INET, socket.SOCK_DGRAM, recv_buffer, data_length_bytes)
    self.__address = address
    self.__port = port

  def _bind(self):
    print(f"Starting up on {self.__address}:{self.__port}")
    self._socket.bind((self.__address, self.__port))

  def recvfrom(self) -> Tuple[bytes, Tuple[str, int]]:
    return self._socket.recvfrom(self._recv_buffer)
  
  def sendto(self, message: str, address: Tuple[str, int]):
    self._socket.sendto(message.encode(), address)