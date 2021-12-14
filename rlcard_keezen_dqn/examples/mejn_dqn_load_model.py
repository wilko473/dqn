import tensorflow as tf
import os

import rlcard
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.agents import RandomAgent
from rlcard.games.keezen.card import CardValue
from rlcard.utils import set_global_seed, tournament

# Make environment
env = rlcard.make('mejn', config={'seed': 0})

# Set a global seed
set_global_seed(0)

# Load pretrained model
graph = tf.Graph()
sess = tf.Session(graph=graph)

with graph.as_default():
    # Set up the agents
    dqn_agent1 = DQNAgent(sess,
                     scope='dqn1',
                     action_num=env.action_num,
                     state_shape=env.state_shape,
                     mlp_layers=[512, 512, 512, 512])
    # dqn_agent2 = DQNAgent(sess,
    #                  scope='dqn2',
    #                  action_num=env.action_num,
    #                  state_shape=env.state_shape,
    #                  mlp_layers=[512, 512, 512, 512])

print("Load model mejn")
# Pretrained model
check_point_path = os.path.join(rlcard.__path__[0], 'models/pretrained/mejn_dqn02')

with sess.as_default():
    with graph.as_default():
        saver = tf.train.Saver()
        saver.restore(sess, tf.train.latest_checkpoint(check_point_path))

# Evaluate the performance. Play with random agents.
print("Create evaluation environment")
evaluate_num = 100  # 4000
random_agent = RandomAgent(env.action_num)
# env.set_agents([dqn_agent1, random_agent, dqn_agent2, random_agent])
env.set_agents([dqn_agent1, random_agent, random_agent, random_agent])
print("Play tournament")
reward = tournament(env, evaluate_num)[0]
print('Average reward against random agents: ', reward)
input("Enter for start match")

state, player_id = env.reset()

# Loop to play the game. state = dict: 'obs', 'legal_actions'
# trajectories[player_id].append(state)
val = "run"
while not env.is_over():
    # Agent plays
    action = env.agents[player_id].step(state)

    # Environment steps
    next_state, next_player_id = env.step(action, env.agents[player_id].use_raw)

    # Set the state and player
    state = next_state
    player_id = next_player_id

    env.game.render()
    val = input("Enter for next move")

# Add a final state to all the players
for player_id in range(env.player_num):
    state = env.get_state(player_id)

# Payoffs
payoffs = env.get_payoffs()
print("Finished: payoffs = " + str(payoffs))


