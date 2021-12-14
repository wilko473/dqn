from typing import List
from rlcard.games.keezen.player import Player
import numpy as np


class FieldColor:
    GREEN = "GREEN"
    RED = "RED"
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    NEUTRAL = "NEUTRAL"


class FieldType:
    START = "START"
    HOME = "HOME"
    NORMAL = "NORMAL"
    WAIT = "WAIT"


class Board:
    """The board contains fields and marbles."""

    startFieldPassingForwards = False  # Indicates if a player can pass its own startfield forwards
    startFieldPassingBackwards = True  # Indicates if a player can pass its own startfield backwards

    def __init__(self, players):
        """Create the board. Creates the fields and marbles."""
        self.fields = []
        self.waitFields = []
        self.startFields = []
        self.homeFields = []
        self.marbles = []
        self.create_fields(players)
        self.create_marbles(players, 4)

    def create_fields(self, players):
        field_id = 0
        for a_player in players:
            for i in range(24):  # 0...23:
                if i in range(0, 4):  # 0...3:
                    home_field = Field(field_id, FieldType.HOME, a_player.player_color)
                    self.homeFields.append(home_field)
                    self.fields.append(home_field)
                elif i == 5:  # case 5:
                    start_field = Field(field_id, FieldType.START, a_player.player_color)
                    self.startFields.append(start_field)
                    self.fields.append(start_field)
                elif i in range(20, 24):  # 20...23:
                    wait_field = Field(field_id, FieldType.WAIT, a_player.player_color)
                    self.waitFields.append(wait_field)
                    self.fields.append(wait_field)
                else:
                    normal_field = Field(field_id, FieldType.NORMAL, FieldColor.NEUTRAL)
                    self.fields.append(normal_field)
                field_id += 1
        # Set previous and next fields
        for i in range(len(self.fields)):  # 0.. < result.fields.count:
            field = self.fields[i]
            index = i % 24
            if index == 1 or index == 2 or index == 3:  # 0
                field.previous_fields.append(self.fields[i + 1])  # i + 4
                field.next_fields.append(self.fields[i - 1])  # i + 1
            elif index == 0:  # 3
                # Last home field --> no next
                self.fields[i].previous_fields.append(self.fields[i + 1])  # -1
            elif index == 4:
                previous_index = i - 9
                if previous_index < 0:
                    previous_index = len(self.fields) + previous_index
                field.previous_fields.append(self.fields[previous_index])
                field.next_fields.append(self.fields[i + 1])
                field.next_fields.append(self.fields[i - 1])  # -4
            elif index == 19:
                field.previous_fields.append(self.fields[i - 1])
                next_index = i + 9
                if next_index > len(self.fields) - 1:
                    next_index = next_index - len(self.fields)
                field.next_fields.append(self.fields[next_index])
            elif index in range(20, 24):  # 20...23:
                pass  # break  # Wait fields have no relation with other fields
            else:
                field.previous_fields.append(self.fields[i - 1])
                field.next_fields.append(self.fields[i + 1])

    def create_marbles(self, players, number_of_marbles_per_player):  # [Marble]:
        """Creates the marbles for each player without putting them on wait fields at the board."""
        marble_id = 0
        for player in players:
            for i in range(0, number_of_marbles_per_player):  # 0..< numberOfMarblesPerPlayer:
                marble = Marble(marble_id, player.player_color, str(i))  # player.location + str(i))
                self.marbles.append(marble)
                marble_id += 1

    def get_marbles_with_color(self, color) -> []:
        return [marble for marble in self.marbles if marble.color_ == color]

    def get_start_field_with_color(self, color):
        return [field for field in self.startFields if field.color_ == color][0]

    def get_last_home_field_with_color(self, color):
        return [field for field in self.homeFields if field.color_ == color and not field.next_fields][0]

    # Helper methods with board_state
    def get_empty_wait_field_with_color(self, color_: FieldColor, fields_with_marbles):  # -> Field:
        for field in self.waitFields:
            if field.color_ == color_ and BoardState.get_marble_for_field_opt(field, fields_with_marbles) is None:
                return field
        return None

    def get_marbles_at_home(self, marble_color, fields_with_marbles) -> []:
        return [marble for marble in self.marbles if marble.color_ == marble_color
                and BoardState.get_field_for_marble(marble, fields_with_marbles).type_ == FieldType.HOME]

    def get_marbles_at_wait(self, marble_color, fields_with_marbles) -> []:  # [Marble]:
        return [marble for marble in self.marbles if marble.color_ == marble_color
                and BoardState.get_field_for_marble(marble, fields_with_marbles).type_ == FieldType.WAIT]

    def is_color_finished(self, color, fields_with_marbles, rules) -> bool:
        home_marbles = self.get_marbles_at_home(color, fields_with_marbles)
        return len(home_marbles) == rules.finish_marble_nrs  # Was 4, smaller to shorten game

    def get_waiting_marble(self, color, fields_with_marbles):  # -> Marble:
        marbles_at_wait = self.get_marbles_at_wait(color, fields_with_marbles)
        if marbles_at_wait:
            return marbles_at_wait[0]
        return None

    @staticmethod
    def get_path_for_marble(marble, run_fields: int, fields_with_marbles, get_shorter_path=False) -> []:
        """Returns a path for a marble if it exists. Assumed is that for Keezen there is max 1 path."""
        current_field = BoardState.get_field_for_marble(marble, fields_with_marbles)
        return Board.get_path_for_color(marble.color_, current_field, run_fields, fields_with_marbles, get_shorter_path)

    @staticmethod
    def get_path_for_color(marble_color, current_field, run_fields: int, fields_with_marbles, get_shorter_path=False):
        """Returns a path for a marble if it exists. Assumed is that for Keezen there is max 1 path."""
        path: List[Field] = []
        for step in range(abs(run_fields)):
            next_fields = current_field.next_fields
            if run_fields < 0:
                next_fields = current_field.previous_fields
            for next_field in next_fields:
                if Board.is_next_field_allowed(marble_color, current_field, next_field, fields_with_marbles,
                                               run_fields < 0):
                    path.append(next_field)
                    current_field = next_field
                    # Only 1 allowed next field is assumed
                    break
        if get_shorter_path or len(path) == abs(run_fields):
            return path
        return []

    @staticmethod
    def is_next_field_allowed(marble_color, current_field, next_field, fields_with_marbles, backwards) -> bool:
        if backwards and next_field not in current_field.previous_fields:
            return False  # Field has to be in previous fields if moving backward
        elif not backwards and next_field not in current_field.next_fields:
            return False  # Field has to be in next fields if moving forward
        elif next_field.type_ == FieldType.HOME and next_field.color_ != marble_color:
            return False  # It is a home field of other player
        elif backwards and current_field.type_ == FieldType.HOME:
            return False  # Marble is on home field: backwards not allowed
        elif backwards and next_field.type_ == FieldType.START and next_field.color_ == marble_color:
            return Board.startFieldPassingBackwards  # Run backwards via start?
        elif not backwards and next_field.type_ == FieldType.START and next_field.color_ == marble_color:
            return Board.startFieldPassingForwards  # Run forwards via start?
        elif next_field.type_ == FieldType.START or next_field.type_ == FieldType.HOME:
            # Check if there is a blocking marble
            if fields_with_marbles is not None:
                marble_on_field = BoardState.get_marble_for_field_opt(next_field, fields_with_marbles)
                if marble_on_field is not None and marble_on_field.color_ == next_field.color_:
                    return False
        return True


class Field:
    """Field type. Has an id, type and color. Knows its next and previous fields."""

    def __init__(self, id_, type_, color_):
        self.id_ = id_
        self.type_ = type_
        self.color_ = color_
        self.next_fields = []
        self.previous_fields = []

    def __str__(self):
        return "Field[{0}], type: {1}, color: {2}.".format(self.id_, self.type_, self.color_)

    def get_str(self, marble):
        if marble:
            return marble.get_str()
        return self.type_[0]


class Marble:
    """Marble type.Has an id and color. The raw id is used for the action space: N0, N1, .., W3, W4."""

    def __init__(self, id_, color_, raw_id):
        self.id_ = id_
        self.color_ = color_
        self.raw_id = raw_id

    def __str__(self):
        return "Marble[{0}], color: {1}.".format(self.id_, self.color_)

    def get_str(self) -> str:
        return self.color_[0]


class BoardState:
    """Manages the positions of marbles on fields. Helper class, does not hold any state."""
    FIELDID_STATEINDEX_MAP = {5: 0, 6: 1, 7: 2, 8: 3, 9: 4, 10: 5, 11: 6, 12: 7, 13: 8, 14: 9, 15: 10, 16: 11, 17: 12,
                              18: 13, 19: 14, 28: 15, 27: 16, 26: 17, 25: 18, 24: 19, 20: 20, 21: 21, 22: 22, 23: 23,
                              29: 24, 30: 25, 31: 26, 32: 27, 33: 28, 34: 29, 35: 30, 36: 31, 37: 32, 38: 33, 39: 34,
                              40: 35, 41: 36, 42: 37, 43: 38, 52: 39, 51: 40, 50: 41, 49: 42, 48: 43, 44: 44, 45: 45,
                              46: 46, 47: 47, 53: 48, 54: 49, 55: 50, 56: 51, 57: 52, 58: 53, 59: 54, 60: 55, 61: 56,
                              62: 57, 63: 58, 64: 59, 65: 60, 66: 61, 67: 62, 76: 63, 75: 64, 74: 65, 73: 66, 72: 67,
                              68: 68, 69: 69, 70: 70, 71: 71, 77: 72, 78: 73, 79: 74, 80: 75, 81: 76, 82: 77, 83: 78,
                              84: 79, 85: 80, 86: 81, 87: 82, 88: 83, 89: 84, 90: 85, 91: 86, 4: 87, 3: 88, 2: 89,
                              1: 90, 0: 91, 92: 92, 93: 93, 94: 94, 95: 95}

    PATH_FOR_LOCATION = [[20, 21, 22, 23, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 28, 29, 30, 31,
                          32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61,
                          62, 63, 64, 65, 66, 67, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91,
                          4, 3, 2, 1, 0],
                         [44, 45, 46, 47, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 52, 53, 54, 55,
                          56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86,
                          87, 88, 89, 90, 91, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 28, 27, 26,
                          25, 24],
                         [68, 69, 70, 71, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 76, 77, 78, 79,
                          80,
                          81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
                          18, 19, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 52, 51, 50, 49, 48],
                         [92, 93, 94, 95, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 4, 5, 6, 7, 8, 9,
                          10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
                          41,
                          42, 43, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 76, 75, 74, 73, 72]]

    @staticmethod
    def get_initial_board_state(marbles, wait_fields) -> {}:
        """Returns the board state with all marbles on the wait fields."""
        fields_with_marbles = dict()
        copy_fields = wait_fields.copy()
        for marble in marbles:
            field = next(copy_field for copy_field in copy_fields if copy_field.color_ == marble.color_)
            fields_with_marbles[field] = marble
            copy_fields.remove(field)
        return fields_with_marbles

    @staticmethod
    def get_field_for_marble(marble: Marble, fields_with_marbles) -> Field:
        for key_field, value_marble in fields_with_marbles.items():
            if value_marble == marble:
                return key_field
        # return self.marbles_with_fields[marble]

    @staticmethod
    def get_marble_for_field(field: Field, fields_with_marbles) -> Marble:
        return fields_with_marbles[field]

    @staticmethod
    def get_marble_for_field_opt(field: Field, fields_with_marbles):
        if field in fields_with_marbles.keys():
            return fields_with_marbles[field]
        return None

    @staticmethod
    def put_marble_on_field(marble, field, fields_with_marbles):  # -> Optional[Marble]:
        """Puts a marble on a field. If the field is not empty, the marble on the destination field is returned."""
        current_field = BoardState.get_field_for_marble(marble, fields_with_marbles)
        if field != current_field:
            already_marble_on_field = BoardState.get_marble_for_field_opt(field, fields_with_marbles)
            if current_field:
                del fields_with_marbles[current_field]
            # Put marble on new field
            fields_with_marbles[field] = marble
            return already_marble_on_field
        return None

    @staticmethod
    def reset(board, fields_with_marbles):
        """Put all marbles on WAIT fields."""
        for marble in board.marbles:
            field = BoardState.get_field_for_marble(marble, fields_with_marbles)
            if field is None or field.type_ != FieldType.WAIT:
                wait_field = board.get_empty_wait_field_with_color(marble.color_, fields_with_marbles)
                BoardState.put_marble_on_field(marble, wait_field, fields_with_marbles)

    # def set_fields_with_marbles(self, fields_with_marbles):
    #     self.fields_with_marbles = dict(fields_with_marbles)
    # self.marbles_with_fields = {value: key for key, value in self.fields_with_marbles.items()}

    # FIRST METHOD WITH BOARD AS ARRAY WITH 1, 2, 3 and 4 for the marbles
    # @staticmethod
    # def get_board_state_as_array(fields_with_marbles, board, players: [Player]):
    #     """Returns the board state as an array from player perspective."""
    #     # start_field_for_player = board.get_start_field_with_color(player.plays_with_color)
    #     # path_from_start = Board.get_path_for_color(player.plays_with_color, start_field_for_player, 82, None)
    #     # board_array = [0] * 96
    #     board_array = bytearray(96)
    #     color_player_index = {}
    #     for player in players:
    #         color_player_index[player.player_color] = players.index(player) + 1  # Value starts with 1, 0 is no marble
    #     for key_field, value_marble in fields_with_marbles.items():
    #         field_index = board.fields.index(key_field)
    #         player_value = color_player_index[value_marble.color_]
    #         board_array[field_index] = player_value
    #     return board_array

    # 2ND METHOD with FIELDID_STATEINDEX_MAP
    #     @staticmethod
    # def get_board_state_as_matrix(fields_with_marbles, board, cur_player: Player, plays_with_color, players: [Player]):
    #     """Returns the board state as an 5x96 matrix from current player perspective."""
    #     board_matrix = np.zeros((5, 96), dtype=int)
    #
    #     # color_player_index = {}
    #     # player = cur_player
    #     # for i in range(len(players)):
    #     #     color_player_index[player.player_color] = players.index(player)
    #     #     player = player.get_next_player(players)
    #     color_player_index = {}
    #     for i in range(len(players)):
    #         temp_player = players[i]
    #         color_player_index[temp_player.player_color] = i
    #
    #     start_field_for_player_id = board.get_start_field_with_color(plays_with_color).id_
    #
    #     # Put 1 for marbles in the matrix
    #     for key_field, value_marble in fields_with_marbles.items():
    #         field_id = board.fields.index(key_field)
    #         matrix_index = BoardState.get_field_index(field_id, start_field_for_player_id)
    #         player_value = color_player_index[value_marble.color_]
    #         board_matrix[player_value][matrix_index] = 1
    #     return board_matrix

    # NEW METHOD WITH PATH_FOR_LOCATION
    # @staticmethod
    # def get_board_state_as_matrix(fields_with_marbles, board, cur_player: Player, plays_with_color, players: [Player]):
    #     """Returns the board state as an 5x96 matrix from current player perspective."""
    #     board_matrix = np.zeros((5, 96), dtype=int)
    #     color_player_index = {}  #
    #     player = cur_player
    #     for i in range(len(players)):
    #         color_player_index[player.player_color] = players.index(player)
    #         player = player.get_next_player(players)
    #     # Put 1 for marbles in the matrix
    #     for key_field, value_marble in fields_with_marbles.items():
    #         field_id = board.fields.index(key_field)
    #         player_value = color_player_index[value_marble.color_]
    #         path = BoardState.PATH_FOR_LOCATION[player_value]  # Path == 72 fields for each player
    #         matrix_index = path.index(field_id)
    #         board_matrix[player_value][matrix_index] = 1
    #     return board_matrix

    # @staticmethod
    # def get_field_index(field_id, start_field_id):
    #     field_index = BoardState.FIELDID_STATEINDEX_MAP[field_id]
    #     home_field_index = BoardState.FIELDID_STATEINDEX_MAP[start_field_id]
    #     result_index = field_index - home_field_index
    #     if result_index < 0:
    #         result_index = result_index + 96
    #     return result_index

    @staticmethod
    def get_board_state_as_matrix(fields_with_marbles, board, cur_player: Player, plays_with_color, players: [Player]):
        num_players = len(players)
        num_fields = len(board.fields)
        board_matrix = np.zeros((num_players + 1, num_fields), dtype=int)
        for i in range(num_players):
            for key_field, value_marble in fields_with_marbles.items():
                if players[i].player_color == value_marble.color_:
                    field_id = board.fields.index(key_field)
                    pos = BoardState.FIELDID_STATEINDEX_MAP[field_id]
                    board_matrix[i][pos] = 1
                    board_matrix[4][pos] = 1  # 5th row contains all marbles
        return board_matrix
