import random
from copy import copy

from rlcard.games.mejn.board import Board, FieldType, BoardState
from rlcard.games.mejn.game import GameState, Game
from rlcard.games.mejn.move import Move


class RandomAgent:
    """Selects a random move."""
    def __init__(self, game: Game):
        self.game = game

    def throw_dice(self) -> int:
        return self.game.throw_dice()

    def get_move(self, moves: [Move], game_state: GameState):
        if not moves:
            return None
        return random.choice(moves)


class RuleBasedAgent:
    """Selects a move based on rule based logic."""
    def __init__(self, game):
        self.game = game
        self.board = game.board

    def throw_dice(self) -> int:
        return self.game.throw_dice()

    def get_move(self, moves: [Move], game_state: GameState):
        if not moves:
            return None
        if len(moves) == 1:
            return moves[0]
        move_evaluations = {}
        evaluator = RuleBasedMoveEvaluator(self.board, self.game)
        for move in moves:
            evaluation_result = evaluator.evaluate_move(move, game_state)
            move_evaluations[move] = evaluation_result
        highest_total = -1000
        best_move = None
        for move in move_evaluations.keys():
            eval_result = move_evaluations[move]
            total = 0.0
            for value in eval_result.values.values():
                total = total + value
            if total > highest_total:
                highest_total = total
                best_move = move
        return best_move


class RuleBasedMoveEvaluator:
    field_values = {}  # Dict with per color a dict with value per field.

    def __init__(self, board, game):
        self.board = board
        self.game = game
        if len(self.field_values) == 0:
            self.field_values = self._get_field_values()
        self.evaluatedMarblePositions = {}

    def _get_field_values(self) -> {}:
        """Run from start to last home field, giving values to the fields."""
        player_field_values = {}
        for player in self.game.players:
            fields_with_values = {}
            wait_fields_for_player = [field for field in self.board.waitFields if
                                      field.color_ == player.player_color]
            for waitField in wait_fields_for_player:
                fields_with_values[waitField] = 0.0
            start_field_for_player = self.board.get_start_field_with_color(player.player_color)
            fields_with_values[start_field_for_player] = 10.0
            path_from_start = Board.get_path_for_color(player.player_color, start_field_for_player, 100, None, True)
            field_value = 1.0
            delta_value = 1.0
            for field in path_from_start:
                if field.type_ == FieldType.START:
                    field_value -= 5
                elif field.type_ == FieldType.HOME:
                    delta_value += 10
                    field_value += 20  # Bonus for home (parking)
                field_value += delta_value
                fields_with_values[field] = field_value
            player_field_values[player.player_color] = fields_with_values
        return player_field_values

    def evaluate_move(self, move, game_state: GameState):
        evaluation_result = EvaluationResult()
        for marble_move in move.marble_moves:
            evaluation_result_before_move = self.evaluate_marble_position(marble_move.marble, move, game_state)
            for mm_hit in marble_move.hit_marble_moves:
                eval_result_hit = self.evaluate_marble_position(mm_hit.marble, move, game_state)
                evaluation_result_before_move.add(eval_result_hit)

            # Move the marble(s)
            c_game_state = copy(game_state)
            _ = BoardState.put_marble_on_field(marble_move.marble, marble_move.to_field,
                                               c_game_state.fields_with_marbles)
            for hit_marble_move in marble_move.hit_marble_moves:
                _ = BoardState.put_marble_on_field(hit_marble_move.marble, hit_marble_move.to_field,
                                                   c_game_state.fields_with_marbles)

            # Evaluate new position
            evaluation_result_after_move = self.evaluate_marble_position(marble_move.marble, move, c_game_state)
            for mm_hit in marble_move.hit_marble_moves:
                eval_result_hit = self.evaluate_marble_position(mm_hit.marble, move, c_game_state)
                evaluation_result_before_move.add(eval_result_hit)
            # Subtract to get marble move result
            evaluation_result_after_move.subtract(evaluation_result_before_move)

            evaluation_result.add(evaluation_result_after_move)
        return evaluation_result

    @staticmethod
    def get_marbles_in_path(fields, fields_with_marbles, with_color=None, without_color=None) -> {}:
        result = {}
        index = 0
        for field in fields:
            marble = BoardState.get_marble_for_field_opt(field, fields_with_marbles)
            if marble is not None and marble != without_color and (with_color is None or marble.color_ == with_color):
                result[index] = marble
            index += 1
        return result

    def get_parameter_name_for_marble(self, marble, parameter_name, game_state) -> str:
        """Determines if the marble is for self or others.
            Returns the correct parameter variant for the parameter_name (self)"""
        if marble.color_ == game_state.move_player.player_color:
            if parameter_name == EvaluationResult.HIT_SELF:
                return EvaluationResult.HIT_SELF
            else:
                return EvaluationResult.PROGRESS_SELF
        else:
            # Opponents colors
            if parameter_name == EvaluationResult.HIT_SELF:
                return EvaluationResult.HIT_OTHERS
            else:
                return EvaluationResult.PROGRESS_OTHERS

    def evaluate_marble_position(self, marble, move, c_game_state):  # -> EvaluationResult:
        """Evaluates a marble position.
         The position depends on:
         - field values (self, opponents)
         - hit risk values (self, opponents)"""
        # Start marble evaluation. Init with zero values
        result = EvaluationResult()
        move_player_marbles = self.game.board.get_marbles_with_color(c_game_state.move_player.player_color)

        # Progress of the marbles on the board
        evaluated_field_values_for_color = self.field_values[marble.color_]
        marble_field = BoardState.get_field_for_marble(marble, c_game_state.fields_with_marbles)
        evaluated_value = evaluated_field_values_for_color[marble_field]
        parameter = self.get_parameter_name_for_marble(marble, EvaluationResult.PROGRESS_SELF, c_game_state)
        if parameter == EvaluationResult.PROGRESS_OTHERS:
            # Others progress is negative for this player
            result.values[parameter] = evaluated_value * -1
        else:
            result.values[parameter] = evaluated_value

        # Determine if marbles within range might be hit from the back
        risk_of_being_hit = 0.0
        field = BoardState.get_field_for_marble(marble, c_game_state.fields_with_marbles)
        if field.type_ != FieldType.WAIT and field.type_ != FieldType.HOME:
            paths_max_length = self.board.get_path_for_color(marble.color_, field, -6, c_game_state.fields_with_marbles)
            if paths_max_length:
                marbles_in_path = self.get_marbles_in_path(paths_max_length, c_game_state.fields_with_marbles)
                for fieldIndex in marbles_in_path.keys():
                    marble_in_path = marbles_in_path[fieldIndex]
                    if marble_in_path:
                        if marble_in_path not in move_player_marbles:
                            risk = 1/6
                            risk_of_being_hit += risk

        # If on other color start field and waiting marbles, then there is a chance of being hit
        field = BoardState.get_field_for_marble(marble, c_game_state.fields_with_marbles)
        if field:
            if field.type_ == FieldType.START and field.color_ != marble.color_:
                waiting_marble = self.board.get_waiting_marble(field.color_, c_game_state.fields_with_marbles)
                if waiting_marble:
                    risk = 1/6
                    risk_of_being_hit += risk

        parameter = self.get_parameter_name_for_marble(marble, EvaluationResult.HIT_SELF, c_game_state)
        if parameter == EvaluationResult.HIT_OTHERS:
            # Others risk chance is positive for this player
            result.values[parameter] = risk_of_being_hit
        else:
            result.values[parameter] = -risk_of_being_hit

        return result


class EvaluationResult:
    PROGRESS_OTHERS = "PROGRESS_OTHERS"
    PROGRESS_SELF = "PROGRESS_SELF"
    HIT_OTHERS = "HIT_OTHERS"
    HIT_SELF = "HIT_SELF"
    PARKING = "PARKING"
    RANDOMNESS = "RANDOMNESS"
    ALL_PARAMS = [PROGRESS_OTHERS, PROGRESS_SELF, HIT_OTHERS, HIT_SELF, PARKING, RANDOMNESS]

    def __init__(self):
        self.values = {}
        for param in EvaluationResult.ALL_PARAMS:
            self.values[param] = 0.0

    def add(self, other_result):
        for param in other_result.values.keys():
            if param in EvaluationResult.ALL_PARAMS:
                self.values[param] = self.values[param] + other_result.values[param]

    def subtract(self, other_result):
        for param in other_result.values.keys():
            if param in EvaluationResult.ALL_PARAMS:
                self.values[param] = self.values[param] - other_result.values[param]
