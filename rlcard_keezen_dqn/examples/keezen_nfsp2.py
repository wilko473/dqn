''' An example of learning a NFSP Agent on Dou Dizhu
'''

import tensorflow as tf
import os

import rlcard
from rlcard.agents import NFSPAgent
from rlcard.agents import RandomAgent
from rlcard.utils import set_global_seed, tournament
from rlcard.utils import Logger

import datetime

# Make environment
env = rlcard.make('keezen', config={'seed': 0})
eval_env = rlcard.make('keezen', config={'seed': 0})

# Set the iterations numbers and how frequently we evaluate the performance
evaluate_every = 5000
evaluate_num = 4000
episode_num = 200000

# The intial memory size
memory_init_size = 5000

# Train the agent every X steps
train_every = 1  # 64

# The paths for saving the logs and learning curves
log_dir = './experiments/keezen_nfsp2_result6/'

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:

    # Initialize a global step
    global_step = tf.Variable(0, name='global_step', trainable=False)

    # Set up the agents
    agent1 = NFSPAgent(sess,
                      scope='nfsp1',
                      action_num=env.action_num,
                      state_shape=env.state_shape,
                      hidden_layers_sizes=[512, 512, 512], # [512, 1024, 2048, 1024, 512],
                      reservoir_buffer_capacity=int(1e4),  # Memory problems with 1e6 -> 1e5 niet genoeg
                      anticipatory_param=0.5,
                      batch_size=32,  # 256,
                      rl_learning_rate=0.00005,
                      sl_learning_rate=0.00001,
                      min_buffer_size_to_learn=memory_init_size,
                      q_replay_memory_size=int(1e3),  # Memory problems with 1e5 -> 1e4 niet genoeg
                      q_replay_memory_init_size=memory_init_size,
                      train_every=train_every,
                      q_train_every=train_every,
                      q_batch_size=32,  #256,
                      q_mlp_layers=[512, 512, 512])  # [512, 1024, 2048, 1024, 512])
    agent2 = NFSPAgent(sess,
                       scope='nfsp2',
                       action_num=env.action_num,
                       state_shape=env.state_shape,
                       hidden_layers_sizes=[512, 512, 512],  # [512, 1024, 2048, 1024, 512],
                       reservoir_buffer_capacity=int(1e4),  # Memory problems with 1e6 -> 1e5 niet genoeg
                       anticipatory_param=0.5,
                       batch_size=32,  # 256,
                       rl_learning_rate=0.00005,
                       sl_learning_rate=0.00001,
                       min_buffer_size_to_learn=memory_init_size,
                       q_replay_memory_size=int(1e3),  # Memory problems with 1e5 -> 1e4 niet genoeg
                       q_replay_memory_init_size=memory_init_size,
                       train_every=train_every,
                       q_train_every=train_every,
                       q_batch_size=32,  # 256,
                       q_mlp_layers=[512, 512, 512])  # [512, 1024, 2048, 1024, 512])

    # agent2 = NFSPAgent(sess,
    #                   scope='nfsp2',
    #                   action_num=env.action_num,
    #                   state_shape=env.state_shape,
    #                   hidden_layers_sizes=[512, 1024, 2048, 1024, 512],
    #                   anticipatory_param=0.5,
    #                   batch_size=256,
    #                   rl_learning_rate=0.00005,
    #                   sl_learning_rate=0.00001,
    #                   min_buffer_size_to_learn=memory_init_size,
    #                   q_replay_memory_size=int(1e5),
    #                   q_replay_memory_init_size=memory_init_size,
    #                   train_every=train_every,
    #                   q_train_every=train_every,
    #                   q_batch_size=256,
    #                   q_mlp_layers=[512, 1024, 2048, 1024, 512])

    agents = []
    # for i in range(env.player_num):
    #     agent = NFSPAgent(sess,
    #                       scope='nfsp' + str(i),
    #                       action_num=env.action_num,
    #                       state_shape=env.state_shape,
    #                       hidden_layers_sizes=[512,1024,2048,1024,512],
    #                       anticipatory_param=0.5,
    #                       batch_size=256,
    #                       rl_learning_rate=0.00005,
    #                       sl_learning_rate=0.00001,
    #                       min_buffer_size_to_learn=memory_init_size,
    #                       q_replay_memory_size=int(1e5),
    #                       q_replay_memory_init_size=memory_init_size,
    #                       train_every = train_every,
    #                       q_train_every=train_every,
    #                       q_batch_size=256,
    #                       q_mlp_layers=[512,1024,2048,1024,512])
    #     agents.append(agent)
    random_agent = RandomAgent(action_num=eval_env.action_num)

    env.set_agents([agent1, random_agent, agent2, random_agent])
    eval_env.set_agents([agent1, random_agent, agent2, random_agent])

    # Initialize global variables
    sess.run(tf.global_variables_initializer())

    # Init a Logger to plot the learning curvefrom rlcard.agents.random_agent import RandomAgent

    logger = Logger(log_dir)

    for episode in range(episode_num):

        # First sample a policy for the episode
        # for agent in agents:
        #     agent.sample_episode_policy()
        agent1.sample_episode_policy()
        # agent2.sample_episode_policy()

        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent memory, and train the agent
        # for i in range(env.player_num):
        #     for ts in trajectories[i]:
        #         agents[i].feed(ts)
        for ts in trajectories[0]:
            agent1.feed(ts)
        for ts in trajectories[2]:
            agent2.feed(ts)

        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:  # and episode > 0:
            # logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])
            startTournament = datetime.datetime.now()
            print("Episode {0}. Play tournament.".format(str(episode)))
            tournament_results = tournament(eval_env, evaluate_num)
            print("result: " + str(tournament_results))
            logger.log_performance(env.timestep, tournament_results[0])
            print("Tournament took: " + str(datetime.datetime.now() - startTournament))

    # Close files in the logger
    logger.close_files()

    # Plot the learning curve
    logger.plot('NFSP')
    
    # Save model
    save_dir = 'models/keezen_nfsp2-6'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    saver = tf.train.Saver()
    saver.save(sess, os.path.join(save_dir, 'model'))

