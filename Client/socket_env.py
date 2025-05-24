import socket
import json
import gym
import numpy as np
from gym import spaces

class SocketEnv(gym.Env):
    """
    Custom Environment for Stable Baselines that interfaces with a socket-based black box system
    """
    def __init__(self, host="localhost", port=59933):
        super(SocketEnv, self).__init__()
        
        # Initialize socket connection
        self.sock = socket.socket()
        self.sock.connect((host, port))
        self.sock_file = self.sock.makefile("r")
        
        # Define action and observation space
        self.action_space = spaces.Box(
            low=np.array([-1.0, -1.0], dtype=np.float32),
            high=np.array([ 1.0,  1.0], dtype=np.float32),
            dtype=np.float32
        )
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(21,),  
# State Space: (agentx, agenty, health, d1x, d1y, 
# d2x, d2y, d3x, d3y, d4x, d4y, d5x, d5y, d1, d2, d3, d4, d5, zx, zy, done)
            dtype=np.float32
        )
        
        self.current_state = None
        
    def reset(self):
        """
        Reset the environment and get initial state
        """

        action_dict = {"vertical": -2, "horizontal": -2} # this is to reset
        self.sock.sendall((json.dumps(action_dict) + "\n").encode())
        line = self.sock_file.readline()
        self.current_state = json.loads(line)
        
        # Convert state to numpy array
        # Adjust this based on your actual state format
        state_array = np.array(list(self.current_state.values()), dtype=np.float32)
        return state_array
    
    def step(self, action):
        """
        Execute one time step within the environment
        """
        # Send action to socket
        vert, horz = action
        action_dict = {"vertical": int(vert), "horizontal": int(horz)}
        self.sock.sendall((json.dumps(action_dict) + "\n").encode())
        
        # Get next state from socket
        line = self.sock_file.readline()
        next_state = json.loads(line)
        
        # Convert state to numpy array
        state_array = np.array(list(next_state.values()), dtype=np.float32)
        
        # Get reward and done flag from state
        total_collected = next_state.get("d1") + next_state.get("d2") +next_state.get("d3") +next_state.get("d4")+ next_state.get("d5")
        already_collected = self.current_state.get("d1") + self.current_state.get("d2") + self.current_state.get("d3") + self.current_state.get("d4") + self.current_state.get("d5")
        new_health = next_state.get("health")
        old_health = self.current_state.get("health")
        
        # reward = 5*(total_collected - already_collected) +2*(new_health - old_health) - 0.01
        reward = 2*(new_health - old_health) - 0.01
        done = next_state.get("done", False)
        if(total_collected == 5):
            done = True
            reward = reward + 100
        # Store current state
        self.current_state = next_state
        
        return state_array, reward, done, {}
    
    def close(self):
        action_dict = {"vertical": 2, "horizontal": 2}
        self.sock.sendall((json.dumps(action_dict) + "\n").encode())
        self.sock.close()