
from stable_baselines3 import PPO, SAC
from socket_env import SocketEnv

# Re-create the environment (must match training)
env = SocketEnv(port=5001)

# Load the trained model
model = SAC.load("COLLECTSALL_13312.zip", env=env)

# Use the model to run the agent
obs, _ = env.reset()
for _ in range(300):  # or any number of steps
    action, _ = model.predict(obs)
    obs, reward, done, _, _ = env.step(action)
    if done:
        obs, _ = env.reset()

env.close()
