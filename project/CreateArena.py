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
server.bind(('0.0.0.0', 5000))  #make sure you map your mac port to 5000 
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

with open('mission.xml', 'r') as f:    
    missionXML= f.read()


#<DrawEntity x="2" y="16" z="2" type="Zombie" yaw="0" pitch="0"/> for zombie 

# try:
my_mission = MalmoPython.MissionSpec(missionXML, False)
# except RuntimeError as e:
#     print("MissionSpec validation error:", e)
#     sys.exit(1)
# my_mission = MalmoPython.MissionSpec()
my_mission_record = MalmoPython.MissionRecordSpec()

# Attempt to start a mission:
max_retries = 3
for retry in range(max_retries):
    try:
        agent_host.startMission( my_mission, my_mission_record )
        break
    except RuntimeError as e:
        if retry == max_retries - 1:
            print("Error starting mission:",e)
            exit(1)
        else:
            time.sleep(2)

# Loop until mission starts:
print("Waiting for the mission to start ", end=' ')
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:",error.text)
     

print()
print("Mission running ", end=' ')

# Loop until mission ends:
time.sleep(1)

temp = 0; 
while world_state.is_mission_running:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:",error.text)
    if temp is 0: 
        agent_host.sendCommand("move 0.2")
        time.sleep(1)  # let it rotate for ~1 second
        agent_host.sendCommand("turn 0")  # stop turning
        temp+= 1 

    #for now this simply just sends the dictionary to the client ie the mac book 
    try:
        res = obv.get_world_state(world_state)
        conn.send((json.dumps(res)+'\n').encode())
    except BrokenPipeError:
        print("Clinet Disconnected")
        break

conn.close()
server.close()
print("Server closed.")

print()
print("Mission ended")
# Mission has ended.
