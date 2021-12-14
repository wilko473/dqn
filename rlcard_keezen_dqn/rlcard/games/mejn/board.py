from typing import List

import numpy as np

from rlcard.games.mejn.player import Player


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
            for i in range(18):
                if i in range(0, 4):
                    home_field = Field(field_id, FieldType.HOME, a_player.player_color)
                    self.homeFields.append(home_field)
                    self.fields.append(home_field)
                elif i == 5:
                    start_field = Field(field_id, FieldType.START, a_player.player_color)
                    self.startFields.append(start_field)
                    self.fields.append(start_field)
                elif i in range(14, 18):
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
            index = i % 18  # 18 fields per quarter of the board
            if index == 1 or index == 2 or index == 3:  # 3 first home fields
                field.previous_fields.append(self.fields[i + 1])
                field.next_fields.append(self.fields[i - 1])
            elif index == 0:
                # Last home field --> no next
                self.fields[i].previous_fields.append(self.fields[i + 1])
            elif index == 4:  # Field before start field
                previous_index = i - 9
                if previous_index < 0:
                    previous_index = len(self.fields) + previous_index
                field.previous_fields.append(self.fields[previous_index])
                field.next_fields.append(self.fields[i + 1])
                field.next_fields.append(self.fields[i - 1])
            elif index == 13:
                field.previous_fields.append(self.fields[i - 1])
                next_index = i + 9
                if next_index > len(self.fields) - 1:
                    next_index = next_index - len(self.fields)
                field.next_fields.append(self.fields[next_index])
            elif index in range(14, 18):
                pass  # Wait fields have no relation with other fields
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

    def is_color_finished(self, color, fields_with_marbles) -> bool:
        home_marbles = self.get_marbles_at_home(color, fields_with_marbles)
        return len(home_marbles) == 4

    def get_waiting_marble(self, color, fields_with_marbles):  # -> Marble:
        marbles_at_wait = self.get_marbles_at_wait(color, fields_with_marbles)
        if marbles_at_wait:
            return marbles_at_wait[0]
        return None

    @staticmethod
    def get_path_for_marble(marble, run_fields: int, fields_with_marbles, get_shorter_path=False) -> []:
        """Returns a path for a marble if it exists. """
        current_field = BoardState.get_field_for_marble(marble, fields_with_marbles)
        return Board.get_path_for_color(marble.color_, current_field, run_fields, fields_with_marbles, get_shorter_path)

    @staticmethod
    def get_path_for_color(marble_color, current_field, run_fields: int, fields_with_marbles, get_shorter_path=False):
        """Returns a path for a marble if it exists. Assumed is that there is max 1 path."""
        path: List[Field] = []
        for step in range(abs(run_fields)):
            next_fields = current_field.next_fields
            for next_field in next_fields:
                if Board.is_next_field_allowed(marble_color, current_field, next_field, fields_with_marbles):
                    path.append(next_field)
                    current_field = next_field
                    # Only 1 allowed next field is assumed
                    break
        if get_shorter_path or len(path) == abs(run_fields):
            return path
        return []

    @staticmethod
    def is_next_field_allowed(marble_color, current_field, next_field, fields_with_marbles) -> bool:  # Not backwards
        if next_field not in current_field.next_fields:
            return False  # Field has to be in next fields if moving forward
        elif next_field.type_ == FieldType.HOME: 
            if next_field.color_ != marble_color:
                return False  # It is a home field of other player
            elif fields_with_marbles:
                # Home field of same color. In this variant marble passing in HOME is not allowed.
                marble_on_next_field = BoardState.get_marble_for_field_opt(next_field, fields_with_marbles)
                if marble_on_next_field and marble_on_next_field.color_ == marble_color:
                    return False
        elif next_field.type_ == FieldType.START and next_field.color_ == marble_color:
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
    """Marble type. Has an id and color. The raw id is used for the action space: N0, N1, .., W3, W4."""
    def __init__(self, id_, color_, raw_id):
        self.id_ = id_
        self.color_ = color_
        self.raw_id = raw_id

    def __str__(self):
        return "Marble[{0}], color: {1}.".format(self.id_, self.color_)

    def get_str(self) -> str:
        return self.color_[0]


class BoardState:
    """Manages the positions of marbles on fields."""

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
            if current_field:  # and self.get_marble_for_field_opt(current_field):
                del fields_with_marbles[current_field]
                # del self.marbles_with_fields[marble]
            # Put marble on new field
            fields_with_marbles[field] = marble
            # self.marbles_with_fields[marble] = field
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

    FIELDID_STATEINDEX_MAP = {5: 0, 6: 1, 7: 2, 8: 3, 9: 4, 10: 5, 11: 6, 12: 7, 13: 8, 22: 9, 21: 10, 20: 11, 19: 12,
                              18: 13, 14: 14, 15: 15, 16: 16, 17: 17, 23: 18, 24: 19, 25: 20, 26: 21, 27: 22, 28: 23,
                              29: 24, 30: 25, 31: 26, 40: 27, 39: 28, 38: 29, 37: 30, 36: 31, 32: 32, 33: 33, 34: 34,
                              35: 35, 41: 36, 42: 37, 43: 38, 44: 39, 45: 40, 46: 41, 47: 42, 48: 43, 49: 44, 58: 45,
                              57: 46, 56: 47, 55: 48, 54: 49, 50: 50, 51: 51, 52: 52, 53: 53, 59: 54, 60: 55, 61: 56,
                              62: 57, 63: 58, 64: 59, 65: 60, 66: 61, 67: 62, 4: 63, 3: 64, 2: 65, 1: 66, 0: 67,
                              68: 68, 69: 69, 70: 70, 71: 71}

    @staticmethod
    def get_board_state_as_matrix(fields_with_marbles, board, players: [Player]):
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
