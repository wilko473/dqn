from rlcard.games.mejn.board import FieldColor, Board
from rlcard.games.mejn.game import Game, GameActions
from rlcard.games.mejn.player import Player, PlayerLocation


class MejnGameAdapter:
    """Adapter class to use the Mejn game in RLCard. The state and actions are converted to dict and ints."""

    game_type = "Mejn"  # "MejnBackwards"  # or "Mejn"

    def __init__(self, allow_step_back=False):
        self.allow_step_back = allow_step_back
        player_north = Player("Green", FieldColor.GREEN, PlayerLocation.NORTH)
        player_east = Player("Red", FieldColor.RED, PlayerLocation.EAST)
        player_south = Player("Blue", FieldColor.BLUE, PlayerLocation.SOUTH)
        player_west = Player("Yellow", FieldColor.YELLOW, PlayerLocation.WEST)
        self.players = [player_north, player_east, player_south, player_west]

        print("Initialize mejn game. game_type: " + MejnGameAdapter.game_type)
        self.game = Game(self.players, Board(self.players))
        self.game_state = None

        self._ACTION_SPACE = {}
        idx = 0
        if MejnGameAdapter.game_type == "Mejn":
            for action_id in GameActions.ALL_ACTIONS_29:
                self._ACTION_SPACE[action_id] = idx
                idx += 1
        elif MejnGameAdapter.game_type == "MejnBackwards":
            for action_id in GameActions.ALL_ACTIONS_BW_53:
                self._ACTION_SPACE[action_id] = idx
                idx += 1

        # self.legal_moves = {}  # actionid --> move  CHANGED: NO MEMBER VARIABLE self.legal_moves

    def init_game(self):
        self.game_state, player_idx = self.game.init_game()
        player_state = self.get_state(player_idx)
        return player_state, player_idx

    def step(self, action):  # action, for example: 'ST13P3'
        """Do a move. Action is the raw id of a move."""
        move = None
        if action != 'NO':
            # move = self.legal_moves[action]  # CHANGED: NO MEMBER VARIABLE self.legal_moves
            allowed_moves = self.game.get_allowed_moves(self.game_state)
            moves = [move for move in allowed_moves if move.raw_action == action]
            # moves = [move for move in self.game.get_allowed_moves(self.game_state) if move.raw_action == action]
            if len(moves) is 1:
                move = moves[0]
            else:
                print("UNEXPECTED NUMBER OF ALLOWED MOVES FOR ACTION " + action + ":" + str(len(moves)))
        self.game_state, rewards, done = self.game.step(move, self.game_state)
        player_idx = self.game.players.index(self.game_state.move_player)
        player_state = self.get_state(player_idx)
        return player_state, player_idx

    def step_back(self):
        prev_game_state = self.game.step_back()
        if prev_game_state:
            self.game_state = prev_game_state
            player_idx = self.game.players.index(self.game_state.move_player)
            player_state = self.get_state(player_idx)
            return player_state, player_idx

    def get_state(self, player_idx):
        player_state = self.game_state.get_state_for_player(self.game.players[player_idx])
        allowed_moves = self.game.get_allowed_moves(self.game_state)
        # CHANGED: NO MEMBER VARIABLE self.legal_moves
        # self.legal_moves.clear()
        # legal_moves_id = []
        # for move in allowed_moves:
        #     # CHANGED to use marble position (0 first, 3 is last)
        #     raw_action = move.get_raw_action(self.game, self.game_state)
        #     legal_moves_id.append(raw_action)
        #     self.legal_moves[raw_action] = move
        #     # ORIGINAL CODE:
        #     # legal_moves_id.append(move.raw_action)
        #     # self.legal_moves[move.raw_action] = move
        # if not legal_moves_id:
        #     legal_moves_id.append(0)  # pass
        #     self.legal_moves['NO'] = None
        legal_moves_id = self.get_legal_actions(self._ACTION_SPACE)
        # END CHANGED: NO MEMBER VARIABLE self.legal_moves
        player_state['legal_moves'] = legal_moves_id
        player_state['allowed_moves'] = allowed_moves
        player_state['game_state'] = self.game_state
        return player_state

    @staticmethod
    def get_action_num():
        if MejnGameAdapter.game_type == "MejnSimple":
            return Game.GAME_ACTIONS  # TODO: Support other action spaces
        return Game.GAME_ACTIONS

    def get_player_id(self):
        return self.game.players.index(self.game_state.move_player)

    def get_player_num(self):
        return len(self.game.players)

    def is_over(self):
        done, rewards = self.game.is_over(self.game_state)
        return done

    def render(self):
        self.game.render(self.game_state)

    # def get_legal_actions(self, action_space) -> [int]:  # Using self.legal_moves, filled by get_state()
    #     legal_action_idx = []
    #     if self.legal_moves:
    #         for moveid in self.legal_moves:
    #             action_idx = action_space[moveid]
    #             if action_idx not in legal_action_idx:
    #                 legal_action_idx.append(action_idx)
    #     return legal_action_idx

    def get_legal_actions(self, action_space) -> [int]:  # No member variable self.legal_moves
        allowed_moves = self.game.get_allowed_moves(self.game_state)
        legal_moves_id = []
        for move in allowed_moves:
            # raw_action = move.get_raw_action(self.game, self.game_state)
            action_idx = action_space[move.raw_action]
            legal_moves_id.append(action_idx)
        if not legal_moves_id:
            no_idx = action_space['NO']
            legal_moves_id.append(no_idx)  # pass
        return legal_moves_id



    # def get_action_idx(self, moves):
    #     action_idxs = []
    #     for move in moves:
    #         action_id = move.raw_action
    #         action_idx = GameActions.ALL_ACTIONS_251.index(action_id)
    #         action_idxs.append(action_idx)
    #         self.legal_moves[action_idx] = move
    #     return action_idxs
