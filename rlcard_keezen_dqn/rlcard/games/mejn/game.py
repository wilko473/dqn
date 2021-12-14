from copy import copy
import random

from rlcard.games.mejn.board import Board, BoardState, FieldType
from rlcard.games.mejn.move import Move, MoveType, MarbleMove
from rlcard.games.mejn.player import Player

from colorama import Fore, Style

class Game:
    """A game of Mens-Erger-Je-Niet. Has rules, players and a board with marbles. The game state is in GameState."""

    GAME_ACTIONS = 29
    GAME_STATE_COLUMNS = 2
    GAME_STATE_ROWS = 96
    KEEP_HISTORY = True

    def __init__(self, players, board):
        self.players = players
        self.board = board
        self.game_history = []  # [GamePosition]

    def init_game(self):
        """Initializes the game. All marbles at wait fields, cards in stock."""
        self.game_history.clear()
        move_number = 0
        fields_with_marbles = BoardState.get_initial_board_state(self.board.marbles, self.board.waitFields)
        move_player = self.players[0]
        game_state = GameState(fields_with_marbles, move_player, move_number, self.throw_dice())
        if self.KEEP_HISTORY:
            self.game_history.append(game_state)
        return game_state, self.players.index(move_player)

    def render(self, game_state):
        field_idx = [[68, 69, -1, -1, 67, 4, 5, -1, -1, 14, 15],
                     [70, 71, -1, -1, 66, 3, 6, -1, -1, 16, 17],
                     [-1, -1, -1, -1, 65, 2, 7, -1, -1, -1, -1],
                     [-1, -1, -1, -1, 64, 1, 8, -1, -1, -1, -1],
                     [59, 60, 61, 62, 63, 0, 9, 10, 11, 12, 13],
                     [58, 57, 56, 55, 54, -1, 18, 19, 20, 21, 22],
                     [49, 48, 47, 46, 45, 36, 27, 26, 25, 24, 23],
                     [-1, -1, -1, -1, 44, 37, 28, -1, -1, -1, -1],
                     [-1, -1, -1, -1, 43, 38, 29, -1, -1, -1, -1],
                     [50, 51, -1, -1, 42, 39, 30, -1, -1, 32, 33],
                     [52, 53, -1, -1, 41, 40, 31, -1, -1, 34, 35]]
        print("player:" + str(game_state.move_player.player_color[0]) + ", move number: " + str(game_state.move_number))
        print("-------------------------")
        # for field_ids in field_idx:
        #     row = "| "
        #     for field_id in field_ids:
        #         value = " "
        #         if field_id > -1:
        #             field = self.board.fields[field_id]
        #             marble = BoardState.get_marble_for_field_opt(field, game_state.fields_with_marbles)
        #             value = field.get_str(marble)
        #             if value == "N":
        #                 value = "O"
        #         row = row + value + " "
        #     print(row + "|")

        print("Move[" + str(game_state.move_number) + "], player: " + str(game_state.move_player) + ", dice: "
              + str(game_state.dice))
        for field_ids in field_idx:
            row = "|"
            for field_id in field_ids:
                value = " "
                if field_id > -1:
                    field = self.board.fields[field_id]
                    marble = BoardState.get_marble_for_field_opt(field, game_state.fields_with_marbles)
                    value = field.get_str(marble)
                    if value == "G":
                        value = str(Fore.GREEN + value + Style.RESET_ALL)
                    elif value == "R":
                        value = str(Fore.RED + value + Style.RESET_ALL)
                    elif value == "B":
                        value = str(Fore.BLUE + value + Style.RESET_ALL)
                    elif value == "Y":
                        value = str(Fore.YELLOW + value + Style.RESET_ALL)
                    if value == "N":
                        value = "O"
                row = row + value + " "
            print(row + "|")
        print("-------------------------")

    def get_allowed_moves(self, game_state) -> [Move]:
        """Returns the allowed moves."""
        allowed_moves: [Move] = []
        player_marbles = self.board.get_marbles_with_color(game_state.move_player.player_color)
        for marble in player_marbles:
            from_field = BoardState.get_field_for_marble(marble, game_state.fields_with_marbles)
            if game_state.dice == 6:  # Just choose between START and RUN; Not required to RUN after START
                # START move
                if from_field.type_ == FieldType.WAIT:
                    start_field = self.board.get_start_field_with_color(marble.color_)
                    marble_on_start = BoardState.get_marble_for_field_opt(start_field, game_state.fields_with_marbles)
                    if not marble_on_start:
                        marble_move = MarbleMove(marble, from_field, start_field, 0)
                        move = Move(MoveType.START, game_state.move_player, [marble_move], 0)
                        allowed_moves.append(move)
            # RUN move
            path = Board.get_path_for_marble(marble, game_state.dice, game_state.fields_with_marbles)
            if path:
                marble_move = MarbleMove(marble, from_field, path[-1], path)
                marble_move.hit_marble_moves = self._get_hit_marble_moves(marble_move, game_state.fields_with_marbles)
                move = Move(MoveType.RUN, game_state.move_player, [marble_move], game_state.dice)
                allowed_moves.append(move)
        if not allowed_moves:
            done, rewards = self.is_over(game_state)
            if not done:
                allowed_moves.append(Move(MoveType.NONE, game_state.move_player, [], 0))
        return allowed_moves

    def throw_dice(self) -> int:
        return random.randint(1, 6)

    def _get_hit_marble_moves(self, marble_move, fields_with_marbles) -> []:
        marble_on_field = BoardState.get_marble_for_field_opt(marble_move.to_field, fields_with_marbles)
        if marble_on_field is not None:
            wait_field = self.board.get_empty_wait_field_with_color(marble_on_field.color_, fields_with_marbles)
            return [MarbleMove(marble_on_field, marble_move.to_field, wait_field, [])]
        return []

    def step(self, move, game_state) -> ():  # GamePosition, reward, done, info: [String: String]):
        """Return next state and next player's id"""
        if move:
            for marble_move in move.marble_moves:
                _ = BoardState.put_marble_on_field(marble_move.marble, marble_move.to_field,
                                                   game_state.fields_with_marbles)
                for hit_marble_move in marble_move.hit_marble_moves:
                    _ = BoardState.put_marble_on_field(hit_marble_move.marble, hit_marble_move.to_field,
                                                       game_state.fields_with_marbles)
            game_state.move_number += 1
        done, rewards = self.is_over(game_state)
        if not done and game_state.dice != 6:
            game_state.move_player = game_state.move_player.get_next_player(self.players)
        game_state.dice = self.throw_dice()
        copy_game_state = copy(game_state)
        if self.KEEP_HISTORY:
            copy_game_state.last_move = move
            self.game_history.append(copy_game_state)
        return copy_game_state, rewards, done

    def is_over(self, game_state):
        """Returns if the game is over. All marbles of a team are at the home fields.
        If the game is finished then the rewards for each player are returned."""
        player_finished = self.board.is_color_finished(game_state.move_player.player_color,
                                                       game_state.fields_with_marbles)
        if player_finished:
            rewards = []
            for player in self.players:
                if player == game_state.move_player:
                    rewards.append(1)
                else:
                    rewards.append(0)
            # print("FINISHED! Moves: " + str(game_state.move_number) + ", player " + str(game_state.move_player)
            #       + " won. Rewards: " + str(rewards))
            return True, rewards
        return False, None

    def step_back(self):
        """Returns and removes the last game_state from game history."""
        if self.game_history:
            prev_game_state = self.game_history.pop()
            return prev_game_state
        return None


class GameState:
    """A GameState holds the state of a game. This means the marble positions, move player, round and move numbers."""

    def __init__(self, fields_with_marbles, move_player, move_number, dice):
        self.fields_with_marbles = dict(fields_with_marbles)
        self.move_player = move_player
        self.move_number = move_number
        self.dice = dice
        self.last_move = None

    def __copy__(self):
        new_one = type(self)(self.fields_with_marbles, self.move_player, self.move_number, self.dice)
        return new_one

    def get_state_for_player(self, player: Player):
        state = dict()
        state['state_for_player'] = player
        state['fields_with_marbles'] = dict(self.fields_with_marbles)
        state['move_player'] = self.move_player
        state['move_number'] = self.move_number
        state['dice'] = self.dice
        return state


class GameActions:
    ALL_ACTIONS_29 = ['NO', 'RU01P0', 'RU01P1', 'RU01P2', 'RU01P3', 'RU02P0', 'RU02P1', 'RU02P2', 'RU02P3', 'RU03P0',
                      'RU03P1', 'RU03P2', 'RU03P3', 'RU04P0', 'RU04P1', 'RU04P2', 'RU04P3', 'RU05P0', 'RU05P1',
                      'RU05P2', 'RU05P3', 'RU06P0', 'RU06P1', 'RU06P2', 'RU06P3', 'STP0', 'STP1', 'STP2', 'STP3']
    ALL_ACTIONS_BW_53 = ['NO', 'RU01P0', 'RU01P1', 'RU01P2', 'RU01P3', 'RU02P0', 'RU02P1', 'RU02P2', 'RU02P3', 'RU03P0',
                         'RU03P1', 'RU03P2', 'RU03P3', 'RU04P0', 'RU04P1', 'RU04P2', 'RU04P3', 'RU05P0', 'RU05P1',
                         'RU05P2', 'RU05P3', 'RU06P0', 'RU06P1', 'RU06P2', 'RU06P3', 'STP0', 'STP1', 'STP2', 'STP3',
                         'RU-1P0', 'RU-1P1', 'RU-1P2', 'RU-1P3', 'RU-2P0', 'RU-2P1', 'RU-2P2', 'RU-2P3', 'RU-3P0',
                         'RU-3P1', 'RU-3P2', 'RU-3P3', 'RU-4P0', 'RU-4P1', 'RU-4P2', 'RU-4P3', 'RU-5P0', 'RU-5P1',
                         'RU-5P2', 'RU-5P3', 'RU-6P0', 'RU-6P1', 'RU-6P2', 'RU-6P3']
