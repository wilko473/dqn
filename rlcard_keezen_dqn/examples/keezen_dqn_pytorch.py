''' An example of learning a Deep-Q Agent on Leduc Holdem
'''
import torch
import os

import rlcard
from rlcard.agents import DQNAgentPytorch as DQNAgent
from rlcard.agents import RandomAgent
from rlcard.utils import set_global_seed, tournament
from rlcard.utils import Logger

import datetime

start = datetime.datetime.now()

# Make environment
env = rlcard.make('keezen', config={'seed': 0})
eval_env = rlcard.make('keezen', config={'seed': 0})

# Set the iterations numbers and how frequently we evaluate the performance
evaluate_every = 1000
evaluate_num = 4000
episode_num = 50000

# The intial memory size
memory_init_size = 5000

# Train the agent every X steps
train_every = 1

# The paths for saving the logs and learning curves
log_dir = './experiments/keezen_dqn_torch_result_2/'

# Set a global seed
set_global_seed(0)

agent1 = DQNAgent(scope='dqn1',
                 action_num=env.action_num,
                 replay_memory_init_size=memory_init_size,
                 train_every=train_every,
                 state_shape=env.state_shape,
                 mlp_layers=[512, 512],
                 device=torch.device('cuda'))
agent2 = DQNAgent(scope='dqn2',
                 action_num=env.action_num,
                 replay_memory_init_size=memory_init_size,
                 train_every=train_every,
                 state_shape=env.state_shape,
                 mlp_layers=[512, 512],
                 device=torch.device('cuda'))
random_agent = RandomAgent(action_num=eval_env.action_num)
env.set_agents([agent1, random_agent, agent2, random_agent])
eval_env.set_agents([agent1, random_agent, agent2, random_agent])

# Init a Logger to plot the learning curve
logger = Logger(log_dir)

for episode in range(episode_num):

    # Generate data from the environment
    trajectories, _ = env.run(is_training=True)

    # Feed transitions into agent memory, and train the agent
    for ts in trajectories[0]:
        agent1.feed(ts)
    for ts in trajectories[2]:
        agent2.feed(ts)

    # Evaluate the performance. Play with random agents.
    if (episode + 1) % evaluate_every == 0:
        print("Episode {0}. Play tournament.".format(str(episode)))
        logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])

# Close files in the logger
logger.close_files()

# Plot the learning curve
logger.plot('DQN')

# Save model
save_dir = 'models/keezen_dqn_pytorch'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
state_dict = agent1.get_state_dict()
print(state_dict. keys())
torch.save(state_dict, os.path.join(save_dir, 'model.pth'))
print("Training took: " + str(datetime.datetime.now() - start))

