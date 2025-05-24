from stable_baselines3 import PPO
from socket_env import SocketEnv

# Create the environment
env = SocketEnv()

# Initialize the agent
model = PPO("MlpPolicy", env, verbose=1)

# Train the agent
model.learn(total_timesteps=100000)

# Save the trained agent
model.save("socket_agent")

# Test the trained agent
obs = env.reset()
for i in range(1000):
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    if dones:
        obs = env.reset()

# Close the environment
env.close() 