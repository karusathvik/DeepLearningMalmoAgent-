from stable_baselines3 import PPO, SAC
from socket_env import SocketEnv

# Create the environment
env = SocketEnv(port=5001)

# Initialize the agent
# model = PPO(
#     policy="MlpPolicy",
#     env=env,
#     learning_rate=1e-3,
#     n_steps=512,
#     batch_size=32,
#     n_epochs=10,
#     gamma=0.99,
#     gae_lambda=0.95,
#     clip_range=0.2,
#     clip_range_vf=None,
#     ent_coef=0.0,
#     vf_coef=0.5,
#     max_grad_norm=0.5,
#     verbose=1,
# )

model = SAC(
    "MlpPolicy", env,
    learning_rate=3e-4,
    buffer_size=50_000,    # replay buffer
    learning_starts=1000,  # collect some data before learning
    batch_size=64,
    tau=0.005,             # target smoothing coefficient
    gamma=0.99,
    ent_coef="auto",       # auto-tune entropy weight
    verbose=1
)

# Number of timesteps between saves
TIMESTEPS_PER_SAVE = 1024

try:
    total_timesteps = 0
    while True:
        model.learn(total_timesteps=TIMESTEPS_PER_SAVE, reset_num_timesteps=False)
        total_timesteps += TIMESTEPS_PER_SAVE
        print(f"Trained {total_timesteps} timesteps — saving model...")
        # Save with the current total timesteps in the filename
        model.save(f"socket_agent")
except KeyboardInterrupt:
    print("Training interrupted by user. Saving final model...")
    model.save(f"socket_agent_final_{total_timesteps}")
finally:
    env.close()

