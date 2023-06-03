from abc import ABC
import socket

class SocketBase(ABC):
  def __init__(self, family: int, typ: int, recv_buffer: int, data_length_bytes: int):
    self._socket = None
    self.__family = family
    self.__typ = typ
    self._recv_buffer = recv_buffer
    self._data_length_bytes = data_length_bytes
      
  def _create_socket(self) -> None:
    self._socket = socket.socket(self.__family, self.__typ)

  def _close(self):
    try:
      self._socket.shutdown(socket.SHUT_RDWR)
      self._socket.close()
    except:
      pass

  def __del__(self):
    self._close()