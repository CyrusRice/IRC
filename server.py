# first of all import the socket library 
import socket             
import json
from threading import Thread

rooms = {}
message = {'type' : '', 'data' : ''}

# function to create threads
def client_connections():
  s = socket.socket()         
  print ("Socket successfully created")
  port = 12345                
  s.bind(('', port))         
  print ("socket binded to %s" %(port)) 
  s.listen(5)     
  print ("socket is listening")            

  while True:
    c, tmp_addr = s.accept()
    #addr = ''.join(str(tmp_addr))
    print('Got connection from', tmp_addr)
    client_thread = Thread(target = client_communications, args = (c, tmp_addr), name='client-thread')
    client_thread.start()

def client_communications(c, tmp_addr):
  addr = ''.join(str(tmp_addr))
  client_msg = json.loads(c.recv(1024))
  while client_msg['type'] != 'DISCONNECT':
    if client_msg['type'] == 'CREATE_ROOM':
      # Create a new room
      rooms[client_msg['data']] = []
      print("room " + client_msg['data'] + " created!")
    elif client_msg['type'] == 'LIST_ROOMS':
      # Return list of all rooms
      rooms_list = 'List of rooms\n---------------\n'
      for key in rooms:
        rooms_list += key + '\n'
      c.send(rooms_list)
    elif client_msg['type'] == 'JOIN_ROOM':
      # add client user/addr to room
      rooms[client_msg['data']].append(addr)
      print("Client " + addr + "successfully joined room " + client_msg['data'])
    elif client_msg['type'] == 'LEAVE_ROOM':
      rooms[client_msg['data']].remove(addr)
      print("Client " + addr + "successfully left room " + client_msg['data'])
    elif client_msg['type'] == 'LIST_MEMBERS':
      room = client_msg['data']
      members_list = 'Members of room ' + room + '\n---------------------\n'
      for client_addr in rooms[room]:
        members_list += client_addr + '\n'
      c.send(members_list)
    #elif client_msg['type'] == 'SEND_MESSAGE':
      #room = client_msg['data']
      #for client_addr in rooms[room]:
        #if client_addr != addr:
          # stuff
    client_msg = json.loads(c.recv(1024))

  # send a thank you message to the client. 
  #c.send("thank you!") 
  print("client " + addr + " closed connection")

  # Close the connection with the client 
  c.close() 

def main():
  connection_thread = Thread(target = client_connections, name='connection-thread')
  connection_thread.start()

if __name__ == "__main__":
    main()
