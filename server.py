# first of all import the socket library 
import socket             
import json
from threading import Thread
from Queue import Queue

rooms = {}
client_inbox = {}
client_terminated = {}
message = {'type' : '', 'data' : ''}

# function to create threads
def client_connections():
  try:
    s = socket.socket()         
    print ("Socket successfully created")
    port = 12345                
    s.bind(('', port))         
    print ("socket binded to %s" %(port)) 
    s.listen(5)     
    print ("socket is listening")            

    while True:
      c, tmp_addr = s.accept()
      addr = ''.join(str(tmp_addr))
      print('Got connection from ', tmp_addr)
      # initialize each clients mailbox after creation
      client_inbox[addr] = Queue()
      # initialize each clients terminated status to false
      client_terminated[addr] = False
      client_comm_thread = Thread(target = client_communications, args = (c, tmp_addr), name='client-comm-thread')
      client_comm_thread.start()
      client_msg_sniffer_thread = Thread(target = client_msg_sniffer, args = (c, tmp_addr), name='client-msg-sniff-thread')
      client_msg_sniffer_thread.start()
  except (socket.error, socket.gaierror, ValueError) as e:
    print(e)
    return


def client_msg_sniffer(c, tmp_addr):
  addr = ''.join(str(tmp_addr))
  while client_terminated[addr] == False:
    msg = client_inbox[addr].get()
    try:
      c.send(msg)
    except (socket.error, socket.gaierror, ValueError) as e:
      print(e)
      client_terminated[addr] = True
      return

def client_communications(c, tmp_addr):
  try:
    addr = ''.join(str(tmp_addr))
    client_msg = json.loads(c.recv(1024))
    while (client_msg['type'] != 'DISCONNECT') and (client_terminated[addr] == False):
      if client_msg['type'] == 'CREATE_ROOM':
        if client_msg['data'] not in rooms:
          # Create a new room
          rooms[client_msg['data']] = []
          print("room " + client_msg['data'] + " created!")
          c.send("room " + client_msg['data'] + " created!")
        else:
          # Room already exists
          c.send("Failed to create room \"" + client_msg['data'] + "\", that room already exists\n")
      elif client_msg['type'] == 'LIST_ROOMS':
        # Return list of all rooms
        rooms_list = 'List of rooms\n---------------\n'
        for key in rooms:
          rooms_list += key + '\n'
        c.send(rooms_list)
      elif client_msg['type'] == 'JOIN_ROOM':
        # Room doesn't exist
        if client_msg['data'] not in rooms:
          c.send("Failed to join room \"" + client_msg['data'] + "\", that room doesn't exist\n") 
        # Client already in room
        elif addr in rooms[client_msg['data']]:
          c.send("Failed to join room \"" + client_msg['data'] + "\", you're already in that room!\n") 
        else:
          # add client user/addr to room
          rooms[client_msg['data']].append(addr)
          print("Client " + addr + "successfully joined room " + client_msg['data'])
          c.send("You've successfully joined room " + client_msg['data'])
      elif client_msg['type'] == 'LEAVE_ROOM':
        # Room doesn't exist
        if client_msg['data'] not in rooms:
          c.send("Failed to leave room \"" + client_msg['data'] + "\", that room doesn't exist\n") 
        # Client not in room
        elif addr not in rooms[client_msg['data']]:
          c.send("Failed to leave room \"" + client_msg['data'] + "\", you weren't in that room!\n") 
        else:
          rooms[client_msg['data']].remove(addr)
          print("Client " + addr + "successfully left room " + client_msg['data'])
          c.send("You've successfully left room " + client_msg['data'])
      elif client_msg['type'] == 'LIST_MEMBERS':
        # Room doesn't exist
        if client_msg['data'] not in rooms:
          c.send("Failed to list members of room \"" + client_msg['data'] + "\", that room doesn't exist\n") 
        else:
          room = client_msg['data']
          members_list = 'Members of room ' + room + '\n---------------------\n'
          for client_addr in rooms[room]:
            members_list += client_addr + '\n'
          c.send(members_list)
      elif client_msg['type'] == 'SEND_MESSAGE':
        # Room doesn't exist
        if client_msg['data'] not in rooms:
          c.send("Failed to send message to room \"" + client_msg['data'] + "\", that room doesn't exist\n") 
        # Client not in room
        elif addr not in rooms[client_msg['data']]:
          c.send("Failed to send message to room \"" + client_msg['data'] + "\", you weren't in that room!\n") 
        else:
          room = client_msg['data']
          for client_addr in rooms[room]:
            client_inbox[client_addr].put('[' + room + '] ' + addr + ': ' + client_msg['body'])
      client_msg = json.loads(c.recv(1024))

    print("client " + addr + " closed connection")
    c.send("You've successfully closed connection from you to the server, exiting Client IRC Application")

    # Close the connection with the client 
    c.close() 
  except (socket.error, socket.gaierror, ValueError) as e:
    print(e)
    client_terminated[addr] = True
    return

def main():
  connection_thread = Thread(target = client_connections, name='connection-thread')
  connection_thread.start()

if __name__ == "__main__":
    main()
