# Card operations
from rlcard.games.keezen.board import BoardState, FieldType, Board
from rlcard.games.keezen.move import Move, MoveType, MarbleMove


class CardOpStart:
    """Card operation implementation for start move."""

    def __init__(self, board: Board):
        """Create card operation for board."""
        self.board = board

    def get_moves(self, player, plays_with_color, card, fields_with_marbles) -> [Move]:
        """Evaluate if the player can move to start in given board position. """
        moves = []
        start_field = self.board.get_start_field_with_color(plays_with_color)
        marble_on_start = BoardState.get_marble_for_field_opt(start_field, fields_with_marbles)
        if marble_on_start is None or marble_on_start.color_ != plays_with_color:
            # No blocking marble on start field
            waiting_marble = self.board.get_waiting_marble(plays_with_color, fields_with_marbles)
            if waiting_marble is not None:
                # There is a marble ready to set up
                waiting_field = BoardState.get_field_for_marble(waiting_marble, fields_with_marbles)
                marble_move = MarbleMove(waiting_marble, waiting_field, start_field, [])
                marble_move.hit_marble_moves = self.get_hit_marble_moves(marble_move, fields_with_marbles)
                move = Move(MoveType.START, player, [card], [marble_move])
                moves.append(move)
        return moves

    def get_hit_marble_moves(self, marble_move, fields_with_marbles) -> []:
        marble_on_field = BoardState.get_marble_for_field_opt(marble_move.to_field, fields_with_marbles)
        if marble_on_field is not None:
            wait_field = self.board.get_empty_wait_field_with_color(marble_on_field.color_, fields_with_marbles)
            return [MarbleMove(marble_on_field, marble_move.to_field, wait_field, [])]
        return []


class CardOpRun:
    """Card operation implementation for run move."""

    def __init__(self, board, run_fields):
        """Create card operation with board and run fields."""
        self.board = board
        self.run_fields = run_fields

    def get_moves(self, player, plays_with_color, card, fields_with_marbles) -> [Move]:
        """Evaluate if the player can run with marbles in given board position. """
        moves = []
        for marble in self.board.get_marbles_with_color(plays_with_color):
            # Assume 1 path
            path = self.board.get_path_for_marble(marble, self.run_fields, fields_with_marbles)
            if path:
                from_field = BoardState.get_field_for_marble(marble, fields_with_marbles)
                marble_move = MarbleMove(marble, from_field, path[-1], path)
                marble_move.hit_marble_moves = self.get_hit_marble_moves(marble_move, fields_with_marbles)
                move = Move(MoveType.RUN, player, [card], [marble_move])
                moves.append(move)
        return moves

    def get_hit_marble_moves(self, marble_move, fields_with_marbles) -> []:
        marble_on_field = BoardState.get_marble_for_field_opt(marble_move.to_field, fields_with_marbles)
        if marble_on_field is not None:
            wait_field = self.board.get_empty_wait_field_with_color(marble_on_field.color_, fields_with_marbles)
            return [MarbleMove(marble_on_field, marble_move.to_field, wait_field, [])]
        return []


class CardOpSwitchOneOwnMarble:
    """Card operation implementation for switch move."""

    def __init__(self, board):
        """Create card operation with board."""
        self.board = board

    def get_moves(self, player, plays_with_color, card, fields_with_marbles) -> [Move]:
        """Evaluate if the player can switch with marbles in given board position. """
        moves = []
        plays_with_marbles = self.board.get_marbles_with_color(plays_with_color)
        for marble1 in plays_with_marbles:
            marble1_field = BoardState.get_field_for_marble(marble1, fields_with_marbles)
            if self.is_marble_switchable(marble1, marble1_field, plays_with_color):
                for marble2 in [marble for marble in self.board.marbles if marble not in plays_with_marbles]:
                    marble2_field = BoardState.get_field_for_marble(marble2, fields_with_marbles)
                    if self.is_marble_switchable(marble2, marble2_field, plays_with_color):
                        marble_move1 = MarbleMove(marble1, marble1_field, marble2_field, [])
                        marble_move2 = MarbleMove(marble2, marble2_field, marble1_field, [])
                        marble_moves = [marble_move1, marble_move2]
                        moves.append(Move(MoveType.SWITCH, player, [card], marble_moves))
        return moves

    @staticmethod
    def is_marble_switchable(marble, marble_field, plays_with_color) -> bool:
        if marble_field.type_ == FieldType.WAIT or marble_field.type_ == FieldType.HOME:
            return False
        elif marble_field.type_ == FieldType.START and marble_field.color_ == marble.color_:
            # If marble on field with same color switch is only allowed for current player
            return marble.color_ == plays_with_color
        return True


class CardOpSplitTwoMarbles:
    """Card operation implementation for split over two marbles move."""

    def __init__(self, board: Board):
        """Create card operation with board and run fields."""
        self.board = board
        self.run_fields = 7

    def get_moves(self, player, plays_with_color, card, fields_with_marbles) -> [Move]:
        """Evaluate if the player can move 7 steps with one or two marbles in given board position. """
        moves = []
        marbles_with_color = self.board.get_marbles_with_color(plays_with_color)
        for marble in marbles_with_color:
            path = self.board.get_path_for_marble(marble, 7, fields_with_marbles)  # Check path length 7
            if path:
                from_field = BoardState.get_field_for_marble(marble, fields_with_marbles)
                marble_move = MarbleMove(marble, from_field, path[-1], path)
                marble_move.hit_marble_moves = self._get_hit_marble_moves(marble_move, fields_with_marbles)
                move = Move(MoveType.SPLIT, player, [card], [marble_move])
                moves.append(move)
            # Check combinations with other own marbles
            for length in range(4, 7):  # 6, 5, and 4, check other marbles: 1, 2 and 3.
                path = self.board.get_path_for_marble(marble, length, fields_with_marbles, True)
                if len(path) == length:
                    # Move marble and check other marbles
                    c_state = fields_with_marbles.copy()  # Shallow copy is sufficient
                    marble_on_field = BoardState.put_marble_on_field(marble, path[-1], c_state)
                    if marble_on_field:  # Put hit marble on wait field
                        BoardState.put_marble_on_field(marble_on_field,
                                                    self.board.get_empty_wait_field_with_color(marble_on_field.color_,
                                                                                               c_state), c_state)
                    for marble2 in [other_marble for other_marble in marbles_with_color
                                    if other_marble != marble and other_marble != marble_on_field]:
                        path2 = self.board.get_path_for_marble(marble2, 7 - length, c_state)
                        if path2:
                            mm1 = MarbleMove(marble, BoardState.get_field_for_marble(marble, fields_with_marbles),
                                             path[-1], path)
                            mm1.hit_marble_moves = self._get_hit_marble_moves(mm1, fields_with_marbles)
                            mm2 = MarbleMove(marble2, BoardState.get_field_for_marble(marble2, fields_with_marbles),
                                             path2[-1], path2)
                            mm2.hit_marble_moves = self._get_hit_marble_moves(mm2, c_state)
                            move = Move(MoveType.SPLIT, player, [card], [mm1, mm2])
                            moves.append(move)
                else:  # Shorter path: check if a own marble is blocking the path
                    b_marble = self._is_blocked_by_own_marble(marble, path, fields_with_marbles)
                    if b_marble is not None:
                        # Check move with different order, try start moving with blocking marble
                        path = self.board.get_path_for_marble(b_marble, 7 - length, fields_with_marbles)
                        if path:
                            c_state = fields_with_marbles.copy()  # Shallow copy is sufficient
                            marble_on_field = BoardState.put_marble_on_field(b_marble, path[-1], c_state)
                            if marble_on_field:  # Put hit marble on wait field
                                BoardState.put_marble_on_field(marble_on_field,
                                                            self.board.get_empty_wait_field_with_color(
                                                                marble_on_field.color_, c_state), c_state)
                            path2 = self.board.get_path_for_marble(marble, length, c_state)
                            if path2:
                                mm1 = MarbleMove(b_marble, BoardState.get_field_for_marble(b_marble, fields_with_marbles), path[-1], path)
                                mm1.hit_marble_moves = self._get_hit_marble_moves(mm1, fields_with_marbles)
                                mm2 = MarbleMove(marble, BoardState.get_field_for_marble(marble, fields_with_marbles), path2[-1], path2)
                                mm2.hit_marble_moves = self._get_hit_marble_moves(mm2, c_state)
                                move = Move(MoveType.SPLIT, player, [card], [mm1, mm2])
                                moves.append(move)
        if not moves:
            # Check if player will finish his last marble to continue with teammate marbles
            if player.player_color == plays_with_color:
                # if player.get_team_mate().player_color == player.get_team_mate().plays_with_color:
                home_marbles = self.board.get_marbles_at_home(plays_with_color, fields_with_marbles)
                if len(home_marbles) == 3:
                    path_length = 0
                    for home_marble in home_marbles:
                        path_length += len(self.board.get_path_for_marble(home_marble, 3, fields_with_marbles, True))
                    if path_length == 0:
                        f_marble = [m for m in marbles_with_color if m not in home_marbles][0]
                        f_path = self.board.get_path_for_marble(f_marble, 6, fields_with_marbles, True)
                        if f_path and f_path[-1].type_ == FieldType.HOME:
                            # Find marbles of teammate that can move
                            tm_marbles = self.board.get_marbles_with_color(player.get_team_mate().player_color)
                            for tm_marble in tm_marbles:
                                path2 = self.board.get_path_for_marble(tm_marble, 7 - len(f_path), fields_with_marbles)
                                if path2:
                                    mm1 = MarbleMove(f_marble, BoardState.get_field_for_marble(f_marble, fields_with_marbles),
                                                     f_path[-1], f_path)
                                    mm2 = MarbleMove(tm_marble, BoardState.get_field_for_marble(tm_marble, fields_with_marbles),
                                                     path2[-1], path2)
                                    mm2.hit_marble_moves = self._get_hit_marble_moves(mm2, fields_with_marbles)
                                    move = Move(MoveType.SPLIT, player, [card], [mm1, mm2])
                                    moves.append(move)
        return moves

    def _get_hit_marble_moves(self, marble_move, fields_with_marbles) -> []:
        marble_on_field = BoardState.get_marble_for_field_opt(marble_move.to_field, fields_with_marbles)
        if marble_on_field is not None:
            wait_field = self.board.get_empty_wait_field_with_color(marble_on_field.color_, fields_with_marbles)
            return [MarbleMove(marble_on_field, marble_move.to_field, wait_field, [])]
        return []

    def _is_blocked_by_own_marble(self, marble, path, fields_with_marbles):
        """Returns a marble if it blocks the path of another marble."""
        last_field = BoardState.get_field_for_marble(marble, fields_with_marbles)
        if path:
            last_field = path[-1]
        if last_field.next_fields:
            for next_field in last_field.next_fields:
                if next_field.type_ == FieldType.HOME and next_field.color_ == marble.color_:
                    return BoardState.get_marble_for_field_opt(next_field, fields_with_marbles)
        return None
