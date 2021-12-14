import random
from copy import copy

from rlcard.games.keezen.board import Board, FieldType, BoardState
from rlcard.games.keezen.cardop import CardOpRun, CardOpSplitTwoMarbles, CardOpStart
from rlcard.games.keezen.game import GameState, GameActions
from rlcard.games.keezen.move import Move, MoveType


class RandomAgent:
    """Selects a random move."""
    def __init__(self, game):
        self.game = game

    def get_move(self, moves: [Move], game_state: GameState):
        if not moves:
            return None
        return random.choice(moves)


class RuleBasedAgent:
    """Selects a move based on rule based logic."""
    def __init__(self, game):
        self.game = game
        self.board = game.board

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
            fields_with_values[start_field_for_player] = 50.0
            path_from_start = Board.get_path_for_color(player.player_color, start_field_for_player, 100, None, True)
            field_value = 1.0
            delta_value = 1.0
            for field in path_from_start:
                if field.type_ == FieldType.START:
                    delta_value += 1
                    field_value += 15  # Bonus for passing start (prevent blocking)
                elif field.type_ == FieldType.HOME:
                    delta_value += 2
                    field_value += 50  # Bonus for home (parking)
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

    def get_run_path_lengths_for_cards(self, cards) -> []:
        """Returns the possible path lengths for cards. Walks to all cards with their card operations.
            Does not include all the split run lengths, just the max."""
        result = set()
        for card in cards:
            card_ops_for_card = self.game.card_ops[card]
            for cardOp in card_ops_for_card:
                if isinstance(cardOp, CardOpRun) or isinstance(cardOp, CardOpSplitTwoMarbles):
                    result.add(cardOp.run_fields)
        return sorted(result)

    @staticmethod
    def get_players_card_count(game_state) -> (int, int, int, int, int):
        """Returns the number of cards of player, opponents and teammate. (own, teammate, opponents, total, stock)"""
        own = len(game_state.player_cards[game_state.move_player])
        teammate = len(game_state.player_cards[game_state.move_player.get_team_mate()])
        opponents = game_state.player_cards - own - teammate
        played = len(game_state.played_cards)
        stock = len(game_state.stock_cards)
        return own, teammate, opponents, played, stock

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

    def get_parameter_name_for_marble(self, marble, parameter_name, game_state: GameState) -> str:
        """Determines if the marble is for self, teammate or others.
            Returns the correct parameter variant for the parameter_name (self)"""
        if marble.color_ == game_state.move_player_plays_with_color():
            # The color the move player is playing with (might be teammate color too)
            if parameter_name == EvaluationResult.HIT_SELF:
                return EvaluationResult.HIT_SELF
            elif parameter_name == EvaluationResult.BLOCK_SELF:
                return EvaluationResult.BLOCK_SELF
            else:
                return EvaluationResult.PROGRESS_SELF
        elif marble.color_ == game_state.players_play_with_color[game_state.move_player.get_team_mate()]:
            # The color the teammate is playing with
            if parameter_name == EvaluationResult.HIT_SELF:
                return EvaluationResult.HIT_TEAMMATE
            elif parameter_name == EvaluationResult.BLOCK_SELF:
                return EvaluationResult.BLOCK_TEAMMATE
            else:
                return EvaluationResult.PROGRESS_TEAMMATE
        else:
            # Opponents colors
            if parameter_name == EvaluationResult.HIT_SELF:
                return EvaluationResult.HIT_OTHERS
            elif parameter_name == EvaluationResult.BLOCK_SELF:
                return EvaluationResult.BLOCK_OTHERS
            else:
                return EvaluationResult.PROGRESS_OTHERS

    def risk_card_action_run(self, run_fields, possible_cards) -> float:
        """Determines the chance that a run card action might be played by other players.
            Returns a value between 0 and 1."""
        if len(possible_cards) == 0:
            return 0.0
        number_of_card_actions = 0
        for card in possible_cards:
            for cardop in self.game.card_ops[card]:
                if isinstance(cardop, CardOpRun):
                    if cardop.run_fields == run_fields:
                        number_of_card_actions += 1
        return number_of_card_actions/len(possible_cards)

    def risk_card_action_start(self, possible_cards) -> float:
        """Determines the chance that a starter cardop might be played by other players.
            Returns a value between 0 and 1."""
        if len(possible_cards) == 0:
            return 0.0
        number_of_card_actions = 0.0
        for card in possible_cards:
            for cardop in self.game.card_ops[card]:
                if isinstance(cardop, CardOpStart):
                    number_of_card_actions += 1
        return number_of_card_actions/len(possible_cards)

    def evaluate_marble_position(self, marble, move, c_game_state: GameState):  # -> EvaluationResult:
        """Evaluates a marble position.
         The position depends on:
         - field values (self, teammate, opponents)
         - block values (self, teammate, opponents)
         - hit risk values (self, teammate, opponents)"""
        # Start marble evaluation. Init with zero values
        result = EvaluationResult()

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

        # cardCounts = self.get_players_card_count(c_game_state)
        unknown_cards = list(c_game_state.stock_cards)
        for c_player in c_game_state.player_cards.keys():
            if c_player != c_game_state.move_player:
                unknown_cards.extend(c_game_state.player_cards[c_player])
        path_lengths = self.get_run_path_lengths_for_cards(unknown_cards)
        if path_lengths and False:  # TODO: check difference with/without
            move_player_plays_with_color = c_game_state.players_play_with_color[c_game_state.move_player]
            team_mate_plays_with_color = c_game_state.players_play_with_color[c_game_state.move_player.get_team_mate()]
            move_player_marbles = self.game.board.get_marbles_with_color(move_player_plays_with_color)
            team_mate_marbles = self.game.board.get_marbles_with_color(team_mate_plays_with_color)

            # Determine if marbles within range might be hit from the back (eg 1,2,3,5,6,7,8,9,10,12)
            risk_of_being_hit = 0.0
            max_path_length = max(path_lengths)
            if max_path_length > 0:
                field = BoardState.get_field_for_marble(marble, c_game_state.fields_with_marbles)
                if field.type_ != FieldType.START or field.color_ != marble.color_:
                    paths_max_length = self.board.get_path_for_color(marble.color_, field, -max_path_length,
                                                                     c_game_state.fields_with_marbles)
                    # for path in paths_max_length:
                    marbles_in_path = self.get_marbles_in_path(paths_max_length, c_game_state.fields_with_marbles)
                    for fieldIndex in marbles_in_path.keys():
                        marble_in_path = marbles_in_path[fieldIndex]
                        if marble_in_path:
                            if marble_in_path not in move_player_marbles and \
                                    marble_in_path not in team_mate_marbles:
                                risk = self.risk_card_action_run(fieldIndex + 1, unknown_cards)
                                risk_of_being_hit += risk
            # Determine if marbles within range might hit from the front (-4)
            min_path_length = min(path_lengths)
            if min_path_length < 0:
                field = BoardState.get_field_for_marble(marble, c_game_state.fields_with_marbles)
                if field.type_ != FieldType.START or field.color_ != marble.color_:
                    paths_min_length = self.board.get_path_for_color(marble.color_, field, -max_path_length,
                                                                     c_game_state.fields_with_marbles)
                    # for path in paths_min_length:
                    marbles_in_path = self.get_marbles_in_path(paths_min_length, c_game_state.fields_with_marbles)
                    for fieldIndex in marbles_in_path.keys():
                        marble_in_path = marbles_in_path[fieldIndex]
                        if marble_in_path:
                            if marble_in_path not in move_player_marbles and \
                                    marble_in_path not in team_mate_marbles:
                                risk = self.risk_card_action_run(fieldIndex + 1, unknown_cards)
                                risk_of_being_hit += risk

            # If on other color start field and waiting marbles, then there is a chance of being hit
            field = BoardState.get_field_for_marble(marble, c_game_state.fields_with_marbles)
            if field:
                if field.type_ == FieldType.START and field.color_ != marble.color_:
                    waiting_marble = self.board.get_waiting_marble(field.color_, c_game_state.fields_with_marbles)
                    if waiting_marble:
                        risk = self.risk_card_action_start(unknown_cards)
                        risk_of_being_hit += risk

            # progressMarble = result.parameters[EvaluationResult.PROGRESS_SELF] {
            #     riskOfBeingHit *= progressMarble
            # }
            parameter = self.get_parameter_name_for_marble(marble, EvaluationResult.HIT_SELF, c_game_state)
            if parameter == EvaluationResult.HIT_OTHERS:
                # Others risk chance is positive for this player
                result.values[parameter] = risk_of_being_hit
            else:
                result.values[parameter] = -risk_of_being_hit

            # Determine blocking parameters: is blocking self, teammate, others
            field = BoardState.get_field_for_marble(marble, c_game_state.fields_with_marbles)
            move_player_plays_with_color = c_game_state.players_play_with_color[c_game_state.move_player]
            if field.type_ == FieldType.START and field.color_ == marble.color_ and \
                    field.color_ == move_player_plays_with_color:
                # The marble is on a start field possibly blocking other marbles
                # If the movePlayer has a starter and a waiting marble it is blocked by his own marble
                self_blocked = 0.0
                waiting_marble = self.board.get_waiting_marble(field.color_, c_game_state.fields_with_marbles)
                if waiting_marble:
                    for card in c_game_state.player_cards[c_game_state.move_player]:
                        if card not in move.cards:
                            card_actions = self.game.card_ops[card]
                            for cardAction in card_actions:
                                if isinstance(cardAction, CardOpStart):
                                    # There is a marble on start and player has a starter
                                    self_blocked = -50
                                    break
                    if self_blocked == 0:
                        # Check if the marble is being blocked by others
                        path = self.board.get_path_for_color(marble.color_, field, max_path_length,
                                                              c_game_state.fields_with_marbles, True)
                        # for path in paths:
                            # Get the path indexes with marbles on it
                        if path:
                            marbles_in_path = self.get_marbles_in_path(path, c_game_state.fields_with_marbles)
                            for index_in_path in marbles_in_path.keys():
                                if marbles_in_path[index_in_path].color_ != marble.color_:
                                    marble_in_path_field = c_game_state.board_state.get_marble_from_field_opt[
                                        marbles_in_path[index_in_path]]
                                    if marble_in_path_field is not None:
                                        # Marble is being blocked. The path length is important.
                                        self_blocked = (marbles_in_path[index_in_path]/12) * -100
                                        break

                    # Check if marble is blocking teammate or opponents
                    paths = self.board.get_path_for_color(marble.color_, field, -max_path_length,
                                                          c_game_state.fields_with_marbles, True)
                    team_mate_blocked = 0.0
                    opponents_blocked = 0.0
                    for path in paths:
                        # Get the path indexes with marbles on it
                        marbles_in_path = self.get_marbles_in_path([path], c_game_state.fields_with_marbles)
                        for marbleInPathIndex in marbles_in_path.keys():
                            blocked_length_factor = (12 - marbleInPathIndex)/12
                            if marbles_in_path[marbleInPathIndex] in team_mate_marbles:
                                team_mate_blocked = -100 * blocked_length_factor
                            elif marbles_in_path[marbleInPathIndex] not in move_player_marbles:
                                opponents_blocked = 100 * blocked_length_factor

                    result.values[EvaluationResult.BLOCK_SELF] = self_blocked
                    result.values[EvaluationResult.BLOCK_TEAMMATE] = team_mate_blocked
                    result.values[EvaluationResult.BLOCK_OTHERS] = opponents_blocked

                    # Chance of being switched is lower on start
                    result.values[EvaluationResult.SWITCHING] = 25
        return result


class EvaluationResult:
    PROGRESS_OTHERS = "PROGRESS_OTHERS"
    PROGRESS_TEAMMATE = "PROGRESS_TEAMMATE"
    PROGRESS_SELF = "PROGRESS_SELF"
    HIT_OTHERS = "HIT_OTHERS"
    HIT_TEAMMATE = "HIT_TEAMMATE"
    HIT_SELF = "HIT_SELF"
    BLOCK_OTHERS = "BLOCK_OTHERS"
    BLOCK_TEAMMATE = "BLOCK_TEAMMATE"
    BLOCK_SELF = "BLOCK_SELF"
    PARKING = "PARKING"
    SWITCHING = "SWITCHING"
    CARD_VALUE = "CARD_VALUE"
    RANDOMNESS = "RANDOMNESS"
    ALL_PARAMS = [PROGRESS_OTHERS, PROGRESS_TEAMMATE, PROGRESS_SELF, HIT_OTHERS, HIT_TEAMMATE, HIT_SELF, BLOCK_OTHERS,
                  BLOCK_TEAMMATE, BLOCK_SELF, PARKING, SWITCHING, CARD_VALUE, RANDOMNESS]

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


class RuleBasedAgentAdapter:

    def __init__(self, rule_based_agent: RuleBasedAgent):
        self.rule_based_agent = rule_based_agent

    def eval_step(self, state):
        allowed_moves = state.get('allowed_moves')
        game_state = state.get('game_state')
        move = self.rule_based_agent.get_move(allowed_moves, game_state)
        if not move:
            return "NO", [1]
        return move.raw_action, [1]
        # Translate move (with marble_moves) back to legal_action (index)
        # move_action_index = GameActions.ALL_ACTIONS_255.index(move.raw_action)
        # legal_actions = state.get('legal_actions')
        # if move_action_index in legal_actions:
        #     return move_action_index, [1]
        # print("NO MOVE!")
        # return None

    def step(self, state):
        action, _ = self.eval_step(state)
        return action

    def use_raw(self):
        return False
