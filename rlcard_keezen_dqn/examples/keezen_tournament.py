import rlcard
import tensorflow as tf
import os

from rlcard.agents import NFSPAgent
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.games.keezen.agent import RuleBasedAgent
from rlcard.utils import set_global_seed, tournament
from rlcard.utils import Logger

evaluate_num = 1   # 1000

# The paths for saving the logs and learning curves
eval_env = rlcard.make('keezen', config={'seed': 0})

random_agent1 = RandomAgent(action_num=eval_env.action_num)
random_agent2 = RandomAgent(action_num=eval_env.action_num)
random_agent3 = RandomAgent(action_num=eval_env.action_num)
random_agent4 = RandomAgent(action_num=eval_env.action_num)
#rulebased_agent1 = RuleBasedAgent(eval_env.game.game)
eval_env.set_agents([random_agent1, random_agent2, random_agent3, random_agent4])

print("Play tournament.")
print("payoffs: " + str(tournament(eval_env, evaluate_num)))

