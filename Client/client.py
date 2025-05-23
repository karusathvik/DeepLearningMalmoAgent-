
import socket
import json

sock = socket.socket()
sock.connect(("localhost", 59933))  # Insert the port that you are using on your mac here 
sock_file = sock.makefile("r")      

try:
    for line in sock_file:
        obs_dict = json.loads(line)
        print(json.dumps(obs_dict))
except KeyboardInterrupt:
    print("Halted")
finally:
    sock.close()

print("Completed")
