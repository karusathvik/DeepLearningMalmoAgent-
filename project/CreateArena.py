from __future__ import print_function
# ------------------------------------------------------------------------------------------------
# Copyright (c) 2016 Microsoft Corporation
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------------------------

# Tutorial sample #1: Run simple mission

import observe as obv
from builtins import range
# import MalmoPython
from malmo import MalmoPython
import os
import sys
import time
import socket
import json

server = socket.socket()
host = '0.0.0.0'
port = 5001
server.bind((host, port))  
server.listen(1)
print("Waiting for host connection on port {}".format(port))
conn, addr = server.accept()
print("Connected by", addr)

if sys.version_info[0] == 2:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
else:
    import functools
    print = functools.partial(print, flush=True)

agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print('ERROR:',e)
    print(agent_host.getUsage())
    exit(1)
if agent_host.receivedArgument("help"):
    print(agent_host.getUsage())
    exit(0)
    
    
with open ('mission.xml', 'r') as f:
    missionXML= f.read() 


max_retries = 3
run = 0

end = False 
reset = False 
firstRun = True


while end == False:
    data = json.loads(conn.recv(1024).decode().strip())
    print("received {}".format(data))
    if data["vertical"] == -2 and data["horizontal"] == -2:
        reset = True
    
    if reset:
        reset = False
        run += 1
        print("\nStarting Episode {}".format(run))
        if firstRun == False and world_state.is_mission_running:              
            agent_host.sendCommand("quit")         
            # Wait until the mission actually terminates
            world_state = agent_host.getWorldState()  
            while world_state.is_mission_running:         
                time.sleep(0.1)                        
                world_state = agent_host.getWorldState()
        my_mission = MalmoPython.MissionSpec(missionXML, False)
        my_mission_record = MalmoPython.MissionRecordSpec()

        firstRun = False
        for retry in range(max_retries):
            try:
                agent_host.startMission(my_mission, my_mission_record)
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print("Error starting mission:", e)
                    conn.close()
                    server.close()
                    sys.exit(1)
                else:
                    time.sleep(2)


        world_state = agent_host.getWorldState()
        print("Waiting for the mission to start ", end=' ')
        while not world_state.has_mission_begun:
            print(".", end="")
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print("Error:", error.text)
       
        print("\nMission running", end=' ')
        time.sleep(0.3)
        world_state = agent_host.getWorldState()
        try:
            res = obv.get_world_state(world_state)
            conn.send((json.dumps(res) + '\n').encode())
            print("sent {}".format(res))
        except BrokenPipeError:
            print("Client Disconnected")
            conn.close()
            server.close()
            sys.exit(0)     
    elif data["vertical"] == 2 and data["horizontal"] == 2:
        end = True
    
    else:
        print(".", end="")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        
        h = data["horizontal"]
        v = data["vertical"]
        agent_host.sendCommand(obv.create_command("move", v))
        agent_host.sendCommand(obv.create_command("strafe", h))
    
                
        try:
            res = obv.get_world_state(world_state)
            conn.send((json.dumps(res) + '\n').encode())
            print("sent {}".format(res))
        except BrokenPipeError:
            print("Client Disconnected")
            conn.close()
            server.close()
            sys.exit(0)

    time.sleep(0.5)
conn.close()
server.close()
print("Server closed.")

print()
print("Mission ended")
# Mission has ended.