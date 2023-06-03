import json
from typing import Dict, Tuple, List
from random import Random

from my_socket.inet_stream_socket import InetStreamServerSocket, InetStreamClientSocket
from my_socket.inet_dgram_socket import InetDgramSocket
from chat_room import ChatRoom
from chat_client import ChatClient

# operations
# 1: create_chat_room  2: join_chat_room  3: get_room_names
class ChatServerHandler:
  def __init__(self, socket: InetStreamServerSocket, address: str):
    self.__socket = socket
    self.__address = address
    self.__chatrooms: Dict[str, Tuple[str, int]] = {}
  
  def __create_message_json(self, room_address: Tuple[str, int], error_message: str) -> str:
    json_data = {
      "room_address": room_address,
      "error_message": error_message
    }

    return json.dumps(json_data)

  def __create_chat_room(self, room_name: str) -> str:
    room_port = Random().randint(8000, 9000)
    chat_socket = InetDgramSocket(self.__address, room_port)
    chat_room = ChatRoom(chat_socket, room_name, (self.__address, room_port))

    room_address = chat_room.get_room_address()
    self.__chatrooms[chat_room.get_name()] = room_address

    chat_room.start()

    return self.__create_message_json(room_address, "")

  def __join_chat_room(self, room_name: str) -> str:
    if not room_name in self.__chatrooms.keys():
      return self.__create_message_json(("", 0), "room is not found")
    else:
      room_address = self.__chatrooms[room_name]
      return self.__create_message_json(room_address, "")
  
  def __get_room_names(self):
    room_names = list(self.__chatrooms.keys())
    print(f"room names: {room_names}")
    error_message = "" if len(room_names) != 0 else "Chat Room is not established"

    json_data = {
      "room_names": room_names,
      "error_message": error_message
    }

    return json.dumps(json_data)

  def __dispatch(self, message: str) -> str:
    message_json = json.loads(message)
    operation = message_json["operation"]
    room_name = message_json["room_name"]

    if operation == 1:
      return self.__create_chat_room(room_name)
    elif operation == 2:
      return self.__join_chat_room(room_name)
    elif operation == 3:
      return self.__get_room_names()

  def start(self):
    self.__socket.communicate(5, self.__dispatch)


class ChatClientHandler:
  def __init__(self, socket: InetStreamClientSocket, address: str):
    self.__socket = socket
    self.__address = address
  
  def __create_message_json(self, operation: int, room_name: str) -> str:
    json_data = {
      "operation":  operation,
      "room_name": room_name
    }

    return json.dumps(json_data)

  def start(self):
    print("Please choose an operation from the following")
    command = int(input("1: Create Chat Room  2: Join Chat Room\n"))
    command = int(command)

    if command == 1:
      self.__create_chat_room()
    elif command == 2:
      self.__join_chat_room()

  def __create_chat_room(self):
    room_name = input("Please enter the Chat Room name\n")
    name = input("Please enter your name\n")

    message = self.__create_message_json(1, room_name)
    response = self.__socket.communicate(message)
    response_json = json.loads(response)

    if response_json["error_message"] != "":
      print(response_json["error_message"])
      self.start()
      return

    chat_socket = InetDgramSocket(self.__address, 9999)
    chat_client = ChatClient(chat_socket, tuple(response_json["room_address"]), name)
    chat_client.start()

  def __join_chat_room(self):
    message = self.__create_message_json(3, "")
    print(type(message))
    response = self.__socket.communicate(message)
    response_json = json.loads(response)

    if response_json["error_message"] != "":
      print(response_json["error_message"])
      self.start()
      return

    room_names: List[str] = response_json["room_names"]
    index = 1
    print("Please choose Chat Room from the following")
    for name in room_names:
      print(f"{index}: {name}")
      index += 1

    room_name = input("")
    message = self.__create_message_json(2, room_name)
    print(type(message))
    response = self.__socket.communicate(message)
    response_json = json.loads(response)

    if response_json["error_message"] != "":
      print(response_json["error_message"])
      self.start()
      return
    
    name = input("Please enter your name\n")
    
    chat_socket = InetDgramSocket(self.__address, 9999)
    chat_client = ChatClient(chat_socket, tuple(response_json["room_address"]), name)
    chat_client.start()