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
terminate = False
connected = True

def client_comm():
  instr = """Welcome to Cyrus's IRC Chat Client Application\n
        -----------------------------------------\n
        Below are the choices you can make\n
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
    try:
      choice = raw_input()
      if terminate:
          return
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
        global connected
        connected = False
        #s.close()
        #print("You've successfully disconnected from the IRC Server, exiting the Client application")
        return
      elif choice == 'i':
        print(instr)
      else:
        print("Invalid choice, enter 'i' to see the list of instructions again")
    except (socket.error, socket.gaierror) as e:
      print(e)
      global connected
      connected = False
      return
  
def client_msg_sniff():
  while True:
      try:
        msg = s.recv(1024)
        print(msg)
        if connected == False or len(msg) == 0:
          s.close()
          return
      except (socket.error, socket.gaierror) as e:
        print(e)
        global terminate
        terminate = True
        return
  

def main():
  # connect to the server on local computer 
  s.connect(('0.0.0.0', port)) 
  print("You've succesfully connected to the IRC Server")
  client_msg_sniff_thread = Thread(target = client_msg_sniff, name = 'client-msg-sniff-thread')
  client_msg_sniff_thread.start()
  client_comm_thread = Thread(target = client_comm, name = 'client-comm-thread')
  client_comm_thread.start()

if __name__ == "__main__":
    main()
