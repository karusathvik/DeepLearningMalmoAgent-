# from stable_baselines3.common.evaluation import evaluate_policy
# from socket_env import SocketEnv
# from stable_baselines3 import PPO, SAC
from socket_env import SocketEnv
from stable_baselines3.common.env_checker import check_env
env = SocketEnv(host="localhost", port=5001)
check_env(env)

# eval_env = SocketEnv(host="localhost", port=5001)
# model = SAC.load("SACModels/socket_agent_final_34816.zip", env=eval_env)
# model.learn(total_timesteps=5000, reset_num_timesteps=False)
# mean_rew, std_rew = evaluate_policy(model, eval_env,
#                                     n_eval_episodes=10,
#                                     deterministic=True)


# from stable_baselines3 import PPO, SAC
# from stable_baselines3.common.vec_env import DummyVecEnv
# from socket_env import SocketEnv
# import numpy as np

# # Re-create the environment (must match training)
# env = DummyVecEnv([lambda: SocketEnv(port=5001)])

# # Load the trained model
# model = SAC.load("SACModels/socket_agent_32768.zip", env=env)

# # 4) Run a few full episodes
# n_episodes = 10
# episode_rewards = []
# for ep in range(n_episodes):
#     obs = env.reset()                # get initial obs
#     done = False
#     total_reward = 0.0
#     while not done:
#         # deterministic=True usistic=True)es the mean action instead of sampling
#         action, _ = model.predict(obs, deterministic=True)
#         obs, reward, done, _ = env.step(action)
#         total_reward += float(reward)
#     episode_rewards.append(total_reward)
#     print(f"Episode {ep+1}: return = {total_reward:.2f}")

# print(f"Average return over {n_episodes} episodes: {np.mean(episode_rewards):.2f}")

# env.close()
