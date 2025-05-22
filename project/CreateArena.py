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
    
missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            
              <About>
                <Summary>Hello world!</Summary>
              </About>
              
            <ServerSection>
              <ServerInitialConditions>
                <Time>
                    <StartTime>13000</StartTime>
                    <AllowPassageOfTime>false</AllowPassageOfTime>
                </Time>
                <Weather>clear</Weather>
              </ServerInitialConditions>
              <ServerHandlers>
                  <FlatWorldGenerator generatorString="3;7,20*1;1;"/>
       
                  <DrawingDecorator>
                      <DrawCuboid x1="-10" y1="15" z1="-10" x2=" 10" y2="58" z2=" 10" type="air"/>
                      <DrawCuboid x1="-10" y1="20" z1="-10" x2=" 10" y2="21" z2=" 10" type="glass"/>
                      <DrawCuboid x1="-10" y1="14" z1="-10" x2=" 10" y2="15" z2=" 10" type="glowstone"/>
                      <DrawItem x=" 3" y="16" z="-9" type="diamond"/>
                      <DrawItem x="-6" y="16" z=" 5" type="diamond"/>
                      <DrawItem x="-7" y="16" z=" 2" type="diamond"/>
                      <DrawItem x=" 1" y="16" z=" 8" type="diamond"/>
                      <DrawItem x=" 9" y="16" z="-6" type="diamond"/>
                      <DrawCuboid x1="-10" y1="14" z1="-10" x2=" 10" y2="15" z2=" 10" type="glowstone"/>
                      <DrawEntity x="2" y="16" z="2" type="Zombie" yaw="0" pitch="0"/>
                  </DrawingDecorator>
                  <ServerQuitFromTimeUp timeLimitMs="30000"/>
                  <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
              </ServerSection>
              <AgentSection mode="Survival">
                <Name>MalmoTutorialBot</Name>
                <AgentStart>
                    <Placement x="0.5" y="17.0" z="0.5" yaw="90"/>
                    <Inventory>
                        <InventoryItem slot="8" type="diamond_pickaxe"/>
                    </Inventory>
                </AgentStart>
                
                <AgentHandlers>
                <ObservationFromNearbyEntities>
                  <Range name="entities" xrange="5" yrange="3" zrange="5"/>
                </ObservationFromNearbyEntities>
                  <ObservationFromFullStats/>
                  <ContinuousMovementCommands turnSpeedDegs="180"/>
                  <InventoryCommands/>
                </AgentHandlers>
  
              </AgentSection>
            </Mission>'''


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

    print(obv.get_world_state(world_state))


print()
print("Mission ended")
# Mission has ended.
