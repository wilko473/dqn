''' An example of mejn with CFR
'''
import numpy as np

import rlcard
from rlcard.agents import CFRAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils import set_global_seed, tournament
from rlcard.utils import Logger

# Make environment and enable human mode
env = rlcard.make('mejn', config={'seed': 0, 'allow_step_back': True})
eval_env = rlcard.make('mejn', config={'seed': 0})

# Set the iterations numbers and how frequently we evaluate the performance and save model
evaluate_every = 100
save_plot_every = 1000
evaluate_num = 10000
episode_num = 10000

# The paths for saving the logs and learning curves
log_dir = './experiments/mejn_cfr_result/'

# Set a global seed
set_global_seed(0)

# Initilize CFR Agent
agent = CFRAgent(env)
agent.load()  # If we have saved model, we first load the model

# Evaluate CFR against random agents
random_agent1 = RandomAgent(action_num=eval_env.action_num)
random_agent2 = RandomAgent(action_num=eval_env.action_num)
random_agent3 = RandomAgent(action_num=eval_env.action_num)

env.set_agents([agent, random_agent1, random_agent2, random_agent3])
eval_env.set_agents([agent, random_agent1, random_agent2, random_agent3])

# Init a Logger to plot the learning curve
logger = Logger(log_dir)

for episode in range(episode_num):
    agent.train()
    print('\rIteration {}'.format(episode), end='')
    # Evaluate the performance. Play with NFSP agents.
    if episode % evaluate_every == 0:
        agent.save()  # Save model
        logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])

# Close files in the logger
logger.close_files()

# Plot the learning curve
logger.plot('CFR')
