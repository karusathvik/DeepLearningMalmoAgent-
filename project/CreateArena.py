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


actions = ["move 1", "move -1", "turn 1", "turn -1"]


server = socket.socket()
server.bind(('0.0.0.0', 5000))  
server.listen(1)
print("Waiting for host connection...")
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
while True:
    run += 1
    print("\nStarting Episode {}".format(run))

    data = conn.recv(1024).decode().strip() # would be from 0-3 where 4 is start, 5 is end
    #wait for the client to say start the mission 
    
    if data.isdigit() and int(data) == 5:
        break
     
    my_mission = MalmoPython.MissionSpec(missionXML, False)
    my_mission_record = MalmoPython.MissionRecordSpec()
    
    
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
    time.sleep(1)

    while world_state.is_mission_running:
        print(".", end="")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()

        
        
        data = conn.recv(1024).decode().strip()
        if data.isdigit():
            idx = int(data)
            if 0 <= idx < len(actions):
                action = actions[idx]
                agent_host.sendCommand(action)
                
        try:
            res = obv.get_world_state(world_state)
            conn.send((json.dumps(res) + '\n').encode())
        except BrokenPipeError:
            print("Client Disconnected")
            conn.close()
            server.close()
            sys.exit(0)

    print("\nEpisode complete.")
    time.sleep(2) 


conn.close()
server.close()
print("Server closed.")

print()
print("Mission ended")
# Mission has ended.