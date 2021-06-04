# Import socket module 
import socket             
import json
from threading import Thread
  
# Create message dictionary object
message = { 'type' : '', 'data' : '', 'body' : ''}
# Create a socket object 
s = socket.socket()           
# Define the port on which you want to connect 
port = 12345                
connected = False

def client_communications():
  instr = """Welcome to Cyrus's IRC Chat Client Application\n
        -----------------------------------------\n
        Below are the choices you can make\n
        c = connect to server\n
        r = create a room\n
        l = list all rooms\n
        j = join a room\n
        e = leave a room\n
        m = list members of a room\n
        s = send message to a room\n
        d = disconnect from server\n 
        i = list instructions again\n"""
  print(instr)
  
  while True:
    choice = raw_input()
    if choice == 'c':
        # connect to the server on local computer 
        s.connect(('0.0.0.0', port)) 
        print("Socket succesfully connected to server")
        connected = True
        client_msg_sniffer_thread = Thread(target = client_msg_sniffer, name = 'client-msg-sniff-thread')
        client_msg_sniffer_thread.start()
    elif choice == 'r':
        # client creating a room
        message['type'] = 'CREATE_ROOM'
        message['data'] = raw_input("Enter a room name: ")
        s.send(json.dumps(message).encode('utf-8'))
    elif choice == 'l':
        # list all rooms
        message['type'] = 'LIST_ROOMS'
        s.send(json.dumps(message).encode('utf-8'))
        print(s.recv(1024))
    elif choice == 'j':
        # join a room
        message['type'] = 'JOIN_ROOM'
        message['data'] = raw_input("Enter a room name: ")
        s.send(json.dumps(message).encode('utf-8'))
    elif choice == 'e':
        # leave a room
        message['type'] = 'LEAVE_ROOM'
        message['data'] = raw_input("Enter a room name: ")
        s.send(json.dumps(message).encode('utf-8'))
    elif choice == 'm':
        # list members of a room
        message['type'] = 'LIST_MEMBERS'
        message['data'] = raw_input("Enter a room name: ")
        s.send(json.dumps(message).encode('utf-8'))
        print(s.recv(1024))
    elif choice == 's':
        # send message to a room
        message['type'] = 'SEND_MESSAGE'
        message['data'] = raw_input("Enter a room name: ")
        message['body'] = raw_input("Enter a message: ")
        s.send(json.dumps(message).encode('utf-8'))
    elif choice == 'd':
        # disconnect from server
        message['type'] = 'DISCONNECT'
        #message['data'] = address?
        s.send(json.dumps(message).encode('utf-8'))
        connected = False
        s.close()
        print("Socket successfully disconnected from server")
    elif choice == 'i':
        print(instr)
    else:
        print("Invalid choice, enter 'i' to see the list of instructions again")
  
def client_msg_sniffer():
  while connected:
    print(s.recv(1024))
  

def main():
  client_comm_thread = Thread(target = client_communications, name = 'client-comm-thread')
  client_comm_thread.start()

if __name__ == "__main__":
    main()
