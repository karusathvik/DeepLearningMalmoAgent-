
from stable_baselines3 import PPO
from socket_env import SocketEnv

# Re-create the environment (must match training)
env = SocketEnv(port=59933)

# Load the trained model
model = PPO.load("/Users/sathvikkaruturi/MalmoProject/DeepLearningMalmoAgent-/socket_agent.zip", env=env)

# Use the model to run the agent
obs, _ = env.reset()
for _ in range(100):  # or any number of steps
    action, _ = model.predict(obs)
    obs, reward, done, _, _ = env.step(action)
    if done:
        obs, _ = env.reset()

env.close()
