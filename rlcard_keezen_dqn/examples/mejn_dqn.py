import rlcard
import tensorflow as tf
import os

from rlcard.agents.dqn_agent import DQNAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils import set_global_seed, tournament
from rlcard.utils import Logger

import datetime

start = datetime.datetime.now()
# Make environment
# env = rlcard.make('mejn', config={})
# eval_env = rlcard.make('mejn', config={})
env = rlcard.make('mejn', config={'seed': 0})
eval_env = rlcard.make('mejn', config={'seed': 0})

# Set the iterations numbers and how frequently we evaluate the performance
evaluate_every = 5000  # 100
evaluate_num = 4000   # 1000
episode_num = 100000

# The intial memory size
memory_init_size = 5000  # 1000

# Train the agent every X steps
train_every = 1

# The paths for saving the logs and learning curves
log_dir = 'experiments/mejn_dqn_result_04/'

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:

    # Initialize a global step
    global_step = tf.Variable(0, name='global_step', trainable=False)

    # Set up the agents
    dqn_agent1 = DQNAgent(sess,
                     scope='dqn1',
                     action_num=env.action_num,
                     replay_memory_init_size=memory_init_size,
                     train_every=train_every,
                     state_shape=env.state_shape,
                     mlp_layers=[128, 256, 128])
                     # mlp_layers=[512, 512, 512, 512])  # learning_rate=0.00005
    # dqn_agent2 = DQNAgent(sess,
    #                  scope='dqn2',
    #                  action_num=env.action_num,
    #                  replay_memory_init_size=memory_init_size,
    #                  train_every=train_every,
    #                  state_shape=env.state_shape,
    #                  mlp_layers=[512, 512, 512, 512])

    random_agent1 = RandomAgent(action_num=eval_env.action_num)
    random_agent2 = RandomAgent(action_num=eval_env.action_num)
    random_agent3 = RandomAgent(action_num=eval_env.action_num)

    env.set_agents([dqn_agent1, random_agent1, random_agent2, random_agent3])
    eval_env.set_agents([dqn_agent1, random_agent1, random_agent2, random_agent3])

    # Initialize global variables
    sess.run(tf.global_variables_initializer())

    # Init a Logger to plot the learning curve
    logger = Logger(log_dir)

    for episode in range(episode_num):

        # # Generate data from the environment
        trajectories, payoffs = env.run(is_training=True)

        # Feed transitions into agent memory, and train the agent(s)
        for ts in trajectories[0]:
            dqn_agent1.feed(ts)
        # for ts in trajectories[2]:
        #     dqn_agent1.feed(ts)

        # Evaluate the performance.
        if episode % evaluate_every == 0 and episode > 0:
            startTournament = datetime.datetime.now()
            print("Episode {0}. Play tournament.".format(str(episode)))
            tournament_results = tournament(eval_env, evaluate_num)
            logger.log_performance(env.timestep, tournament_results[0])
            # logger.log_performance(env.timestep, tournament_results[2])
            print("Tournament results: " + str(tournament_results))
            print("Tournament took: " + str(datetime.datetime.now() - startTournament))

    # Close files in the logger
    logger.close_files()

    # Plot the learning curve
    logger.plot('DQN')
    
    # Save model
    save_dir = 'models/mejn_dqn04'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    saver = tf.train.Saver()
    saver.save(sess, os.path.join(save_dir, 'model'))

    print("Training took: " + str(datetime.datetime.now() - start))

