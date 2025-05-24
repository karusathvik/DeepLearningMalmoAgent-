import socket
import json
import random 

def pick_random_action():
    return random.randrange(0, 4); 


sock = socket.socket()
sock.connect(("localhost", 59933))  # Insert the port that you are using on your mac here 
sock_file = sock.makefile("r")      


#indicate that it started 

sock.send((str(4) + '\n').encode())
try:
    while True:
        action = pick_random_action()
        sock.send((str(action) + '\n').encode()) 
        line = sock_file.readline()               
        if not line:
            break
        obs_dict = json.loads(line)
        print(json.dumps(obs_dict))

except KeyboardInterrupt:
    print("Halted")
    sock.send((str(5) + '\n').encode())
    #ie send it ended 
finally:
    sock.close()

print("Completed")