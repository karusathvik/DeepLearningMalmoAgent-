from stable_baselines3 import SAC
from socket_env import SocketEnv

env = SocketEnv(port=5001)

model = SAC.load('socket_agent.zip', env=env)

for ep in range(1, 100000):
    obs, _ = env.reset()
    done = False
    total_reward = 0.0
    while not done:
        # deterministic=True picks the mean action
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, _, _ = env.step(action)
        total_reward += reward
    print(f"Episode {ep}: total_reward = {total_reward:.2f}")

env.close()