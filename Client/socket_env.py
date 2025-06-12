import socket
import json
import gymnasium as gym
import numpy as np
from gymnasium import spaces
import csv

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
            shape=(25,),  
# State Space: (agentx, agenty, health, d1x, d1y, 
# d2x, d2y, d3x, d3y, d4x, d4y, d5x, d5y, d1, d2, d3, d4, d5, zx, zy, done)
            dtype=np.float32
        )
        self.c_step = 0
        self.collectedDiamonds = 0
        self.totalReward = 0
        self.numHits = 0
        self.stats = []
        self.current_state = None
        
    def reset(self, *, seed=None, **kwargs):
        """
        Reset the environment and get initial state
        """
        self.stats.append([self.c_step, self.collectedDiamonds, self.totalReward, self.numHits])

        arr = np.array(self.stats)
        np.savetxt("stats.csv", arr, delimiter=",", fmt="%s")

        self.c_step = 0
        self.collectedDiamonds = 0
        self.totalReward = 0
        self.numHits = 0

        print(f"Reset and at {self.c_step}")
        self.current_state = None
        action_dict = {"vertical": -2, "horizontal": -2} # this is to reset
        self.sock.sendall((json.dumps(action_dict) + "\n").encode())
        line = self.sock_file.readline()
        self.current_state = json.loads(line)
        
        # Convert state to numpy array
        # Adjust this based on your actual state format
        state_array = np.array(list(self.current_state.values()), dtype=np.float32)
        
        return state_array, {}


    def step(self, action):
        """
        Execute one time step within the environment
        """
        self.c_step += 1 
        # Send action to socket
        vert, horz = action
        action_dict = {"vertical": float(vert), "horizontal": float(horz)}
        self.sock.sendall((json.dumps(action_dict) + "\n").encode())
        oldX = self.current_state.get("agentx")
        oldY = self.current_state.get("agenty")
        # Get next state from socket
        line = self.sock_file.readline()
        next_state = json.loads(line)

        # Convert state to numpy array
        state_array = np.array(list(next_state.values()), dtype=np.float32)

        # Reward calculation
        reward = 0
        done = next_state.get("done", False)

        # Current and previous diamond collection
        collected = sum(next_state.get(f"d{i}", 0) for i in range(1, 6))
        prev_collected = sum(self.current_state.get(f"d{i}", 0) for i in range(1, 6))
        agentx = next_state.get("agentx")
        agenty = next_state.get("agenty")
        xmin = -10
        xmax = 10
        zmin = -10
        zmax = 10
        def _euclidean(x1, y1, x2, y2):
            return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        corner_dist = min(_euclidean(agentx, agenty, xmin, zmin), _euclidean(agentx, agenty, xmax, zmin), _euclidean(agentx, agenty, xmin, zmax), _euclidean(agentx, agenty, xmax, zmax))
# whenever the agent is closer than 2 units to a wall, penalize:
        if corner_dist < 2.0:
            reward -= (2.0 - corner_dist) * 300
            
        # Health change
        new_health = next_state.get("health", 0)
        old_health = self.current_state.get("health", 0)
        health_loss = old_health - new_health
        if health_loss > 0:
            self.numHits += 1
            reward -= 200 
        if new_health <= 0 or (done==True and collected < 5):
            done = True
            reward -= 3000
        reward += _euclidean(oldX, oldY, next_state.get("agentx"), next_state.get("agenty"))*15
        # Diamond collection reward
        if collected > prev_collected:
            reward += 6200 - self.c_step*25
        if collected == 5:
            reward += 25000 - self.c_step*50
            done = True
        self.collectedDiamonds = max(collected, self.collectedDiamonds)
        self.totalReward += reward
        # Distance shaping
        




        # Penalize being close to zombie
        # zx = next_state.get("zx")
        # zy = next_state.get("zy")
        # if zx is not None and zy is not None:
        #     zombie_dist = _euclidean(agentx, agenty, zx, zy)
        #     if zombie_dist < 3.5:
        #         reward -= (3.5 - zombie_dist) * 20
        # Distance-based shaping toward nearest uncollected diamond
        # diamond_locs = [
        #     (next_state.get(f"d{i}x", 0.0), next_state.get(f"d{i}y", 0.0)) for i in range(1, 6)
        # ]
        # collected_flags = [next_state.get(f"d{i}", 0) for i in range(1, 6)]

        # List of uncollected diamond coordinates
        # uncollected = [pos for pos, collected in zip(diamond_locs, collected_flags) if collected == 0]

        # if uncollected:
        #     nearest_dist = min(_euclidean(agentx, agenty, dx, dy) for dx, dy in uncollected)
        #     reward += max(0, (10 - nearest_dist)) * 2  # up to +20 reward

        # Update current state
        self.current_state = next_state


        if reward:
            print(f"{self.c_step} received feedback reward = {reward}")

        return state_array, reward, done, False, {}

    def close(self):
        action_dict = {"vertical": 2, "horizontal": 2}
        self.sock.sendall((json.dumps(action_dict) + "\n").encode())
        self.sock.close()