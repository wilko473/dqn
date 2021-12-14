import rlcard
import tensorflow as tf
import os

from rlcard.agents import NFSPAgent
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.games.keezen.agent import RuleBasedAgent, RuleBasedAgentAdapter
from rlcard.utils import set_global_seed, tournament
from rlcard.utils import Logger

import datetime

start = datetime.datetime.now()
# Make environment
# env = rlcard.make('keezen', config={})
# eval_env = rlcard.make('keezen', config={})
env = rlcard.make('keezen', config={})  # config={'seed': 0})
eval_env = rlcard.make('keezen', config={})  # , config={'seed': 0})

# Set the iterations numbers and how frequently we evaluate the performance
evaluate_every = 1000  # 100
evaluate_num = 4000   # 1000 TODO
episode_num = 1  # 100000  # 100000

# The intial memory size
memory_init_size = 5000  # 1000

# Train the agent every X steps
train_every = 5  # 1

# The paths for saving the logs and learning curves
log_dir = 'experiments/keezen_rba_result_1/'  # TODO: change

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:

    # Initialize a global step
    global_step = tf.Variable(0, name='global_step', trainable=False)

    # Set up the agents
    # dqn_agent1 = DQNAgent(sess,
    #                  scope='dqn1',
    #                  action_num=env.action_num,
    #                  replay_memory_init_size=memory_init_size,
    #                  train_every=train_every,
    #                  state_shape=env.state_shape,
    #                  mlp_layers=[512, 512, 512])
    # dqn_agent2 = DQNAgent(sess,
    #                  scope='dqn2'
    #                        '',
    #                  action_num=env.action_num,
    #                  replay_memory_init_size=memory_init_size,
    #                  train_every=train_every,
    #                  state_shape=env.state_shape,
    #                  mlp_layers=[512, 1024, 1024, 512])
    # nfsp_agent1 = NFSPAgent(sess,
    #                   scope='nfsp1',
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
    # nfsp_agent2 = NFSPAgent(sess,
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

    rule_based_agent = RuleBasedAgent(eval_env.game.game)
    rule_based_agent_adapter = RuleBasedAgentAdapter(rule_based_agent)



    random_agent1 = RandomAgent(action_num=eval_env.action_num)
    random_agent2 = RandomAgent(action_num=eval_env.action_num)
    #random_agent3 = RandomAgent(action_num=eval_env.action_num)
    # env.set_agents([dqn_agent1, random_agent1, dqn_agent1, random_agent2])
    # eval_env.set_agents([dqn_agent1, random_agent1, dqn_agent1, random_agent2])

    eval_env.set_agents([rule_based_agent_adapter, random_agent1, rule_based_agent_adapter, random_agent2])

    # Initialize global variables
    sess.run(tf.global_variables_initializer())

    # Init a Logger to plot the learning curve
    logger = Logger(log_dir)

    for episode in range(episode_num):

        # # Generate data from the environment
        # trajectories, payoffs = env.run(is_training=True)
        #
        # # Feed transitions into agent memory, and train the agent(s)
        # for ts in trajectories[0]:
        #     dqn_agent1.feed(ts)
        # for ts in trajectories[2]:
        #     dqn_agent1.feed(ts)

        # Evaluate the performance.
        if episode % evaluate_every == 0:
            print("Episode {0}. Play tournament.".format(str(episode)))
            logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])
            #logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[2])

    # Close files in the logger
    logger.close_files()

    # Plot the learning curve
    logger.plot('DQN')
    
    # Save model
    save_dir = 'models/keezen_dqn'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    saver = tf.train.Saver()
    saver.save(sess, os.path.join(save_dir, 'model'))

    print("Training took: " + str(datetime.datetime.now() - start))

