import rlcard
import tensorflow as tf
import os
import torch

from rlcard.agents import NFSPAgent
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils import set_global_seed, tournament
from rlcard.utils import Logger

import datetime

# Make environment
# env = rlcard.make('keezen', config={})
# eval_env = rlcard.make('keezen', config={})
env = rlcard.make('keezen', config={'seed': 0})
eval_env_0 = rlcard.make('keezen', config={'seed': 0})
# eval_env_1 = rlcard.make('keezen', config={'seed': 0})
# eval_env_2 = rlcard.make('keezen', config={'seed': 0})
# eval_env_3 = rlcard.make('keezen', config={'seed': 0})

# Set the iterations numbers and how frequently we evaluate the performance
evaluate_every = 5000  # 100
evaluate_num = 4000   # 1000
episode_num = 75000  # 100000

# The intial memory size
memory_init_size = 5000

# Train the agent every X steps
train_every = 1

# The paths for saving the logs and learning curves
log_dir = 'experiments/keezen_nfsp_result_4/'

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:

    # Initialize a global step
    global_step = tf.Variable(0, name='global_step', trainable=False)

    # agents = []
    # for i in range(env.player_num):
    #     agent = NFSPAgent(sess,
    #                       scope='nfsp' + str(i),
    #                       action_num=env.action_num,
    #                       state_shape=env.state_shape,
    #                       hidden_layers_sizes=[512, 1024, 512],
    #                       min_buffer_size_to_learn=memory_init_size,
    #                       q_replay_memory_init_size=memory_init_size,
    #                       train_every=train_every,
    #                       q_train_every=train_every,
    #                       q_mlp_layers=[512, 1024, 512])
    #     agents.append(agent)
    # agent1 = NFSPAgent(sess,
    #                   scope='nfsp1',
    #                   action_num=env.action_num,
    #                   state_shape=env.state_shape,
    #                   hidden_layers_sizes=[512, 512],
    #                   min_buffer_size_to_learn=memory_init_size,
    #                   q_replay_memory_init_size=memory_init_size,
    #                   train_every=train_every,
    #                   q_train_every=train_every,
    #                   q_mlp_layers=[512, 512, 512])

    agent1 = NFSPAgent(sess,
                      scope='nfsp1',
                      action_num=env.action_num,
                      state_shape=env.state_shape,
                      hidden_layers_sizes=[512, 1024, 2048, 1024, 512],
                      anticipatory_param=0.5,
                      batch_size=256,
                      rl_learning_rate=0.00005,
                      sl_learning_rate=0.00001,
                      min_buffer_size_to_learn=memory_init_size,
                      q_replay_memory_size=int(1e5),
                      q_replay_memory_init_size=memory_init_size,
                      train_every=train_every,
                      q_train_every=train_every,
                      q_batch_size=256,
                      q_mlp_layers=[512, 1024, 2048, 1024, 512])


    # agent2 = NFSPAgent(sess,
    #                   scope='nfsp2',
    #                   action_num=env.action_num,
    #                   state_shape=env.state_shape,
    #                   hidden_layers_sizes=[512, 512],
    #                   min_buffer_size_to_learn=memory_init_size,
    #                   q_replay_memory_init_size=memory_init_size,
    #                   train_every=train_every,
    #                   q_train_every=train_every,
    #                   q_mlp_layers=[512, 512],
    #                   device=torch.device('gpu'))


    random_agent = RandomAgent(action_num=eval_env_0.action_num)

    agents = [agent1, random_agent, random_agent, random_agent]

    env.set_agents(agents)
    eval_env_0.set_agents([agent1, random_agent, random_agent, random_agent])
    # eval_env_1.set_agents([agents[1], random_agent, random_agent, random_agent])
    # eval_env_2.set_agents([agents[2], random_agent, random_agent, random_agent])
    # eval_env_3.set_agents([agents[3], random_agent, random_agent, random_agent])

    # Initialize global variables
    sess.run(tf.global_variables_initializer())

    # Init a Logger to plot the learning curve
    logger = Logger(log_dir)

    for episode in range(episode_num):

        # First sample a policy for the episode
        # agents[0].sample_episode_policy()
        # agents[2].sample_episode_policy()

        # Generate data from the environment
        trajectories, payoffs = env.run(is_training=True)

        # Feed transitions into agent memory, and train the agent(s)
        # for i in range(env.player_num):
        for ts in trajectories[0]:
            agent1.feed(ts)
        # for ts in trajectories[2]:
        #     agents[2].feed(ts)

        # Evaluate the performance.
        if episode % evaluate_every == 0 and episode > 0:
            startTournament = datetime.datetime.now()
            print("Episode {0}. Now play tournament.".format(str(episode)))
            tournament_results = tournament(eval_env_0, evaluate_num)
            logger.log_performance(env.timestep, tournament_results[0])
            print("Tournament took: " + str(datetime.datetime.now() - startTournament))
            # logger.log_performance(env.timestep, tournament(eval_env_1, evaluate_num)[0])

    # Close files in the logger
    logger.close_files()

    # Plot the learning curve
    logger.plot('NFSP')
    
    # Save model
    save_dir = 'models/keezen_nfsp'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    saver = tf.train.Saver()
    saver.save(sess, os.path.join(save_dir, 'model'))
