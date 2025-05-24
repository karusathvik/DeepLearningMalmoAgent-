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
        # You'll need to adjust these based on your actual state and action spaces
        self.action_space = spaces.Discrete(4)  # Example: 4 discrete actions
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(10,),  # Example: 10-dimensional state space
            dtype=np.float32
        )
        
        self.current_state = None
        
    def reset(self):
        """
        Reset the environment and get initial state
        """
        # Read initial state from socket
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
        action_dict = {"action": int(action)}
        self.sock.sendall((json.dumps(action_dict) + "\n").encode())
        
        # Get next state from socket
        line = self.sock_file.readline()
        next_state = json.loads(line)
        
        # Convert state to numpy array
        state_array = np.array(list(next_state.values()), dtype=np.float32)
        
        # Get reward and done flag from state
        # Adjust this based on your actual state format
        reward = next_state.get("reward", 0.0)
        done = next_state.get("done", False)
        
        # Store current state
        self.current_state = next_state
        
        return state_array, reward, done, {}
    
    def close(self):
        """
        Clean up resources
        """
        self.sock.close()
        
    def render(self, mode='human'):
        """
        Optional: Implement if you want to visualize the environment
        """
        pass 