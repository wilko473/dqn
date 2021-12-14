import numpy as np

from rlcard.envs import Env
from rlcard.games.keezen.board import BoardState
from rlcard.games.keezen.card import CardState
from rlcard.games.keezen.game import GameActions
from rlcard.games.keezen.keezengameadapter import KeezenGameAdapter


class KeezenEnv(Env):
    """ Keezen Environment."""

    def __init__(self, config):
        self.game = KeezenGameAdapter()
        self.action_num = self.game.get_action_num()
        self._ACTION_LIST = []  # List with all action ids, such as 'NO','DL','RU01P0','RO01P1' etc
        self._ACTION_SPACE = {}  # Map action indexes to action ids String (action id) --> int (action index)
        idx = 0
        if self.game.game.rules.game_type == "Keez":
            self._ACTION_LIST = GameActions.ALL_ACTIONS_271
            for action_id in self._ACTION_LIST:
                self._ACTION_SPACE[action_id] = idx
                idx += 1
        elif self.game.game.rules.game_type == "KeezSimple":
            self._ACTION_LIST = GameActions.ALL_ACTIONS_SIMPLE
            for action_id in self._ACTION_LIST:
                self._ACTION_SPACE[action_id] = idx
                idx += 1
        # FIXED: self._ACTION_LIST = list(self._ACTION_SPACE.values())
        super().__init__(config)
        self.state_shape = [5, 97]  # 97 123 TODO, 97 for player+board, 123 for player+board+cards

    # OLD: 2x bytearray 96
    # def _extract_state(self, state):
    #     obs = np.zeros((1, 2, 96), dtype=int)
    #     fields_with_marbles = state['fields_with_marbles']
    #     board_array = BoardState.get_board_state_as_array(fields_with_marbles, self.game.game.board, self.game.game.players)
    #     card_array = CardState.get_card_state_as_array(self.game.game_state.move_player,
    #                                                    self.game.game.players, self.game.game.cards,
    #                                                    self.game.game_state.stock_cards, self.game.game_state.player_cards,
    #                                                    self.game.game_state.played_cards)
    #     obs[0][0] = board_array
    #     obs[0][1] = card_array
    #     extracted_state = {}
    #     extracted_state['obs'] = obs
    #     player = state['state_for_player']
    #     extracted_state['player_id'] = self.game.game.players.index(player)
    #     extracted_state['legal_actions'] = self._get_legal_actions()
    #     # extracted_state = {'obs': obs, 'legal_actions': self._get_legal_actions()}
    #     return extracted_state

    def _extract_state(self, state):
        # obs = np.zeros((5, 122), dtype=bool)  # 5x0 = active player, 5x13 is player cards, 5x13 is played cards, 5x96 is marbles on board
        fields_with_marbles = state['fields_with_marbles']
        cur_player = state['state_for_player']
        # cur_player = self.game.players[0]
        play_with_color = state['players_play_with_color']

        cur_player_plays_with_color = play_with_color[cur_player]
        # own_cards = CardState.get_card_state_as_matrix(self.game.game_state.player_cards[cur_player])
        # played_cards = CardState.get_card_state_as_matrix(self.game.game_state.played_cards)
        board_matrix = BoardState.get_board_state_as_matrix(fields_with_marbles, self.game.game.board, cur_player,
                                                            cur_player_plays_with_color, self.game.game.players)
        active_player = np.zeros((5, 1), dtype=int)
        index_of_cur_player = self.game.game.players.index(cur_player)
        active_player[index_of_cur_player][0] = 1
        obs = np.hstack((active_player, board_matrix))  # ACTIVE PLAYER AND BOARD STATE

        # Board only:
        # obs = board_matrix

        # Board and card state
        #obs = np.hstack((active_player, own_cards))
        #obs = np.hstack((obs, played_cards))
        #obs = np.hstack((obs, board_matrix))

        extracted_state = {}
        extracted_state['obs'] = obs
        extracted_state['player_id'] = self.game.game.players.index(cur_player)
        extracted_state['legal_actions'] = self._get_legal_actions()
        extracted_state['allowed_moves'] = state.get("allowed_moves")
        extracted_state['game_state'] = state.get("game_state")
        return extracted_state

    def get_payoffs(self):
        """ Get the payoffs of players. Returns: payoffs (list): a list of payoffs for each player"""
        is_over, rewards = self.game.game.is_over(self.game.game_state)
        if not is_over:
            return None
        payoffs = np.array([0, 0, 0, 0])
        i = 0
        # high_reward = 0
        for reward in rewards:
            # if reward > 100:
            #     high_reward = reward
            payoffs[i] = reward
            i += 1
        # if high_reward > 0:
        #     print("HIGH reward in env.get_payoffs: " + str(payoffs))
        return payoffs

    def _decode_action(self, action_idx):
        """ Action id -> the action in the game."""
        action_id = self._ACTION_LIST[action_idx]
        return action_id

    def _get_legal_actions(self):
        """ Get all legal actions idxs for current state."""
        legal_action_idx = self.game.get_legal_actions(self._ACTION_SPACE)
        return legal_action_idx
        # legal_action_idx = []
        # if self.game.legal_moves:
        #     for moveid in self.game.legal_moves:
        #         action_idx = self._ACTION_SPACE[moveid]
        #         if action_idx not in legal_action_idx:
        #             legal_action_idx.append(action_idx)
        # return legal_action_idx

    def get_perfect_information(self):  # TODO: implement?
        """ Get the perfect information of the current state."""
        state = {}
        print("!!get_perfect_information!!")
        raise NotImplementedError
        return state
