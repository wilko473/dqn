from rlcard.games.mejn.board import Field, Marble
from rlcard.games.mejn.player import Player


class MoveType:
    START = "START"
    RUN = "RUN"
    NONE = "NONE"


class Move:
    """Represents a move of a player moving marbles."""

    def __init__(self, move_type: MoveType, player: Player, marble_moves, steps: int):
        """Creates a move."""
        self.move_type = move_type
        self.player = player
        self.marble_moves = marble_moves
        self.steps = steps
        self.raw_action = self._get_raw_action()

    def __str__(self):
        return "Move: {0} by player {1}.".format(self.move_type, self.player.name)

    def _get_raw_action(self):
        if self.move_type == MoveType.NONE:
            return "NO"
        elif self.move_type == MoveType.START:
            return "STP" + str(self.marble_moves[0].marble.raw_id)
        elif self.move_type == MoveType.RUN:
            return "RU" + str(self.steps).zfill(2) + "P" + str(self.marble_moves[0].marble.raw_id)


class MarbleMove:
    """Represents the move of a marble from one field to another.
    This marble move can contain moves of marbles that are hit."""

    def __init__(self, marble: Marble, from_field: Field, to_field: Field, steps: [Field]):
        self.marble = marble
        self.from_field = from_field
        self.to_field = to_field
        self.steps = steps
        self.hit_marble_moves = {}  # The hit marble moves are set during move creation.

    def __str__(self):
        return "Move {0} marble with ID {1} from field {2} to {3}. Hits: {4}.".format(self.marble.color_,
                                self.marble.id_, self.from_field.id_, self.to_field.id_, len(self.hit_marble_moves))
